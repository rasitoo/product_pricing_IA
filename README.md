# product\_pricing\_IA

Asistente de pricing de segunda mano impulsado por IA. Recibe fotos de un producto,
genera una descripción de venta y un precio sugerido con trazabilidad de señales, y exige
aprobación humana obligatoria antes de exportar cualquier borrador. El despliegue es
progresivo: local con Docker → cloud (AWS) en fases posteriores.

---

## Índice

1. [Cómo se desarrolló este proyecto (SpecKit)](#1-cómo-se-desarrolló-este-proyecto-speckit)
2. [Arquitectura general](#2-arquitectura-general)
3. [Módulo de IA — el corazón del sistema](#3-módulo-de-ia--el-corazón-del-sistema)
4. [Interfaz de revisión en carrusel](#4-interfaz-de-revisión-en-carrusel)
5. [Observabilidad y control de costes](#5-observabilidad-y-control-de-costes)
6. [Estructura del repositorio](#6-estructura-del-repositorio)
7. [Arranque rápido](#7-arranque-rápido)
8. [Tests](#8-tests)
9. [Variables de entorno](#9-variables-de-entorno)
10. [Notebook de demostración de la IA](#10-notebook-de-demostración-de-la-ia)

---

## 1. Cómo se desarrolló este proyecto (SpecKit)

Este proyecto se diseñó y construyó siguiendo el flujo de trabajo **SpecKit**, un proceso
estructurado de especificación → planificación → implementación asistido por IA (GitHub Copilot).

### Fases de SpecKit

| Fase | Comando | Artefacto generado |
|---|---|---|
| **Specify** | `/speckit.specify` | `spec.md` — requisitos funcionales, escenarios de usuario, criterios de éxito |
| **Clarify** | `/speckit.clarify` | Preguntas de ambigüedad resueltas e integradas en la spec |
| **Plan** | `/speckit.plan` | `plan.md` — arquitectura, modelo de datos, contratos de API, investigación técnica |
| **Tasks** | `/speckit.tasks` | `tasks.md` — tareas ordenadas por dependencia |
| **Implement** | `/speckit.implement` | Código fuente generado e integrado por el agente |

### Features especificadas

#### Feature 001 — Asistente de Venta Reventa por Foto

Especificación inicial del sistema completo. Define:

- Flujo de ingesta de fotos vía API propia (v1).
- Pipeline de análisis IA: visión + búsqueda en tiempo real + pricing.
- Revisión humana obligatoria para todas las propuestas.
- Exportación manual de borradores aprobados en v1 (sin publicación externa automática).
- Observabilidad de coste, calidad y fallos del LLM.
- Despliegue progresivo local → cloud.

Artefactos: [specs/001-resale-pricing-assistant/](specs/001-resale-pricing-assistant/)

#### Feature 002 — Interfaz de Revisión en Carrusel Estilo Tinder

Interfaz web sin autenticación para que los operadores revisen las propuestas una a una.
Define:

- Carrusel visual (swipe derecha = aprobar, swipe izquierda = rechazar).
- Formulario inline para correcciones de descripción y precio.
- Bloqueo optimista de propuestas (TTL 60 s) para revisión multi-dispositivo.
- Retroalimentación de correcciones al backend como señal de reentrenamiento.
- Indicador de estado offline con reintento automático al recuperar red.

Artefactos: [specs/002-carousel-review-ui/](specs/002-carousel-review-ui/)

### Por qué SpecKit

- **Trazabilidad total**: cada decisión de diseño está documentada en `spec.md` y `plan.md`
  antes de existir una línea de código.
- **Clarificaciones explícitas**: las ambigüedades de requisitos se resuelven en sesiones
  de clarificación y quedan registradas en la spec.
- **Restricciones de IA como primer ciudadano**: las specs incluyen secciones obligatorias de
  coste/calidad (`CQR-*`) y reproducibilidad (`RDA-*`) para cualquier feature con IA.
- **Implementación asistida**: el agente implementa a partir del `tasks.md` generado,
  reduciendo la deuda técnica y manteniendo coherencia con la spec.

---

## 2. Arquitectura general

```
┌─────────────────────────────────────────────────────────────────┐
│  Operador / Cliente                                             │
│  POST /api/v1/products  ──►  POST /api/v1/images/{id}          │
└────────────────┬────────────────────────────────────────────────┘
                 │  FastAPI (backend/src/main.py)
                 ▼
┌────────────────────────────────┐
│  API REST (FastAPI + Uvicorn)  │
│  /api/v1/products              │
│  /api/v1/images                │
│  /api/v1/proposals             │
│  /api/v1/reviews               │
│  /api/v1/review-queue          │
│  /api/v1/review-lock           │
│  /api/v1/exports               │
│  /api/v1/metrics/llm           │
└──────────┬─────────────────────┘
           │
    ┌──────▼──────┐       ┌──────────────────────────┐
    │  PostgreSQL  │       │  Celery Worker           │
    │  (SQLAlchemy)│◄──────│  process_product task    │
    └─────────────┘       │  ┌──────────────────────┐│
                          │  │  PricingService       ││
                          │  │  ├─ LLMClient         ││
                          │  │  │  (GPT-4o vision)   ││
                          │  │  └─ ExternalComparable││
                          │  │     Client            ││
                          │  └──────────────────────┘│
                          └──────────────────────────┘
           │
    ┌──────▼──────────────────────────────────────┐
    │  Frontend React (Vite)                      │
    │  Carrusel de revisión — sin autenticación   │
    └─────────────────────────────────────────────┘
```

**Stack tecnológico**

| Capa | Tecnología |
|---|---|
| Backend | Python 3.13, FastAPI, Uvicorn, SQLAlchemy 2, Alembic |
| Cola de tareas | Celery + Redis |
| Base de datos | PostgreSQL 16 (Docker local) |
| IA | OpenAI GPT-4o (visión multimodal) |
| Búsqueda web | DuckDuckGo Search (`ddgs`) |
| Frontend | React 18, Vite, TanStack Query |
| Gestión de entorno | `uv` (entorno virtual + dependencias) |
| Tests | pytest, pytest-asyncio, testcontainers |

---

## 3. Módulo de IA — el corazón del sistema

### Pipeline de análisis de un producto

El pipeline se ejecuta como tarea Celery asíncrona
([backend/src/workers/process_product_job.py](backend/src/workers/process_product_job.py))
para desacoplar la latencia de la petición HTTP.

```
Fotos (base64 / disco)
        │
        ▼
┌───────────────────────┐
│  LLMClient            │  GPT-4o vision — analiza hasta 9 imágenes
│  (clients.py)         │  Devuelve: descripción, precio sugerido,
│                       │  confidence_score, product_keywords
└──────────┬────────────┘
           │  product_keywords
           ▼
┌───────────────────────┐
│  ExternalComparable   │  DuckDuckGo Search en tiempo real
│  Client               │  Busca comparables por palabras clave
│  (clients.py)         │  Devuelve lista de precios de mercado
└──────────┬────────────┘
           │
           ▼
┌───────────────────────────────────────────────────────────┐
│  PricingService.build_proposal()  (pricing_service.py)    │
│                                                           │
│  precio_final = LLM × 0.6  +  media_mercado × 0.4        │
│  banda [min, max] = ± 15%                                 │
│  trazabilidad: rationale_internal + rationale_external    │
└───────────────────────────────────────────────────────────┘
```

### Prompt de sistema (LLMClient)

El prompt instruye al modelo a responder **únicamente con JSON válido** con cuatro campos:
`description`, `suggested_price`, `confidence`, `product_keywords`.

Además se inyecta contexto dinámico en el prompt:

- **Correcciones de operadores**: las últimas 15 correcciones humanas de descripción o
  precio se incluyen en el prompt para que el modelo aprenda a evitar esos patrones de error.
- **Historial interno**: las últimas 10 ventas reales de nuestra plataforma con precio,
  condición y similitud, usadas como referencia de precios reales.
- **Precios de mercado**: resumen de las señales obtenidas por `ExternalComparableClient`
  con la media del mercado online.

Código: [backend/src/services/clients.py](backend/src/services/clients.py)

### Contexto de enriquecimiento

Antes de llamar al LLM, el worker construye el contexto desde la base de datos:

```python
context = {
    "feedback_signals": [...],   # Correcciones recientes de operadores
    "historical_refs":  [...],   # Ventas históricas propias
}
```

Esto permite que el modelo se **retroalimente progresivamente** de las decisiones humanas
sin necesidad de fine-tuning: las correcciones del operador en la interfaz de revisión se
almacenan como `FeedbackSignal` y se incluyen automáticamente en el prompt del siguiente
análisis.

### Modo stub (desarrollo sin API key)

Cuando `LLM_STUB=true` o `OPENAI_API_KEY` está vacía, `LLMClient` devuelve datos
sintéticos sin realizar ninguna llamada real. Esto permite desarrollar y ejecutar tests
sin incurrir en costes.

### Control de presupuesto diario

`CostGuardrailService` comprueba el gasto acumulado del día antes de cada llamada al LLM.
Si el gasto supera `LLM_DAILY_BUDGET_USD` (por defecto 25 USD), la llamada se bloquea y
se registra con `outcome = "blocked_by_budget"` en la tabla `llm_metrics`.

Código: [backend/src/services/cost_guardrail_service.py](backend/src/services/cost_guardrail_service.py)

---

## 4. Interfaz de revisión en carrusel

La interfaz web ([frontend/src/pages/ReviewPage.jsx](frontend/src/pages/ReviewPage.jsx))
no requiere autenticación. Muestra las propuestas una a una en formato carrusel:

- **Swipe derecha / botón ✓** → aprobar la propuesta tal como está.
- **Swipe izquierda / botón ✗** → rechazar; formulario inline opcional para corregir
  descripción y/o precio.
- **Undo (5 s)** → posibilidad de deshacer la última acción.
- **Bloqueo optimista** → la propuesta en revisión se bloquea para otras sesiones (TTL 60 s).
- **Estado offline** → si se pierde la conexión, la acción se guarda en memoria y se
  reintenta automáticamente al recuperar la red.

Las correcciones confirmadas se envían al backend como `FeedbackSignal`, cerrando el
bucle de retroalimentación hacia el pipeline de IA.

---

## 5. Observabilidad y control de costes

Cada llamada al LLM se registra en la tabla `llm_metrics` con:

| Campo | Descripción |
|---|---|
| `outcome` | `success`, `error`, `timeout`, `blocked_by_budget` |
| `cost_usd` | Coste estimado de la llamada |
| `latency_ms` | Latencia total de la llamada |
| `model_name` | Versión del modelo usada |
| `prompt_version` | Versión del prompt |

El endpoint `GET /api/v1/metrics/llm` devuelve un resumen agregado:
tasa de éxito, coste total, coste medio por llamada, latencia p95 y número de bloqueos
por presupuesto.

---

## 6. Estructura del repositorio

```
product_pricing_IA/
├── backend/
│   ├── src/
│   │   ├── api/v1/          # Routers FastAPI (products, proposals, reviews, etc.)
│   │   ├── config/          # Settings (pydantic-settings), database, middleware
│   │   ├── models/          # Modelos SQLAlchemy (Product, AIProposal, FeedbackSignal…)
│   │   ├── repositories/    # Acceso a datos por entidad
│   │   ├── services/
│   │   │   ├── clients.py            # LLMClient (GPT-4o) + ExternalComparableClient
│   │   │   ├── pricing_service.py    # Orquesta LLM + web + blending de precios
│   │   │   ├── cost_guardrail_service.py  # Control de presupuesto diario
│   │   │   ├── llm_metrics_service.py     # Registro y resumen de métricas LLM
│   │   │   ├── review_service.py          # Aprobación / rechazo / edición
│   │   │   └── …
│   │   └── workers/
│   │       ├── celery_app.py              # Configuración de Celery
│   │       └── process_product_job.py     # Tarea asíncrona de análisis IA
│   ├── migrations/          # Migraciones Alembic
│   └── tests/               # unit / integration / contract
├── frontend/
│   └── src/
│       ├── pages/           # ReviewPage (carrusel), etc.
│       ├── components/      # CarouselCard, SwipeableCard…
│       ├── hooks/           # useReviewQueue, useOfflineSync…
│       └── services/        # Clientes HTTP (TanStack Query)
├── infra/
│   └── docker/
│       └── docker-compose.yml   # PostgreSQL 16 + Redis
├── notebooks/
│   ├── pricing-eval.ipynb       # Evaluación de calidad/coste (RDA-002)
│   └── ia-demo.ipynb            # Demostración interactiva del pipeline de IA
└── specs/
    ├── 001-resale-pricing-assistant/   # Spec, plan, tasks de la feature 001
    └── 002-carousel-review-ui/         # Spec, plan, tasks de la feature 002
```

---

## 7. Arranque rápido

### 1. Levantar dependencias locales (PostgreSQL + Redis)

```bash
docker compose -f infra/docker/docker-compose.yml up -d
```

### 2. Entorno Python con uv

```bash
uv venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

uv sync
```

### 3. Configurar variables de entorno

Copia el archivo de ejemplo y rellena las claves:

```bash
cp .env.example .env.local
```

Las variables mínimas para desarrollo son:

```env
OPENAI_API_KEY=sk-...          # Vacío → usa stub (sin coste)
LLM_STUB=true                  # true en dev/test para evitar llamadas reales
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/pricing
REDIS_URL=redis://localhost:6379/0
```

### 4. Ejecutar backend

```bash
uv run uvicorn backend.src.main:app --reload --port 8000
```

### 5. Ejecutar worker Celery (en otra terminal)

```bash
uv run celery -A backend.src.workers.celery_app worker --loglevel=info
```

### 6. Ejecutar frontend

```bash
cd frontend
npm install
npm run dev
```

La interfaz de revisión estará disponible en `http://localhost:5173`.
La API estará disponible en `http://localhost:8000`.
La documentación interactiva de la API en `http://localhost:8000/docs`.

---

## 8. Tests

```bash
# Backend — todos los tests
uv run pytest backend/tests -q

# Backend — solo unitarios (sin Docker)
uv run pytest backend/tests/unit -q

# Frontend
cd frontend && npm test -- --run
```

Los tests de integración usan `testcontainers` para levantar PostgreSQL y Redis
automáticamente; no requieren un Docker Compose activo por separado.

---

## 9. Variables de entorno

| Variable | Por defecto | Descripción |
|---|---|---|
| `OPENAI_API_KEY` | `""` | Clave de API de OpenAI. Vacía activa el stub. |
| `LLM_STUB` | `false` | `true` para usar respuestas sintéticas sin llamadas reales. |
| `LLM_DAILY_BUDGET_USD` | `25.0` | Límite de gasto diario en USD antes de bloquear llamadas. |
| `LLM_REQUEST_TIMEOUT_SECONDS` | `30` | Timeout por llamada al LLM. |
| `DATABASE_URL` | `sqlite:///./app.db` | URL de conexión a la base de datos. |
| `REDIS_URL` | `redis://localhost:6379/0` | URL de Redis (broker de Celery). |
| `IMAGE_STORAGE_MODE` | `local` | Modo de almacenamiento de imágenes (`local` o `s3`). |
| `IMAGE_STORAGE_PATH` | `data/uploads` | Ruta local de almacenamiento de imágenes. |

Las variables se leen desde `.env.local` (ignorado por git).

---

## 10. Notebook de demostración de la IA

El notebook [notebooks/ia-demo.ipynb](notebooks/ia-demo.ipynb) contiene una demostración
interactiva del pipeline completo de IA **sin necesidad de base de datos ni de API key**
(usa el modo stub por defecto).

Cubre:

1. Construcción del prompt de sistema con contexto de retroalimentación.
2. Llamada al LLM stub y análisis del resultado.
3. Búsqueda de comparables (mock) y blending de precios.
4. Interpretación de la trazabilidad (`rationale_internal` / `rationale_external`).
5. Proyección de costes por volumen con el guardrail de presupuesto.

Para ejecutarlo:

```bash
uv run jupyter lab notebooks/ia-demo.ipynb
```

El notebook de evaluación de calidad con datos piloto reales está en
[notebooks/pricing-eval.ipynb](notebooks/pricing-eval.ipynb).
