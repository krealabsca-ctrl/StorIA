"""Entry point de la aplicación FastAPI."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import api_router
from app.config import settings
from app.database import Base, engine

# Crear tablas de base de datos
Base.metadata.create_all(bind=engine)

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="StorAI API",
    description="Sistema Integral de Inventario, Ecommerce y Bot de Telegram",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas de la API
app.include_router(api_router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Estado y assets
# ---------------------------------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api")
def api_root():
    return {
        "message": "StorAI API",
        "version": "1.0.0",
        "modules": {
            "inventory": "Gestión de inventario y backoffice",
            "ecommerce": "Catálogo web y facturación",
            "telegram_bot": "Bot de Telegram para personal",
            "chat": "Chat bot público (cliente) y privado (admin)",
        },
    }


# ---------------------------------------------------------------------------
# Vistas HTML (frontend)
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
def view_landing():
    """Página pública del cliente con chat al bot."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/admin", include_in_schema=False)
def view_admin_login():
    """Login del backoffice."""
    return FileResponse(STATIC_DIR / "admin.html")


@app.get("/admin/dashboard", include_in_schema=False)
def view_admin_dashboard():
    """Dashboard interno con chat administrativo."""
    return FileResponse(STATIC_DIR / "dashboard.html")
