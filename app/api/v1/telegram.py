"""Telegram users API routes"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.models.users import User
from app.models.telegram_users import TelegramUser, TelegramQueryLog
from app.schemas.telegram import (
    TelegramUserCreate, TelegramUserUpdate, TelegramUser as TelegramUserSchema,
    TelegramQueryLogCreate, TelegramQueryLog as TelegramQueryLogSchema,
)
from app.telegram_bot.analytics import generate_analytics_report

router = APIRouter()


@router.post("/users/", response_model=TelegramUserSchema, status_code=status.HTTP_201_CREATED)
def create_telegram_user(
    telegram_user: TelegramUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Registrar nuevo usuario de Telegram (empleado)"""
    # Verificar si el ID de Telegram ya existe
    existing = db.query(TelegramUser).filter(
        TelegramUser.telegram_id == telegram_user.telegram_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="El ID de Telegram ya está registrado")
    
    db_telegram_user = TelegramUser(**telegram_user.dict())
    db.add(db_telegram_user)
    db.commit()
    db.refresh(db_telegram_user)
    return db_telegram_user


@router.get("/users/", response_model=List[TelegramUserSchema])
def list_telegram_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar todos los usuarios de Telegram"""
    users = db.query(TelegramUser).offset(skip).limit(limit).all()
    return users


@router.get("/users/{telegram_user_id}", response_model=TelegramUserSchema)
def get_telegram_user(
    telegram_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener usuario de Telegram por ID"""
    user = db.query(TelegramUser).filter(TelegramUser.id == telegram_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario de Telegram no encontrado")
    return user


@router.put("/users/{telegram_user_id}", response_model=TelegramUserSchema)
def update_telegram_user(
    telegram_user_id: int,
    user_update: TelegramUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar usuario de Telegram"""
    user = db.query(TelegramUser).filter(TelegramUser.id == telegram_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario de Telegram no encontrado")
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{telegram_user_id}/verify", response_model=TelegramUserSchema)
def verify_telegram_user(
    telegram_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Verificar usuario de Telegram (autorizar acceso al bot)"""
    user = db.query(TelegramUser).filter(TelegramUser.id == telegram_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario de Telegram no encontrado")
    
    user.is_verified = True
    db.commit()
    db.refresh(user)
    return user


@router.get("/analytics/")
def get_analytics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener analytics del bot de Telegram"""
    report = generate_analytics_report(days=days)
    return report


@router.get("/query-logs/", response_model=List[TelegramQueryLogSchema])
def list_query_logs(
    skip: int = 0,
    limit: int = 100,
    telegram_user_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar logs de consultas del bot"""
    query = db.query(TelegramQueryLog)
    
    if telegram_user_id:
        query = query.filter(TelegramQueryLog.telegram_user_id == telegram_user_id)
    
    logs = query.order_by(TelegramQueryLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs
