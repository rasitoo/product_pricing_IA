# Quickstart - Interfaz de Revisión en Carrusel Estilo Tinder

## Prerequisitos

- Entorno de la feature 001 operativo (Docker Compose con PostgreSQL + Redis + backend FastAPI).
- Node.js >= 18 instalado.
- `uv` instalado para gestión del entorno Python.

## 1. Aplicar migración de base de datos

```bash
# Desde la raíz del repositorio
uv run alembic upgrade head
```

La migración añade:
- Valor `modified_pending_reapproval` al enum `publicationdraft_status`.
- Tabla `review_lock` con campos `proposal_id`, `session_id`, `locked_at`, `expires_at`.
- Tabla `feedback_signal` con campos `proposal_id`, `review_id`, `field_name`, `original_value`, `corrected_value`.

## 2. Arrancar el backend

```bash
# Desde la raíz del repositorio
uv run uvicorn backend.src.main:app --reload --port 8000
```

Verificar que los nuevos endpoints responden:

```bash
curl -s http://localhost:8000/api/v1/review-queue \
  -H "X-Session-Id: 00000000-0000-0000-0000-000000000001" | python -m json.tool
```

Respuesta esperada con cola vacía: `HTTP 204 No Content`.

## 3. Instalar dependencias del frontend

```bash
cd frontend
npm install
```

Las nuevas dependencias requeridas por esta feature:

```bash
npm install @use-gesture/react react-spring
```

## 4. Arrancar el frontend en modo desarrollo

```bash
# Desde frontend/
npm run dev
```

Abrir en el navegador: `http://localhost:5173`

La interfaz cargará directamente el carrusel de revisión sin solicitar credenciales.
Con la cola vacía se mostrará el mensaje "No hay propuestas pendientes de revisión".

## 5. Crear una propuesta de prueba

```bash
# Crear un producto de prueba (requiere tener imágenes en data/uploads/)
curl -s -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "source_channel": "api",
    "photos": [{"filename": "test.jpg", "content_base64": "<base64>"}]
  }'
```

O bien usar el seed script de la feature 001 si existe en `infra/scripts/`.

## 6. Flujo de revisión en carrusel

1. La tarjeta de la propuesta aparece con las fotos del producto en el visor deslizable.
2. **Aceptar**: arrastrar la tarjeta hacia la derecha o pulsar el botón ✓.
3. **Rechazar**: arrastrar hacia la izquierda o pulsar el botón ✗. Opcionalmente, añadir motivo en el formulario que aparece.
4. **Modificar y rechazar**: tras pulsar ✗, editar descripción y/o precio en el formulario inline y confirmar.
5. El toast de deshacer aparece 5 segundos; durante ese tiempo la acción no se envía al backend.
6. Tras confirmar, el carrusel avanza automáticamente a la siguiente propuesta.

## 7. Ejecutar los tests

```bash
# Tests del backend (desde raíz)
uv run pytest backend/tests/ -v

# Tests del frontend
cd frontend && npm test
```

## Variables de entorno relevantes

Sin variables de entorno nuevas para esta feature. Las variables de la feature 001 aplican directamente (`DATABASE_URL`, `REDIS_URL`, `OPENAI_API_KEY`, etc.).
