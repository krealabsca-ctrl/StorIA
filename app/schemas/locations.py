"""Schemas for warehouse location management"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    aisle: Optional[str] = Field(None, max_length=20)
    shelf: Optional[str] = Field(None, max_length=20)
    level: Optional[str] = Field(None, max_length=20)
    zone: Optional[str] = Field(None, max_length=50)
    location_type: str = Field(default="shelf", max_length=50)
    capacity: Optional[int] = Field(None, ge=0)
    is_active: bool = True


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    aisle: Optional[str] = Field(None, max_length=20)
    shelf: Optional[str] = Field(None, max_length=20)
    level: Optional[str] = Field(None, max_length=20)
    zone: Optional[str] = Field(None, max_length=50)
    location_type: Optional[str] = Field(None, max_length=50)
    capacity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class Location(LocationBase):
    id: int
    full_location: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductLocationBase(BaseModel):
    product_id: int
    location_id: int
    quantity: int = Field(default=0, ge=0)
    is_primary: bool = False


class ProductLocationCreate(ProductLocationBase):
    pass


class ProductLocationUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)
    is_primary: Optional[bool] = None


class ProductLocation(ProductLocationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
