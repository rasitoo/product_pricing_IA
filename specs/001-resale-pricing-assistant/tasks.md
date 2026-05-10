# Tasks: Asistente de Venta Reventa por Foto

**Input**: Design documents from `/specs/001-resale-pricing-assistant/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests incluidos por requerimiento explicito del spec (RDA-003) y constitucion del proyecto.

**Organization**: Tareas agrupadas por historia de usuario para implementacion y validacion independiente.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicializar estructura de proyecto, tooling y entorno local reproducible.

- [X] T001 Crear estructura base backend/frontend/infra/notebooks segun plan en backend/src/, frontend/src/, infra/docker/, notebooks/
- [X] T002 Inicializar entorno Python con uv y workflow de lock en pyproject.toml
- [X] T003 Agregar dependencias backend con `uv add` en pyproject.toml
- [X] T004 [P] Agregar dependencias de desarrollo backend con `uv add --dev` en pyproject.toml
- [X] T005 [P] Inicializar proyecto frontend JS con Vite y React en frontend/package.json
- [X] T006 [P] Crear configuracion inicial Docker Compose para PostgreSQL y Redis en infra/docker/docker-compose.yml
- [X] T007 Crear plantilla de variables de entorno y politicas de secretos en backend/.env.example
- [X] T008 [P] Crear notebook base de evaluacion coste/calidad en notebooks/pricing-eval.ipynb

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestructura comun bloqueante para todas las historias.

**⚠️ CRITICAL**: Ninguna historia se implementa hasta completar esta fase.

- [X] T009 Configurar app FastAPI base y router raiz en backend/src/main.py
- [X] T010 [P] Implementar configuracion central y carga de secrets via entorno en backend/src/config/settings.py
- [X] T011 Configurar motor SQLAlchemy, sesion y base declarativa en backend/src/config/database.py
- [X] T012 Crear migracion inicial de entidades core en backend/migrations/versions/0001_initial_schema.py
- [X] T013 [P] Implementar cliente base para proveedor LLM y cliente HTTP externo en backend/src/services/clients.py
- [X] T014 [P] Implementar servicio de storage de imagenes con abstraccion local/S3-compatible en backend/src/services/storage_service.py
- [X] T015 [P] Configurar Celery app y cola Redis para trabajos asincronos en backend/src/workers/celery_app.py
- [X] T016 Implementar middleware de logging, correlacion y manejo de errores en backend/src/api/dependencies/middleware.py
- [X] T017 Implementar guardrails de coste (budget diario, cutoff, timeout/retry) en backend/src/services/cost_guardrail_service.py
- [X] T018 [P] Añadir test de integracion de infraestructura (DB + Redis + app boot) en backend/tests/integration/test_infrastructure_boot.py
- [X] T019 [P] Añadir test de seguridad de configuracion (sin secretos en logs) en backend/tests/unit/test_settings_secrets.py
- [X] T020 [P] Añadir test de guardrails de coste sobre API de pago mockeada en backend/tests/unit/test_cost_guardrails.py

**Checkpoint**: Fundacion lista. Historias pueden comenzar.

---

## Phase 3: User Story 1 - Valorar Producto por Foto (Priority: P1) 🎯 MVP

**Goal**: Recibir fotos por API y generar propuesta IA con descripcion, precio y explicacion de señales internas/externas.

**Independent Test**: Crear producto con fotos validas y verificar propuesta completa con trazabilidad de pricing sin depender de UI de aprobacion.

### Tests for User Story 1

- [X] T021 [P] [US1] Crear contrato para POST /api/v1/products en backend/tests/contract/test_create_product_contract.py
- [X] T022 [P] [US1] Crear contrato para GET /api/v1/proposals/{proposal_id} en backend/tests/contract/test_get_proposal_contract.py
- [X] T023 [P] [US1] Crear test de integracion de ingesta y analisis IA en backend/tests/integration/test_product_analysis_flow.py
- [X] T024 [P] [US1] Crear test de rechazo por baja calidad de imagen en backend/tests/integration/test_low_quality_image_rejection.py
- [X] T025 [P] [US1] Crear test unitario de deduplicacion de imagenes por hash en backend/tests/unit/test_image_deduplication.py

### Implementation for User Story 1

- [X] T026 [P] [US1] Implementar modelo Product en backend/src/models/product.py
- [X] T027 [P] [US1] Implementar modelo ProductImage en backend/src/models/product_image.py
- [X] T028 [P] [US1] Implementar modelo AIProposal en backend/src/models/ai_proposal.py
- [X] T029 [P] [US1] Implementar modelo HistoricalReference en backend/src/models/historical_reference.py
- [X] T030 [P] [US1] Implementar modelo ExternalComparable en backend/src/models/external_comparable.py
- [X] T031 [P] [US1] Implementar modelo LLMMetric en backend/src/models/llm_metric.py
- [X] T032 [US1] Implementar repositorio de productos/propuestas en backend/src/repositories/product_repository.py
- [X] T033 [US1] Implementar servicio de analisis y pricing con señales internas+externas en backend/src/services/pricing_service.py
- [X] T034 [US1] Implementar worker de procesamiento asincrono de fotos y propuesta IA en backend/src/workers/process_product_job.py
- [X] T035 [US1] Implementar endpoint POST /api/v1/products en backend/src/api/v1/products.py
- [X] T036 [US1] Implementar endpoint GET /api/v1/proposals/{proposal_id} en backend/src/api/v1/proposals.py
- [X] T037 [US1] Registrar metricas LLM por llamada y por producto en backend/src/services/llm_metrics_service.py
- [X] T038 [US1] Actualizar notebook con metodologia/resultados/coste de US1 en notebooks/pricing-eval.ipynb

**Checkpoint**: US1 funciona de forma independiente (MVP tecnico).

---

## Phase 4: User Story 2 - Flujo de Revisión y Preparación de Publicación (Priority: P2)

**Goal**: Permitir revision humana obligatoria en web JS para aprobar/denegar/editar propuestas y generar borrador exportable.

**Independent Test**: Operador revisa propuesta existente y el sistema cambia estados correctamente, habilitando export solo tras aprobacion.

### Tests for User Story 2

- [X] T039 [P] [US2] Crear contrato para POST /api/v1/proposals/{proposal_id}/review en backend/tests/contract/test_review_proposal_contract.py
- [X] T040 [P] [US2] Crear contrato para POST /api/v1/products/{product_id}/export en backend/tests/contract/test_export_product_contract.py
- [X] T041 [P] [US2] Crear test de integracion de aprobacion humana obligatoria en backend/tests/integration/test_human_approval_required.py
- [X] T042 [P] [US2] Crear test de integracion de revision concurrente en backend/tests/integration/test_concurrent_review_conflict.py
- [X] T043 [P] [US2] Crear test frontend de flujo aprobar/editar/rechazar en frontend/tests/review-flow.spec.js

### Implementation for User Story 2

- [X] T044 [P] [US2] Implementar modelo OperatorReview en backend/src/models/operator_review.py
- [X] T045 [P] [US2] Implementar modelo PublicationDraft en backend/src/models/publication_draft.py
- [X] T046 [US2] Implementar servicio de revision y transicion de estados en backend/src/services/review_service.py
- [X] T047 [US2] Implementar servicio de exportacion manual tras aprobacion en backend/src/services/export_service.py
- [X] T048 [US2] Implementar endpoint POST /api/v1/proposals/{proposal_id}/review en backend/src/api/v1/reviews.py
- [X] T049 [US2] Implementar endpoint POST /api/v1/products/{product_id}/export en backend/src/api/v1/exports.py
- [X] T050 [P] [US2] Implementar cliente API frontend para propuestas/revisiones/export en frontend/src/services/api.js
- [X] T051 [P] [US2] Implementar pagina de evaluacion operativa en frontend/src/pages/ReviewPage.jsx
- [X] T052 [P] [US2] Implementar componentes UI de aprobacion/denegacion/edicion en frontend/src/components/ProposalReviewPanel.jsx
- [X] T053 [US2] Implementar reglas UI para bloquear publicacion sin aprobacion en frontend/src/state/reviewState.js
- [X] T054 [US2] Actualizar notebook con resultados de calidad operativa de US2 en notebooks/pricing-eval.ipynb

**Checkpoint**: US2 funciona de forma independiente sobre propuestas existentes.

---

## Phase 5: User Story 3 - Canales de Ingesta Adicionales y Automatización Progresiva (Priority: P3)

**Goal**: Preparar extension a canales adicionales y automatizacion progresiva sin romper API-first ni aprobacion humana de v1.

**Independent Test**: Simular canal adicional y verificar creacion de borrador + analisis, manteniendo politica de aprobacion humana y exportacion manual.

### Tests for User Story 3

- [X] T055 [P] [US3] Crear contrato para normalizacion de canal de entrada en backend/tests/contract/test_channel_ingestion_contract.py
- [X] T056 [P] [US3] Crear test de integracion de adaptador de canal adicional en backend/tests/integration/test_additional_channel_ingestion.py
- [X] T057 [P] [US3] Crear test de integracion que asegura aprobacion humana obligatoria en flujo de canal adicional en backend/tests/integration/test_channel_still_requires_human_approval.py

### Implementation for User Story 3

- [X] T058 [P] [US3] Implementar abstraccion de canal de entrada y mapeo de payload en backend/src/services/channel_adapter_service.py
- [X] T059 [US3] Implementar endpoint interno de ingesta normalizada para futuros canales en backend/src/api/v1/channel_ingestion.py
- [X] T060 [US3] Extender modelo Product para metadatos de canal adicional en backend/src/models/product.py
- [X] T061 [US3] Implementar trazabilidad para futura autoaprobacion de alta confianza sin activarla en backend/src/services/autoapproval_policy_service.py
- [X] T062 [US3] Implementar seccion UI de origen de canal y estado de automatizacion en frontend/src/components/ChannelMetadataPanel.jsx
- [X] T063 [US3] Actualizar notebook con comparativa de ingesta API vs canal adicional en notebooks/pricing-eval.ipynb

**Checkpoint**: US3 queda funcional y desacoplada, con capacidad diferida activable por configuracion.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Endurecer seguridad, observabilidad, rendimiento y calidad transversal.

- [X] T064 [P] Documentar arquitectura y decisiones finales en README.md
- [X] T065 [P] Endurecer politicas de validacion de input y limites de payload imagen en backend/src/api/dependencies/validation.py
- [X] T066 [P] Añadir endpoint GET /api/v1/metrics/llm y agregaciones de coste/calidad en backend/src/api/v1/metrics.py
- [X] T067 [P] Crear test de contrato para GET /api/v1/metrics/llm en backend/tests/contract/test_llm_metrics_contract.py
- [X] T068 [P] Crear test de integracion de fallo de proveedor LLM con recovery en backend/tests/integration/test_llm_failure_recovery.py
- [X] T069 Verificar que no existe uso de pip install y que dependencias nuevas usan uv add en pyproject.toml
- [X] T070 Validar quickstart end-to-end local (Docker + uv + frontend) en specs/001-resale-pricing-assistant/quickstart.md
- [X] T071 Consolidar comparativa final baseline vs propuesta (calidad/coste/fallos) en notebooks/pricing-eval.ipynb

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): sin dependencias.
- Foundational (Phase 2): depende de Setup y bloquea todas las historias.
- User Stories (Phase 3-5): dependen de Foundational.
- Polish (Phase 6): depende de las historias completadas.

### User Story Dependencies

- US1 (P1): inicia tras Foundational; no depende de otras historias.
- US2 (P2): inicia tras Foundational; usa propuestas generadas en US1 pero se puede probar de forma independiente con fixtures.
- US3 (P3): inicia tras Foundational; extiende canal de entrada sin romper flujos de US1/US2.

### Dependency Graph

- US1 -> US2 -> US3
- US2 requiere artefactos de propuesta de US1 para flujo operativo real.
- US3 reutiliza pipeline de US1 y politicas de US2.

---

## Parallel Execution Examples

### User Story 1

- Ejecutar en paralelo T021, T022, T023, T024, T025 (tests)
- Ejecutar en paralelo T026, T027, T028, T029, T030, T031 (modelos)

### User Story 2

- Ejecutar en paralelo T039, T040, T041, T042, T043 (tests)
- Ejecutar en paralelo T050, T051, T052 (frontend)

### User Story 3

- Ejecutar en paralelo T055, T056, T057 (tests)
- Ejecutar en paralelo T058 y T062 (backend adapter + componente UI)

---

## Implementation Strategy

### MVP First (US1)

1. Completar Phase 1 y Phase 2.
2. Completar US1 (Phase 3).
3. Validar independencia con los tests de US1.
4. Demostrar valor de negocio inicial (ingesta + propuesta IA + pricing explicable).

### Incremental Delivery

1. MVP tecnico con US1.
2. Agregar US2 para control operativo humano y export manual.
3. Agregar US3 para escalado de canales y automatizacion progresiva.
4. Cerrar con fase de polish para calidad/coste/seguridad.

### Parallel Team Strategy

1. Equipo completo en Setup + Foundational.
2. Luego dividir por frente:
   - Dev A: backend US1/US3
   - Dev B: backend US2 + contratos
   - Dev C: frontend US2/US3
3. Integrar por checkpoints de historia independiente.
