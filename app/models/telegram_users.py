"""Models for Telegram bot users and analytics"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, Float
from sqlalchemy.orm import relationship
from app.models.base import BaseMixin
from app.database import Base


class TelegramUser(BaseMixin, Base):
    """Usuario de Telegram autorizado (empleado)"""
    __tablename__ = "telegram_users"
    
    # Identificación de Telegram
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    telegram_username = Column(String(100), nullable=True, index=True)
    telegram_first_name = Column(String(100), nullable=True)
    telegram_last_name = Column(String(100), nullable=True)
    
    # Relación con usuario del sistema
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Estado
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Verificado por admin
    
    # Relaciones
    user = relationship("User", back_populates="telegram_user")
    query_logs = relationship("TelegramQueryLog", back_populates="telegram_user", cascade="all, delete-orphan")


class TelegramQueryLog(BaseMixin, Base):
    """Log de consultas realizadas por el bot de Telegram"""
    __tablename__ = "telegram_query_logs"
    
    telegram_user_id = Column(Integer, ForeignKey("telegram_users.id"), nullable=False)
    
    # Consulta
    query_text = Column(String(500), nullable=False)  # Texto buscado por el usuario
    query_type = Column(String(50), nullable=True)  # 'name', 'sku', 'category'
    
    # Resultados
    products_found = Column(Integer, default=0, nullable=False)  # Cantidad de productos encontrados
    response_time_ms = Column(Float, nullable=True)  # Tiempo de respuesta en milisegundos
    
    # Metadatos
    product_ids = Column(Text, nullable=True)  # IDs de productos encontrados (comma-separated)
    
    # Relaciones
    telegram_user = relationship("TelegramUser", back_populates="query_logs")
