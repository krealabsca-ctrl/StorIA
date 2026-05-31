"""Models for ecommerce orders"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseMixin
from app.database import Base


class OrderStatus(str, enum.Enum):
    """Estado de orden de cliente"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Order(BaseMixin, Base):
    """Orden de compra de cliente (ecommerce)"""
    __tablename__ = "orders"
    
    # Identificación
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Cliente
    customer_name = Column(String(200), nullable=False)
    customer_email = Column(String(100), nullable=False)
    customer_phone = Column(String(50), nullable=True)
    
    # Dirección de envío
    shipping_address = Column(Text, nullable=False)
    shipping_city = Column(String(100), nullable=False)
    shipping_country = Column(String(100), default="Colombia", nullable=False)
    
    # Montos
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    shipping_cost = Column(Float, default=0.0, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    # Estado
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    is_paid = Column(Boolean, default=False)
    
    # Fechas
    order_date = Column(String, default=datetime.utcnow, nullable=False)
    shipped_date = Column(String, nullable=True)
    delivered_date = Column(String, nullable=True)
    
    # Notas
    customer_notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Relaciones
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    invoice = relationship("Invoice", back_populates="order", uselist=False, cascade="all, delete-orphan")


class OrderItem(BaseMixin, Base):
    """Ítem de orden de compra"""
    __tablename__ = "order_items"
    
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Detalles del producto al momento de la compra
    product_name = Column(String(200), nullable=False)
    product_sku = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    
    # Relaciones
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
