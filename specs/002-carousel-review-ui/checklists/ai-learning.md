# Specification Quality Checklist: Aprendizaje IA y Señales de Retroalimentación

**Purpose**: Validate that AI learning, feedback signal, and historical context requirements are complete, clear, consistent, and measurable
**Created**: 2026-05-09
**Feature**: [spec.md](../spec.md) | [data-model.md](../data-model.md)
**Actor/Timing**: Reviewer (PR) — before merging changes to the AI learning pipeline
**Depth**: Standard
**Focus areas**: FeedbackSignal completeness · prompt enrichment clarity · historical context coverage · measurability · edge cases · traceability

---

## Requirement Completeness

- [ ] CHK001 - ¿Están definidos todos los campos que el operador puede corregir y que generan un `FeedbackSignal`? ¿El spec limita explícitamente a `description_text` y `suggested_price` o permite campos futuros? [Completeness, Spec §FR-013, data-model.md §FeedbackSignal]
- [ ] CHK002 - ¿Están especificados los requisitos para el caso en que el operador modifica ambos campos a la vez (descripción Y precio)? ¿Se crean uno o dos `FeedbackSignal`? [Completeness, data-model.md §Reglas de integridad]
- [ ] CHK003 - ¿Están definidos los requisitos para el caso en que el operador rechaza sin modificar ningún campo? ¿Se crea o no `FeedbackSignal`? [Completeness, Spec §FR-005, data-model.md §FeedbackSignal]
- [ ] CHK004 - ¿El spec define qué volumen de señales históricas (`FeedbackSignal` + `HistoricalReference`) se pasa al modelo en cada llamada? ¿Están documentados los límites (últimas 15 correcciones, últimas 10 ventas)? [Completeness, Gap]
- [ ] CHK005 - ¿Están definidos los requisitos para el pipeline downstream que consume los `FeedbackSignal`? ¿El spec dice quién lee esa tabla y con qué frecuencia? [Completeness, Gap]
- [ ] CHK006 - ¿El spec define qué ocurre con los `FeedbackSignal` si la propuesta asociada se elimina? ¿Hay requisito de retención o borrado en cascada? [Completeness, Gap]
- [ ] CHK007 - ¿Están especificados los requisitos de trazabilidad entre `FeedbackSignal`, `OperatorReview` y `AIProposal`? ¿El spec garantiza que siempre existe la cadena `FeedbackSignal → OperatorReview → AIProposal`? [Completeness, data-model.md §Reglas de integridad]

---

## Requirement Clarity

- [ ] CHK008 - ¿El término "reentrenamiento del modelo de IA" en FR-013 está definido con precisión? ¿El spec aclara si se refiere a fine-tuning, RLHF, few-shot prompting u otro mecanismo? [Ambiguity, Spec §FR-013]
- [ ] CHK009 - ¿"Aprende de estos patrones" (sección del prompt del sistema) está cuantificado? ¿El spec define cómo el modelo debe usar las correcciones (ponderar, ignorar outliers, priorizar las más recientes)? [Clarity, Gap]
- [ ] CHK010 - ¿"Señal de retroalimentación para el reentrenamiento" (FR-013) es operacionalmente distinto de "ajuste del modelo de IA" (mencionado en las clarificaciones)? ¿El spec usa estos términos de forma consistente? [Consistency, Spec §FR-013]
- [ ] CHK011 - ¿El requisito RDA-002 especifica con suficiente precisión qué métricas de `FeedbackSignal` debe mostrar el notebook? ¿"Tasa de corrección por campo" está definida como una fórmula o solo como descripción cualitativa? [Clarity, Spec §RDA-002]
- [ ] CHK012 - ¿"Distribución de delta de precio" (RDA-002) está definida? ¿El spec especifica si es delta absoluto (€), delta porcentual (%) o ambos, y sobre qué ventana temporal? [Clarity, Ambiguity, Spec §RDA-002]
- [ ] CHK013 - ¿El spec define el significado de `similarity_score` en `HistoricalReference`? ¿Está claro cómo se calcula, quién lo asigna y qué rango de valores tiene? [Clarity, Gap]

---

## Requirement Consistency

- [ ] CHK014 - ¿FR-007 ("preservar contenido original junto con versión corregida") es consistente con la estructura de `FeedbackSignal` (`original_value` + `corrected_value`)? ¿No hay conflicto entre dónde se almacena la versión original: en `AIProposal` o en `FeedbackSignal`? [Consistency, Spec §FR-007, data-model.md §FeedbackSignal]
- [ ] CHK015 - ¿La regla "si `decision = edit`, se DEBE crear al menos un `FeedbackSignal`" (data-model) es consistente con FR-005 que dice que el formulario de edición es opcional? ¿Puede el operador abrir el formulario, no cambiar nada y confirmar? [Consistency, Spec §FR-005, data-model.md §Reglas de integridad]
- [ ] CHK016 - ¿El estado `modified_pending_reapproval` al que pasa la propuesta (FR-013) es consistente con la cola de revisión (FR-002)? ¿El spec garantiza que estas propuestas reentran en la cola inmediatamente y no en el siguiente ciclo? [Consistency, Spec §FR-002, §FR-013]
- [ ] CHK017 - ¿El requisito de enviar `original_value` y `corrected_value` como strings (data-model) es consistente con los tipos reales de los campos (`description_text` es texto, `suggested_price` es numérico)? ¿El spec define el formato de serialización del precio? [Consistency, Gap]

