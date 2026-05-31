"""Teclados inline para el Bot de Telegram"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard():
    """Teclado del menú principal"""
    keyboard = [
        [
            InlineKeyboardButton("🔍 Buscar Producto", callback_data="search"),
            InlineKeyboardButton("🏷️ Buscar por SKU", callback_data="search_sku")
        ],
        [
            InlineKeyboardButton("📂 Por Categoría", callback_data="search_category"),
            InlineKeyboardButton("📊 Stock Crítico", callback_data="low_stock")
        ],
        [
            InlineKeyboardButton("❓ Ayuda", callback_data="help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_product_actions_keyboard(product_id: int):
    """Teclado de acciones para un producto específico"""
    keyboard = [
        [
            InlineKeyboardButton("📍 Ver Ubicación", callback_data=f"location_{product_id}"),
            InlineKeyboardButton("📊 Ver Historial", callback_data=f"history_{product_id}")
        ],
        [
            InlineKeyboardButton("🔙 Volver", callback_data="back")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
