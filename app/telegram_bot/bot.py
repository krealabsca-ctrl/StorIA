"""Configuración principal del Bot de Telegram"""
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from app.config import settings
from app.telegram_bot.handlers import (
    start_command,
    help_command,
    search_command,
    search_by_sku_command,
    search_by_category_command,
    handle_message,
    error_handler
)
from app.core.logging_config import setup_logging

# Configurar logging
logger = setup_logging()


def create_bot_application() -> Application:
    """Crear y configurar la aplicación del bot de Telegram"""
    
    # Crear aplicación
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Registrar handlers de comandos
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("buscar", search_command))
    application.add_handler(CommandHandler("sku", search_by_sku_command))
    application.add_handler(CommandHandler("categoria", search_by_category_command))
    
    # Handler para mensajes de texto (búsqueda por nombre)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Handler de errores
    application.add_error_handler(error_handler)
    
    logger.info("Bot de Telegram configurado exitosamente")
    return application


def run_bot():
    """Ejecutar el bot de Telegram"""
    application = create_bot_application()
    
    logger.info(f"Iniciando bot de Telegram: @{settings.TELEGRAM_BOT_USERNAME}")
    
    # Iniciar el bot con polling
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == "__main__":
    run_bot()
