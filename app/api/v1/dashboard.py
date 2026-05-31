"""Dashboard API routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_db, get_current_active_user
from app.models.users import User
from app.models.inventory import Product, StockStatus
from app.models.locations import Location
from app.models.telegram_users import TelegramQueryLog
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener resumen del dashboard"""
    
    # Total de productos
    total_products = db.query(func.count(Product.id)).scalar()
    
    # Productos por estado de stock
    available_products = db.query(func.count(Product.id)).filter(
        Product.stock_status == StockStatus.AVAILABLE
    ).scalar()
    
    low_stock_products = db.query(func.count(Product.id)).filter(
        Product.stock_status == StockStatus.LOW_STOCK
    ).scalar()
    
    out_of_stock_products = db.query(func.count(Product.id)).filter(
        Product.stock_status == StockStatus.OUT_OF_STOCK
    ).scalar()
    
    # Valor total del inventario
    total_inventory_value = db.query(func.sum(Product.stock_current * Product.cost_price)).scalar() or 0
    
    # Total de ubicaciones
    total_locations = db.query(func.count(Location.id)).scalar()
    
    # Consultas del bot en los últimos 7 días
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    bot_queries = db.query(func.count(TelegramQueryLog.id)).filter(
        TelegramQueryLog.created_at >= seven_days_ago
    ).scalar()
    
    return {
        "total_products": total_products,
        "available_products": available_products,
        "low_stock_products": low_stock_products,
        "out_of_stock_products": out_of_stock_products,
        "total_inventory_value": total_inventory_value,
        "total_locations": total_locations,
        "bot_queries_last_7_days": bot_queries
    }


@router.get("/low-stock-alerts")
def get_low_stock_alerts(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener alertas de stock bajo"""
    products = db.query(Product).filter(
        Product.stock_status == StockStatus.LOW_STOCK,
        Product.is_active == True
    ).order_by(Product.stock_current.asc()).limit(limit).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "stock_current": p.stock_current,
            "stock_minimum": p.stock_minimum,
            "shortage": p.stock_minimum - p.stock_current
        }
        for p in products
    ]


@router.get("/inventory-value")
def get_inventory_value_by_category(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener valor del inventario por categoría"""
    from app.models.inventory import Category
    
    results = db.query(
        Category.name,
        func.sum(Product.stock_current * Product.cost_price).label('total_value')
    ).join(
        Product, Category.id == Product.category_id
    ).filter(
        Product.is_active == True
    ).group_by(
        Category.id, Category.name
    ).all()
    
    return [
        {
            "category": name,
            "total_value": float(total_value) if total_value else 0.0
        }
        for name, total_value in results
    ]
