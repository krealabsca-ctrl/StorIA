"""Chat endpoints — bot del cliente y asistente del admin.

Estos endpoints son intencionalmente públicos (sin JWT) porque alimentan
los widgets de chat en el frontend. El chat del cliente nunca expone
costos ni ubicaciones. El chat del admin sí expone ubicaciones físicas
en el almacén y stock detallado.
"""
from __future__ import annotations

import re
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.inventory import Brand, Category, Product, StockStatus
from app.models.locations import Location, ProductLocation


router = APIRouter()


# ---------- Schemas ----------

class ChatMessage(BaseModel):
    """Mensaje entrante del usuario."""

    message: str = Field(..., min_length=1, max_length=500)


class ProductHit(BaseModel):
    """Producto encontrado, formato compacto para el chat."""

    id: int
    sku: str
    name: str
    price: float
    in_stock: bool
    stock_current: Optional[int] = None  # solo se llena en el chat admin
    location: Optional[str] = None       # solo se llena en el chat admin


class ChatResponse(BaseModel):
    """Respuesta del bot."""

    reply: str
    intent: str
    products: List[ProductHit] = []
    suggestions: List[str] = []


# ---------- Utilidades de búsqueda ----------

_STOPWORDS = {
    "el", "la", "los", "las", "un", "una", "de", "del", "y", "o",
    "para", "por", "con", "que", "donde", "donde", "como", "es",
    "necesito", "quiero", "tienen", "tienes", "tiene", "buscar",
    "busco", "muestra", "muestrame", "muéstrame", "puedo", "ver",
    "hay", "esta", "está", "estan", "están", "informacion", "información",
    "producto", "productos", "ubicacion", "ubicación", "stock",
    "cuanto", "cuánto", "cual", "cuál", "donde", "dónde",
}


def _tokenize(text: str) -> List[str]:
    text = text.lower().strip()
    tokens = re.findall(r"[a-záéíóúñü0-9\-\"/]+", text)
    return [t for t in tokens if t and t not in _STOPWORDS]


def _detect_sku(text: str) -> Optional[str]:
    # SKUs en este sistema son del tipo TOR-HEX-001, HERR-DES-001, etc.
    m = re.search(r"\b([A-Z]{2,5}-[A-Z0-9]{2,5}-\d{2,4})\b", text.upper())
    return m.group(1) if m else None


def _search_products(db: Session, query: str, limit: int = 5) -> List[Product]:
    sku = _detect_sku(query)
    if sku:
        product = db.query(Product).filter(Product.sku == sku).first()
        return [product] if product else []

    tokens = _tokenize(query)
    if not tokens:
        return []

    q = db.query(Product).filter(Product.is_active.is_(True))
    filters = []
    for tok in tokens:
        like = f"%{tok}%"
        filters.append(Product.name.ilike(like))
        filters.append(Product.description.ilike(like))
        filters.append(Product.sku.ilike(like))
    q = q.filter(or_(*filters))
    return q.limit(limit).all()


def _format_location(db: Session, product_id: int) -> Optional[str]:
    """Devuelve la mejor ubicación física del producto (primaria si existe)."""
    pl = (
        db.query(ProductLocation)
        .filter(ProductLocation.product_id == product_id)
        .order_by(ProductLocation.is_primary.desc(), ProductLocation.quantity.desc())
        .first()
    )
    if not pl:
        return None
    loc = db.query(Location).filter(Location.id == pl.location_id).first()
    if not loc:
        return None
    return f"{loc.code} ({loc.full_location}) — {pl.quantity} uds"


def _intent(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ("hola", "buenas", "buen día", "buenas tardes", "hey")):
        return "greeting"
    if any(w in t for w in ("gracias", "thanks", "thank you")):
        return "thanks"
    if any(w in t for w in ("ubicacion", "ubicación", "donde", "dónde", "pasillo", "estante")):
        return "location_query"
    if any(w in t for w in ("stock", "cuanto", "cuánto", "cuántas", "cantidad", "inventario")):
        return "stock_query"
    if any(w in t for w in ("precio", "cuesta", "vale", "cuánto", "costo")):
        return "price_query"
    if any(w in t for w in ("categoria", "categoría", "categorías", "lista", "catálogo", "catalogo")):
        return "category_query"
    return "product_search"


# ---------- Endpoints ----------

