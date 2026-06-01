"""Script para inicializar la base de datos con datos de prueba completos.

Pobla:
- Categorías, subcategorías y marcas (catálogo de ferretería)
- Ubicaciones de almacén
- Usuarios del sistema (admin, manager, warehouse_staff, sales)
- Usuarios de Telegram asociados
- Proveedores
- Productos con stock realista (varios estados)
- Asignaciones producto ↔ ubicación
- Movimientos de stock históricos
- Órdenes de clientes (ecommerce) de muestra
"""
import os
import sys
from datetime import datetime, timedelta
from random import choice, randint, seed

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.database import Base, SessionLocal, engine
from app.models import (
    Brand,
    Category,
    Location,
    Order,
    OrderItem,
    OrderStatus,
    Product,
    ProductLocation,
    StockMovement,
    Subcategory,
    Supplier,
    TelegramUser,
    User,
    UserRole,
)
from app.models.inventory import MovementType

seed(42)  # determinismo para repeticiones


def create_tables():
    print("🔨 Creando tablas de la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")


# ---------------------------------------------------------------------------
# Catálogo: categorías, subcategorías, marcas
# ---------------------------------------------------------------------------

CATEGORIES = [
    ("Herramientas", "Herramientas manuales y eléctricas"),
    ("Tornillería", "Tornillos, tuercas y arandelas"),
    ("Electricidad", "Componentes eléctricos y cableado"),
    ("Plomería", "Tubos, accesorios y fontanería"),
    ("Pinturas", "Pinturas y accesorios"),
    ("Seguridad", "Equipo de protección personal"),
    ("Jardinería", "Herramientas y accesorios de jardín"),
]

SUBCATEGORIES = {
    "Herramientas": ["Destornilladores", "Martillos", "Llaves", "Taladros", "Sierras"],
    "Tornillería": ["Hexagonales", "Phillips", "Allen", "Tuercas", "Arandelas"],
    "Electricidad": ["Cables", "Interruptores", "Tomacorrientes", "Bombillas LED"],
    "Plomería": ["Tubos PVC", "Codos", "Llaves de paso", "Tees"],
    "Pinturas": ["Esmaltes", "Vinilos", "Brochas", "Rodillos"],
    "Seguridad": ["Cascos", "Guantes", "Gafas", "Botas"],
    "Jardinería": ["Mangueras", "Tijeras", "Palas"],
}

BRANDS = [
    ("Stanley", "Herramientas de calidad profesional"),
    ("DeWalt", "Herramientas eléctricas industriales"),
    ("3M", "Productos industriales y seguridad"),
    ("Bosch", "Herramientas y accesorios"),
    ("Makita", "Herramientas eléctricas"),
    ("Truper", "Línea económica de ferretería"),
    ("Pavco", "Tubería y accesorios de PVC"),
    ("Phillips", "Iluminación y eléctricos"),
    ("Sherwin-Williams", "Pinturas y recubrimientos"),
]


def seed_categories(db: Session):
    print("📦 Creando categorías...")
    for name, desc in CATEGORIES:
        if not db.query(Category).filter(Category.name == name).first():
            db.add(Category(name=name, description=desc))
    db.commit()
    print(f"✅ {len(CATEGORIES)} categorías creadas")


def seed_subcategories(db: Session):
    print("📂 Creando subcategorías...")
    count = 0
    for cat_name, subs in SUBCATEGORIES.items():
        cat = db.query(Category).filter(Category.name == cat_name).first()
        if not cat:
            continue
        for sub in subs:
            if not db.query(Subcategory).filter(
                Subcategory.name == sub, Subcategory.category_id == cat.id
            ).first():
                db.add(Subcategory(name=sub, category_id=cat.id))
                count += 1
    db.commit()
    print(f"✅ {count} subcategorías creadas")


def seed_brands(db: Session):
    print("🏷️  Creando marcas...")
    for name, desc in BRANDS:
        if not db.query(Brand).filter(Brand.name == name).first():
            db.add(Brand(name=name, description=desc))
    db.commit()
    print(f"✅ {len(BRANDS)} marcas creadas")


