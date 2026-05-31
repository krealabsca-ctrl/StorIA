"""Entry point de la aplicación FastAPI"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.api import api_router
from app.database import engine, Base

# Crear tablas de base de datos
Base.metadata.create_all(bind=engine)

# Crear aplicación FastAPI
app = FastAPI(
    title="StorAI API",
    description="Sistema Integral de Inventario, Ecommerce y Bot de Telegram",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir router de API
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    """Endpoint raíz"""
    return {
        "message": "StorAI API",
        "version": "1.0.0",
        "modules": {
            "inventory": "Gestión de inventario y backoffice",
            "ecommerce": "Catálogo web y facturación",
            "telegram_bot": "Bot de Telegram para personal"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
