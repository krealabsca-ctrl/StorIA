# StorAI - Sistema Integral de Inventario, Ecommerce y Bot de Telegram

## Arquitectura del Proyecto

StorAI es un sistema robusto que combina:
- **Módulo 1:** Inventario Robusto & Backoffice (Dashboard Administrativo)
- **Módulo 2:** Ecommerce & Facturación Electrónica
- **Módulo 3:** Bot de Telegram Inteligente para Personal Interno

## Stack Tecnológico

- **Backend Framework:** FastAPI (Python 3.11+)
- **Base de Datos:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.0
- **Bot de Telegram:** python-telegram-bot v20+
- **Autenticación:** JWT
- **API Documentation:** Swagger/OpenAPI automática

## Estructura de Carpetas

```
storai/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point de FastAPI
│   ├── config.py               # Configuración general
│   ├── database.py             # Conexión a BD
│   ├── dependencies.py         # Dependencias de inyección
│   │
│   ├── core/                   # Utilidades core
│   │   ├── __init__.py
│   │   ├── security.py         # JWT, hashing
│   │   └── logging_config.py   # Configuración de logs
│   │
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── base.py             # Base model
│   │   ├── inventory.py        # Productos, categorías, stock
│   │   ├── locations.py        # Ubicaciones en almacén
│   │   ├── suppliers.py        # Proveedores
│   │   ├── users.py            # Usuarios del sistema
│   │   ├── telegram_users.py   # Usuarios de Telegram
│   │   ├── orders.py           # Pedidos de ecommerce
│   │   └── invoices.py         # Facturas electrónicas
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── inventory.py
│   │   ├── locations.py
│   │   ├── suppliers.py
│   │   ├── users.py
│   │   ├── telegram.py
│   │   ├── orders.py
│   │   └── invoices.py
│   │
│   ├── api/                    # Rutas de la API
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependencias de rutas
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── api.py          # Router principal
│   │   │   ├── inventory.py    # Endpoints de inventario
│   │   │   ├── locations.py    # Endpoints de ubicaciones
│   │   │   ├── suppliers.py    # Endpoints de proveedores
│   │   │   ├── dashboard.py    # Endpoints de dashboard
│   │   │   ├── ecommerce.py    # Endpoints de ecommerce
│   │   │   └── invoices.py     # Endpoints de facturación
│   │
│   ├── services/                # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── inventory_service.py
│   │   ├── location_service.py
│   │   ├── order_service.py
│   │   └── invoice_service.py
│   │
│   ├── telegram_bot/           # Módulo del Bot de Telegram
│   │   ├── __init__.py
│   │   ├── bot.py              # Configuración del bot
│   │   ├── handlers.py         # Manejadores de comandos
│   │   ├── keyboards.py        # Teclados inline
│   │   └── analytics.py        # Logs de consultas
│   │
│   └── static/                 # Archivos estáticos
│       └── css/
│
├── tests/                      # Tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_inventory.py
│   └── test_telegram.py
│
├── alembic/                    # Migraciones de BD
│   ├── versions/
│   └── env.py
│
├── scripts/                    # Scripts utilitarios
│   ├── seed_db.py              # Datos iniciales
│   └── create_admin.py
│
├── .env.example                # Variables de entorno ejemplo
├── .gitignore
├── requirements.txt            # Dependencias Python
├── pyproject.toml             # Configuración del proyecto
├── docker-compose.yml          # Docker para desarrollo
└── README.md
```

## Instalación

### macOS/Linux
```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales (DATABASE_URL, TELEGRAM_BOT_TOKEN, etc.)

# OPCIÓN 1: Usar PostgreSQL local (requiere PostgreSQL instalado)
# brew install postgresql  # macOS
# brew services start postgresql
# createdb storai

# OPCIÓN 2: Usar Docker para PostgreSQL
# docker-compose up -d

# Ejecutar script de inicialización de base de datos
python3 scripts/seed_db.py

# Iniciar servidor FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Iniciar Bot de Telegram (en terminal separado)
python3 -m app.telegram_bot.bot
```

### Windows
```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env
# Editar .env con tus credenciales

# Iniciar PostgreSQL (opcional con Docker)
docker-compose up -d

# Ejecutar script de inicialización de base de datos
python scripts/seed_db.py

# Iniciar servidor FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Iniciar Bot de Telegram (en terminal separado)
python -m app.telegram_bot.bot
```

## Documentación de la API

Una vez iniciado el servidor:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Características Principales

### Módulo 1: Inventario & Backoffice
- Control de stock estricto con alertas
- Ubicación física precisa en almacén
- Clasificación por categorías, subcategorías y marcas
- Gestión de proveedores
- Dashboard con gráficas y reportes

### Módulo 2: Ecommerce & Facturación
- Catálogo web sincronizado en tiempo real
- Carrito de compras y checkout
- Facturación electrónica (XML/JSON)
- Descuento automático de stock

### Módulo 3: Bot de Telegram
- Consultas de stock por nombre, SKU o categoría
- Validación de empleados por ID de Telegram
- Respuestas con ubicación física exacta
- Análisis de tiempos y patrones de búsqueda
- Logs para optimización de disposición física

## Seguridad

- Autenticación JWT para usuarios del sistema
- Validación de IDs de Telegram para empleados
- Encriptación de contraseñas con bcrypt
- CORS configurado para dominios permitidos
