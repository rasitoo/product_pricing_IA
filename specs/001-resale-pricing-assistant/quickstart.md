# Quickstart - Asistente de Venta Reventa por Foto

## 1) Prerrequisitos
- Python 3.13
- uv instalado
- Docker Desktop (para PostgreSQL y Redis locales)
- Node.js 20+ para frontend JS

## 2) Levantar infraestructura local
Desde la raiz del repositorio:

```bash
docker compose -f infra/docker/docker-compose.yml up -d postgres redis
```

## 3) Configurar backend Python con uv

```bash
uv venv
. .venv/Scripts/activate
uv add fastapi uvicorn sqlalchemy alembic pydantic-settings psycopg[binary] celery redis httpx
uv add --dev pytest pytest-asyncio testcontainers
```

Variables de entorno sugeridas (archivo .env.local, fuera de git):

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/pricing_db
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=replace-me
LLM_DAILY_BUDGET_USD=25
IMAGE_STORAGE_MODE=local
IMAGE_STORAGE_PATH=./data/uploads
```

## 4) Aplicar migraciones

```bash
uv run alembic upgrade head
```

## 5) Ejecutar backend API

```bash
uv run uvicorn backend.src.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## 6) Ejecutar worker de background

```bash
uv run celery -A backend.src.workers.celery_app worker -l info
```

## 7) Configurar frontend JS de revision

```bash
cd frontend
npm install
npm run dev
```

UI de operacion: http://localhost:5173

## 8) Flujo funcional v1
- Crear producto con fotos via API.
- Esperar propuesta IA y revisar justificacion (interna + externa).
- Aprobar, denegar o editar en la web JS.
- Exportar borrador aprobado para publicacion manual.

## 9) Pruebas

```bash
uv run pytest
```

## 10) Notebook de evaluacion
Crear/actualizar notebook paralelo en notebooks/pricing-eval.ipynb con:
- metodologia de evaluacion
- resultados baseline vs propuesta
- coste por corrida y por producto
- conclusiones y siguientes iteraciones
