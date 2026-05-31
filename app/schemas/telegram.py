"""Schemas for Telegram bot users"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TelegramUserBase(BaseModel):
    telegram_id: int
    telegram_username: Optional[str] = Field(None, max_length=100)
    telegram_first_name: Optional[str] = Field(None, max_length=100)
    telegram_last_name: Optional[str] = Field(None, max_length=100)
    user_id: Optional[int] = None
    is_active: bool = True
    is_verified: bool = False


class TelegramUserCreate(TelegramUserBase):
    pass


class TelegramUserUpdate(BaseModel):
    telegram_username: Optional[str] = Field(None, max_length=100)
    telegram_first_name: Optional[str] = Field(None, max_length=100)
    telegram_last_name: Optional[str] = Field(None, max_length=100)
    user_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class TelegramUser(TelegramUserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TelegramQueryLogBase(BaseModel):
    telegram_user_id: int
    query_text: str = Field(..., max_length=500)
    query_type: Optional[str] = Field(None, max_length=50)
    products_found: int = Field(default=0, ge=0)
    response_time_ms: Optional[float] = None
    product_ids: Optional[str] = None


class TelegramQueryLogCreate(TelegramQueryLogBase):
    pass


class TelegramQueryLog(TelegramQueryLogBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
