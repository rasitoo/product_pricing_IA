<!--
Sync Impact Report
- Version change: 1.0.0 -> 1.0.1
- Modified principles:
	- V. Seguridad de Secretos y Control de Costes de API -> V. Seguridad de Secretos, Control de Costes de API y Gestion Estandarizada de Entorno
- Added sections:
	- Ninguna
- Removed sections:
	- Ninguna
- Templates requiring updates:
	- ✅ updated: .specify/templates/plan-template.md
	- ✅ updated: .specify/templates/spec-template.md
	- ✅ updated: .specify/templates/tasks-template.md
	- ✅ no action required: .specify/templates/commands/*.md (ruta no existe)
- Follow-up TODOs:
	- Ninguno
-->
# product_pricing_IA Constitution

## Core Principles

### I. Optimizacion Calidad-Coste Basada en Evidencia
Toda decision tecnica sobre modelos, prompts o pipelines MUST justificarse con evidencia
medible de calidad frente a coste. Cada propuesta MUST comparar baseline vs propuesta
en las mismas condiciones y reportar mejora o deterioro de calidad, latencia y coste de
ejecucion. Rationale: optimizar IA sin medir el coste total produce decisiones inestables
o economicamente inviables.

### II. Experimentacion Reproducible y Trazable
Cada experimento MUST registrar configuracion completa (modelo, prompts, parametros,
seed cuando aplique, conjunto de evaluacion, version de codigo y fecha). Los resultados
MUST poder reproducirse desde repositorio y datos versionados. Rationale: sin trazabilidad
no se puede validar que una mejora calidad/coste sea real y sostenible.

### III. Codigo Limpio y Testeable (NON-NEGOTIABLE)
El codigo MUST ser modular, legible y testeable de forma automatizada. Toda logica nueva
MUST incluir pruebas unitarias y, cuando haya integracion con servicios externos, pruebas de
integracion con mocks o stubs para evitar coste accidental. Ningun cambio se integra sin
pasar lint, tests y revision de mantenibilidad. Rationale: el codigo limpio reduce deuda
tecnica y hace seguras las iteraciones frecuentes de optimizacion.

### IV. Documentacion Ejecutable en Notebook Paralelo
Todo hito funcional que afecte rendimiento o coste MUST incluir un notebook paralelo (.ipynb)
con resumen de enfoque, metodologia, resultados, visualizaciones y conclusiones. El notebook
MUST enlazar artefactos de ejecucion y explicar limites conocidos. Rationale: la documentacion
ejecutable acelera aprendizaje del equipo y auditoria tecnica de decisiones.

### V. Seguridad de Secretos, Control de Costes de API y Gestion Estandarizada de Entorno
Las claves de API MUST gestionarse fuera del codigo fuente (variables de entorno/secret manager)
y nunca almacenarse en texto plano. Las llamadas a APIs de pago MUST incluir limites de uso,
timeouts y mecanismos de corte por presupuesto. Cada ejecucion relevante MUST reportar consumo
estimado y coste acumulado. En proyectos Python, la creacion del entorno virtual y la gestion
de dependencias MUST realizarse con uv; la incorporacion de librerias MUST hacerse mediante
`uv add`. Rationale: proteger secretos, prevenir sobrecostes y estandarizar el entorno mejora
reproducibilidad y reduce desalineaciones entre desarrollo y ejecucion.

## Requisitos Operativos y de Rendimiento

- Las metricas de calidad MUST definirse por feature en spec.md (por ejemplo, precision,
	recall, score humano o metricas de negocio).
- Cada evaluacion MUST incluir coste por corrida y coste por unidad util (por ejemplo,
	coste por tarea resuelta o por 1,000 solicitudes).
- Las optimizaciones MUST priorizar mejora de razon calidad/coste, no solo maxima calidad.
- El proyecto MUST mantener un flujo reproducible local/CI para ejecutar tests y evaluaciones.
- Los notebooks de resumen MUST almacenarse junto al codigo y versionarse en git.
- En proyectos Python, el entorno virtual MUST gestionarse con uv y las dependencias MUST
	incorporarse con `uv add`.

## Flujo de Desarrollo y Puertas de Calidad

- En specify/plan, cada feature MUST declarar hipotesis de optimizacion, baseline y criterios
	de exito medibles de calidad y coste.
- En tasks, cada historia MUST incluir tareas de implementacion, pruebas y actualizacion de
	notebook de resultados.
- Antes de merge, la PR MUST incluir evidencia comparativa baseline vs propuesta y verificacion
	de que no expone secretos.
- Cualquier incremento esperado de coste operativo MUST documentarse junto con umbrales de
	rollback y plan de mitigacion.
- Si una evaluacion no es reproducible o no cuantifica coste, el cambio MUST bloquearse.

## Governance

Esta constitucion prevalece sobre practicas informales del proyecto. Toda modificacion MUST
registrarse mediante PR con motivacion, impacto esperado y actualizacion de plantillas
afectadas. Las decisiones de versionado de la constitucion siguen semver:

- MAJOR: cambios incompatibles en principios o eliminacion/redefinicion material.
- MINOR: adicion de principios o expansion normativa sustancial.
- PATCH: aclaraciones editoriales sin cambiar obligaciones.

Cada PR MUST incluir una comprobacion de cumplimiento constitucional. En revisiones de plan,
spec y tasks, el equipo MUST verificar explicitamente trazabilidad experimental, calidad/coste,
testabilidad, documentacion en notebook, control de secretos/costes de API y uso de uv para
entorno/dependencias Python.

**Version**: 1.0.1 | **Ratified**: 2026-05-05 | **Last Amended**: 2026-05-05