# ---------------------------------------------------------------------------
# Ubicaciones de almacén
# ---------------------------------------------------------------------------

def seed_locations(db: Session):
    print("📍 Creando ubicaciones en el almacén...")
    zones = [
        ("A", "Zona Norte", 3, 3),   # pasillo, zona, estantes, niveles
        ("B", "Zona Sur", 3, 3),
        ("C", "Zona Este", 2, 3),
        ("D", "Zona Oeste", 2, 2),
    ]
    count = 0
    for aisle, zone, shelves, levels in zones:
        for s in range(1, shelves + 1):
            for lv in range(1, levels + 1):
                code = f"{aisle}-{s:02d}-{lv}"
                if db.query(Location).filter(Location.code == code).first():
                    continue
                loc = Location(
                    code=code,
                    name=f"Pasillo {aisle} Estante {s:02d} Nivel {lv}",
                    aisle=aisle,
                    shelf=f"{s:02d}",
                    level=str(lv),
                    zone=zone,
                    location_type="shelf",
                    capacity=100 + 25 * (3 - lv),
                )
                loc.generate_full_location()
                db.add(loc)
                count += 1
    db.commit()
    print(f"✅ {count} ubicaciones creadas")


# ---------------------------------------------------------------------------
# Usuarios del sistema (4 roles cubiertos)
# ---------------------------------------------------------------------------

USERS = [
    # username, email, full_name, phone, role, password, telegram_id, tg_username
    ("admin", "admin@storai.com", "Administrador del Sistema", "+573001234567",
     UserRole.ADMIN, "admin123", 123456789, "admin_telegram"),
    ("gerente", "gerente@storai.com", "Laura Pérez", "+573009876543",
     UserRole.MANAGER, "gerente123", 987654321, "gerente_telegram"),
    ("operario", "operario@storai.com", "Carlos Méndez", "+573005555555",
     UserRole.WAREHOUSE_STAFF, "operario123", 555555555, "operario_telegram"),
    ("operario2", "operario2@storai.com", "Ana Torres", "+573005555556",
     UserRole.WAREHOUSE_STAFF, "operario123", 555555556, "ana_torres"),
    ("vendedor", "vendedor@storai.com", "Diego Ramírez", "+573004443322",
     UserRole.SALES, "vendedor123", 444433322, "diego_sales"),
    ("vendedor2", "vendedor2@storai.com", "Sofía Castro", "+573004443323",
     UserRole.SALES, "vendedor123", 444433323, "sofia_sales"),
]


def seed_users(db: Session):
    print("👤 Creando usuarios y telegram users...")
    created = 0
    for (username, email, full_name, phone, role, pwd,
         tg_id, tg_username) in USERS:
        u = db.query(User).filter(User.username == username).first()
        if not u:
            u = User(
                username=username,
                email=email,
                full_name=full_name,
                phone=phone,
                role=role,
                is_active=True,
                hashed_password=get_password_hash(pwd),
            )
            db.add(u)
            db.flush()
            created += 1
        if not db.query(TelegramUser).filter(TelegramUser.telegram_id == tg_id).first():
            db.add(TelegramUser(
                telegram_id=tg_id,
                telegram_username=tg_username,
                telegram_first_name=full_name.split()[0],
                telegram_last_name=" ".join(full_name.split()[1:]) or None,
                user_id=u.id,
                is_active=True,
                is_verified=True,
            ))
    db.commit()
    print(f"✅ Usuarios procesados (creados {created}, total {len(USERS)})")


# ---------------------------------------------------------------------------
# Proveedores
# ---------------------------------------------------------------------------

