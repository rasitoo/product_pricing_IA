# Implementation Plan: Interfaz de Revisión en Carrusel Estilo Tinder

**Branch**: `002-carousel-review-ui` | **Date**: 2026-05-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-carousel-review-ui/spec.md`

## Summary

Reemplazar la consola de revisión basada en formulario de la feature 001 por una interfaz estilo Tinder: carrusel de una propuesta a la vez con fotos deslizables, swipe o botones para aceptar/rechazar, formulario inline opcional para modificaciones, mecanismo de bloqueo optimista con TTL de 60 s y registro de señales de retroalimentación para reentrenamiento de la IA. El frontend usa React + `@use-gesture/react` + `react-spring`. El backend extiende la API FastAPI existente con tres nuevos endpoints de cola/lock y amplía el endpoint de revisión para crear `FeedbackSignal` y gestionar el nuevo estado `modified_pending_reapproval`.

## Technical Context

**Language/Version**: Python 3.13 (backend), JavaScript ES2023 (frontend)
**Python Environment & Package Manager**: uv para entorno virtual y dependencias; nuevas librerías via `uv add`
**Primary Dependencies (backend)**: FastAPI, SQLAlchemy, Alembic, Pydantic — mismo stack que feature 001; sin dependencias Python nuevas
**Primary Dependencies (frontend nuevas)**: `@use-gesture/react`, `react-spring` — añadir con `npm install`
**Storage**: PostgreSQL 16 — dos tablas nuevas (`review_lock`, `feedback_signal`) + enum ampliado en `publication_draft`
**Testing**: pytest (backend), Vitest (frontend); mocks para llamadas HTTP en tests unitarios de frontend
**Target Platform**: Navegadores de escritorio modernos (Chrome, Firefox, Edge); sin soporte móvil en v1
**Project Type**: Extensión de aplicación web existente (backend API + frontend de operaciones)
**Performance Goals**: Carga de siguiente propuesta en carrusel < 2 s; respuesta de endpoints de lock < 100 ms p95
**Constraints**: Sin autenticación (red privada/interna); sin publicación externa; swipe + botones como mecanismo de interacción; desktop-only
**Evaluation Metrics**: Tasa de corrección por campo (descripción vs precio), tiempo promedio de revisión por propuesta, tasa de conflictos de lock concurrente
**Cost Budget**: Sin coste adicional de IA por esta feature; coste de sesión operativa se mide via métricas existentes de la feature 001
**Scale/Scope**: 1–5 operadores simultáneos, 100–300 propuestas/día

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Baseline and proposed solution are both defined with measurable quality and cost outputs. *(Métricas de revisión humana definidas en spec: tasa de corrección, tiempo de revisión, tasa de conflictos.)*
- [x] Experiment reproducibility is defined. *(No hay nuevos modelos de IA; el pipeline de feedback es trazable via FeedbackSignal con valores original/corregido.)*
- [x] API key handling and secret storage strategy are defined without plaintext secrets. *(Sin nuevas claves; las existentes usan variables de entorno, sin cambio.)*
- [x] Cost guardrails are defined. *(Sin nuevas llamadas a APIs de pago; los guardrails de la feature 001 aplican.)*
- [x] Test strategy includes unit tests and integration tests/mocks for paid API interactions. *(Tests unitarios para lógica de lock/estado carrusel; tests de integración con testcontainers para PostgreSQL; no hay nuevas APIs de pago.)*
- [x] Notebook deliverable (.ipynb) is planned. *(Se actualiza `notebooks/pricing-eval.ipynb` para incluir métricas de revisión humana si los datos lo justifican; no es un notebook nuevo.)*
- [x] For Python features, environment and dependencies are managed with uv, and new packages use `uv add`. *(Sin dependencias Python nuevas; las de frontend se gestionan con npm.)*

## Project Structure

### Documentation (this feature)

```text
specs/002-carousel-review-ui/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
backend/
├── src/
│   ├── api/
│   │   └── v1/
│   │       ├── proposals.py          # GET endpoint extendido con imágenes
│   │       ├── reviews.py            # POST extendido: FeedbackSignal + modified_pending_reapproval
│   │       ├── review_queue.py       # NUEVO: GET /review-queue
│   │       └── review_lock.py        # NUEVO: POST/DELETE /lock + POST /lock/heartbeat
│   ├── models/
│   │   ├── review_lock.py            # NUEVO: modelo ReviewLock
│   │   └── feedback_signal.py        # NUEVO: modelo FeedbackSignal
│   ├── services/
│   │   ├── review_service.py         # EXTENDIDO: crear FeedbackSignal, cambiar estado
│   │   └── review_lock_service.py    # NUEVO: adquirir, renovar, liberar locks
│   └── repositories/
│       └── product_repository.py     # EXTENDIDO: consulta de cola con prioridad
├── migrations/versions/
│   └── 0002_carousel_review.py       # NUEVO: tablas review_lock, feedback_signal + enum
└── tests/
    ├── unit/
    │   └── test_review_lock_service.py
    ├── integration/
    │   └── test_review_queue_endpoint.py
    └── contract/
        └── test_carousel_openapi.py

frontend/
├── src/
│   ├── pages/
│   │   └── CarouselPage.jsx          # NUEVO: página principal del carrusel
│   ├── components/
│   │   ├── CarouselCard.jsx          # NUEVO: tarjeta deslizable con animación spring
│   │   ├── PhotoViewer.jsx           # NUEVO: visor de fotos con scroll-snap
│   │   ├── EditFormPanel.jsx         # NUEVO: formulario inline de modificación
│   │   └── UndoToast.jsx             # NUEVO: toast de 5 s con acción deshacer
│   ├── hooks/
│   │   ├── useCarouselQueue.js       # NUEVO: lógica de carga de cola y avance
│   │   └── useLockHeartbeat.js       # NUEVO: heartbeat cada 20 s
│   ├── services/
│   │   └── api.js                    # EXTENDIDO: fetchNextQueueItem, lock/unlock/heartbeat
│   └── state/
│       └── sessionId.js              # NUEVO: UUID v4 anónimo en sessionStorage
└── tests/
    ├── CarouselCard.test.jsx
    ├── useCarouselQueue.test.js
    └── useLockHeartbeat.test.js
```

**Structure Decision**: Arquitectura web existente backend/frontend. Se añaden módulos nuevos sin modificar la estructura de carpetas existente. La página de carrusel coexiste con `ReviewPage.jsx` (la consola de la feature 001 permanece accesible durante la transición).

## Complexity Tracking

No se identifican violaciones constitucionales.

## Post-Design Constitution Re-Check

- [x] Baseline/propuesta medibles en calidad/coste: métricas de revisión humana (tasa de corrección por campo, tiempo de revisión) trazadas via FeedbackSignal y LLMMetric existente.
- [x] Reproducibilidad: FeedbackSignal registra valor original y corregido; trazable desde cualquier propuesta.
- [x] Secrets: sin claves nuevas; variables de entorno de la feature 001 aplican.
- [x] Guardrails de coste: sin nuevas APIs de pago; el lock TTL previene bloqueos indefinidos.
- [x] Tests: unit (lógica de lock y estado de carrusel) + integration (endpoints de cola y lock con testcontainers) + contract (validación OpenAPI).
- [x] Entorno Python con uv; dependencias frontend con npm; sin mezcla de gestores.
