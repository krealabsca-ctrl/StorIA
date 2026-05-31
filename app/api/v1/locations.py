"""Warehouse locations API routes"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.models.users import User
from app.models.locations import Location, ProductLocation
from app.schemas.locations import (
    LocationCreate, LocationUpdate, Location,
    ProductLocationCreate, ProductLocationUpdate, ProductLocation
)

router = APIRouter()


@router.post("/locations/", response_model=Location, status_code=status.HTTP_201_CREATED)
def create_location(
    location: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear nueva ubicación en almacén"""
    db_location = Location(**location.dict())
    db_location.generate_full_location()
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


@router.get("/locations/", response_model=List[Location])
def list_locations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar todas las ubicaciones"""
    locations = db.query(Location).filter(Location.is_active == True).offset(skip).limit(limit).all()
    return locations


@router.get("/locations/{location_id}", response_model=Location)
def get_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener ubicación por ID"""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    return location


@router.put("/locations/{location_id}", response_model=Location)
def update_location(
    location_id: int,
    location_update: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar ubicación"""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    
    update_data = location_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(location, field, value)
    
    location.generate_full_location()
    db.commit()
    db.refresh(location)
    return location


@router.post("/product-locations/", response_model=ProductLocation, status_code=status.HTTP_201_CREATED)
def assign_product_location(
    product_location: ProductLocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Asignar producto a ubicación"""
    db_product_location = ProductLocation(**product_location.dict())
    db.add(db_product_location)
    db.commit()
    db.refresh(db_product_location)
    return db_product_location


@router.get("/products/{product_id}/locations", response_model=List[ProductLocation])
def get_product_locations(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener ubicaciones de un producto"""
    locations = db.query(ProductLocation).filter(
        ProductLocation.product_id == product_id
    ).all()
    return locations


@router.put("/product-locations/{location_id}", response_model=ProductLocation)
def update_product_location(
    location_id: int,
    location_update: ProductLocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar cantidad en ubicación de producto"""
    product_location = db.query(ProductLocation).filter(
        ProductLocation.id == location_id
    ).first()
    
    if not product_location:
        raise HTTPException(status_code=404, detail="Asignación de ubicación no encontrada")
    
    update_data = location_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product_location, field, value)
    
    db.commit()
    db.refresh(product_location)
    return product_location
