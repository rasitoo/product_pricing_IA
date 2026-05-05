# Data Model - Asistente de Venta Reventa por Foto

## Entidad: Product
- Purpose: Representa el producto de segunda mano ingresado por API.
- Fields:
  - id (UUID, PK)
  - external_reference (string, nullable)
  - source_channel (enum: api, whatsapp, telegram; v1 solo api)
  - title (string, nullable)
  - category (string, nullable)
  - tags (jsonb)
  - status (enum: draft, analyzing, proposed, in_review, approved, rejected, export_ready)
  - created_at (timestamp)
  - updated_at (timestamp)
- Validation Rules:
  - Debe tener al menos una imagen valida asociada para pasar a analyzing.
  - source_channel en v1 debe ser api.
- State Transitions:
  - draft -> analyzing -> proposed -> in_review -> approved|rejected -> export_ready (si approved)

## Entidad: ProductImage
- Purpose: Almacena imagenes del producto y metadatos de procesamiento.
- Fields:
  - id (UUID, PK)
  - product_id (UUID, FK Product.id)
  - storage_uri (string)
  - sha256_hash (string)
  - width (int, nullable)
  - height (int, nullable)
  - mime_type (string)
  - ai_annotations (jsonb, nullable)
  - quality_score (numeric, nullable)
  - created_at (timestamp)
- Validation Rules:
  - sha256_hash obligatorio para deduplicacion.
  - mime_type permitido: image/jpeg, image/png, image/webp.

## Entidad: AIProposal
- Purpose: Resultado generado por IA para descripcion y pricing.
- Fields:
  - id (UUID, PK)
  - product_id (UUID, FK Product.id)
  - description_text (text)
  - suggested_price (numeric(12,2))
  - suggested_price_min (numeric(12,2), nullable)
  - suggested_price_max (numeric(12,2), nullable)
  - confidence_score (numeric(5,2))
  - rationale_internal (jsonb)
  - rationale_external (jsonb)
  - expected_days_to_sell (int, nullable)
  - model_name (string)
  - prompt_version (string)
  - created_at (timestamp)
- Validation Rules:
  - suggested_price > 0.
  - confidence_score entre 0 y 1.

## Entidad: OperatorReview
- Purpose: Decision humana sobre propuesta IA.
- Fields:
  - id (UUID, PK)
  - proposal_id (UUID, FK AIProposal.id)
  - operator_id (string)
  - decision (enum: approve, reject, edit)
  - edited_description_text (text, nullable)
  - edited_price (numeric(12,2), nullable)
  - reject_reason (text, nullable)
  - notes (text, nullable)
  - created_at (timestamp)
- Validation Rules:
  - decision=reject requiere reject_reason.
  - En v1 siempre debe existir al menos una review para habilitar export_ready.

## Entidad: HistoricalReference
- Purpose: Referencias internas de ventas historicas para pricing.
- Fields:
  - id (UUID, PK)
  - product_id (UUID, FK Product.id)
  - comparable_product_id (string)
  - sold_price (numeric(12,2))
  - sold_at (timestamp)
  - condition_label (string, nullable)
  - similarity_score (numeric(5,2), nullable)

## Entidad: ExternalComparable
- Purpose: Referencias externas de mercado obtenidas en tiempo real.
- Fields:
  - id (UUID, PK)
  - proposal_id (UUID, FK AIProposal.id)
  - source_name (string)
  - listing_url (text)
  - listed_price (numeric(12,2), nullable)
  - currency (string(3), nullable)
  - observed_at (timestamp)
  - confidence (numeric(5,2), nullable)

## Entidad: PublicationDraft
- Purpose: Borrador exportable para publicacion manual o futura integracion externa.
- Fields:
  - id (UUID, PK)
  - product_id (UUID, FK Product.id)
  - proposal_id (UUID, FK AIProposal.id)
  - export_format (enum: json, csv, html)
  - payload (jsonb)
  - status (enum: ready, exported, published_external)
  - created_at (timestamp)
  - updated_at (timestamp)
- Validation Rules:
  - En v1 solo se permite status ready/exported; published_external reservado para fases futuras.

## Entidad: LLMMetric
- Purpose: Observabilidad de coste, calidad y fallos.
- Fields:
  - id (UUID, PK)
  - product_id (UUID, FK Product.id, nullable)
  - proposal_id (UUID, FK AIProposal.id, nullable)
  - provider (string)
  - model_name (string)
  - input_tokens (int)
  - output_tokens (int)
  - cost_usd (numeric(12,6))
  - latency_ms (int)
  - outcome (enum: success, timeout, error, blocked_by_budget)
  - error_type (string, nullable)
  - created_at (timestamp)

## Relacionamientos Clave
- Product 1:N ProductImage
- Product 1:N AIProposal
- AIProposal 1:N OperatorReview
- AIProposal 1:N ExternalComparable
- Product 1:N HistoricalReference
- Product 1:N LLMMetric
- AIProposal 1:1 PublicationDraft (v1)

## Reglas de Integridad
- No existe PublicationDraft listo para exportar sin OperatorReview con decision approve.
- Product.status debe reflejar el ultimo estado de negocio segun eventos de propuesta/revision.
- Todas las llamadas a proveedor IA deben registrar al menos un LLMMetric.
