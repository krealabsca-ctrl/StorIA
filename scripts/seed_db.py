"""Script para inicializar la base de datos con datos de prueba"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import (
    User, UserRole, TelegramUser, Category, Subcategory, Brand,
    Product, Location, ProductLocation, Supplier
)
from app.core.security import get_password_hash


def create_tables():
    """Crear todas las tablas de la base de datos"""
    print("🔨 Creando tablas de la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")


def seed_categories(db: Session):
    """Crear categorías de ejemplo"""
    print("📦 Creando categorías...")
    
    categories_data = [
        {"name": "Herramientas", "description": "Herramientas manuales y eléctricas"},
        {"name": "Tornillería", "description": "Tornillos, tuercas y arandelas"},
        {"name": "Electricidad", "description": "Componentes eléctricos y cableado"},
        {"name": "Plomería", "description": "Tubos, accesorios y fontanería"},
        {"name": "Pinturas", "description": "Pinturas y accesorios de pintura"},
    ]
    
    for cat_data in categories_data:
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if not existing:
            category = Category(**cat_data)
            db.add(category)
    
    db.commit()
    print(f"✅ {len(categories_data)} categorías creadas")


def seed_subcategories(db: Session):
    """Crear subcategorías de ejemplo"""
    print("📂 Creando subcategorías...")
    
    # Obtener categorías
    herramientas = db.query(Category).filter(Category.name == "Herramientas").first()
    tornilleria = db.query(Category).filter(Category.name == "Tornillería").first()
    
    subcategories_data = [
        {"name": "Destornilladores", "category_id": herramientas.id if herramientas else 1},
        {"name": "Martillos", "category_id": herramientas.id if herramientas else 1},
        {"name": "Llaves", "category_id": herramientas.id if herramientas else 1},
        {"name": "Tornillos Hexagonales", "category_id": tornilleria.id if tornilleria else 2},
        {"name": "Tornillos Phillips", "category_id": tornilleria.id if tornilleria else 2},
    ]
    
    for sub_data in subcategories_data:
        existing = db.query(Subcategory).filter(Subcategory.name == sub_data["name"]).first()
        if not existing:
            subcategory = Subcategory(**sub_data)
            db.add(subcategory)
    
    db.commit()
    print(f"✅ {len(subcategories_data)} subcategorías creadas")


def seed_brands(db: Session):
    """Crear marcas de ejemplo"""
    print("🏷️ Creando marcas...")
    
    brands_data = [
        {"name": "Stanley", "description": "Herramientas de calidad profesional"},
        {"name": "DeWalt", "description": "Herramientas eléctricas"},
        {"name": "3M", "description": "Productos industriales"},
        {"name": "Bosch", "description": "Herramientas y accesorios"},
    ]
    
    for brand_data in brands_data:
        existing = db.query(Brand).filter(Brand.name == brand_data["name"]).first()
        if not existing:
            brand = Brand(**brand_data)
            db.add(brand)
    
    db.commit()
    print(f"✅ {len(brands_data)} marcas creadas")


def seed_locations(db: Session):
    """Crear ubicaciones en el almacén"""
    print("📍 Creando ubicaciones en el almacén...")
    
    locations_data = [
        {
            "code": "A-01-1",
            "name": "Pasillo A Estante 01 Nivel 1",
            "aisle": "A",
            "shelf": "01",
            "level": "1",
            "zone": "Zona Norte",
            "location_type": "shelf",
            "capacity": 100
        },
        {
            "code": "A-01-2",
            "name": "Pasillo A Estante 01 Nivel 2",
            "aisle": "A",
            "shelf": "01",
            "level": "2",
            "zone": "Zona Norte",
            "location_type": "shelf",
            "capacity": 100
        },
        {
            "code": "A-02-1",
            "name": "Pasillo A Estante 02 Nivel 1",
            "aisle": "A",
            "shelf": "02",
            "level": "1",
            "zone": "Zona Norte",
            "location_type": "shelf",
            "capacity": 150
        },
        {
            "code": "B-01-1",
            "name": "Pasillo B Estante 01 Nivel 1",
            "aisle": "B",
            "shelf": "01",
            "level": "1",
            "zone": "Zona Sur",
            "location_type": "shelf",
            "capacity": 120
        },
    ]
    
    for loc_data in locations_data:
        existing = db.query(Location).filter(Location.code == loc_data["code"]).first()
        if not existing:
            location = Location(**loc_data)
            location.generate_full_location()
            db.add(location)
    
    db.commit()
    print(f"✅ {len(locations_data)} ubicaciones creadas")


def seed_users(db: Session):
    """Crear usuarios de ejemplo"""
    print("👤 Creando usuarios...")
    
    # Usuario admin
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if not existing_admin:
        admin = User(
            username="admin",
            email="admin@storai.com",
            full_name="Administrador del Sistema",
            phone="+573001234567",
            role=UserRole.ADMIN,
            is_active=True,
            hashed_password=get_password_hash("admin123")
        )
        db.add(admin)
        db.flush()
        
        # Crear usuario de Telegram para el admin
        telegram_admin = TelegramUser(
            telegram_id=123456789,
            telegram_username="admin_telegram",
            telegram_first_name="Admin",
            telegram_last_name="StorAI",
            user_id=admin.id,
            is_active=True,
            is_verified=True
        )
        db.add(telegram_admin)
    
    # Usuario gerente
    existing_manager = db.query(User).filter(User.username == "gerente").first()
    if not existing_manager:
        manager = User(
            username="gerente",
            email="gerente@storai.com",
            full_name="Gerente de Almacén",
            phone="+573009876543",
            role=UserRole.MANAGER,
            is_active=True,
            hashed_password=get_password_hash("gerente123")
        )
        db.add(manager)
        db.flush()
        
        # Crear usuario de Telegram para el gerente
        telegram_manager = TelegramUser(
            telegram_id=987654321,
            telegram_username="gerente_telegram",
            telegram_first_name="Gerente",
            telegram_last_name="Almacén",
            user_id=manager.id,
            is_active=True,
            is_verified=True
        )
        db.add(telegram_manager)
    
    # Usuario operario
    existing_staff = db.query(User).filter(User.username == "operario").first()
    if not existing_staff:
        staff = User(
            username="operario",
            email="operario@storai.com",
            full_name="Operario de Almacén",
            phone="+573005555555",
            role=UserRole.WAREHOUSE_STAFF,
            is_active=True,
            hashed_password=get_password_hash("operario123")
        )
        db.add(staff)
        db.flush()
        
        # Crear usuario de Telegram para el operario
        telegram_staff = TelegramUser(
            telegram_id=555555555,
            telegram_username="operario_telegram",
            telegram_first_name="Operario",
            telegram_last_name="Almacén",
            user_id=staff.id,
            is_active=True,
            is_verified=True
        )
        db.add(telegram_staff)
    
    db.commit()
    print("✅ Usuarios creados (admin, gerente, operario)")


def seed_products(db: Session):
    """Crear productos de ejemplo"""
    print("🔩 Creando productos...")
    
    # Obtener categorías y marcas
    herramientas = db.query(Category).filter(Category.name == "Herramientas").first()
    tornilleria = db.query(Category).filter(Category.name == "Tornillería").first()
    stanley = db.query(Brand).filter(Brand.name == "Stanley").first()
    
    products_data = [
        {
            "sku": "TOR-HEX-001",
            "barcode": "7501234567890",
            "name": "Tornillo Hexagonal 1/4\"",
            "description": "Tornillo hexagonal de acero inoxidable, 1/4 pulgada",
            "category_id": tornilleria.id if tornilleria else 2,
            "brand_id": stanley.id if stanley else 1,
            "cost_price": 0.50,
            "sale_price": 1.20,
            "stock_current": 150,
            "stock_minimum": 20,
            "is_active": True,
            "is_available_for_sale": True
        },
        {
            "sku": "TOR-HEX-002",
            "barcode": "7501234567891",
            "name": "Tornillo Hexagonal 3/8\"",
            "description": "Tornillo hexagonal de acero inoxidable, 3/8 pulgada",
            "category_id": tornilleria.id if tornilleria else 2,
            "brand_id": stanley.id if stanley else 1,
            "cost_price": 0.75,
            "sale_price": 1.80,
            "stock_current": 8,
            "stock_minimum": 15,
            "is_active": True,
            "is_available_for_sale": True
        },
        {
            "sku": "HERR-DES-001",
            "barcode": "7501234567892",
            "name": "Destornillador Phillips #2",
            "description": "Destornillador Phillips tamaño 2, mango ergonómico",
            "category_id": herramientas.id if herramientas else 1,
            "brand_id": stanley.id if stanley else 1,
            "cost_price": 3.50,
            "sale_price": 7.50,
            "stock_current": 45,
            "stock_minimum": 10,
            "is_active": True,
            "is_available_for_sale": True
        },
    ]
    
    for prod_data in products_data:
        existing = db.query(Product).filter(Product.sku == prod_data["sku"]).first()
        if not existing:
            product = Product(**prod_data)
            product.update_stock_status()
            db.add(product)
    
    db.commit()
    print(f"✅ {len(products_data)} productos creados")


def seed_suppliers(db: Session):
    """Crear proveedores de ejemplo"""
    print("🏢 Creando proveedores...")
    
    suppliers_data = [
        {
            "name": "Distribuidora Industrial S.A.",
            "code": "PROV-001",
            "contact_person": "Carlos Rodríguez",
            "email": "compras@distribuidora.com",
            "phone": "+573001112233",
            "address": "Calle 123 #45-67",
            "city": "Bogotá",
            "country": "Colombia",
            "tax_id": "900123456-1",
            "is_active": True
        },
        {
            "name": "Herramientas Pro Ltda.",
            "code": "PROV-002",
            "contact_person": "María González",
            "email": "ventas@herramientaspro.com",
            "phone": "+573004445566",
            "address": "Avenida 45 #67-89",
            "city": "Medellín",
            "country": "Colombia",
            "tax_id": "900987654-2",
            "is_active": True
        },
    ]
    
    for supp_data in suppliers_data:
        existing = db.query(Supplier).filter(Supplier.code == supp_data["code"]).first()
        if not existing:
            supplier = Supplier(**supp_data)
            db.add(supplier)
    
    db.commit()
    print(f"✅ {len(suppliers_data)} proveedores creados")


def main():
    """Función principal para inicializar la base de datos"""
    print("🚀 Inicializando base de datos de StorAI...\n")
    
    try:
        # Crear tablas
        create_tables()
        
        # Crear sesión de base de datos
        db = SessionLocal()
        
        try:
            # Sembrar datos
            seed_categories(db)
            seed_subcategories(db)
            seed_brands(db)
            seed_locations(db)
            seed_users(db)
            seed_products(db)
            seed_suppliers(db)
            
            print("\n✅ Base de datos inicializada exitosamente!")
            print("\n📝 Credenciales de prueba:")
            print("   - Admin: admin / admin123")
            print("   - Gerente: gerente / gerente123")
            print("   - Operario: operario / operario123")
            print("\n🤖 IDs de Telegram para prueba:")
            print("   - Admin: 123456789")
            print("   - Gerente: 987654321")
            print("   - Operario: 555555555")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n❌ Error al inicializar la base de datos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