---

## Acceptance Criteria Quality

- [ ] CHK018 - ¿Los criterios de aceptación del User Story 4 (rechazo con modificaciones) son suficientes para verificar objetivamente que se creó un `FeedbackSignal` correcto? ¿El escenario 4 especifica qué campos del `FeedbackSignal` deben inspeccionarse? [Acceptance Criteria, Spec §User Story 4]
- [ ] CHK019 - ¿SC-003 ("95% de acciones registradas sin pérdida") incluye explícitamente los `FeedbackSignal` o solo las aprobaciones/rechazos sin corrección? [Acceptance Criteria, Spec §SC-003]
- [ ] CHK020 - ¿RDA-002 tiene criterios de aceptación medibles? ¿Se especifica un umbral mínimo de registros de `FeedbackSignal` necesarios para que las métricas del notebook sean estadísticamente significativas? [Measurability, Spec §RDA-002]

---

## Scenario Coverage

- [ ] CHK021 - ¿El spec cubre el escenario en que `FeedbackSignal` se crea con éxito pero la actualización de estado de la propuesta a `modified_pending_reapproval` falla? ¿Hay requisito de atomicidad o transacción? [Coverage, Exception Flow, Gap]
- [ ] CHK022 - ¿El spec cubre el flujo de segunda revisión de una propuesta `modified_pending_reapproval`? ¿Qué ocurre si el segundo revisor también la modifica? ¿Se acumulan `FeedbackSignal`? [Coverage, Alternate Flow, Gap]
- [ ] CHK023 - ¿El spec cubre el escenario en que el contexto de aprendizaje (señales históricas) está vacío (primera propuesta del sistema, sin correcciones previas)? ¿Hay requisito de fallback? [Coverage, Edge Case, Gap]
- [ ] CHK024 - ¿El spec cubre el escenario en que `HistoricalReference` tiene registros con `sold_price = null` o `similarity_score` fuera de rango? ¿Hay requisito de validación o filtrado? [Coverage, Edge Case, Gap]
- [ ] CHK025 - ¿El spec cubre el comportamiento de la búsqueda web (DuckDuckGo) cuando no devuelve precios? ¿Hay requisito de fallback al precio LLM puro sin blending? [Coverage, Exception Flow, Gap]

---

## Non-Functional Requirements

- [ ] CHK026 - ¿Están definidos los requisitos de latencia para la generación de propuestas con contexto enriquecido (señales + históricos + búsqueda web)? ¿El aumento de latencia frente a la generación sin contexto está acotado? [Non-Functional, Gap]
- [ ] CHK027 - ¿CQR-001 ("sin llamadas adicionales de IA") cubre explícitamente la búsqueda web con DuckDuckGo? ¿El spec aclara que DuckDuckGo no tiene coste de API o que el coste es despreciable? [Non-Functional, Clarity, Spec §CQR-001]
- [ ] CHK028 - ¿El spec define requisitos de privacidad para los `FeedbackSignal`? ¿Los valores corregidos por el operador (que pueden contener descripciones de productos) están sujetos a alguna política de retención o anonimización? [Non-Functional, Gap]
- [ ] CHK029 - ¿El spec define qué ocurre cuando el presupuesto diario de IA (`llm_daily_budget_usd`) se agota durante el procesado de una propuesta? ¿Hay requisito de degradación controlada? [Non-Functional, Spec §CQR-001, Gap]

---

## Dependencies & Assumptions

- [ ] CHK030 - ¿El spec valida explícitamente la asunción de que el backend (feature 001) ya expone endpoints de señales históricas? ¿O es `HistoricalReference` una tabla nueva que requiere un mecanismo de carga? [Assumption, Spec §Assumptions]
- [ ] CHK031 - ¿Está documentada la dependencia de `clients.py` en la variable de entorno `openai_api_key`? ¿El spec especifica el comportamiento cuando la key no está configurada en producción (no solo en tests con `LLM_STUB`)? [Dependency, Spec §CQR-004]
- [ ] CHK032 - ¿El spec documenta la dependencia de DuckDuckGo como fuente de precios de mercado? ¿Incluye el riesgo de que el servicio esté temporalmente no disponible y su impacto en la calidad de la propuesta? [Dependency, Assumption, Gap]

---

## Ambiguities & Conflicts

- [ ] CHK033 - ¿El blending de precios (LLM 60% + mercado 40%) está documentado en el spec o solo en el código? ¿Debería estar como requisito explícito con sus pesos y condiciones de aplicación? [Ambiguity, Gap]
- [ ] CHK034 - ¿El spec define si la retroalimentación del operador afecta a propuestas futuras de cualquier producto o solo del mismo producto? ¿El contexto de `FeedbackSignal` pasado al LLM es global o filtrado por categoría? [Ambiguity, Spec §FR-013, Gap]
- [ ] CHK035 - ¿"Pendiente de reaprobación al inicio de la cola" (FR-002, FR-013) especifica qué ocurre si hay múltiples propuestas `modified_pending_reapproval` simultáneas? ¿Se ordenan entre sí por fecha, por operador o por número de correcciones? [Ambiguity, Spec §FR-002]
