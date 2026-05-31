"""Schemas for supplier management"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from app.models.suppliers import OrderStatus


class SupplierBase(BaseModel):
    name: str = Field(..., max_length=200)
    code: str = Field(..., max_length=50)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    tax_id: Optional[str] = Field(None, max_length=50)
    is_active: bool = True
    notes: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    tax_id: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class Supplier(SupplierBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PurchaseOrderBase(BaseModel):
    supplier_id: int
    order_number: str = Field(..., max_length=50)
    expected_date: Optional[str] = None
    total_amount: float = Field(default=0.0, ge=0)
    status: OrderStatus = OrderStatus.PENDING
    notes: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    pass


class PurchaseOrderUpdate(BaseModel):
    expected_date: Optional[str] = None
    total_amount: Optional[float] = Field(None, ge=0)
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None


class PurchaseOrder(PurchaseOrderBase):
    id: int
    order_date: datetime
    received_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
