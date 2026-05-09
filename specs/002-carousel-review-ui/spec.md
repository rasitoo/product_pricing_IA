# Feature Specification: Interfaz de Revisión en Carrusel Estilo Tinder

**Feature Branch**: `002-carousel-review-ui`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "quiero que la web no necesite iniciar sesion, quiero que sea algo tipo tinder, como un carrousel con las fotos y los contenidos generados por la ia donde puedes aceptar lo generado o denegarlo, aportando cambios"

## Clarifications

### Session 2026-05-09

- Q: ¿Cuál debe ser el mecanismo principal de interacción para aceptar/rechazar? → A: Swipe táctil + botones visibles como alternativa (escritorio y móvil).
- Q: ¿Qué ocurre si el operador rechaza sin aportar ningún cambio? → A: El operador puede rechazar directamente sin editar; el motivo es un campo opcional en el formulario.
- Q: ¿En qué dispositivos debe funcionar como prioridad? → A: Solo escritorio (pantallas grandes, ratón); el soporte móvil queda fuera de alcance de esta versión.
- Q: ¿Cuánto tiempo debe durar el TTL del bloqueo optimista de una propuesta? → A: 60 segundos.
- Q: ¿Qué estado final tiene una propuesta rechazada con modificaciones? → A: Pasa a estado "modificada, pendiente de reaprobación" y las correcciones se retroalimentan al sistema de IA para reentrenamiento.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Revisar Propuesta sin Iniciar Sesión (Priority: P1)

Como operador de ventas, quiero acceder directamente a la cola de propuestas generadas por la IA sin necesidad de autenticarme, para revisar y tomar decisiones de forma ágil desde cualquier dispositivo.

**Why this priority**: Es la base de toda la interfaz. Si el acceso sin sesión no funciona, el resto de la funcionalidad no es accesible. Define el modelo de acceso de toda la feature.

**Independent Test**: Abriendo la URL de la aplicación en un navegador sin credenciales previas, el sistema debe mostrar directamente la pantalla de revisión con la primera propuesta pendiente. Entrega valor desde el primer momento sin fricción de registro.

**Acceptance Scenarios**:

1. **Given** un navegador sin sesión activa, **When** el usuario abre la URL de la aplicación, **Then** el sistema muestra la interfaz de revisión sin solicitar credenciales.
2. **Given** la interfaz cargada, **When** no hay propuestas pendientes en cola, **Then** el sistema muestra un mensaje claro indicando que la cola está vacía.
3. **Given** la interfaz cargada, **When** hay al menos una propuesta pendiente, **Then** se muestra la primera propuesta en formato carrusel de forma inmediata.

---

### User Story 2 - Navegar por el Carrusel de Propuestas (Priority: P1)

Como operador de ventas, quiero ver las fotos del producto junto con el contenido generado por la IA (descripción y precio sugerido) en una tarjeta visual, para evaluar la propuesta de un vistazo antes de decidir.

**Why this priority**: El carrusel es el mecanismo central de la experiencia. Sin él no existe interacción posible con las propuestas.

**Independent Test**: Dado un conjunto de propuestas en cola, el operador puede desplazarse entre ellas viendo las fotos del producto y el contenido generado. Puede probarse de forma aislada con propuestas de prueba sin necesidad de ejecutar la acción de aprobación o rechazo.

**Acceptance Scenarios**:

1. **Given** una propuesta con varias fotos, **When** el usuario visualiza la tarjeta, **Then** las fotos se muestran en un visor deslizable dentro de la propia tarjeta.
2. **Given** una propuesta activa, **When** el usuario la visualiza, **Then** el sistema muestra la descripción generada por la IA y el precio sugerido en la misma tarjeta.
3. **Given** varias propuestas en cola, **When** el usuario acepta o rechaza la actual, **Then** la siguiente propuesta pendiente se presenta automáticamente en el carrusel.
4. **Given** la tarjeta activa, **When** el usuario no realiza ninguna acción, **Then** la propuesta permanece visible sin cambios de estado hasta que el operador decide.

---

### User Story 3 - Aceptar una Propuesta Generada (Priority: P2)

Como operador de ventas, quiero aprobar con un gesto o botón el contenido generado por la IA tal como está, para agilizar la revisión cuando la propuesta es correcta.

**Why this priority**: La acción de aceptación es el flujo feliz principal. Sin ella el sistema no puede marcar propuestas como listas para exportación.

**Independent Test**: Seleccionando la acción de aceptar sobre una propuesta, el sistema la marca como aprobada y avanza al siguiente elemento. Puede verificarse revisando el estado en la base de datos sin depender de la publicación externa.

**Acceptance Scenarios**:

1. **Given** una propuesta visible en el carrusel, **When** el operador acepta la propuesta, **Then** el sistema registra la aprobación con fecha, hora y referencia del operador (identificador de sesión o dispositivo) y avanza a la siguiente.
2. **Given** una propuesta aceptada, **When** se consulta su estado, **Then** aparece como "aprobada" y lista para exportación manual.
3. **Given** una propuesta aceptada por error, **When** el operador desea revertir antes de confirmar, **Then** el sistema ofrece la posibilidad de deshacer la última acción durante al menos 5 segundos (FR-010).

