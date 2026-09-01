# Hallazgos de preflight antes de revisión humana

> Estado al 2026-09-01. Son riesgos del arnés actual, no resultados agronómicos. Los P0 deben resolverse antes de entregar salidas a revisores.

## P0-1 — La referencia puede quedar anclada por la salida

`make_blind_packet()` incluye en un mismo registro la nota/contexto y la salida completa del sistema. Las instrucciones dicen leer primero la nota, pero eso no impide que la salida influya en los campos de referencia.

**Corrección requerida:** generar dos artefactos separados. Fase A contiene solo nota/contexto/rúbrica. Fase B contiene la salida ciega y solo se libera después de hashear la anotación de Fase A.

**Verificación:** test que rechace en Fase A las claves `output`, `system_alias`, proveedor, split, referencia, score, tareas y telemetría.

## P0-2 — `benchmark_validated` no implementa todos los gates documentados

La condición actual comprueba completitud básica, referencia adjudicada, presencia de task reviews y algún acuerdo. No comprueba entrevistas, segunda revisión de privacidad, freeze humano ni umbrales de F1/omisiones/afirmaciones/task precision/seguridad.

**Corrección requerida:** un reporte de readiness por gate con razón de fallo y `--require-validated` dependiente de todos los gates vinculantes.

**Verificación:** tests negativos independientes por cada gate y un test positivo completo con datos humanos de prueba claramente marcados como fixtures, nunca como evidencia real.

## P0-3 — Formularios estructuralmente vacíos pueden contar

La validación de anotaciones exige origen, ciego, consentimiento, IDs y presencia de las 11 claves, pero no comprueba que prioridad, omisiones, evidencia, fecha, privacidad y campos requeridos estén realmente completos. La validación de salida es aún más permisiva.

**Corrección requerida:** validación de esquema estricta, estados permitidos, tareas completas, fecha válida, `privacy_check: passed` y consistencia entre cantidad de tareas y etiquetas.

**Verificación:** las plantillas sin completar deben ser ignoradas y aumentar `invalid_or_nonhuman_records_ignored`.

## P0-4 — Task precision puede duplicar la segunda revisión

La métrica agrega todas las etiquetas humanas válidas. En los 10 casos dobles, las tareas quedarían contadas dos veces y el resultado dependería de la cantidad de revisores, no solo de casos/tareas.

**Corrección requerida:** separar `primary_task_precision`, acuerdo doble y `adjudicated_task_precision`; definir una única métrica vinculante sin duplicados.

**Verificación:** agregar una segunda revisión no debe cambiar la precisión primaria; sí debe producir acuerdo y desacuerdo.

## P0-5 — No se exige doble revisión de las salidas

Readiness exige dos anotadores en los 10 casos de referencia, pero no exige dos `output_reviews` completos para esos mismos casos. Podría aparecer acuerdo de referencia mientras falta acuerdo de tareas.

**Corrección requerida:** exigir 10 pares completos tanto en referencia como en salida y reportar IDs faltantes.

**Verificación:** `--require-validated` falla si uno de los 10 casos carece de segundo output review.

## P1 — Independencia y exposición previa

Los registros permiten `possible_prior_exposure`, pero la métrica no produce un análisis de sensibilidad ni excluye/segmenta esos pares. Además, un adjudicador que también revisó necesita declaración explícita.

**Corrección recomendada:** reportar resultados con todos los revisores y una sensibilidad sin exposición previa; declarar superposición de roles.

## Orden de resolución

1. Separar Fase A/Fase B.
2. Endurecer esquemas y completitud.
3. Corregir task precision y doble output review.
4. Hacer que readiness/`--require-validated` refleje todos los gates.
5. Añadir análisis de exposición y roles.

Ninguno de estos cambios toca las reglas de `policy.py` ni requiere datos reales, servicios externos o gasto.
