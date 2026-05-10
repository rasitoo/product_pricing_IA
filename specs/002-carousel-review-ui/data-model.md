# Data Model - Interfaz de Revisión en Carrusel Estilo Tinder

> Esta feature extiende el modelo de datos de la feature 001 (Asistente de Venta Reventa por Foto).
> Las entidades existentes se modifican solo donde es estrictamente necesario; el resto permanece sin cambios.

---

## Cambios sobre entidades existentes

### Entidad: PublicationDraft (modificada)
- Cambio: Nuevo valor de enum en `status`: `modified_pending_reapproval`
- Valores completos del enum `status`:
  - `ready` — aprobada, lista para exportar
  - `exported` — ya exportada manualmente
  - `published_external` — reservado para fases futuras
  - `modified_pending_reapproval` *(nuevo)* — rechazada con modificaciones, en espera de segunda aprobación; aparece al inicio de la cola
- Migration: Alembic `ALTER TYPE` para añadir el nuevo valor al enum PostgreSQL.

### Entidad: OperatorReview (sin cambios de esquema)
- El valor `edit` en `decision` ya existe y cubre el caso de rechazo con modificaciones.
- Semántica ampliada: cuando `decision = edit`, el sistema DEBE crear registros `FeedbackSignal` asociados con los campos modificados.

---

## Nuevas entidades

### Entidad: ReviewLock
- Purpose: Bloqueo optimista de una propuesta para evitar que dos sesiones la revisen simultáneamente.
- Fields:
  - id (UUID, PK)
  - proposal_id (UUID, FK AIProposal.id, UNIQUE — solo un lock activo por propuesta)
  - session_id (string) — identificador anónimo de sesión del navegador (UUID v4 generado en cliente)
  - locked_at (timestamp)
  - expires_at (timestamp) — `locked_at + 60 s`; renovable via heartbeat
- Validation Rules:
  - Solo puede existir un `ReviewLock` activo por `proposal_id` en cualquier momento.
  - Un lock se considera expirado si `expires_at < now()`; los locks expirados son ignorados y eliminados en la próxima consulta de cola.
  - El heartbeat del frontend renueva `expires_at` a `now() + 60 s`; si no llega heartbeat en 60 s el lock expira automáticamente.
- State Transitions:
  - (inexistente) → locked (POST /lock)
  - locked → renewed (POST /lock/heartbeat)
  - locked → released (DELETE /lock — al confirmar acción o cerrar sesión)
  - locked → expired (pasados 60 s sin heartbeat)

### Entidad: FeedbackSignal
- Purpose: Registro estructurado de correcciones del operador sobre el contenido generado por la IA, destinado al pipeline de reentrenamiento.
- Fields:
  - id (UUID, PK)
  - proposal_id (UUID, FK AIProposal.id)
  - review_id (UUID, FK OperatorReview.id)
  - field_name (string) — nombre del campo corregido: `description_text` | `suggested_price`
  - original_value (text) — valor original generado por la IA (serializado como string)
  - corrected_value (text) — valor introducido por el operador (serializado como string)
  - created_at (timestamp)
- Validation Rules:
  - `field_name` debe ser uno de los valores permitidos: `description_text`, `suggested_price`.
  - `original_value` y `corrected_value` son obligatorios y no pueden ser iguales (no se registra feedback sin cambio real).
  - Se crea uno o dos registros por review con `decision = edit` (uno por cada campo modificado).

---

## Nueva entidad de cola (vista lógica, sin tabla)

### Cola de Revisión (ReviewQueue)
- Purpose: Vista ordenada de propuestas pendientes de revisión, sin tabla propia en base de datos.
- Implementación: Consulta SQL sobre `AIProposal` + `Product` + `ReviewLock` + `ProductImage` con las siguientes reglas:
  - Incluye propuestas donde `Product.status IN ('in_review')` y `PublicationDraft.status IN ('modified_pending_reapproval')` _(o bien propuestas sin PublicationDraft aún aprobada)_.
  - Excluye propuestas con `ReviewLock` activo para una `session_id` distinta a la del solicitante.
  - **Excluye propuestas sin ninguna imagen asociada** (`LEFT JOIN product_images WHERE product_images.id IS NOT NULL`); estas propuestas deben ser corregidas antes de entrar en cola (FR-016).
  - Ordenación: `PublicationDraft.status = 'modified_pending_reapproval'` primero, luego `AIProposal.created_at ASC`. Entre propuestas del mismo estado, ordenar por `updated_at ASC` para priorizar las más antiguas.
  - La respuesta incluye el campo `locked_by_me: bool` (true si el lock activo pertenece a la session_id del solicitante).

---

## Relacionamientos nuevos o ampliados

- AIProposal 0..1 ReviewLock (un lock activo o ninguno por propuesta)
- OperatorReview 0..N FeedbackSignal (cero si no hay edición; uno o dos si `decision = edit`)

---

## Reglas de integridad nuevas

- No puede existir más de un `ReviewLock` activo (no expirado) por `proposal_id`.
- Un `FeedbackSignal` solo puede crearse cuando existe una `OperatorReview` con `decision = edit` como padre.
- Si `OperatorReview.decision = edit`, el sistema DEBE crear al menos un `FeedbackSignal` (no se permite editar sin registrar qué cambió).
- Cuando se crea un `FeedbackSignal`, `PublicationDraft.status` pasa a `modified_pending_reapproval` y `Product.status` permanece en `in_review`.
