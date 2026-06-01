# StorAI - Sistema Integral de Inventario, Ecommerce y Bot de Telegram

## Arquitectura del Proyecto

StorAI es un sistema robusto que combina:
- **Módulo 1:** Inventario Robusto & Backoffice (Dashboard Administrativo)
- **Módulo 2:** Ecommerce & Facturación Electrónica
- **Módulo 3:** Bot de Telegram Inteligente para Personal Interno

## Stack Tecnológico

- **Backend Framework:** FastAPI (Python 3.11 / 3.12 — **no 3.14**)
- **Base de Datos:** PostgreSQL 15 (vía Docker)
- **Driver PostgreSQL:** psycopg v3 (`postgresql+psycopg://...`)
- **ORM:** SQLAlchemy 2.0
- **Bot de Telegram:** python-telegram-bot v20+
- **Autenticación:** JWT + passlib/bcrypt 4.0.1
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

## Requisitos previos

- **Python 3.11 o 3.12** (NO uses 3.14 — pydantic-core 2.23.x no compila contra PyO3 0.22 en 3.14).
- **Docker Desktop** (para levantar PostgreSQL y Redis sin instalarlos en el host).
- macOS, Linux o Windows con WSL2.

Si solo tienes Python 3.14 instalado, instala 3.12 con [pyenv](https://github.com/pyenv/pyenv):

```bash
brew install pyenv
pyenv install 3.12.8
```

## Instalación paso a paso (macOS/Linux)

```bash
# 1. Clonar el repo y entrar al directorio
cd StorIA

# 2. Crear el venv con Python 3.12 EXPLÍCITAMENTE
#    (sustituye la ruta por la de tu instalación si es distinta)
/Users/$USER/.pyenv/versions/3.12.8/bin/python3.12 -m venv venv

# 3. Activar el venv
source venv/bin/activate

# 4. Verificar que estás en 3.12 antes de continuar
python --version   # debe decir Python 3.12.x

# 5. Actualizar pip e instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 6. Configurar variables de entorno
cp .env.example .env
# Edita .env si necesitas cambiar credenciales o tokens

# 7. Levantar PostgreSQL y Redis con Docker
#    (asegúrate de que Docker Desktop está corriendo)
docker compose up -d

# 8. Esperar a que Postgres acepte conexiones
until docker exec storai-postgres pg_isready -U postgres >/dev/null 2>&1; do sleep 1; done

# 9. Crear tablas e insertar datos de prueba
python scripts/seed_db.py

# 10. Levantar el servidor FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

En otra terminal (con el venv activado) puedes arrancar el bot de Telegram:

```bash
source venv/bin/activate
python -m app.telegram_bot.bot
```

## Verificación

Con el servidor corriendo:

```bash
curl http://localhost:8000/health
# {"status":"healthy"}

curl http://localhost:8000/
# {"message":"StorAI API","version":"1.0.0", ...}
```

O abre en el navegador:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Credenciales de prueba (creadas por seed_db.py)

| Rol      | Usuario  | Password    | Telegram ID  |
|----------|----------|-------------|--------------|
| Admin    | admin    | admin123    | 123456789    |
| Gerente  | gerente  | gerente123  | 987654321    |
| Operario | operario | operario123 | 555555555    |

## Detener el entorno

```bash
# Apagar FastAPI: Ctrl+C en la terminal donde corre uvicorn
# Apagar contenedores:
docker compose down

# Borrar también los volúmenes (resetea la BD):
docker compose down -v
```

## Notas de compatibilidad

- **DATABASE_URL** usa el driver `postgresql+psycopg://...` (psycopg v3). No uses el esquema `postgresql://` solo, porque SQLAlchemy intentaría cargar `psycopg2` que no está en `requirements.txt`.
- **bcrypt está fijado a 4.0.1** por compatibilidad con `passlib==1.7.4`. Las versiones 5.x rompen `passlib.handlers.bcrypt`.
- **psycopg[binary]==3.2.13** es el mínimo con wheels publicados en PyPI.

## Instalación en Windows

```powershell
# Crear venv con Python 3.12 (instálalo desde python.org si no lo tienes)
py -3.12 -m venv venv
venv\Scripts\activate

python --version   # debe ser 3.12.x

pip install --upgrade pip
pip install -r requirements.txt

copy .env.example .env

docker compose up -d
python scripts\seed_db.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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
