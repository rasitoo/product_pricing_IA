# Tasks: Interfaz de Revisión en Carrusel Estilo Tinder

**Input**: Design documents from `/specs/002-carousel-review-ui/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/openapi-carousel.yaml ✓

**Tests**: Incluidos según constitución para lógica de lock, cola y acciones de revisión.

**Organization**: Tareas agrupadas por historia de usuario para implementación y prueba independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Paralelizable (distintos ficheros, sin dependencias en tareas incompletas)
- **[Story]**: Historia de usuario a la que pertenece (US1–US4)
- Las fases de Setup y Foundation no llevan etiqueta de historia

---

## Phase 1: Setup

**Purpose**: Preparar el entorno de frontend para la feature sin tocar lógica de negocio.

- [X] T001 Instalar dependencias frontend `@use-gesture/react` y `react-spring` en `frontend/package.json` y actualizar `package-lock.json`
- [X] T002 Registrar ruta `/carousel` apuntando a `CarouselPage` en `frontend/src/main.jsx`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestructura de base de datos y extensiones de repositorio que TODAS las historias necesitan. Debe completarse antes de cualquier historia.

**⚠️ CRÍTICO**: Ninguna historia puede implementarse hasta completar esta fase.

- [X] T003 Crear modelo SQLAlchemy `ReviewLock` en `backend/src/models/review_lock.py` (campos: id, proposal_id UNIQUE FK, session_id, locked_at, expires_at)
- [X] T004 [P] Crear modelo SQLAlchemy `FeedbackSignal` en `backend/src/models/feedback_signal.py` (campos: id, proposal_id FK, review_id FK, field_name, original_value, corrected_value, created_at)
- [X] T005 Crear migración Alembic `backend/migrations/versions/0002_carousel_review.py`: añadir valor `modified_pending_reapproval` al enum `publicationdraft_status`; crear tablas `review_lock` y `feedback_signal`
- [X] T006 Extender `backend/src/repositories/product_repository.py` con método `get_review_queue(session_id)`: consulta que excluye locks activos de otras sesiones y ordena `modified_pending_reapproval` primero, luego `created_at ASC`; incluye conteo de cola
- [X] T007 [P] Extender `GET /api/v1/proposals/{proposal_id}` en `backend/src/api/v1/proposals.py` para devolver lista de imágenes con `url` y `thumbnail_url` según contrato `openapi-carousel.yaml`

**Checkpoint**: Base de datos migrada y repositorio extendido — las historias pueden implementarse en paralelo a partir de aquí.

---

## Phase 3: User Story 1 — Revisar Propuesta sin Iniciar Sesión (Priority: P1) 🎯 MVP

**Goal**: El operador abre la URL y ve directamente la cola de revisión sin credenciales; con cola vacía ve mensaje claro; con propuestas ve la primera en formato carrusel.

**Independent Test**: Abrir `http://localhost:5173/carousel` sin ningún token — debe mostrar la interfaz o el mensaje de cola vacía. Con una propuesta en BD con `Product.status = in_review`, debe aparecer la tarjeta.

### Implementación US1

- [X] T008 [US1] Crear `frontend/src/state/sessionId.js`: genera UUID v4 y lo persiste en `sessionStorage`; exporta `getSessionId()`
- [X] T009 [US1] Extender `frontend/src/services/api.js`: añadir función `fetchNextQueueItem()` que llama `GET /api/v1/review-queue` con cabecera `X-Session-Id`
- [X] T010 [US1] Crear servicio backend `backend/src/services/review_lock_service.py`: métodos `acquire(proposal_id, session_id)`, `renew(proposal_id, session_id)`, `release(proposal_id, session_id)`; TTL = 60 s; limpia locks expirados en cada operación
- [X] T011 [US1] Crear router backend `backend/src/api/v1/review_queue.py`: `GET /api/v1/review-queue` — llama `product_repository.get_review_queue(session_id)`, adquiere lock automáticamente en la propuesta devuelta, retorna `ReviewQueueItem` o 204 si cola vacía
- [X] T012 [US1] Registrar `review_queue` router en `backend/src/main.py`
- [X] T013 [US1] Crear `frontend/src/pages/CarouselPage.jsx`: muestra estado de carga, mensaje de cola vacía (FR-012) e indicador de posición en cola (FR-009); consume `fetchNextQueueItem()` al montar

### Tests US1

- [X] T014 [P] [US1] Test unitario `backend/tests/unit/test_review_lock_service.py`: adquirir lock, renovar TTL, liberar, expiración pasado TTL, conflicto de sesión distinta
- [X] T015 [P] [US1] Test de integración `backend/tests/integration/test_review_queue_endpoint.py`: cola vacía devuelve 204; propuesta disponible devuelve 200 con `ReviewQueueItem`; propuesta con lock ajeno queda excluida

