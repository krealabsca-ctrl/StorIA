# Arquitectura de StorAI

## Visión General

StorAI es un sistema integral de gestión de inventario, ecommerce y bot de Telegram diseñado para optimizar las operaciones de almacén y venta. La arquitectura está basada en microservicios con una API REST centralizada.

## Stack Tecnológico

### Backend
- **Framework:** FastAPI 0.109.0
- **Python:** 3.11+
- **ORM:** SQLAlchemy 2.0
- **Base de Datos:** PostgreSQL 15+
- **Autenticación:** JWT (python-jose)
- **Bot de Telegram:** python-telegram-bot 20.7

### Infraestructura
- **Contenedorización:** Docker & Docker Compose
- **Cache:** Redis (opcional para sesiones)
- **API Documentation:** Swagger/OpenAPI (automático con FastAPI)

## Arquitectura de Capas

```
┌─────────────────────────────────────────────────────────┐
│                    Clientes                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Dashboard  │  │   Ecommerce   │  │  Bot Telegram│ │
│  │   Admin      │  │   Web         │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  API Gateway (FastAPI)                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  /api/v1/inventory  │  /api/v1/ecommerce        │  │
│  │  /api/v1/dashboard  │  /api/v1/telegram          │  │
│  │  /api/v1/users      │  /api/v1/locations         │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  Business Logic Layer                    │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │ Inventory Service│  │ Order Service    │            │
│  │ Location Service  │  │ Invoice Service  │            │
│  └──────────────────┘  └──────────────────┘            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  Data Access Layer (ORM)                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │  SQLAlchemy Models (Product, Order, User, etc.)  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  PostgreSQL Database                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Tables: products, orders, users, locations, etc │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Módulos del Sistema

### 1. Módulo de Inventario & Backoffice
**Responsabilidades:**
- Gestión completa de productos (CRUD)
- Control de stock con alertas automáticas
- Clasificación por categorías, subcategorías y marcas
- Gestión de proveedores y órdenes de compra
- Dashboard administrativo con métricas en tiempo real

**Endpoints principales:**
- `POST /api/v1/inventory/products/` - Crear producto
- `GET /api/v1/inventory/products/` - Listar productos
- `GET /api/v1/inventory/products/{id}` - Obtener producto
- `PUT /api/v1/inventory/products/{id}` - Actualizar producto
- `POST /api/v1/inventory/products/{id}/stock` - Ajustar stock
- `GET /api/v1/inventory/products/low-stock/` - Alertas de stock bajo

### 2. Módulo de Ecommerce & Facturación
**Responsabilidades:**
- Catálogo web sincronizado en tiempo real
- Carrito de compras y checkout
- Gestión de pedidos de clientes
- Facturación electrónica (XML/JSON)
- Descuento automático de stock al confirmar venta

**Endpoints principales:**
- `POST /api/v1/ecommerce/orders/` - Crear orden
- `GET /api/v1/ecommerce/orders/{id}` - Obtener orden
- `POST /api/v1/ecommerce/invoices/` - Generar factura

### 3. Módulo de Bot de Telegram (Diferenciador)
**Responsabilidades:**
- Consultas de stock por nombre, SKU o categoría
- Validación de empleados por ID de Telegram
- Respuestas con ubicación física exacta
- Analytics de consultas para optimización
- Logs de tiempos de respuesta

**Comandos del bot:**
- `/start` - Iniciar sesión
- `/buscar <nombre>` - Buscar por nombre
- `/sku <código>` - Buscar por SKU
- `/categoria <nombre>` - Buscar por categoría
- Búsqueda directa (escribir nombre sin comando)

## Modelo de Datos

### Entidades Principales

**Producto (Product)**
```python
- id, sku, barcode, name, description
- category_id, subcategory_id, brand_id
- cost_price, sale_price
- stock_current, stock_minimum, stock_status
- is_active, is_available_for_sale
```

**Ubicación (Location)**
```python
- id, code, name
- aisle, shelf, level, zone
- full_location (formato: "Pasillo A - Estante 3 - Nivel 2")
- location_type, capacity
```

**Usuario de Telegram (TelegramUser)**
```python
- telegram_id, telegram_username
- user_id (relación con User del sistema)
- is_active, is_verified
```

**Log de Consultas (TelegramQueryLog)**
```python
- telegram_user_id, query_text, query_type
- products_found, response_time_ms
- product_ids (para analytics)
```

## Flujo de Datos

### Consulta de Stock vía Bot de Telegram

```
1. Usuario envía mensaje al bot
   ↓
2. Bot verifica si telegram_id está autorizado
   ↓
3. Bot consulta base de datos (SQLAlchemy)
   ↓
4. Bot formatea respuesta con:
   - Nombre y SKU
   - Stock actual
   - Ubicación física exacta
   - Estado de disponibilidad
   ↓
5. Bot envía respuesta al usuario
   ↓
6. Bot registra log de consulta (analytics)
```

### Proceso de Venta Ecommerce

```
1. Cliente crea orden
   ↓
2. Sistema valida stock disponible
   ↓
3. Sistema genera factura electrónica
   ↓
4. Sistema descuenta stock automáticamente
   ↓
5. Sistema registra movimiento de stock
   ↓
6. Sistema actualiza estado de producto
```

## Seguridad

### Autenticación
- JWT tokens para API REST
- Validación de IDs de Telegram para bot
- Hashing de contraseñas con bcrypt

### Autorización
- Roles: Admin, Manager, Warehouse Staff, Sales
- Verificación de usuario activo
- Validación de permisos por endpoint

## Escalabilidad

### Horizontal Scaling
- API stateless (puede escalar horizontalmente)
- Bot de Telegram puede ejecutarse en múltiples instancias
- PostgreSQL con connection pooling

### Optimizaciones
- Índices en campos de búsqueda (sku, name, barcode)
- Caching de consultas frecuentes (Redis)
- Paginación en listados
- Query optimization con SQLAlchemy

## Monitoreo y Analytics

### Métricas del Bot
- Productos más buscados
- Usuarios más activos
- Tiempos de respuesta promedio
- Distribución de tipos de consulta
- Tendencias de búsqueda por día

### Dashboard Administrativo
- Total de productos
- Productos por estado de stock
- Valor total del inventario
- Alertas de stock bajo
- Consultas del bot (últimos 7 días)

## Próximos Pasos

### Fase 2 (Sugerida)
- Frontend React para Dashboard y Ecommerce
- Integración con pasarela de pago real
- Reportes PDF y exportación de datos
- Notificaciones push para alertas
- Integración con ERP externo

### Fase 3 (Sugerida)
- Módulo de compras y proveedores avanzado
- Gestión de devoluciones y garantías
- Análisis predictivo de demanda
- Integración con sistemas de logística
- Mobile app para operarios
