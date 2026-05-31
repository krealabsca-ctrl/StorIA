"""Schemas for electronic invoicing"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class InvoiceItemBase(BaseModel):
    product_name: str = Field(..., max_length=200)
    product_sku: str = Field(..., max_length=50)
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    tax_rate: float = Field(..., ge=0)


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItem(InvoiceItemBase):
    id: int
    invoice_id: int
    tax_amount: float
    subtotal: float
    total: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    customer_name: str = Field(..., max_length=200)
    customer_identification: str = Field(..., max_length=50)
    customer_email: EmailStr
    currency: str = Field(default="USD", max_length=3)
    tax_rate: float = Field(..., ge=0)


class InvoiceCreate(InvoiceBase):
    order_id: int
    items: List[InvoiceItemCreate]


class Invoice(InvoiceBase):
    id: int
    invoice_number: str
    invoice_prefix: str
    order_id: int
    invoice_date: datetime
    due_date: Optional[datetime] = None
    subtotal: float
    tax_amount: float
    total_amount: float
    status: str
    xml_content: Optional[str] = None
    json_content: Optional[str] = None
    qr_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    invoice_items: List[InvoiceItem] = []
    
    class Config:
        from_attributes = True