SUPPLIERS = [
    ("Distribuidora Industrial S.A.", "PROV-001", "Carlos Rodríguez",
     "compras@distribuidora.com", "+573001112233", "Calle 123 #45-67",
     "Bogotá", "Colombia", "900123456-1"),
    ("Herramientas Pro Ltda.", "PROV-002", "María González",
     "ventas@herramientaspro.com", "+573004445566", "Avenida 45 #67-89",
     "Medellín", "Colombia", "900987654-2"),
    ("Eléctricos del Caribe S.A.S.", "PROV-003", "Juan Hernández",
     "j.hernandez@electricaribe.co", "+573005556677", "Cra 50 #80-12",
     "Barranquilla", "Colombia", "901111222-3"),
    ("Pinturas Andina", "PROV-004", "Patricia Vélez",
     "ventas@pinturasandina.com", "+573006667788", "Diagonal 33 #12-45",
     "Cali", "Colombia", "902222333-4"),
    ("Importadora de Tornillería", "PROV-005", "Roberto Silva",
     "roberto@imptornilleria.com", "+573007778899", "Calle 12 #34-56",
     "Bogotá", "Colombia", "903333444-5"),
]


def seed_suppliers(db: Session):
    print("🏢 Creando proveedores...")
    for (name, code, contact, email, phone, addr, city, country, tax) in SUPPLIERS:
        if db.query(Supplier).filter(Supplier.code == code).first():
            continue
        db.add(Supplier(
            name=name, code=code, contact_person=contact, email=email,
            phone=phone, address=addr, city=city, country=country,
            tax_id=tax, is_active=True,
        ))
    db.commit()
    print(f"✅ {len(SUPPLIERS)} proveedores creados")


# ---------------------------------------------------------------------------
# Productos
# ---------------------------------------------------------------------------

