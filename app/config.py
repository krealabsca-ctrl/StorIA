"""Configuración general de la aplicación"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    """Configuración de la aplicación usando variables de entorno"""
    
    # Database
    DATABASE_URL: str
    DATABASE_URL_ASYNC: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_BOT_USERNAME: str
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Ecommerce
    CURRENCY: str = "USD"
    TAX_RATE: float = 0.16
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
