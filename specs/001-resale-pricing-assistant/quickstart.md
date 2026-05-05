# Quickstart - Asistente de Venta Reventa por Foto

## 1) Prerrequisitos
- Python 3.13
- [uv](https://docs.astral.sh/uv/) instalado
- Node.js 20+
- Docker Desktop (opcional — solo necesario para PostgreSQL/Redis en entorno real)

---

## Modo rápido (SQLite local, sin Docker)

Para desarrollo y pruebas locales la aplicación usa **SQLite** por defecto. No es necesario Docker.

### 2a) Instalar dependencias Python

```bash
uv sync
```

> Todas las dependencias están declaradas en `pyproject.toml`. No ejecutar `pip install`.

### 3a) Levantar backend

```bash
uv run uvicorn backend.src.main:app --reload --port 8000
```

La base de datos `app.db` (SQLite) se crea automáticamente al arrancar.

API docs: http://localhost:8000/docs

### 4a) Ejecutar tests

```bash
uv run pytest backend/tests -q
```

Los tests usan `test.db` (SQLite) y no requieren servicios externos.

### 5a) Frontend de revisión operativa

```bash
cd frontend
npm install
npm run dev
```

UI de operación: http://localhost:5173

---

## Modo producción (PostgreSQL + Redis vía Docker)

### 2b) Levantar infraestructura

```bash
docker compose -f infra/docker/docker-compose.yml up -d postgres redis
```

### 3b) Variables de entorno

Crear `backend/.env.local` (fuera de git):

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/pricing_db
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=replace-me
LLM_DAILY_BUDGET_USD=25
IMAGE_STORAGE_MODE=local
IMAGE_STORAGE_PATH=./data/uploads
```

### 4b) Instalar dependencias y aplicar migraciones

```bash
uv sync
uv run alembic upgrade head
```

### 5b) Levantar backend y worker Celery

```bash
uv run uvicorn backend.src.main:app --reload --port 8000
# En otra terminal:
uv run celery -A backend.src.workers.celery_app worker -l info
```

---

## Flujo funcional v1

1. Crear producto con fotos vía `POST /api/v1/products`.
2. Recuperar propuesta IA vía `GET /api/v1/proposals/{proposal_id}`.
3. El operador revisa, aprueba/deniega/edita en la web JS (http://localhost:5173).
4. Exportar borrador aprobado vía `POST /api/v1/products/{product_id}/export`.

---

## Notebook de evaluación

```bash
uv run jupyter notebook notebooks/pricing-eval.ipynb
```

Contiene metodología, métricas baseline vs propuesta IA y comparativa de canales de ingesta.
- resultados baseline vs propuesta
- coste por corrida y por producto
- conclusiones y siguientes iteraciones
