"""Schemas for inventory management"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.inventory import StockStatus, MovementType


# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Subcategory Schemas
class SubcategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    category_id: int
    is_active: bool = True


class SubcategoryCreate(SubcategoryBase):
    pass


class SubcategoryUpdate(SubcategoryBase):
    pass


class Subcategory(SubcategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Brand Schemas
class BrandBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    website: Optional[str] = Field(None, max_length=255)
    is_active: bool = True


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BrandBase):
    pass


class Brand(BrandBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Product Schemas
class ProductBase(BaseModel):
    sku: str = Field(..., max_length=50)
    barcode: Optional[str] = Field(None, max_length=50)
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category_id: int
    subcategory_id: Optional[int] = None
    brand_id: Optional[int] = None
    cost_price: float = Field(..., gt=0)
    sale_price: float = Field(..., gt=0)
    stock_minimum: int = Field(default=5, ge=0)
    is_active: bool = True
    is_available_for_sale: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = Field(None, max_length=50)
    barcode: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    brand_id: Optional[int] = None
    cost_price: Optional[float] = Field(None, gt=0)
    sale_price: Optional[float] = Field(None, gt=0)
    stock_minimum: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_available_for_sale: Optional[bool] = None


class Product(ProductBase):
    id: int
    stock_current: int
    stock_status: StockStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductWithLocation(Product):
    locations: List[dict] = []
    total_inventory_value: float
    
    class Config:
        from_attributes = True


# Stock Movement Schemas
class StockMovementBase(BaseModel):
    product_id: int
    movement_type: MovementType
    quantity: int = Field(..., gt=0)
    reason: Optional[str] = Field(None, max_length=255)
    reference_id: Optional[int] = None
    reference_type: Optional[str] = Field(None, max_length=50)


class StockMovementCreate(StockMovementBase):
    pass


class StockMovement(StockMovementBase):
    id: int
    previous_stock: int
    new_stock: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Stock Adjustment Schema
class StockAdjustment(BaseModel):
    product_id: int
    new_quantity: int = Field(..., ge=0)
    reason: str = Field(..., max_length=255)
