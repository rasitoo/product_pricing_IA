# product_pricing_IA

Asistente de pricing de segunda mano con IA, aprobacion humana obligatoria y despliegue progresivo.

## Arquitectura

- Backend Python/FastAPI en [backend/src/main.py](backend/src/main.py)
- Frontend JS/React para revision en [frontend/src/pages/ReviewPage.jsx](frontend/src/pages/ReviewPage.jsx)
- Base de datos PostgreSQL local via Docker Compose en [infra/docker/docker-compose.yml](infra/docker/docker-compose.yml)
- Metrica de coste/fallos LLM en endpoint `GET /api/v1/metrics/llm`

## Arranque rapido

1. Levantar dependencias locales:

```bash
docker compose -f infra/docker/docker-compose.yml up -d
```

2. Entorno Python y dependencias con uv:

```bash
uv venv
. .venv/Scripts/activate
uv sync
```

3. Ejecutar backend:

```bash
uv run uvicorn backend.src.main:app --reload --port 8000
```

4. Ejecutar frontend:

```bash
cd frontend
npm install
npm run dev
```

## Tests

```bash
uv run pytest backend/tests -q
cd frontend && npm test -- --run
```