**Checkpoint**: US1 completa — operador accede sin login, ve cola vacía o primera propuesta.

---

## Phase 4: User Story 2 — Navegar por el Carrusel de Propuestas (Priority: P1)

**Goal**: La tarjeta muestra fotos del producto en visor deslizable, descripción IA y precio sugerido; tras cualquier acción la siguiente propuesta se carga automáticamente.

**Independent Test**: Crear 3 propuestas de prueba — la tarjeta muestra la primera con sus fotos, descripción y precio. Con stub del backend (Vitest mock), `useCarouselQueue` avanza a la siguiente al llamar `onAction()`.

### Implementación US2

- [X] T016 [US2] Crear `frontend/src/components/PhotoViewer.jsx`: contenedor horizontal con `scroll-snap-type: x mandatory`; una imagen por slide; para >10 fotos muestra las primeras 9 + tira de miniaturas clicables (FR-003, CQR-003)
- [X] T017 [US2] Crear `frontend/src/components/CarouselCard.jsx`: integra `PhotoViewer` + descripción + precio + rango de confianza; aplica `useDrag` de `@use-gesture/react` y `useSpring` de `react-spring` para la animación de traslación/rotación de tarjeta al arrastrar (umbral de decisión: 100 px)
- [X] T018 [US2] Crear `frontend/src/hooks/useCarouselQueue.js`: gestiona estado `currentItem`, `queueTotal`, `isLoading`; expone `advance()` que llama `fetchNextQueueItem()` y actualiza estado
- [X] T019 [US2] Crear `frontend/src/hooks/useLockHeartbeat.js`: llama `POST /api/v1/proposals/{id}/lock/heartbeat` cada 20 s mientras hay propuesta activa; cancela intervalo al desmontar o cambiar propuesta
- [X] T020 [US2] Crear router backend `backend/src/api/v1/review_lock.py`: `POST /lock` (adquirir/renovar), `DELETE /lock` (liberar), `POST /lock/heartbeat` (renovar TTL); valida ownership de sesión en DELETE y heartbeat
- [X] T021 [US2] Registrar `review_lock` router en `backend/src/main.py` (depende de T012 — mismo fichero; ejecutar en secuencia)
- [X] T022 [US2] Extender `frontend/src/services/api.js`: añadir `lockProposal()`, `unlockProposal()`, `heartbeatLock()`
- [X] T023 [US2] Conectar `CarouselPage.jsx` con `useCarouselQueue` + `useLockHeartbeat` + indicador visual de `queueTotal` (FR-009)

### Tests US2

- [X] T024 [P] [US2] Test unitario `frontend/tests/CarouselCard.test.jsx`: renderiza fotos, descripción y precio; drag más allá del umbral dispara `onSwipeRight`/`onSwipeLeft`
- [X] T025 [P] [US2] Test unitario `frontend/tests/useCarouselQueue.test.js`: `advance()` carga siguiente item; estado vacío cuando backend devuelve 204
- [X] T026 [P] [US2] Test unitario `frontend/tests/useLockHeartbeat.test.js`: llama heartbeat a intervalos de 20 s; cancela al desmontar
- [X] T027 [P] [US2] Test de integración `backend/tests/integration/test_review_lock_endpoint.py`: adquirir lock devuelve `expires_at`; heartbeat renueva TTL; release devuelve 204; sesión ajena devuelve 403

**Checkpoint**: US2 completa — tarjeta visible con fotos deslizables, descripción, precio e indicador de cola.

---

## Phase 5: User Story 3 — Aceptar una Propuesta (Priority: P2)

**Goal**: El operador arrastra la tarjeta a la derecha o pulsa ✓ para aprobar; aparece toast de 5 s con opción de deshacer; si no deshace, el backend registra la aprobación y el carrusel avanza.

**Independent Test**: Con una propuesta en estado `in_review`, aceptar via UI → `Product.status = approved`, `PublicationDraft.status = ready`, lock liberado, `OperatorReview.decision = approve` en BD.

### Implementación US3

- [X] T028 [US3] Añadir botón de aceptación visible (✓) y swipe-derecha a `frontend/src/components/CarouselCard.jsx`; emite evento `onApprove` al superar umbral (FR-004)
- [X] T029 [US3] Crear `frontend/src/components/UndoToast.jsx`: muestra toast durante 5 s con botón "Deshacer"; llama `onConfirm()` al expirar o `onUndo()` si el operador cancela antes (FR-010)
- [X] T030 [US3] Extender `frontend/src/hooks/useCarouselQueue.js`: al recibir `onApprove`, muestra `UndoToast`; solo llama `reviewProposal({decision:'approve'})` si `onConfirm()` se ejecuta; tras confirmar libera lock y llama `advance()`
- [X] T031 [US3] Extender `frontend/src/services/api.js`: función `reviewProposal(proposalId, payload)` con cabecera `X-Session-Id`
- [X] T032 [US3] Extender `backend/src/services/review_service.py`: validar que la sesión posee el lock activo antes de registrar la revisión; liberar lock tras `decision = approve`; actualizar `PublicationDraft.status = ready` y `Product.status = approved`
- [X] T033 [US3] Extender `backend/src/api/v1/reviews.py`: leer `X-Session-Id` de cabecera y pasarlo a `review_service`; devolver 409 si la sesión no posee el lock

