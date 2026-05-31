"""Logging configuration for the application"""
import logging
import sys
from app.config import settings


def setup_logging():
    """Configurar logging para la aplicación"""
    logging.basicConfig(
        level=logging.INFO if not settings.DEBUG else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/app.log", encoding="utf-8")
        ]
    )
    return logging.getLogger(__name__)
