# Phase 0 Research - Asistente de Venta Reventa por Foto

## Decision 1: Backend API en Python con FastAPI asincrono
- Decision: Usar FastAPI + Uvicorn + httpx asincrono para API y orquestacion de llamadas externas.
- Rationale: Reduce complejidad de concurrencia para subida de fotos y llamadas a LLM/fuentes externas. Entrega OpenAPI automaticamente para frontend y pruebas de contrato.
- Alternatives considered: Django/DRF (mas pesado para MVP), Flask (menos opinionado y sin ventajas directas para asincronia en este caso).

## Decision 2: Frontend web en JavaScript para aprobacion operativa
- Decision: Implementar frontend con React + Vite + TanStack Query.
- Rationale: Encaja con flujo de revision humana (aprobar, denegar, editar) y sincronizacion de estados de propuestas con buena DX.
- Alternatives considered: Vue (valido pero sin ventaja clara para este equipo), UI server-rendered desde backend (acopla excesivamente y dificulta evolucion independiente).

## Decision 3: Persistencia principal en PostgreSQL con arranque local en Docker
- Decision: PostgreSQL 16 como base principal, ejecutado en Docker Compose en fases tempranas.
- Rationale: Modelo relacional claro para Producto/Propuesta/Revision/Metricas y migraciones robustas. Permite comenzar sin AWS y migrar luego a RDS sin rediseño.
- Alternatives considered: SQLite (insuficiente para concurrencia y trazabilidad operativa), MongoDB (menos natural para relaciones y auditoria de estados).

## Decision 4: Estrategia de almacenamiento de imagenes por fases
- Decision: Fase inicial en filesystem local con metadatos en PostgreSQL y abstraccion de storage para evolucion a S3-compatible/S3.
- Rationale: Cumple requisito de fases independientes sin dependencia cloud inicial y evita deuda de migracion posterior.
- Alternatives considered: Guardar blobs binarios en PostgreSQL (peor operabilidad y backup en escala), forzar S3 desde inicio (rompe restriccion de independencia temprana).

## Decision 5: Procesamiento en background para tareas de IA
- Decision: Celery + Redis para jobs asincronos (analisis de imagen, enriquecimiento, logging de coste).
- Rationale: Evita bloquear requests y permite politicas de retry/timeout/circuit breaker sobre APIs de pago.
- Alternatives considered: Solo tareas en request sin cola (riesgo de timeouts y mala UX), RQ (mas simple pero menos flexible para crecimiento).

## Decision 6: ORM y migraciones
- Decision: SQLAlchemy + Alembic para modelos y migraciones versionadas.
- Rationale: Trazabilidad de cambios de esquema y buena integracion con Python backend moderno.
- Alternatives considered: SQL crudo manual (alto riesgo en cambios iterativos), otro ORM no estandar en ecosistema (menor compatibilidad).

## Decision 7: Metricas iniciales de calidad/coste/fallos
- Decision: Registrar por producto y por llamada: tokens/coste LLM, latencia, estado de error, tasa de aprobacion sin edicion y delta de precio propuesto vs aprobado.
- Rationale: Permite evaluar optimizacion real de calidad-coste y cumplir constitucion.
- Alternatives considered: Medir solo coste (insuficiente para calidad), medir solo calidad humana (sin control economico).

## Decision 8: Contrato de API versionado
- Decision: OpenAPI 3.1 con rutas /api/v1 para productos, propuestas, revisiones y metricas.
- Rationale: Estabilidad para frontend JS y preparacion para canales adicionales en fases posteriores.
- Alternatives considered: Sin versionado (alto riesgo de ruptura), GraphQL (sobredimensionado para alcance v1).

## Decision 9: Secrets y control de costes
- Decision: Variables de entorno para secretos, .env local fuera de git, limites diarios de gasto y corte de ejecucion al exceder umbral.
- Rationale: Evita exposicion de claves y sobrecostes accidentales en APIs de pago.
- Alternatives considered: Secretos hardcodeados (inaceptable), sin cutoff de gasto (riesgo operativo alto).

## Decision 10: Gestion de entorno Python
- Decision: Gestionar entorno y dependencias con uv y agregar librerias mediante uv add.
- Rationale: Requisito constitucional explicito y reproducibilidad entre entornos.
- Alternatives considered: pip/venv tradicional (no alineado con constitucion vigente).