---

### User Story 4 - Rechazar una Propuesta (con o sin Modificaciones) (Priority: P2)

Como operador de ventas, quiero rechazar el contenido generado —opcionalmente aportando correcciones de descripción o precio— para descartar o mejorar la propuesta antes de que avance en el flujo.

**Why this priority**: Es el flujo de control de calidad. Sin él la herramienta no cubre el caso de uso de revisión con gobernanza descrito en la feature 001.

**Independent Test**: Dado una propuesta visible, el operador puede introducir texto libre o modificar el precio sugerido y enviar esa versión corregida. El sistema debe guardar la versión corregida y el motivo de cambio. Puede probarse sin publicación externa.

**Acceptance Scenarios**:

1. **Given** una propuesta visible en el carrusel, **When** el operador selecciona la acción de rechazar (swipe izquierda o botón), **Then** el sistema registra el rechazo inmediatamente y avanza al siguiente elemento; adicionalmente ofrece la opción de abrir el formulario inline para añadir motivo o correcciones (no obligatorio).
2. **Given** el formulario de modificación abierto, **When** el operador edita la descripción o el precio y confirma, **Then** el sistema guarda la versión corregida con registro del cambio y motivo opcional.
3. **Given** una propuesta modificada y confirmada, **When** se consulta su historial, **Then** se conservan tanto la versión original de la IA como la versión corregida por el operador, y la propuesta aparece en estado "modificada, pendiente de reaprobación" al inicio de la cola.
4. **Given** una propuesta confirmada como modificada, **When** el sistema la registra, **Then** las correcciones del operador (descripción y/o precio) se envían al backend como señal de retroalimentación para el reentrenamiento o ajuste del modelo de IA.
5. **Given** el formulario de modificación abierto, **When** el operador cierra sin confirmar, **Then** el sistema descarta los cambios y vuelve a la vista del carrusel sin modificar el estado de la propuesta.

---

### Edge Cases

- ¿Qué ocurre si se pierde la conexión de red mientras el operador está revisando una propuesta?
- ¿Cómo se comporta el sistema si dos dispositivos/usuarios acceden a la misma cola simultáneamente y seleccionan la misma propuesta?
- ¿Qué sucede si una propuesta no tiene fotos asociadas (solo texto generado)?
- ¿Cómo se muestra una propuesta con un número muy elevado de fotos (>10)?
- ¿Qué ocurre si el operador intenta aceptar una propuesta que ya fue procesada por otro dispositivo?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE mostrar la interfaz de revisión sin requerir autenticación ni registro.
- **FR-002**: El sistema DEBE presentar las propuestas pendientes en un carrusel visual de una en una, ordenadas por estado (`modified_pending_reapproval` primero) y luego por fecha de creación ascendente.
- **FR-003**: Cada tarjeta del carrusel DEBE mostrar todas las fotos del producto en un visor deslizable, la descripción generada por la IA y el precio sugerido.
- **FR-004**: El usuario DEBE poder aceptar la propuesta actual mediante swipe táctil hacia la derecha o mediante un botón de aceptación visible; ambas formas deben estar disponibles simultáneamente.
- **FR-005**: El usuario DEBE poder rechazar la propuesta actual mediante swipe táctil hacia la izquierda o mediante un botón de rechazo visible. El rechazo directo (sin editar campos) es válido; el formulario inline con los campos de descripción y precio es opcional, y el campo de motivo de rechazo es siempre opcional.
- **FR-006**: El sistema DEBE registrar cada acción de aprobación o rechazo con marca temporal y un identificador de sesión anónimo del dispositivo.
- **FR-007**: El sistema DEBE preservar el contenido original generado por la IA junto con la versión corregida por el operador cuando se realiza una modificación.
- **FR-008**: El sistema DEBE avanzar automáticamente al siguiente elemento pendiente tras confirmar cualquier acción sobre la propuesta actual.
- **FR-009**: El sistema DEBE mostrar un indicador visual del número de propuestas pendientes en cola.
- **FR-010**: El sistema DEBE ofrecer la posibilidad de deshacer la última acción (aceptar/rechazar) durante al menos 5 segundos tras realizarla.
- **FR-011**: El sistema DEBE bloquear una propuesta para otras sesiones mientras está siendo revisada activamente, liberándola automáticamente si la sesión revisora se desconecta o no renueva el bloqueo en 60 segundos (bloqueo con TTL de 60 s).
- **FR-012**: El sistema DEBE mostrar un mensaje claro cuando la cola de propuestas pendientes está vacía.
- **FR-013**: Cuando el operador confirma modificaciones sobre una propuesta, el sistema DEBE enviar al backend las correcciones (campos modificados y sus valores) como señal de retroalimentación para el reentrenamiento del modelo de IA; la propuesta pasa a estado "modificada, pendiente de reaprobación" y vuelve al inicio de la cola.