@router.post("/customer", response_model=ChatResponse)
def chat_customer(payload: ChatMessage, db: Session = Depends(get_db)):
    """Chat público para clientes del ecommerce.

    No expone ubicaciones físicas ni costos internos: solo precio de venta,
    si hay stock disponible y categorías. Si el cliente pregunta por una
    ubicación, lo redirige a contacto.
    """
    text = payload.message
    intent = _intent(text)

    if intent == "greeting":
        cats = db.query(Category).filter(Category.is_active.is_(True)).limit(5).all()
        return ChatResponse(
            reply="¡Hola! Soy el asistente de StorAI. Puedo ayudarte a encontrar productos en nuestro catálogo. ¿Qué necesitas?",
            intent=intent,
            suggestions=[f"Productos de {c.name}" for c in cats] or ["Ver catálogo", "Buscar por SKU"],
        )

    if intent == "thanks":
        return ChatResponse(
            reply="¡Con gusto! Si necesitas algo más, escríbeme.",
            intent=intent,
        )

    if intent == "category_query":
        cats = db.query(Category).filter(Category.is_active.is_(True)).all()
        return ChatResponse(
            reply="Estas son nuestras categorías disponibles:",
            intent=intent,
            suggestions=[c.name for c in cats],
        )

    if intent == "location_query":
        # Cliente pregunta por ubicación física → no se la damos.
        return ChatResponse(
            reply=(
                "La ubicación física en bodega es información interna. "
                "Si quieres adquirir el producto puedo darte el precio y "
                "decirte si tenemos stock. ¿De qué producto se trata?"
            ),
            intent=intent,
        )

    # Búsqueda de producto (incluye precio/stock)
    products = _search_products(db, text)
    if not products:
        return ChatResponse(
            reply=(
                "No encontré productos que coincidan con tu búsqueda. "
                "Intenta con el nombre del producto o un SKU (por ejemplo TOR-HEX-001)."
            ),
            intent=intent,
            suggestions=["Ver categorías", "Buscar Stanley", "Buscar Bosch"],
        )

    hits = [
        ProductHit(
            id=p.id,
            sku=p.sku,
            name=p.name,
            price=round(p.sale_price, 2),
            in_stock=p.stock_status != StockStatus.OUT_OF_STOCK,
        )
        for p in products
    ]

    if len(hits) == 1:
        h = hits[0]
        avail = "Disponible ahora" if h.in_stock else "Sin stock por ahora"
        reply = (
            f"Encontré **{h.name}** (SKU {h.sku}). "
            f"Precio: ${h.price:.2f}. {avail}."
        )
    else:
        reply = f"Encontré {len(hits)} productos que pueden interesarte:"

    return ChatResponse(reply=reply, intent=intent, products=hits)


@router.post("/admin", response_model=ChatResponse)
def chat_admin(payload: ChatMessage, db: Session = Depends(get_db)):
    """Chat para el panel administrativo.

    A diferencia del chat del cliente, este SÍ expone:
    - Ubicación física exacta del producto en el almacén
    - Stock actual y nivel de stock (low/out)
    - SKU y precios de costo y venta
    """
    text = payload.message
    intent = _intent(text)

    if intent == "greeting":
        return ChatResponse(
            reply=(
                "Hola admin. Escríbeme el nombre de un producto o un SKU "
                "y te diré dónde está y cuánto stock queda."
            ),
            intent=intent,
            suggestions=["Buscar TOR-HEX-001", "destornillador phillips", "Productos con stock bajo"],
        )

    if intent == "thanks":
        return ChatResponse(reply="A la orden.", intent=intent)

    if "bajo" in text.lower() and "stock" in text.lower():
        lows = (
            db.query(Product)
            .filter(Product.stock_status == StockStatus.LOW_STOCK, Product.is_active.is_(True))
            .limit(10)
            .all()
        )
        if not lows:
            return ChatResponse(reply="No hay productos con stock bajo ahora mismo.", intent="stock_query")
        hits = [
            ProductHit(
                id=p.id,
                sku=p.sku,
                name=p.name,
                price=round(p.sale_price, 2),
                in_stock=True,
                stock_current=p.stock_current,
                location=_format_location(db, p.id),
            )
            for p in lows
        ]
        return ChatResponse(
            reply=f"Hay {len(hits)} productos con stock bajo:",
            intent="stock_query",
            products=hits,
        )

    products = _search_products(db, text, limit=8)
    if not products:
        return ChatResponse(
            reply=(
                "No encontré productos con esa búsqueda. Probá con el SKU "
                "completo o parte del nombre."
            ),
            intent=intent,
            suggestions=["Buscar TOR-HEX-001", "destornillador", "Productos con stock bajo"],
        )

    hits: List[ProductHit] = []
    for p in products:
        hits.append(
            ProductHit(
                id=p.id,
                sku=p.sku,
                name=p.name,
                price=round(p.sale_price, 2),
                in_stock=p.stock_status != StockStatus.OUT_OF_STOCK,
                stock_current=p.stock_current,
                location=_format_location(db, p.id),
            )
        )

    if len(hits) == 1:
        h = hits[0]
        loc_part = f"📍 {h.location}" if h.location else "⚠️ Sin ubicación asignada"
        stock_part = (
            f"Stock actual: **{h.stock_current}** uds" if h.stock_current is not None else ""
        )
        reply = (
            f"**{h.name}** — SKU {h.sku}\n"
            f"{loc_part}\n"
            f"{stock_part}\n"
            f"Precio venta: ${h.price:.2f}"
        )
    else:
        reply = f"Encontré {len(hits)} productos. Cada tarjeta muestra ubicación y stock:"

    return ChatResponse(reply=reply, intent=intent, products=hits)
