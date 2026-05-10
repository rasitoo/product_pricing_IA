# Phase 0 Research - Interfaz de Revisión en Carrusel Estilo Tinder

## Decision 1: Librería de gestos de swipe en React (desktop + touch)
- Decision: `@use-gesture/react` + `react-spring` para detección de arrastre y animación de tarjetas.
- Rationale: `@use-gesture/react` es la librería de referencia para detección de drag/swipe en React, funciona con ratón y touch sin distinción, y se integra de forma nativa con `react-spring` para animaciones fluidas de traslación y rotación de tarjeta (efecto Tinder). Ambas son ligeras, mantenidas activamente y sin dependencias externas de peso.
- Alternatives considered: `framer-motion` (válida pero introduce más superficie de API para este caso puntual), CSS drag nativo (difícil de controlar con umbrales de decisión), librerías de "swipe card" precompiladas (menos flexibles, difíciles de adaptar al diseño propio).

## Decision 2: Visor de fotos dentro de la tarjeta
- Decision: Visor de imágenes personalizado con `CSS scroll-snap` horizontal, sin librería adicional.
- Rationale: El objetivo es desktop-first con número reducido de fotos por producto (1–5 en la mayoría de casos). Un contenedor horizontal con `scroll-snap-type: x mandatory` cubre el caso sin añadir dependencias. Para >10 fotos se muestran miniaturas clicables adicionales debajo del visor principal.
- Alternatives considered: `Swiper.js` (válido pero añade ~50 KB y config extra para un caso cubierto con CSS), `react-image-gallery` (opinionated en UI, difícil de adaptar).

## Decision 3: Mecanismo de bloqueo optimista de propuestas (TTL 60 s)
- Decision: Tabla `ReviewLock` en PostgreSQL con campo `expires_at`; el frontend envía heartbeat cada 20 s para renovar el TTL; el backend limpia locks expirados en cada petición de cola.
- Rationale: Es la solución más simple compatible con la infraestructura ya existente (PostgreSQL + FastAPI). No requiere Redis pub/sub ni websockets. El heartbeat cada 20 s garantiza renovación antes de que expire el TTL de 60 s con margen triple. Los locks expirados se eliminan en la consulta de cola ("limpieza perezosa") sin necesidad de un worker separado.
- Alternatives considered: Redis TTL con SETNX (válido y más eficiente a escala, pero añade complejidad cuando Redis ya existe en el stack para Celery — se puede migrar en fases posteriores si la escala lo requiere), websockets para presencia en tiempo real (sobredimensionado para 1–5 operadores simultáneos).

## Decision 4: Almacenamiento de señales de retroalimentación para IA
- Decision: Nueva tabla `FeedbackSignal` en PostgreSQL; cada fila registra campo modificado, valor original de la IA y valor corregido por el operador, vinculada a `OperatorReview`.
- Rationale: Datos estructurados en PostgreSQL permiten consultas analíticas directas (qué campos se corrigen más, distribución de deltas de precio) sin infraestructura adicional. Es el primer punto de datos para futuros pipelines de fine-tuning o RLHF.
- Alternatives considered: Log de texto en fichero (no consultable), evento en cola Celery (añade complejidad para almacenamiento persistente), tabla en base de datos separada (aislamiento innecesario en esta fase).

## Decision 5: Estado "modificada, pendiente de reaprobación"
- Decision: Añadir valor `modified_pending_reapproval` al enum `PublicationDraft.status` y hacer que las propuestas con ese estado aparezcan al inicio de la cola de revisión (ORDER BY status = 'modified_pending_reapproval' DESC, created_at ASC).
- Rationale: Reutiliza el modelo de datos existente sin crear una entidad nueva. El cambio de estado es un campo de enum en Alembic (migración simple). La cola prioriza propuestas modificadas para que el operador vea primero sus propias correcciones y las apruebe o rechace definitivamente.
- Alternatives considered: Cola separada para propuestas modificadas (mayor complejidad de consulta y UI), volver a estado `in_review` genérico (pierde la distinción semántica necesaria para el pipeline de IA).

## Decision 6: Gestión de estado del carrusel en el frontend
- Decision: Estado local de React con `useState`/`useReducer` + llamadas directas a `fetch` (sin TanStack Query ni Redux).
- Rationale: El flujo es lineal: cargar siguiente propuesta → bloquear → decidir → enviar → cargar siguiente. No hay sincronización de caché compleja entre componentes. Añadir TanStack Query (no está en `package.json` aún) para este patrón secuencial añadiría boilerplate sin beneficio real.
- Alternatives considered: TanStack Query (adecuado si hubiera múltiples vistas consumiendo las mismas propuestas simultáneamente, no es el caso en v1), Zustand/Redux (sobredimensionado para estado de una sola página).

## Decision 7: Acción de deshacer (undo) con ventana de 5 segundos
- Decision: Toast de deshacer implementado con `setTimeout` en el frontend; la acción de revisión se envía al backend solo al expirar el toast o al hacer clic en "Confirmar". Si el operador hace clic en "Deshacer" antes de que expire, la acción se cancela localmente sin llamada al backend.
- Rationale: Evita la complejidad de revertir registros en base de datos. La decisión se envía al backend solo cuando es definitiva. El bloqueo de la propuesta permanece activo durante la ventana de 5 s.
- Alternatives considered: Enviar la acción al backend inmediatamente y revertir con llamada de "undo" (requiere endpoint adicional y lógica de inversión en base de datos), sin undo (peor UX, la spec lo requiere).

## Decision 8: Identificador de sesión anónimo
- Decision: UUID v4 generado en el frontend al cargar la aplicación y almacenado en `sessionStorage`; se envía como cabecera `X-Session-Id` en todas las peticiones de revisión.
- Rationale: Simple, sin dependencias, sin datos personales, cumple la trazabilidad requerida por FR-006. `sessionStorage` garantiza que cada pestaña nueva genera un ID nuevo (correcto para el modelo de bloqueo por sesión).
- Alternatives considered: Cookie persistente (sobrevive a cierre de pestaña, no deseable para identificador de sesión de revisión), fingerprint de navegador (invasivo y no necesario para trazabilidad interna).
