"""Models for supplier management"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseMixin
from app.database import Base


class OrderStatus(str, enum.Enum):
    """Estado de orden de compra"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class Supplier(BaseMixin, Base):
    """Proveedor de productos"""
    __tablename__ = "suppliers"
    
    # Información básica
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    contact_person = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    
    # Dirección
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Información fiscal
    tax_id = Column(String(50), nullable=True)
    
    # Estado
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Relaciones
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier", cascade="all, delete-orphan")


class PurchaseOrder(BaseMixin, Base):
    """Orden de compra a proveedor"""
    __tablename__ = "purchase_orders"
    
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Fechas
    order_date = Column(String, default=datetime.utcnow, nullable=False)
    expected_date = Column(String, nullable=True)
    received_date = Column(String, nullable=True)
    
    # Montos
    total_amount = Column(Float, default=0.0, nullable=False)
    
    # Estado
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relaciones
    supplier = relationship("Supplier", back_populates="purchase_orders")