# (sku, name, description, categoria, marca, costo, venta, stock_inicial, stock_min)
PRODUCTS = [
    # Tornillería
    ("TOR-HEX-001", 'Tornillo Hexagonal 1/4"', "Tornillo hexagonal acero inox 1/4\"",
     "Tornillería", "Stanley", 0.50, 1.20, 150, 20),
    ("TOR-HEX-002", 'Tornillo Hexagonal 3/8"', "Tornillo hexagonal acero inox 3/8\"",
     "Tornillería", "Stanley", 0.75, 1.80, 8, 15),     # low
    ("TOR-PHI-001", 'Tornillo Phillips 1/4"', "Tornillo Phillips 1/4\" autorroscante",
     "Tornillería", "Truper", 0.40, 0.95, 0, 25),      # out
    ("TOR-ALN-001", 'Tornillo Allen M6', "Tornillo Allen M6 grado 8.8",
     "Tornillería", "Bosch", 0.60, 1.40, 220, 30),

    # Herramientas
    ("HERR-DES-001", "Destornillador Phillips #2", "Destornillador Phillips tamaño 2, mango ergonómico",
     "Herramientas", "Stanley", 3.50, 7.50, 45, 10),
    ("HERR-DES-002", "Destornillador Plano 1/4\"", "Destornillador plano 1/4\", mango con grip",
     "Herramientas", "Truper", 2.80, 6.20, 38, 10),
    ("HERR-MAR-001", "Martillo de Uña 16oz", "Martillo de uña 16oz con mango de fibra",
     "Herramientas", "Stanley", 8.50, 18.90, 22, 5),
    ("HERR-MAR-002", "Mazo de Goma 24oz", "Mazo de goma negro, 24oz",
     "Herramientas", "Truper", 6.20, 13.50, 14, 6),
    ("HERR-LLA-001", "Llave Inglesa 8\"", "Llave inglesa ajustable 8 pulgadas",
     "Herramientas", "Bosch", 9.00, 20.00, 18, 6),
    ("HERR-TAL-001", "Taladro Percutor 600W", "Taladro percutor 600W con maletín",
     "Herramientas", "DeWalt", 78.00, 145.00, 9, 3),
    ("HERR-TAL-002", "Taladro Inalámbrico 12V", "Taladro inalámbrico 12V + 2 baterías",
     "Herramientas", "Makita", 95.00, 178.00, 4, 3),     # low
    ("HERR-SIE-001", "Sierra Circular 7-1/4\"", "Sierra circular 7-1/4\" 1400W",
     "Herramientas", "DeWalt", 110.00, 210.00, 0, 2),    # out

    # Electricidad
    ("ELE-CAB-001", "Cable THW Cal. 12 (m)", "Cable eléctrico THW calibre 12 por metro",
     "Electricidad", "Phillips", 0.45, 1.10, 800, 100),
    ("ELE-INT-001", "Interruptor Sencillo Blanco", "Interruptor sencillo línea blanca",
     "Electricidad", "Phillips", 1.20, 3.20, 65, 15),
    ("ELE-TOM-001", "Tomacorriente Doble", "Tomacorriente doble con tierra",
     "Electricidad", "Phillips", 2.10, 4.80, 48, 12),
    ("ELE-LED-001", "Bombilla LED 9W E27", "Bombilla LED 9W rosca E27 luz cálida",
     "Electricidad", "Phillips", 1.80, 4.50, 120, 25),
    ("ELE-LED-002", "Tubo LED T8 18W", "Tubo LED T8 18W 1.2m blanco frío",
     "Electricidad", "Phillips", 5.50, 12.00, 30, 10),

    # Plomería
    ("PLO-TUB-001", "Tubo PVC 1/2\" x 3m", "Tubo PVC presión 1/2\" x 3m",
     "Plomería", "Pavco", 3.20, 7.50, 55, 15),
    ("PLO-COD-001", "Codo PVC 1/2\" 90°", "Codo PVC 1/2\" a 90 grados",
     "Plomería", "Pavco", 0.30, 0.90, 180, 40),
    ("PLO-LLA-001", "Llave de Paso 1/2\"", "Llave de paso 1/2\" bronce",
     "Plomería", "Pavco", 4.80, 10.50, 28, 8),

    # Pinturas
    ("PIN-ESM-001", "Esmalte Blanco 1gal", "Esmalte sintético blanco brillante 1 galón",
     "Pinturas", "Sherwin-Williams", 12.50, 26.00, 40, 8),
    ("PIN-VIN-001", "Vinilo Tipo 1 Blanco 1gal", "Pintura vinilo tipo 1 blanco 1 galón",
     "Pinturas", "Sherwin-Williams", 9.00, 19.50, 35, 10),
    ("PIN-BRO-001", "Brocha 3\"", "Brocha de cerda natural 3 pulgadas",
     "Pinturas", "Truper", 1.40, 3.20, 88, 20),
    ("PIN-ROD-001", "Rodillo 9\" + Felpa", "Rodillo 9\" con felpa de lana",
     "Pinturas", "Truper", 2.20, 4.80, 60, 15),

    # Seguridad
    ("SEG-CAS-001", "Casco de Seguridad Amarillo", "Casco de seguridad tipo I, amarillo",
     "Seguridad", "3M", 6.50, 14.00, 50, 10),
    ("SEG-GAF-001", "Gafas de Protección Claras", "Gafas de protección lentes claros",
     "Seguridad", "3M", 2.10, 5.20, 110, 20),
    ("SEG-GUA-001", "Guantes de Nitrilo (par)", "Guantes de nitrilo industrial talla M",
     "Seguridad", "3M", 1.10, 3.00, 7, 25),                # low
    ("SEG-BOT-001", "Botas de Seguridad Talla 42", "Botas con punta de acero talla 42",
     "Seguridad", "3M", 22.00, 48.00, 16, 4),

    # Jardinería
    ("JAR-MAN-001", "Manguera 15m 1/2\"", "Manguera de jardín 15m 1/2\" con conector",
     "Jardinería", "Truper", 8.00, 18.50, 24, 6),
    ("JAR-TIJ-001", "Tijera para Podar", "Tijera para podar ramas mango ergonómico",
     "Jardinería", "Stanley", 5.50, 12.50, 19, 5),
    ("JAR-PAL-001", "Pala Cuadrada", "Pala cuadrada con mango de madera",
     "Jardinería", "Truper", 7.20, 16.00, 0, 4),           # out
]


