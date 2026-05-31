"""Schemas for ecommerce orders"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from app.models.orders import OrderStatus


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    order_id: int
    product_name: str
    product_sku: str
    subtotal: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    customer_name: str = Field(..., max_length=200)
    customer_email: EmailStr
    customer_phone: Optional[str] = Field(None, max_length=50)
    shipping_address: str
    shipping_city: str = Field(..., max_length=100)
    shipping_country: str = Field(default="Colombia", max_length=100)
    customer_notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    is_paid: Optional[bool] = None
    internal_notes: Optional[str] = None


class Order(OrderBase):
    id: int
    order_number: str
    subtotal: float
    tax_amount: float
    shipping_cost: float
    total_amount: float
    status: OrderStatus
    is_paid: bool
    order_date: datetime
    shipped_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItem] = []
    
    class Config:
        from_attributes = True