### Tests US3

- [X] T034 [P] [US3] Test de integración `backend/tests/integration/test_review_approve.py`: flujo completo lock → approve → verificar `Product.status = approved`, `PublicationDraft.status = ready`, lock eliminado
- [X] T035 [P] [US3] Test unitario `frontend/tests/useCarouselQueue.test.js` (extensión): `onApprove` muestra toast; deshacer en < 5 s no llama `reviewProposal`; confirmar sí lo llama

**Checkpoint**: US3 completa — flujo de aprobación funciona de extremo a extremo con ventana de deshacer.

---

## Phase 6: User Story 4 — Rechazar una Propuesta (con o sin Modificaciones) (Priority: P2)

**Goal**: El operador arrastra a la izquierda o pulsa ✗ para rechazar directamente; opcionalmente abre formulario inline para editar descripción/precio; al confirmar edición el backend crea `FeedbackSignal` y la propuesta pasa a `modified_pending_reapproval`.

**Independent Test**: Rechazar con edición de descripción → `OperatorReview.decision = edit`, 1 `FeedbackSignal` con `field_name = description_text`, `PublicationDraft.status = modified_pending_reapproval`, propuesta aparece al inicio de la cola. Rechazar sin edición → `OperatorReview.decision = reject`, sin `FeedbackSignal`.

### Implementación US4

- [X] T036 [US4] Añadir botón de rechazo visible (✗) y swipe-izquierda a `frontend/src/components/CarouselCard.jsx`; emite `onReject` (FR-005)
- [X] T037 [US4] Crear `frontend/src/components/EditFormPanel.jsx`: formulario inline con campos `description` (textarea, precargado con valor IA) y `price` (number input, precargado); campo `reject_reason` opcional; botones "Confirmar" y "Cancelar" (FR-005, FR-007)
- [X] T038 [US4] Extender `frontend/src/hooks/useCarouselQueue.js`: al recibir `onReject`, registra rechazo directo con toast de deshacer; si el operador abre `EditFormPanel` y confirma, llama `reviewProposal({decision:'edit', ...campos})` y avanza
- [X] T039 [US4] Extender `backend/src/services/review_service.py`: cuando `decision = edit`, crear registros `FeedbackSignal` por cada campo modificado con valor original de `AIProposal` y valor corregido; actualizar `PublicationDraft.status = modified_pending_reapproval`; liberar lock
- [X] T040 [US4] Extender `backend/src/api/v1/reviews.py`: validar que `decision = edit` tenga al menos un campo editado (`edited_description` o `edited_price`) con valor distinto al original; devolver 422 si no; incluir `feedback_signals_created` en respuesta
- [X] T041 [US4] Verificar que `product_repository.get_review_queue` prioriza `modified_pending_reapproval` correctamente (ya cubierto en T006; añadir assertion explícita si falta)

### Tests US4

- [X] T042 [P] [US4] Test unitario `backend/tests/unit/test_feedback_signal.py`: creación de 1 y 2 señales, validación de `original_value != corrected_value`, campo inválido devuelve error
- [X] T043 [P] [US4] Test de integración `backend/tests/integration/test_review_edit.py`: lock → edit descripción → `FeedbackSignal` creado, `PublicationDraft.status = modified_pending_reapproval`; propuesta aparece primera en cola siguiente
- [X] T044 [P] [US4] Test de integración `backend/tests/integration/test_review_reject.py`: lock → reject sin edición → `OperatorReview.decision = reject`, sin `FeedbackSignal`, lock liberado

**Checkpoint**: US4 completa — flujo de rechazo con y sin modificaciones; señal de retroalimentación registrada.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validación de contrato, manejo de errores y casos límite identificados en spec.md.