def seed_products(db: Session):
    print("🔩 Creando productos...")
    cat_map = {c.name: c.id for c in db.query(Category).all()}
    brand_map = {b.name: b.id for b in db.query(Brand).all()}

    barcode_seq = 7501234567000
    count = 0
    for (sku, name, desc, cat, brand, cost, sale, stock, stock_min) in PRODUCTS:
        if db.query(Product).filter(Product.sku == sku).first():
            continue
        p = Product(
            sku=sku,
            barcode=str(barcode_seq + count),
            name=name,
            description=desc,
            category_id=cat_map.get(cat),
            brand_id=brand_map.get(brand),
            cost_price=cost,
            sale_price=sale,
            stock_current=stock,
            stock_minimum=stock_min,
            is_active=True,
            is_available_for_sale=True,
        )
        p.update_stock_status()
        db.add(p)
        count += 1
    db.commit()
    print(f"✅ {count} productos creados (total catálogo: {len(PRODUCTS)})")


# ---------------------------------------------------------------------------
# Asignaciones producto ↔ ubicación
# ---------------------------------------------------------------------------

def seed_product_locations(db: Session):
    print("🗺️  Asignando productos a ubicaciones...")
    products = db.query(Product).all()
    locations = db.query(Location).all()
    if not locations:
        print("⚠️  No hay ubicaciones, salto el paso")
        return

    count = 0
    # Cada producto: una ubicación primaria + 30% chance de secundaria
    for i, p in enumerate(products):
        # ubicación primaria: distribuida por categoría para no apelotonarlas
        primary = locations[i % len(locations)]
        if not db.query(ProductLocation).filter(
            ProductLocation.product_id == p.id,
            ProductLocation.location_id == primary.id,
        ).first():
            db.add(ProductLocation(
                product_id=p.id,
                location_id=primary.id,
                quantity=p.stock_current,
                is_primary=True,
            ))
            count += 1
        # secundaria opcional, con una fracción del stock
        if p.stock_current > 30 and (i % 3 == 0):
            sec = locations[(i + 7) % len(locations)]
            if sec.id != primary.id and not db.query(ProductLocation).filter(
                ProductLocation.product_id == p.id,
                ProductLocation.location_id == sec.id,
            ).first():
                db.add(ProductLocation(
                    product_id=p.id,
                    location_id=sec.id,
                    quantity=max(1, p.stock_current // 4),
                    is_primary=False,
                ))
                count += 1
    db.commit()
    print(f"✅ {count} asignaciones producto↔ubicación creadas")


# ---------------------------------------------------------------------------
# Movimientos de stock históricos (para que /dashboard tenga datos)
# ---------------------------------------------------------------------------

def seed_stock_movements(db: Session):
    print("📈 Generando movimientos de stock históricos...")
    products = db.query(Product).limit(15).all()
    count = 0
    for p in products:
        # Entrada inicial
        db.add(StockMovement(
            product_id=p.id,
            movement_type=MovementType.IN,
            quantity=p.stock_current + 20,
            previous_stock=0,
            new_stock=p.stock_current + 20,
            reason="Compra inicial a proveedor",
            reference_type="purchase",
        ))
        # Salida posterior
        sold = randint(5, 20)
        db.add(StockMovement(
            product_id=p.id,
            movement_type=MovementType.OUT,
            quantity=sold,
            previous_stock=p.stock_current + 20,
            new_stock=p.stock_current + 20 - sold,
            reason="Venta a cliente",
            reference_type="order",
        ))
        count += 2
    db.commit()
    print(f"✅ {count} movimientos de stock creados")


# ---------------------------------------------------------------------------
# Clientes / órdenes (no hay tabla Customer, son campos en Order)
# ---------------------------------------------------------------------------

CUSTOMERS = [
    ("María Fernández", "maria.fernandez@example.com", "+573201112233",
     "Calle 100 #15-23, apto 502", "Bogotá"),
    ("Andrés López", "andres.lopez@example.com", "+573102224455",
     "Cra 70 #50-10", "Medellín"),
    ("Camila Ríos", "camila.rios@example.com", "+573150006677",
     "Avenida 6N #12-34", "Cali"),
    ("Felipe Salazar", "f.salazar@example.com", "+573004448899",
     "Calle 84 #11-20", "Barranquilla"),
    ("Daniela Ortiz", "daniela.ortiz@example.com", "+573009990011",
     "Carrera 7 #80-55, of 301", "Bogotá"),
]


def seed_orders(db: Session):
    print("🛒 Creando órdenes de cliente (ecommerce) de muestra...")
    products = db.query(Product).filter(Product.is_active.is_(True)).all()
    if not products:
        print("⚠️  No hay productos, salto el paso")
        return

    count = 0
    today = datetime.utcnow()
    statuses = [
        OrderStatus.DELIVERED.value, OrderStatus.SHIPPED.value,
        OrderStatus.PROCESSING.value, OrderStatus.PENDING.value, OrderStatus.DELIVERED.value,
    ]
    for idx, (name, email, phone, addr, city) in enumerate(CUSTOMERS, start=1):
        order_number = f"ORD-2026-{idx:04d}"
        if db.query(Order).filter(Order.order_number == order_number).first():
            continue

        # 1-3 ítems por orden
        chosen = []
        for _ in range(randint(1, 3)):
            chosen.append(choice(products))

        subtotal = 0.0
        items_payload = []
        for prod in chosen:
            qty = randint(1, 4)
            line = round(prod.sale_price * qty, 2)
            subtotal += line
            items_payload.append((prod, qty, line))

        tax = round(subtotal * 0.16, 2)
        shipping = 5.0 if subtotal < 100 else 0.0
        total = round(subtotal + tax + shipping, 2)

        order_date = today - timedelta(days=idx * 2)
        order = Order(
            order_number=order_number,
            customer_name=name,
            customer_email=email,
            customer_phone=phone,
            shipping_address=addr,
            shipping_city=city,
            shipping_country="Colombia",
            subtotal=subtotal,
            tax_amount=tax,
            shipping_cost=shipping,
            total_amount=total,
            status=statuses[idx - 1],
            is_paid=statuses[idx - 1] != OrderStatus.PENDING.value,
            order_date=order_date.isoformat(),
            customer_notes=None,
        )
        db.add(order)
        db.flush()

        for (prod, qty, line) in items_payload:
            db.add(OrderItem(
                order_id=order.id,
                product_id=prod.id,
                product_name=prod.name,
                product_sku=prod.sku,
                quantity=qty,
                unit_price=prod.sale_price,
                subtotal=line,
            ))
        count += 1
    db.commit()
    print(f"✅ {count} órdenes de cliente creadas")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("🚀 Inicializando base de datos de StorAI...\n")
    try:
        create_tables()
        db = SessionLocal()
        try:
            seed_categories(db)
            seed_subcategories(db)
            seed_brands(db)
            seed_locations(db)
            seed_users(db)
            seed_suppliers(db)
            seed_products(db)
            seed_product_locations(db)
            seed_stock_movements(db)
            seed_orders(db)

            print("\n✅ Base de datos inicializada exitosamente!\n")
            print("📝 Credenciales de prueba:")
            print("   - admin     / admin123      (ADMIN)")
            print("   - gerente   / gerente123    (MANAGER)")
            print("   - operario  / operario123   (WAREHOUSE_STAFF)")
            print("   - operario2 / operario123   (WAREHOUSE_STAFF)")
            print("   - vendedor  / vendedor123   (SALES)")
            print("   - vendedor2 / vendedor123   (SALES)")
            print("\n🤖 IDs de Telegram registrados (todos verificados):")
            for u in USERS:
                print(f"   - {u[0]:<10s} → {u[6]}")
        finally:
            db.close()
    except Exception as e:  # pylint: disable=broad-except
        print(f"\n❌ Error al inicializar la base de datos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
