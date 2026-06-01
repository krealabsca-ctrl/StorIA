"""Inventory API routes"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.models.users import User
from app.models.inventory import Product, Category, Brand, StockMovement, MovementType
from app.schemas.inventory import (
    ProductCreate, ProductUpdate, Product as ProductSchema, ProductWithLocation,
    CategoryCreate, CategoryUpdate, Category as CategorySchema,
    BrandCreate, BrandUpdate, Brand as BrandSchema,
    StockMovementCreate, StockMovement as StockMovementSchema, StockAdjustment
)

router = APIRouter()


# Category endpoints
@router.post("/categories/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear nueva categoría"""
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/categories/", response_model=List[CategorySchema])
def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar todas las categorías"""
    categories = db.query(Category).offset(skip).limit(limit).all()
    return categories


@router.get("/categories/{category_id}", response_model=CategorySchema)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener categoría por ID"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category


# Brand endpoints
@router.post("/brands/", response_model=BrandSchema, status_code=status.HTTP_201_CREATED)
def create_brand(
    brand: BrandCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear nueva marca"""
    db_brand = Brand(**brand.dict())
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand


@router.get("/brands/", response_model=List[BrandSchema])
def list_brands(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar todas las marcas"""
    brands = db.query(Brand).offset(skip).limit(limit).all()
    return brands


# Product endpoints
@router.post("/products/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear nuevo producto"""
    db_product = Product(**product.dict())
    db_product.stock_current = 0
    db_product.update_stock_status()
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/products/", response_model=List[ProductSchema])
def list_products(
    skip: int = 0,
    limit: int = 100,
    category_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar productos con filtros opcionales"""
    query = db.query(Product).filter(Product.is_active == True)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/products/{product_id}", response_model=ProductSchema)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener producto por ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.get("/products/sku/{sku}", response_model=ProductSchema)
def get_product_by_sku(
    sku: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener producto por SKU"""
    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.put("/products/{product_id}", response_model=ProductSchema)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar producto"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    product.update_stock_status()
    db.commit()
    db.refresh(product)
    return product


@router.post("/products/{product_id}/stock", response_model=StockMovementSchema)
def adjust_stock(
    product_id: int,
    adjustment: StockAdjustment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Ajustar stock de producto"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    previous_stock = product.stock_current
    new_stock = adjustment.new_quantity
    
    # Determinar tipo de movimiento
    if new_stock > previous_stock:
        movement_type = MovementType.IN
        quantity = new_stock - previous_stock
    elif new_stock < previous_stock:
        movement_type = MovementType.OUT
        quantity = previous_stock - new_stock
    else:
        raise HTTPException(status_code=400, detail="El stock no cambió")
    
    # Actualizar stock
    product.stock_current = new_stock
    product.update_stock_status()
    
    # Registrar movimiento
    movement = StockMovement(
        product_id=product_id,
        movement_type=movement_type,
        quantity=quantity,
        previous_stock=previous_stock,
        new_stock=new_stock,
        reason=adjustment.reason,
        reference_type="adjustment"
    )
    
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


@router.get("/products/{product_id}/movements", response_model=List[StockMovementSchema])
def get_product_movements(
    product_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener historial de movimientos de stock de un producto"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    movements = db.query(StockMovement).filter(
        StockMovement.product_id == product_id
    ).order_by(StockMovement.created_at.desc()).offset(skip).limit(limit).all()
    
    return movements


@router.get("/products/low-stock/", response_model=List[ProductSchema])
def get_low_stock_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener productos con stock bajo"""
    from app.models.inventory import StockStatus
    
    products = db.query(Product).filter(
        Product.stock_status == StockStatus.LOW_STOCK,
        Product.is_active == True
    ).all()
    
    return products


@router.get("/products/out-of-stock/", response_model=List[ProductSchema])
def get_out_of_stock_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener productos agotados"""
    from app.models.inventory import StockStatus
    
    products = db.query(Product).filter(
        Product.stock_status == StockStatus.OUT_OF_STOCK,
        Product.is_active == True
    ).all()
    
    return products
