# Feature Specification: Asistente de Venta Reventa por Foto

**Feature Branch**: `001-resale-pricing-assistant`  
**Created**: 2026-05-05  
**Status**: Draft  
**Input**: User description: "Aplicación de ventas que recibe fotos de productos, genera descripción y precio justo para segunda mano, con revisión humana, publicación en plataformas y entrada vía WhatsApp/Telegram, con monitoreo de costes/calidad/fallos y despliegue progresivo hasta AWS"

## Clarifications

### Session 2026-05-05

- Q: ¿Qué alcance debe tener la publicación externa en la primera versión? → A: Sin publicación externa en la primera versión; solo generar borrador aprobado y exportable.
- Q: ¿Qué canal de entrada debe incluir la primera versión? → A: Solo API propia en la primera versión; mensajería después.
- Q: ¿En qué fuentes debe basarse el pricing de la primera versión? → A: Historial interno y búsqueda en internet en tiempo real.
- Q: ¿Qué política de aprobación debe regir en la primera versión? → A: Aprobación humana obligatoria, con futura excepción solo para productos de alta confianza.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Valorar Producto por Foto (Priority: P1)

Como vendedor, quiero enviar fotos de un objeto y recibir una propuesta de descripción y precio de venta de segunda mano, para publicar más rápido sin redactar ni investigar manualmente.

**Why this priority**: Es el núcleo de valor del producto y permite un MVP utilizable aunque no exista integración con canales externos.

**Independent Test**: Puede probarse de forma independiente cargando fotos de prueba y verificando que el sistema devuelve una ficha con descripción, precio sugerido, rango de confianza y explicación resumida de factores de precio.

**Acceptance Scenarios**:

1. **Given** un producto con al menos una foto válida, **When** el vendedor inicia el análisis, **Then** el sistema genera una descripción de venta legible y un precio sugerido para segunda mano.
2. **Given** una propuesta de precio generada, **When** el vendedor consulta el detalle, **Then** el sistema muestra la base del cálculo con referencias internas, señales obtenidas en internet en tiempo real y estado detectado del producto.
3. **Given** un producto sin calidad mínima de imagen, **When** se ejecuta el análisis, **Then** el sistema rechaza el procesamiento con una indicación clara para recapturar fotos.

---

### User Story 2 - Flujo de Revisión y Preparación de Publicación (Priority: P2)

Como operador de ventas, quiero revisar, aprobar, corregir o rechazar la propuesta de la IA antes de exportarla para publicación, para mantener control comercial y minimizar anuncios erróneos.

**Why this priority**: Aporta gobernanza del proceso y reduce riesgo operativo; permite uso real en producción aunque la publicación externa automática quede fuera de la primera versión.

**Independent Test**: Puede probarse con propuestas generadas previamente, validando que el operador puede aprobar, editar o rechazar y que solo las aprobadas pasan al estado exportable o publicable manualmente.

**Acceptance Scenarios**:

1. **Given** una propuesta en estado pendiente de revisión, **When** el operador la aprueba, **Then** el sistema la marca como lista para exportación o publicación manual con trazabilidad de quién aprobó y cuándo.
2. **Given** una propuesta con errores de texto o precio, **When** el operador aplica correcciones, **Then** el sistema guarda versión corregida y justificación de cambios.
3. **Given** una propuesta rechazada, **When** el operador registra motivo de rechazo, **Then** el sistema conserva el historial y evita su publicación automática.
4. **Given** una propuesta con alta confianza calculada por el sistema, **When** el operador la revisa en la primera versión, **Then** la aprobación humana sigue siendo obligatoria y la posible autoaprobación queda diferida a fases futuras.

---

### User Story 3 - Canales de Ingesta Adicionales y Automatización Progresiva (Priority: P3)

Como vendedor móvil, quiero disponer de canales adicionales a la API propia para iniciar el flujo automáticamente en fases posteriores, para reducir fricción y ampliar la automatización sin bloquear la primera versión.

**Why this priority**: Amplía adopción y prepara automatización futura, pero depende de que P1 y P2 estén estables y no es necesario para entregar una primera fase usable.

**Independent Test**: Puede probarse en una fase posterior conectando un canal adicional de entrada y verificando creación automática de borrador y transición a estado revisable sin depender de publicación externa.

