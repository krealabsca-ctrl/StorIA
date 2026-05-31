"""Models for warehouse location management"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseMixin
from app.database import Base


class Location(BaseMixin, Base):
    """Ubicación física en el almacén"""
    __tablename__ = "locations"
    
    # Identificación
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    
    # Estructura física
    aisle = Column(String(20), nullable=True)  # Pasillo (ej: "A")
    shelf = Column(String(20), nullable=True)  # Estante (ej: "3")
    level = Column(String(20), nullable=True)  # Nivel (ej: "2")
    zone = Column(String(50), nullable=True)  # Zona (ej: "Zona Norte")
    
    # Descripción formateada
    full_location = Column(String(200), nullable=True)  # "Pasillo A - Estante 3 - Nivel 2"
    
    # Metadatos
    location_type = Column(String(50), default="shelf")  # shelf, rack, bin, floor
    capacity = Column(Integer, nullable=True)  # Capacidad máxima
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    product_locations = relationship("ProductLocation", back_populates="location", cascade="all, delete-orphan")
    
    def generate_full_location(self):
        """Generar descripción completa de la ubicación"""
        parts = []
        if self.aisle:
            parts.append(f"Pasillo {self.aisle}")
        if self.shelf:
            parts.append(f"Estante {self.shelf}")
        if self.level:
            parts.append(f"Nivel {self.level}")
        if self.zone:
            parts.append(f"Zona {self.zone}")
        
        self.full_location = " - ".join(parts) if parts else self.name
        return self.full_location


class ProductLocation(BaseMixin, Base):
    """Asociación entre producto y ubicación física"""
    __tablename__ = "product_locations"
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    quantity = Column(Integer, default=0, nullable=False)  # Cantidad en esta ubicación específica
    is_primary = Column(Boolean, default=False)  # Ubicación principal del producto
    
    # Relaciones
    product = relationship("Product", back_populates="locations")
    location = relationship("Location", back_populates="product_locations")
