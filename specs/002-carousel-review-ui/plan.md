# Implementation Plan: Interfaz de Revisión en Carrusel Estilo Tinder

**Branch**: `002-carousel-review-ui` | **Date**: 2026-05-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/002-carousel-review-ui/spec.md`

## Summary

Interfaz de revisión de propuestas generadas por IA estilo Tinder: carrusel de tarjetas (fotos + descripción + precio) donde el operador acepta o rechaza con swipe/botón, sin autenticación. El backend expone endpoints de cola con bloqueo optimista (TTL 60 s) y registra señales de retroalimentación para el modelo de IA cuando el operador corrige campos. La feature está **completamente implementada y sus tests pasan** (74 tests: 47 backend + 27 frontend). Este plan documenta la arquitectura y sirve de referencia para tareas de mantenimiento y extensión.

## Technical Context

**Language/Version**: Python 3.13 (backend) · Node.js 18+ / React 18 (frontend)
**Python Environment & Package Manager**: `uv`; nuevas librerías con `uv add`
**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy 2.x, Alembic, Celery, `openai==2.36.0`, `ddgs==9.14.2`
- Frontend: React 18, Vite 5, `@use-gesture/react`, `react-spring`, Vitest 2, `@testing-library/react`

**Storage**: SQLite (tests) / PostgreSQL (producción); imágenes en `data/uploads/{product_id}/`
**Testing**: `pytest` (backend) · `vitest` (frontend); stub LLM activado con `LLM_STUB=true`
**Target Platform**: Escritorio (Chrome, Firefox, Edge); soporte móvil fuera de alcance v1
**Project Type**: Web application fullstack (FastAPI + React/Vite)
**Performance Goals**: Carga de tarjeta <2 s (SC-005); revisión por propuesta <60 s (SC-002)
**Constraints**: Sin autenticación (red privada); bloqueo optimista TTL 60 s; máx. 10 fotos en visor
**Evaluation Metrics**: Tasa de corrección por campo (FeedbackSignal), delta de precio operador vs IA
**Cost Budget**: Sin llamadas adicionales de IA en esta feature (CQR-001); presupuesto IA heredado de feature 001 ($25/día)
**Scale/Scope**: 1–5 operadores simultáneos; cola de propuestas de decenas a cientos de ítems

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Baseline y solución propuesta definidos con salidas medibles: tasa de aprobación/rechazo y tasa de corrección por campo (FeedbackSignal) son las métricas de calidad; coste IA sin incremento (CQR-001).
- [x] Reproducibilidad: stub LLM (`LLM_STUB=true`) en tests garantiza ejecución sin coste real; notebook `pricing-eval.ipynb` actualizable con métricas FeedbackSignal (RDA-002).
- [x] API keys: `openai_api_key` en `.env.local` (excluido de git); nunca en código fuente (Principio V).
- [x] Guardianes de coste: timeout configurable (`llm_request_timeout_seconds`), presupuesto diario `llm_daily_budget_usd`, stub automático cuando key vacía o `LLM_STUB=true`.
- [x] Estrategia de tests: unitarios (lógica de estado carrusel, ReviewLock), integración con mocks (LLM stub), contrato OpenAPI. 47 backend + 27 frontend pasan.
- [x] Notebook: `notebooks/pricing-eval.ipynb` existe; RDA-002 especifica actualización con métricas FeedbackSignal tras implementación.
- [x] Entorno Python gestionado con `uv`; dependencias añadidas con `uv add` (openai, ddgs).

## Project Structure

### Documentation (esta feature)

```
specs/002-carousel-review-ui/
├── plan.md                        # Este archivo
├── research.md                    # Decisiones técnicas de arquitectura (8 decisiones)
├── data-model.md                  # Modelo de datos: ReviewLock, FeedbackSignal, cola
├── quickstart.md                  # Guía de arranque local
├── contracts/
│   └── openapi-carousel.yaml      # Contrato OpenAPI de endpoints de revisión
└── tasks.md                       # Tareas de implementación (T001–T054, completadas)
```

### Source Code (raíz del repositorio)

```
backend/
├── src/
│   ├── models/
│   │   ├── review_lock.py          # Tabla ReviewLock (TTL 60 s)
│   │   ├── feedback_signal.py      # Señales de retroalimentación IA
│   │   ├── ai_proposal.py          # AIProposal (status enum extendido)
│   │   ├── product_image.py        # Imágenes de producto
│   │   └── operator_review.py      # Registro de decisiones del operador
│   ├── services/
│   │   ├── review_service.py       # Lógica de aprobación/rechazo/edición
│   │   ├── review_lock_service.py  # Adquirir/renovar/liberar bloqueos
│   │   ├── pricing_service.py      # Blend LLM 60% + mercado 40%
│   │   ├── clients.py              # LLMClient (gpt-4o) + ExternalComparableClient (DDGS)
│   │   └── storage_service.py      # Guardar/servir imágenes locales
│   ├── api/v1/
│   │   ├── review_queue.py         # GET /review-queue (cola con bloqueo)
│   │   ├── reviews.py              # POST /proposals/{id}/approve|reject|edit
│   │   ├── review_lock.py          # POST /proposals/{id}/lock, heartbeat, DELETE
│   │   ├── images.py               # GET/POST/DELETE /products/{id}/images
│   │   └── proposals.py            # GET /proposals/{id}
│   └── workers/
│       └── process_product_job.py  # Celery task con contexto IA enriquecido
└── tests/
    ├── contract/
    ├── integration/
    └── unit/

