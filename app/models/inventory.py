"""Models for inventory management"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.models.base import BaseMixin
from app.database import Base


class StockStatus(str, enum.Enum):
    """Estado de stock"""
    AVAILABLE = "available"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"


class MovementType(str, enum.Enum):
    """Tipo de movimiento de stock"""
    IN = "in"
    OUT = "out"
    ADJUSTMENT = "adjustment"


class Category(BaseMixin, Base):
    """Categoría de productos"""
    __tablename__ = "categories"
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    subcategories = relationship("Subcategory", back_populates="category", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="category")


class Subcategory(BaseMixin, Base):
    """Subcategoría de productos"""
    __tablename__ = "subcategories"
    
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    category = relationship("Category", back_populates="subcategories")
    products = relationship("Product", back_populates="subcategory")


class Brand(BaseMixin, Base):
    """Marca de productos"""
    __tablename__ = "brands"
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    products = relationship("Product", back_populates="brand")


class Product(BaseMixin, Base):
    """Producto de inventario"""
    __tablename__ = "products"
    
    # Identificación
    sku = Column(String(50), unique=True, nullable=False, index=True)
    barcode = Column(String(50), unique=True, nullable=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Clasificación
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    
    # Precios
    cost_price = Column(Float, nullable=False)
    sale_price = Column(Float, nullable=False)
    
    # Stock
    stock_current = Column(Integer, default=0, nullable=False)
    stock_minimum = Column(Integer, default=5, nullable=False)
    stock_status = Column(Enum(StockStatus), default=StockStatus.AVAILABLE, nullable=False)
    
    # Estado
    is_active = Column(Boolean, default=True)
    is_available_for_sale = Column(Boolean, default=True)
    
    # Relaciones
    category = relationship("Category", back_populates="products")
    subcategory = relationship("Subcategory", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    locations = relationship("ProductLocation", back_populates="product", cascade="all, delete-orphan")
    stock_movements = relationship("StockMovement", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
    
    @property
    def total_inventory_value(self) -> float:
        """Valor total del inventario para este producto"""
        return self.stock_current * self.cost_price
    
    def update_stock_status(self):
        """Actualizar estado de stock basado en niveles actuales"""
        if self.stock_current == 0:
            self.stock_status = StockStatus.OUT_OF_STOCK
        elif self.stock_current <= self.stock_minimum:
            self.stock_status = StockStatus.LOW_STOCK
        else:
            self.stock_status = StockStatus.AVAILABLE


class StockMovement(BaseMixin, Base):
    """Movimiento de stock (entrada/salida/ajuste)"""
    __tablename__ = "stock_movements"
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    movement_type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Integer, nullable=False)
    previous_stock = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=True)
    reference_id = Column(Integer, nullable=True)  # ID de orden, compra, etc.
    reference_type = Column(String(50), nullable=True)  # 'order', 'purchase', 'adjustment'
    
    # Relaciones
    product = relationship("Product", back_populates="stock_movements")
