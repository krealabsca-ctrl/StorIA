"""Handlers para comandos y mensajes del Bot de Telegram"""
import logging
import time
from datetime import datetime
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import (
    TelegramUser, Product, ProductLocation, Location, 
    TelegramQueryLog, StockStatus
)
from app.config import settings

logger = logging.getLogger(__name__)


def get_db_session() -> Session:
    """Obtener sesión de base de datos"""
    return SessionLocal()


def verify_telegram_user(telegram_id: int) -> Optional[TelegramUser]:
    """Verificar si el usuario de Telegram está autorizado como empleado"""
    db = get_db_session()
    try:
        telegram_user = db.query(TelegramUser).filter(
            TelegramUser.telegram_id == telegram_id,
            TelegramUser.is_active == True,
            TelegramUser.is_verified == True
        ).first()
        return telegram_user
    finally:
        db.close()


def log_query(telegram_user_id: int, query_text: str, query_type: str, 
              products_found: int, response_time_ms: float, product_ids: str = None):
    """Registrar consulta en el log de analytics"""
    db = get_db_session()
    try:
        log = TelegramQueryLog(
            telegram_user_id=telegram_user_id,
            query_text=query_text,
            query_type=query_type,
            products_found=products_found,
            response_time_ms=response_time_ms,
            product_ids=product_ids
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error(f"Error al registrar log de consulta: {e}")
        db.rollback()
    finally:
        db.close()


def format_product_message(product: Product, locations: list) -> str:
    """Formatear mensaje de respuesta con información del producto"""
    
    # Determinar estado de disponibilidad
    status_emoji = {
        StockStatus.AVAILABLE: "✅",
        StockStatus.LOW_STOCK: "⚠️",
        StockStatus.OUT_OF_STOCK: "❌"
    }
    status_text = {
        StockStatus.AVAILABLE: "Disponible",
        StockStatus.LOW_STOCK: "Stock Crítico",
        StockStatus.OUT_OF_STOCK: "Agotado"
    }
    
    emoji = status_emoji.get(product.stock_status, "❓")
    status = status_text.get(product.stock_status, "Desconocido")
    
    # Formatear ubicaciones
    locations_text = ""
    if locations:
        locations_list = []
        for loc in locations:
            if loc.location and loc.location.full_location:
                locations_list.append(f"📍 {loc.location.full_location} ({loc.quantity} unidades)")
        locations_text = "\n" + "\n".join(locations_list) if locations_list else "\n📍 Ubicación no asignada"
    else:
        locations_text = "\n📍 Ubicación no asignada"
    
    message = f"""
*{emoji} {product.name}*

📋 *SKU:* {product.sku}
📊 *Stock Actual:* {product.stock_current} unidades
📉 *Stock Mínimo:* {product.stock_minimum} unidades
🏷️ *Estado:* {status}
💰 *Precio Venta:* ${product.sale_price:,.2f}
{locations_text}
"""
    return message


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /start"""
    user = update.effective_user
    
    # Verificar si el usuario está autorizado
    telegram_user = verify_telegram_user(user.id)
    
    if not telegram_user:
        await update.message.reply_text(
            "❌ *Acceso Denegado*\n\n"
            "Este bot es exclusivo para empleados autorizados de StorAI.\n"
            "Si eres empleado, contacta al administrador para registrar tu cuenta de Telegram.",
            parse_mode='Markdown'
        )
        return
    
    # Mensaje de bienvenida
    welcome_message = f"""
👋 *Bienvenido a StorAI Bot, {user.first_name}!*

Este bot te ayuda a consultar el inventario de forma rápida y eficiente.

*Comandos disponibles:*
🔍 `/buscar <nombre>` - Buscar producto por nombre
🏷️ `/sku <código>` - Buscar producto por SKU
📂 `/categoria <nombre>` - Buscar por categoría
❓ `/help` - Ver ayuda detallada

*También puedes escribir directamente el nombre de un producto para buscarlo.*
"""
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /help"""
    help_message = """
*📖 Guía de Uso del Bot StorAI*

*Comandos de Búsqueda:*
🔍 `/buscar <nombre>` - Busca productos por nombre
   Ejemplo: `/buscar tornillo`
   
🏷️ `/sku <código>` - Busca por SKU exacto
   Ejemplo: `/sku TOR-001`
   
📂 `/categoria <nombre>` - Busca por categoría
   Ejemplo: `/categoria herramientas`

*Búsqueda Directa:*
Simplemente escribe el nombre del producto sin comando.
Ejemplo: `tornillo hexagonal`

*Información de Respuesta:*
Cada búsqueda te mostrará:
- ✅ Nombre y SKU del producto
- 📊 Cantidad actual en stock
- 📍 Ubicación física exacta en el almacén
- 🏷️ Estado de disponibilidad (Disponible/Crítico/Agotado)

*Nota:* Todas las consultas son registradas para análisis y optimización.
"""
    await update.message.reply_text(help_message, parse_mode='Markdown')


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /buscar"""
    user = update.effective_user
    
    # Verificar autorización
    if not verify_telegram_user(user.id):
        await update.message.reply_text("❌ Acceso denegado. Usuario no autorizado.")
        return
    
    # Obtener término de búsqueda
    if not context.args:
        await update.message.reply_text(
            "❌ Debes proporcionar un término de búsqueda.\n"
            "Uso: `/buscar <nombre del producto>`",
            parse_mode='Markdown'
        )
        return
    
    query_text = " ".join(context.args)
    await perform_search(update, user.id, query_text, "name")


async def search_by_sku_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /sku"""
    user = update.effective_user
    
    # Verificar autorización
    if not verify_telegram_user(user.id):
        await update.message.reply_text("❌ Acceso denegado. Usuario no autorizado.")
        return
    
    # Obtener SKU
    if not context.args:
        await update.message.reply_text(
            "❌ Debes proporcionar un SKU.\n"
            "Uso: `/sku <código SKU>`",
            parse_mode='Markdown'
        )
        return
    
    query_text = context.args[0].upper()
    await perform_search(update, user.id, query_text, "sku")


async def search_by_category_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /categoria"""
    user = update.effective_user
    
    # Verificar autorización
    if not verify_telegram_user(user.id):
        await update.message.reply_text("❌ Acceso denegado. Usuario no autorizado.")
        return
    
    # Obtener categoría
    if not context.args:
        await update.message.reply_text(
            "❌ Debes proporcionar una categoría.\n"
            "Uso: `/categoria <nombre de categoría>`",
            parse_mode='Markdown'
        )
        return
    
    query_text = " ".join(context.args)
    await perform_search(update, user.id, query_text, "category")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mensajes de texto (búsqueda por nombre)"""
    user = update.effective_user
    query_text = update.message.text
    
    # Verificar autorización
    if not verify_telegram_user(user.id):
        await update.message.reply_text("❌ Acceso denegado. Usuario no autorizado.")
        return
    
    # Realizar búsqueda
    await perform_search(update, user.id, query_text, "name")


async def perform_search(update: Update, telegram_id: int, query_text: str, query_type: str):
    """Realizar búsqueda de productos y enviar respuesta"""
    start_time = time.time()
    db = get_db_session()
    
    try:
        # Construir consulta según tipo
        query = db.query(Product).filter(Product.is_active == True)
        
        if query_type == "sku":
            query = query.filter(Product.sku.ilike(f"%{query_text}%"))
        elif query_type == "category":
            query = query.join(Product.category).filter(
                Category.name.ilike(f"%{query_text}%")
            )
        else:  # name
            query = query.filter(Product.name.ilike(f"%{query_text}%"))
        
        products = query.limit(10).all()
        
        # Calcular tiempo de respuesta
        response_time_ms = (time.time() - start_time) * 1000
        
        # Obtener usuario de Telegram para logging
        telegram_user = db.query(TelegramUser).filter(
            TelegramUser.telegram_id == telegram_id
        ).first()
        
        if not products:
            await update.message.reply_text(
                f"🔍 *No se encontraron productos*\n\n"
                f"Búsqueda: `{query_text}`\n"
                f"Intenta con otro término o usa `/help` para ver los comandos.",
                parse_mode='Markdown'
            )
            
            # Registrar log aunque no haya resultados
            if telegram_user:
                log_query(
                    telegram_user.id, query_text, query_type, 
                    0, response_time_ms
                )
            return
        
        # Preparar mensajes de respuesta
        product_ids = []
        for product in products:
            product_ids.append(str(product.id))
        
        # Registrar log de consulta
        if telegram_user:
            log_query(
                telegram_user.id, query_text, query_type,
                len(products), response_time_ms, ",".join(product_ids)
            )
        
        # Enviar resultados
        if len(products) == 1:
            # Un solo producto - mostrar detalles completos
            product = products[0]
            locations = db.query(ProductLocation).filter(
                ProductLocation.product_id == product.id
            ).all()
            message = format_product_message(product, locations)
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            # Múltiples productos - mostrar lista resumida
            header = f"🔍 *Se encontraron {len(products)} productos*\n\n"
            messages = []
            
            for i, product in enumerate(products[:5], 1):
                status_emoji = {
                    StockStatus.AVAILABLE: "✅",
                    StockStatus.LOW_STOCK: "⚠️",
                    StockStatus.OUT_OF_STOCK: "❌"
                }
                emoji = status_emoji.get(product.stock_status, "❓")
                messages.append(
                    f"{i}. {emoji} *{product.name}*\n"
                    f"   SKU: `{product.sku}` | Stock: {product.stock_current}"
                )
            
            if len(products) > 5:
                messages.append(f"\n_... y {len(products) - 5} más_")
            
            message = header + "\n".join(messages)
            await update.message.reply_text(message, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Error en búsqueda: {e}")
        await update.message.reply_text(
            "❌ Ocurrió un error al realizar la búsqueda. Por favor intenta nuevamente."
        )
    finally:
        db.close()


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler de errores del bot"""
    logger.error(f"Error en bot: {context.error}", exc_info=context.error)
    
    if update:
        await update.message.reply_text(
            "❌ Ocurrió un error inesperado. El administrador ha sido notificado."
        )
