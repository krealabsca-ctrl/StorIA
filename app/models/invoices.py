"""Models for electronic invoicing"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseMixin
from app.database import Base


class Invoice(BaseMixin, Base):
    """Factura electrónica"""
    __tablename__ = "invoices"
    
    # Identificación fiscal
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    invoice_prefix = Column(String(10), default="INV", nullable=False)
    
    # Relación con orden
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    
    # Información del cliente
    customer_name = Column(String(200), nullable=False)
    customer_identification = Column(String(50), nullable=False)  # NIT/RUT/Cédula
    customer_email = Column(String(100), nullable=False)
    
    # Fechas
    invoice_date = Column(String, default=datetime.utcnow, nullable=False)
    due_date = Column(String, nullable=True)
    
    # Montos
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    tax_rate = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    # Estado
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(String(20), default="draft", nullable=False)  # draft, sent, paid, cancelled
    
    # Representación fiscal (XML/JSON)
    xml_content = Column(Text, nullable=True)  # XML firmado (simulado)
    json_content = Column(Text, nullable=True)  # JSON estructurado
    qr_code = Column(String(255), nullable=True)  # URL o base64 del QR
    
    # Relaciones
    order = relationship("Order", back_populates="invoice")
    invoice_items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(BaseMixin, Base):
    """Ítem de factura electrónica"""
    __tablename__ = "invoice_items"
    
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    
    # Detalles del producto
    product_name = Column(String(200), nullable=False)
    product_sku = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    tax_rate = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    
    # Relaciones
    invoice = relationship("Invoice", back_populates="invoice_items")
