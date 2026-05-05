# Implementation Plan: Asistente de Venta Reventa por Foto

**Branch**: `001-resale-pricing-assistant` | **Date**: 2026-05-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-resale-pricing-assistant/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Construir una plataforma por fases para recibir fotos de productos, generar descripcion y propuesta de precio con IA, y permitir aprobacion humana obligatoria en una web de operacion antes de exportar/publicar manualmente en v1. El backend se implementa en Python con API asincrona y observabilidad de coste/calidad/fallos de LLM; el frontend de revision se implementa en JavaScript. El almacenamiento usa PostgreSQL (inicialmente via Docker) y objetos de imagen con estrategia progresiva local -> S3-compatible -> S3 AWS.

## Technical Context

**Language/Version**: Python 3.13 (backend), JavaScript ES2023 (frontend)  
**Python Environment & Package Manager**: uv para entorno virtual y dependencias; nuevas librerias via `uv add`
**Primary Dependencies**: FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic Settings, Celery, Redis, httpx, pytest, pytest-asyncio; React + Vite + TanStack Query en frontend  
**Storage**: PostgreSQL 16 para datos transaccionales; imagenes en filesystem local en fases iniciales con abstraccion para S3-compatible/S3 en fases posteriores  
**Testing**: pytest (unit/integration/contract), testcontainers para PostgreSQL/Redis en integracion, mocks/stubs para APIs de pago  
**Target Platform**: Linux containers (local Docker y despliegue cloud progresivo)  
**Project Type**: Aplicacion web con backend API + frontend de operaciones  
**Performance Goals**: p95 < 2 min para generar propuesta completa; p95 < 500 ms para endpoints de consulta/revision; disponibilidad >= 99% en horario operativo  
**Constraints**: Aprobacion humana obligatoria en v1; sin publicacion externa automatica en v1; API propia como canal unico v1; sin dependencia obligatoria de AWS en fases tempranas  
**Evaluation Metrics**: tasa de aprobacion sin edicion, delta de precio propuesta vs precio final, coste medio por producto, tasa de fallo de llamadas LLM, latencia E2E por propuesta  
**Cost Budget**: limite diario inicial de gasto LLM 25 USD en dev/piloto y 150 USD en ciclo de evaluacion de feature; corte automatico al superar umbral configurable  
**Scale/Scope**: MVP para 1-5 operadores, 100-300 productos/dia, 1-5 fotos por producto

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Baseline and proposed solution are both defined with measurable quality and cost outputs.
- [x] Experiment reproducibility is defined (dataset/snapshot, model version, prompts, parameters).
- [x] API key handling and secret storage strategy are defined without plaintext secrets.
- [x] Cost guardrails are defined (budget caps, timeout/retry policy, stop conditions).
- [x] Test strategy includes unit tests and integration tests/mocks for paid API interactions.
- [x] Notebook deliverable (.ipynb) is planned for methodology, results, and conclusions.
- [x] For Python features, environment and dependencies are managed with uv, and new packages use `uv add`.

## Project Structure

### Documentation (this feature)

```text
specs/001-resale-pricing-assistant/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── v1/
│   │   └── dependencies/
│   ├── models/
│   ├── services/
│   ├── repositories/
│   ├── workers/
│   └── config/
├── migrations/
└── tests/
  ├── unit/
  ├── integration/
  └── contract/

frontend/
├── src/
│   ├── pages/
│   ├── components/
│   ├── services/
│   ├── hooks/
│   └── state/
└── tests/

infra/
├── docker/
│   └── docker-compose.yml
└── scripts/

notebooks/
└── pricing-eval.ipynb
```

**Structure Decision**: Se adopta arquitectura web con separacion backend/frontend para soportar flujo de revision humana en UI, manteniendo contratos HTTP estables y evolucion independiente de cada capa. La persistencia principal es PostgreSQL y el pipeline de analisis IA se desacopla en workers para controlar latencia y coste.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations identified.

## Post-Design Constitution Re-Check

- [x] Baseline/propuesta siguen medibles en calidad/coste tras diseno de datos y contratos.
- [x] Reproducibilidad definida (versionado de prompts/modelo/dataset y notebook paralelo).
- [x] Secrets y claves permanecen fuera de codigo, via entorno/secret manager.
- [x] Guardrails de coste (presupuesto diario, timeout/retry y corte) permanecen definidos.
- [x] Estrategia de testing mantiene unit + integration + mocks para APIs de pago.
- [x] Entorno Python y dependencias definidos con uv y `uv add`.