- [X] T045 [P] Crear test de contrato `backend/tests/contract/test_carousel_openapi.py`: validar que los endpoints implementados (`/review-queue`, `/lock`, `/lock/heartbeat`, `/proposals/{id}/review` extendido) cumplen el esquema `specs/002-carousel-review-ui/contracts/openapi-carousel.yaml`
- [X] T046 [P] Añadir manejo de error de red en `frontend/src/pages/CarouselPage.jsx`: si `fetchNextQueueItem` falla, mostrar banner de error con botón de reintento; no dejar la UI bloqueada
- [X] T047 [P] Añadir manejo de 409 (propuesta ya tomada) en `frontend/src/hooks/useCarouselQueue.js`: llamar `advance()` automáticamente para saltar a la siguiente propuesta disponible
- [X] T048 [P] Añadir manejo de propuesta sin fotos en `frontend/src/components/PhotoViewer.jsx`: mostrar placeholder visual cuando `images` es lista vacía (edge case spec.md)
- [X] T049 [P] Actualizar `frontend/src/main.jsx` para que la ruta raíz `/` redirija a `/carousel` (acceso directo sin sesión, FR-001)
- [X] T050 [P] Actualizar `notebooks/pricing-eval.ipynb` con métricas de FeedbackSignal: tasa de corrección por campo (`description_text` vs `suggested_price`) y distribución de delta de precio entre valor original IA y valor corregido por operador (RDA-002)
- [X] T051 [P] Añadir test de rendimiento en `frontend/tests/performance.spec.js` (Playwright): medir tiempo desde apertura de URL hasta primera propuesta visible (SC-001 < 10 s) y tiempo de avance entre propuestas (SC-005 < 2 s)
- [X] T052 [P] Test unitario `frontend/tests/CarouselPage.test.jsx`: renderiza mensaje de cola vacía; renderiza `CarouselCard` cuando hay item; muestra banner de error con botón de reintento si falla la llamada a API (Constitución III)
- [X] T053 [P] Test unitario `frontend/tests/UndoToast.test.jsx`: llama `onConfirm` tras 5 s si no se deshace; llama `onUndo` si se pulsa el botón antes de que expire; no llama ningún callback si está desmontado (Constitución III)
- [X] T054 [P] Test unitario `frontend/tests/EditFormPanel.test.jsx`: campos precargados con valores originales; "Cancelar" llama `onCancel` sin emitir cambios; "Confirmar" emite solo los campos modificados; no emite si no hay cambios respecto al original (Constitución III)

---

## Dependency Graph

```
T001 → T002 → [frontend independiente de backend hasta T009]
T003 → T005
T004 → T005
T005 → T006 → T007
       ↓
T006 → T010, T011 (US1 backend)
T008 → T009 → T013 (US1 frontend)
T010, T011 → T012 → T014, T015
             ↓
T016 → T017 → T024 (US2 frontend)
T018 → T025
T019 → T026
T020 → T012 → T021 → T027
T022, T023 (dependen de T016-T021 completados)
             ↓
T028 → T029 → T030 → T031 → T034, T035 (US3)
T032, T033 dependen de T030
             ↓
T036 → T037 → T038 → T042 (US4 frontend)
T039 → T040 → T041 → T043, T044 (US4 backend)
             ↓
T045–T049 (polish, todos paralelizables entre sí)
```

## Parallel Execution Examples

### Sprint 1 — Setup + Foundation (secuencial)
```
T001 → T002 (setup frontend)
T003 ∥ T004 → T005 → T006 ∥ T007 (modelos + migración)
```

### Sprint 2 — US1 + US2 en paralelo tras Foundation
```
Backend: T010 → T011 → T012 ∥ T014 ∥ T015
Frontend: T008 → T009 → T013 ∥ T016 → T017 → T024
          T018 → T025  ∥  T019 → T026
          T020 → T021 → T022 → T023 ∥ T027
```

### Sprint 3 — US3 + US4 en paralelo
```
Backend US3: T032 → T033 → T034 ∥ T035
Backend US4: T039 → T040 → T041 → T042 ∥ T043 ∥ T044
Frontend US3: T028 → T029 → T030 → T031
Frontend US4: T036 → T037 → T038
```

### Sprint 4 — Polish (todo en paralelo)
```
T045 ∥ T046 ∥ T047 ∥ T048 ∥ T049 ∥ T050 ∥ T051 ∥ T052 ∥ T053 ∥ T054
```

## Implementation Strategy

**MVP mínimo (US1 + US2)**: Fases 1, 2, 3 y 4 — el operador accede sin login, ve la cola y puede navegar por las tarjetas con fotos y contenido IA. Sin acciones de aprobación aún.

**MVP completo (US1–US4)**: Todas las fases hasta Phase 6 incluida — flujo de aprobación, rechazo directo y modificación con retroalimentación a la IA.

**Entrega incremental sugerida**:
1. Sprint 1: Setup + Foundation (T001–T007)
2. Sprint 2: US1 + US2 (T008–T027) — carrusel navegable
3. Sprint 3: US3 + US4 (T028–T044) — decisiones completas
4. Sprint 4: Polish (T045–T054)
