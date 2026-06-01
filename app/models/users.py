"""Models for user management"""
from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseMixin
from app.database import Base


class UserRole(str, enum.Enum):
    """Roles de usuario en el sistema"""
    ADMIN = "admin"
    MANAGER = "manager"
    WAREHOUSE_STAFF = "warehouse_staff"
    SALES = "sales"


class User(BaseMixin, Base):
    """Usuario del sistema"""
    __tablename__ = "users"
    
    # Autenticación
    email = Column(String(100), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Información personal
    full_name = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=True)
    
    # Rol y estado
    role = Column(
        Enum(UserRole, name="user_role",
             values_callable=lambda x: [e.value for e in x]),
        default=UserRole.WAREHOUSE_STAFF,
        nullable=False,
    )
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    telegram_user = relationship("TelegramUser", back_populates="user", uselist=False, cascade="all, delete-orphan")