**Acceptance Scenarios**:

1. **Given** una fase posterior con canal adicional habilitado, **When** el sistema recibe fotos por ese canal, **Then** se crea un borrador de producto y se inicia el análisis automáticamente.
2. **Given** un borrador aprobado por operador, **When** la primera versión no dispone de publicación externa activa, **Then** el sistema genera un formato exportable y conserva el estado listo para publicación manual.
3. **Given** futuras integraciones de entrada aún no activas, **When** el operador usa la primera versión, **Then** la API propia sigue siendo suficiente para completar el flujo de principio a fin.

---

### Edge Cases

- Fotos duplicadas o del mismo producto enviadas varias veces en pocos minutos por API o por futuros canales adicionales.
- Producto no identificable por imagen (fondo confuso, objeto parcialmente visible).
- Inconsistencia entre historial interno y señales de precio obtenidas en internet en tiempo real.
- Aprobación concurrente por dos operadores sobre la misma propuesta.
- Propuesta de alta confianza marcada como autoaprobable antes de que esa capacidad esté habilitada.
- Fallo temporal del proveedor de IA durante generación de descripción o pricing.
- Falta de publicación externa activa en primera versión pese a existir propuesta aprobada.
- Coste acumulado de IA supera el umbral diario definido para operación.
- Entornos iniciales sin infraestructura cloud final deben seguir siendo funcionales.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST permitir la creación de un borrador de producto a partir de una o varias fotos.
- **FR-002**: System MUST generar una descripción de venta de segunda mano lista para revisión humana.
- **FR-003**: System MUST estimar un precio sugerido y un rango razonable de venta para cada producto.
- **FR-004**: System MUST mostrar la justificación principal de la recomendación de precio con trazabilidad de señales utilizadas.
- **FR-005**: System MUST almacenar historial de propuestas, revisiones, aprobaciones, correcciones y rechazos por producto.
- **FR-006**: System MUST incluir una página de evaluación para revisar resultados del LLM, base de pricing y decisión operativa (aprobar/corregir/rechazar).
- **FR-007**: System MUST permitir corrección manual de descripción y precio antes de exportar o publicar manualmente.
- **FR-008**: System MUST bloquear cualquier publicación automática si no existe aprobación explícita de un operador autorizado.
- **FR-009**: System MUST soportar integración con canales de entrada por API para recepción de fotos.
- **FR-010**: System MUST tratar la API propia como canal obligatorio de la primera versión y mantener los canales de mensajería como capacidad diferida a fases posteriores.
- **FR-011**: System MUST generar una salida exportable para publicación manual de propuestas aprobadas en la primera versión.
- **FR-012**: System MUST aprender de resultados históricos de productos similares vendidos para ajustar recomendaciones futuras de precio y plazo estimado de venta.
- **FR-013**: System MUST operar por fases, manteniendo utilidad en cada fase sin dependencia obligatoria del entorno cloud final.
- **FR-014**: System MUST registrar métricas operativas de calidad, coste y fallos de las llamadas al proveedor LLM.
- **FR-015**: System MUST permitir consulta de coste acumulado por periodo y por flujo operativo.
- **FR-016**: System MUST dejar preparada la trazabilidad necesaria para integrar publicación automática en plataformas externas en fases posteriores sin rediseñar el flujo de aprobación.
- **FR-017**: System MUST dejar preparada la trazabilidad necesaria para integrar canales de mensajería en fases posteriores sin rediseñar el flujo principal basado en API.
- **FR-018**: System MUST exigir aprobación humana para todos los productos en la primera versión, incluso cuando el sistema marque alta confianza.
- **FR-019**: System MUST complementar el pricing de la primera versión con búsqueda en internet en tiempo real para detectar comparables y señales actuales de mercado.
- **FR-020**: System MUST diferenciar en la explicación del precio qué señales provienen del historial interno y cuáles provienen de fuentes externas consultadas en tiempo real.
- **FR-021**: System MUST dejar preparada la trazabilidad y reglas necesarias para habilitar una futura excepción de autoaprobación solo en productos de alta confianza.

### Cost & Quality Requirements *(mandatory for AI features)*

