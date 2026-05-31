"""Main API router for v1"""
from fastapi import APIRouter
from app.api.v1 import inventory, locations, users, telegram, dashboard

api_router = APIRouter()

# Include routers
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