frontend/
├── src/
│   ├── components/
│   │   ├── CarouselCard.jsx        # Tarjeta con swipe (@use-gesture + react-spring)
│   │   ├── PhotoViewer.jsx         # Visor scroll-snap, máx. 10 fotos
│   │   ├── EditFormPanel.jsx       # Formulario inline descripción/precio
│   │   └── UndoToast.jsx           # Toast con ventana undo 5 s
│   ├── pages/
│   │   └── ReviewPage.jsx          # Página principal del carrusel
│   ├── services/
│   │   └── reviewApi.js            # Llamadas fetch al backend
│   └── state/
│       └── useReviewQueue.js       # Hook gestión de cola y bloqueos
└── tests/
    ├── CarouselCard.test.jsx
    ├── EditFormPanel.test.jsx
    ├── PhotoViewer.test.jsx
    ├── UndoToast.test.jsx
    └── review-flow.spec.js
```

**Structure Decision**: Web application fullstack (Opción 2). Backend FastAPI en `backend/`, frontend React/Vite en `frontend/`. Sin proyectos adicionales.

## Complexity Tracking

No hay violaciones constitucionales que justificar. Toda la complejidad (bloqueo optimista, retroalimentación IA, búsqueda web) está justificada por requisitos funcionales explícitos en el spec.

## Phase 0: Research — Decisiones Técnicas

> Completado. Ver [research.md](research.md) para el detalle completo de las 8 decisiones.

| # | Decisión | Elección |
|---|----------|----------|
| 1 | Librería de gestos swipe | `@use-gesture/react` + `react-spring` |
| 2 | Visor de fotos | CSS `scroll-snap` nativo, sin dependencia extra |
| 3 | Bloqueo optimista | Tabla `ReviewLock` en PostgreSQL + heartbeat 20 s |
| 4 | Señales de retroalimentación IA | Tabla `FeedbackSignal` en PostgreSQL |
| 5 | Estado "modificada pendiente reaprobación" | Valor enum en `PublicationDraft.status` |
| 6 | Estado del carrusel en frontend | `useState`/`useReducer` + `fetch` nativo |
| 7 | Acción deshacer (undo 5 s) | Toast + `setTimeout`; envío al backend solo al confirmar |
| 8 | Identificador de sesión anónimo | UUID v4 en `sessionStorage`; cabecera `X-Session-Id` |

**Decisiones derivadas de clarificaciones (mayo 2026):**

| # | Edge case | Decisión |
|---|-----------|----------|
| 9 | Pérdida de red | Acción en memoria; reintento automático; indicador offline (FR-014) |
| 10 | Propuesta bloqueada (segundo operador) | Omitida silenciosamente; recibe la siguiente libre (FR-015) |
| 11 | Propuesta sin fotos | Excluida de la cola; debe corregirse antes de revisión (FR-016) |
| 12 | >10 fotos en visor | Mostrar máx. 10 + indicador "N fotos más" (CQR-006) |
| 13 | Propuesta ya procesada (conflicto) | Toast no bloqueante + avance automático (FR-017) |

## Phase 1: Design & Contracts

### Data Model

Ver [data-model.md](data-model.md) para el esquema completo.

| Entidad | Estado | Cambios |
|---------|--------|---------|
| `PublicationDraft` | Modificada | Nuevo valor enum `modified_pending_reapproval` |
| `ReviewLock` | Nueva | TTL 60 s, UNIQUE por `proposal_id` |
| `FeedbackSignal` | Nueva | Correcciones campo a campo para pipeline IA |
| `ProductImage` | Existente | Endpoints de gestión añadidos |
| `ReviewQueue` | Vista lógica | Sin tabla; consulta SQL con exclusión de bloqueadas y sin-foto |

**Reglas de negocio críticas:**
- Cola excluye propuestas bloqueadas por otra sesión (FR-015)
- Cola excluye propuestas sin imágenes asociadas (FR-016)
- Conflicto 409 en approve/reject → frontend muestra toast + avanza (FR-017)
- Acción pendiente offline se reintenta automáticamente (FR-014)
- Visor limita a 10 fotos; resto con indicador (CQR-006)

### API Contracts

Ver [contracts/openapi-carousel.yaml](contracts/openapi-carousel.yaml).

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/v1/review-queue` | Cola ordenada (excluye bloqueadas por otros + sin foto) |
| `POST` | `/api/v1/proposals/{id}/approve` | Aprobar propuesta |
| `POST` | `/api/v1/proposals/{id}/reject` | Rechazar con motivo opcional |
| `POST` | `/api/v1/proposals/{id}/edit` | Rechazar con correcciones → crea FeedbackSignal |
| `POST` | `/api/v1/proposals/{id}/lock` | Adquirir bloqueo; 409 si bloqueada por otra sesión |
| `POST` | `/api/v1/proposals/{id}/lock/heartbeat` | Renovar TTL a now+60 s |
| `DELETE` | `/api/v1/proposals/{id}/lock` | Liberar bloqueo al confirmar acción |
| `GET` | `/api/v1/products/{id}/images` | Listar imágenes del producto |
| `POST` | `/api/v1/products/{id}/images` | Subida multipart (SHA256 dedup, 20 MB) |
| `DELETE` | `/api/v1/products/{id}/images/{img_id}` | Eliminar imagen |

**Códigos de respuesta relevantes:**
- `204` — Cola vacía
- `409` — Conflicto: propuesta ya bloqueada o ya procesada
- `422` — UUID inválido u otros errores de validación

### Quickstart

Ver [quickstart.md](quickstart.md) para instrucciones de arranque local completas.

## Constitution Check Post-Design

- [x] Métricas de calidad y coste definidas (FeedbackSignal, sin coste adicional de IA).
- [x] Reproducibilidad garantizada (stub LLM, tests aislados).
- [x] Sin secretos en código; `.env.local` en `.gitignore`.
- [x] Guardianes de coste activos (timeout, budget, stub).
- [x] 74 tests pasan (47 backend + 27 frontend).
- [x] Notebook planificado para actualización de métricas (RDA-002).
- [x] `uv` para entorno y dependencias Python.
- [x] Nuevas reglas de negocio (FR-014 a FR-017, CQR-006) documentadas en spec y data-model.