- **CQR-001**: Feature MUST definir métricas de calidad objetivo para descripción, pricing y coherencia comercial antes de iterar optimizaciones.
- **CQR-002**: Feature MUST comparar baseline vs propuesta en calidad, coste y tasa de error sobre el mismo conjunto de evaluación.
- **CQR-003**: Feature MUST definir umbrales de gasto y criterios de parada para evitar sobrecostes de API LLM.
- **CQR-004**: Feature MUST gestionar secretos de API fuera del código fuente y sin exposición en logs funcionales.
- **CQR-005**: For Python features, virtual environment and dependency management MUST use uv, and new libraries MUST be added with `uv add`.

### Reproducibility & Documentation Artifacts *(mandatory for AI features)*

- **RDA-001**: Feature MUST definir un protocolo reproducible de evaluación con datasets/versiones de referencia.
- **RDA-002**: Feature MUST incluir y mantener un notebook `.ipynb` paralelo con metodología, resultados, análisis de coste y conclusiones.
- **RDA-003**: Feature MUST definir estrategia de pruebas para lógica core, integraciones externas y rutas de fallo.

### Key Entities *(include if feature involves data)*

- **Producto**: Item de segunda mano con fotos, metadatos, estado de publicación y trazabilidad operativa.
- **PropuestaIA**: Resultado generado por IA con descripción, precio sugerido, rango de precio, argumentos y métricas de confianza.
- **RevisionOperador**: Decisión humana (aprobación/corrección/rechazo) con comentarios, cambios y marca temporal.
- **ReferenciaHistorica**: Registro de ventas previas y comparables usados para calibrar recomendaciones.
- **ComparableExterno**: Resultado de búsqueda en internet usado como referencia puntual de mercado para pricing.
- **CanalEntrada**: Origen de ingestión (API directa o mensajería) con estado de procesamiento.
- **PublicacionExterna**: Resultado de envío de anuncio por plataforma de compraventa.
- **MetricaLLM**: Medidas de coste, calidad y fallos por ejecución y por periodo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Al menos 90% de productos con fotos válidas reciben propuesta inicial completa (descripción + precio + justificación) en menos de 2 minutos.
- **SC-002**: El tiempo medio de preparación de anuncio por producto se reduce al menos un 60% respecto al flujo manual inicial.
- **SC-003**: Al menos 85% de propuestas aprobadas por operadores quedan listas para publicación manual sin retrabajo adicional de contenido.
- **SC-004**: El error absoluto medio de precio recomendado frente al precio final de cierre mejora al menos 20% frente al baseline inicial.
- **SC-005**: El coste medio de LLM por producto procesado se mantiene dentro del presupuesto objetivo definido por operación.
- **SC-006**: Al menos 95% de incidencias de fallo de LLM y publicación quedan registradas con causa y estado de recuperación.
- **SC-007**: Cada fase entregada del proyecto es usable de forma autónoma sin requerir despliegue cloud final para demostrar valor.
- **SC-008**: La primera versión permite completar el flujo de ingestión, valoración y revisión usando únicamente la API propia.
- **SC-009**: Al menos 80% de propuestas de pricing muestran evidencia trazable combinando historial interno y comparables externos obtenidos en tiempo real.

## Assumptions

- El alcance inicial se centra en productos de segunda mano de categorías con señales visuales suficientes para estimación.
- Los operadores revisores están disponibles para validación antes de cualquier publicación automática.
- La primera versión no permite autoaprobación; cualquier excepción basada en alta confianza se evaluará en fases posteriores.
- La primera versión no incluye publicación automática en plataformas externas; esa capacidad se habilitará progresivamente por prioridad de negocio.
- La primera versión usará solo API propia como canal de entrada; mensajería se añade en fases posteriores.
- La solución debe poder ejecutarse en entorno local/controlado durante fases tempranas y migrar a cloud en fases avanzadas sin rediseño total.
- Existe acceso legal y operativo a datos históricos de ventas para alimentar el aprendizaje de recomendaciones.
- La solución podrá consultar fuentes públicas en internet para enriquecer pricing en tiempo real dentro de límites de coste y cumplimiento.
- El cumplimiento normativo de datos personales y términos de plataformas externas será tratado como requisito operativo del proyecto.