### Cost & Quality Requirements *(mandatory para features con IA)*

- **CQR-001**: La interfaz no introduce llamadas adicionales a modelos de IA; los costes de IA son los ya registrados por la feature 001 (generación de propuestas).
- **CQR-002**: La carga de cada tarjeta del carrusel (incluyendo fotos) DEBE completarse en menos de 2 segundos en condiciones normales de red (SC-005).
- **CQR-003**: El manejo de imágenes DEBE evitar transferir imágenes en resolución completa innecesaria; se usarán miniaturas o versiones optimizadas para la vista de carrusel.
- **CQR-004**: No se utilizan claves de API adicionales en el frontend; todas las llamadas al backend se realizan sin exponer secretos en el cliente.
- **CQR-005**: La gestión del entorno y dependencias de backend usa `uv`; nuevas librerías se añaden con `uv add`.

### Reproducibility & Documentation Artifacts *(mandatory para features con IA)*

- **RDA-001**: Esta feature no introduce nuevos modelos de evaluación; los protocolos de evaluación de IA son los definidos en la feature 001.
- **RDA-002**: No se requiere notebook de evaluación propio; el notebook existente (`notebooks/pricing-eval.ipynb`) DEBE actualizarse con métricas de FeedbackSignal (tasa de corrección por campo y distribución de delta de precio) una vez implementada la feature.
- **RDA-003**: La estrategia de pruebas incluye: tests unitarios para la lógica de estado del carrusel, tests de integración para las acciones de aprobación/rechazo contra el backend, y tests end-to-end para el flujo completo de revisión.

### Key Entities *(include if feature involves data)*

- **Propuesta (PublicationDraft)**: Unidad central de revisión; contiene fotos, descripción y precio generados por IA, estado (pendiente / aprobada / rechazada / modificada-pendiente-reaprobación) y trazabilidad de la acción del operador. Las propuestas en estado "modificada, pendiente de reaprobación" vuelven al inicio de la cola.
- **Revisión de Operador (OperatorReview)**: Registro de la acción tomada (aceptar/rechazar+modificar), versión corregida si aplica, identificador de sesión anónimo y marca temporal.
- **Cola de Revisión**: Vista ordenada de propuestas en estado "pendiente de revisión" o "modificada, pendiente de reaprobación", con soporte de bloqueo optimista con TTL de 60 s para acceso concurrente. Las propuestas modificadas aparecen al inicio de la cola.
- **Retroalimentación al Modelo (FeedbackSignal)**: Registro estructurado de las correcciones del operador (campo modificado, valor original de la IA, valor corregido por el operador) vinculado a una Propuesta, destinado al pipeline de reentrenamiento del modelo de IA.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El operador puede acceder a la interfaz y comenzar a revisar propuestas en menos de 10 segundos desde que abre la URL, sin pasos de autenticación.
- **SC-002**: El tiempo promedio de revisión por propuesta (aceptar o rechazar con comentario) no supera los 60 segundos.
- **SC-003**: El 95% de las acciones de aceptación o rechazo se registran correctamente en el sistema sin pérdida de datos, medido en condiciones normales de red.
- **SC-004**: La interfaz es completamente funcional en los navegadores de escritorio más usados (Chrome, Firefox, Edge); el soporte móvil queda fuera del alcance de esta versión.
- **SC-005**: El carrusel carga la siguiente propuesta en menos de 2 segundos tras confirmar la acción sobre la actual.
- **SC-006**: La tasa de errores de conflicto por acceso concurrente a la misma propuesta es inferior al 1% del total de acciones registradas.

## Assumptions

- Se asume que el acceso sin autenticación es aceptable porque el entorno de despliegue es una red privada o interna; la exposición pública sin sesión queda fuera de alcance de la primera versión.
- Se asume que el identificador de sesión anónimo (cookie o token local sin cuenta) es suficiente para la trazabilidad de revisiones en esta fase.
- Se asume que el backend (feature 001) ya expone endpoints para consultar propuestas pendientes, aprobar, rechazar y actualizar una propuesta; esta feature solo consume esa API.
- Se asume que las fotos ya están almacenadas y accesibles como URLs desde el backend; la subida de imágenes es responsabilidad de la feature 001.
- Se asume que el soporte multi-idioma queda fuera de alcance de esta versión; la interfaz está en español.
- Se asume que la interfaz de carrusel es la única vista de la aplicación en esta versión; no hay pantallas adicionales (listados, búsqueda, historial de revisiones).
- Se asume que el dispositivo objetivo principal es escritorio (navegador, ratón/teclado); el soporte táctil y móvil queda fuera del alcance de esta versión. El swipe táctil mencionado en FR-004/FR-005 es un mecanismo adicional para usuarios con pantalla táctil en escritorio, no un requisito de soporte móvil.
- Soporte de acceso concurrente desde múltiples sesiones de escritorio es un requisito, pero la resolución de conflictos se basa en bloqueo optimista con TTL, sin edición colaborativa en tiempo real.
