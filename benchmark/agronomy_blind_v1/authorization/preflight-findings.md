# Hallazgos de preflight antes de revisión humana

> Estado al 2026-09-01: **5/5 P0 cerrados técnicamente; validación humana todavía `NOT_AUTHORIZED`.** Son controles del arnés, no resultados agronómicos. Ningún test o fixture sintético cuenta como revisión humana.

## P0-1 — La referencia puede quedar anclada por la salida

**Estado: RESUELTO** en `4390a4c`. Fase A (`reference_annotation`) y Fase B (`output_review`) se escriben en archivos distintos; el evaluador rechaza un destino compartido. Fase B exige el hash de la anotación Fase A del mismo revisor.

**Hallazgo original:** `make_blind_packet()` incluía en un mismo registro la nota/contexto y la salida completa del sistema. Las instrucciones de orden no impedían que la salida influyera en los campos de referencia.

**Corrección requerida:** generar dos artefactos separados. Fase A contiene solo nota/contexto/rúbrica. Fase B contiene la salida ciega y solo se libera después de hashear la anotación de Fase A.

**Verificación:** test que rechace en Fase A las claves `output`, `system_alias`, proveedor, split, referencia, score, tareas y telemetría.

## P0-2 — `benchmark_validated` no implementa todos los gates documentados

**Estado: RESUELTO** en `19ab37f`. `validation_gates` enumera cada condición, valor, umbral y razón de fallo. `--require-validated` depende de todas; hay un test negativo independiente por gate y un fixture positivo 30/10 marcado `test_fixture_only` y `evidence_claim_allowed: false`.

**Hallazgo original:** la condición comprobaba solo completitud básica, referencia adjudicada, presencia de task reviews y algún acuerdo. No comprobaba entrevistas, segunda revisión de privacidad, freeze humano ni todos los umbrales.

**Corrección requerida:** un reporte de readiness por gate con razón de fallo y `--require-validated` dependiente de todos los gates vinculantes.

**Verificación:** tests negativos independientes por cada gate y un test positivo completo con datos humanos de prueba claramente marcados como fixtures, nunca como evidencia real.

## P0-3 — Formularios estructuralmente vacíos pueden contar

**Estado: RESUELTO** en `19ab37f`. El esquema `1.1.0-candidate` valida IDs, asignación, fecha, consentimiento, privacidad, campos, citas, omisiones, prioridad, tareas completas, etiquetas permitidas y hashes. Las cuatro plantillas incompletas son rechazadas y contabilizadas como inválidas en tests.

**Hallazgo original:** la validación exigía origen, ciego, consentimiento, IDs y presencia de 11 claves, pero no comprobaba contenido, evidencia, fecha, privacidad ni completitud de tareas.

**Corrección requerida:** validación de esquema estricta, estados permitidos, tareas completas, fecha válida, `privacy_check: passed` y consistencia entre cantidad de tareas y etiquetas.

**Verificación:** las plantillas sin completar deben ser ignoradas y aumentar `invalid_or_nonhuman_records_ignored`.

## P0-4 — Task precision puede duplicar la segunda revisión

**Estado: RESUELTO** en `19ab37f`. La métrica vinculante es `primary_task_precision`; `task_precision` es su alias de compatibilidad. Las etiquetas secundarias se reportan separadas y alimentan acuerdo, no el denominador. `adjudicated_task_precision` permanece explícitamente `null` hasta existir una adjudicación de tareas.

**Hallazgo original:** la métrica agregaba todas las etiquetas válidas y duplicaba las tareas de los 10 casos con revisor secundario.

**Corrección requerida:** separar `primary_task_precision`, acuerdo doble y `adjudicated_task_precision`; definir una única métrica vinculante sin duplicados.

**Verificación:** agregar una segunda revisión no debe cambiar la precisión primaria; sí debe producir acuerdo y desacuerdo.

## P0-5 — No se exige doble revisión de las salidas

**Estado: RESUELTO** en `19ab37f`. Se exigen 30 salidas primarias completas y 10 secundarias completas sobre los mismos packet/alias, con revisores distintos y hashes Fase A válidos. El reporte lista IDs faltantes; un test de CLI demuestra salida 2 al quitar una sola secundaria.

**Hallazgo original:** readiness exigía dobles de referencia, pero no dos `output_reviews` completos sobre esos mismos casos.

**Corrección requerida:** exigir 10 pares completos tanto en referencia como en salida y reportar IDs faltantes.

**Verificación:** `--require-validated` falla si uno de los 10 casos carece de segundo output review.

## P1 — Independencia y exposición previa

**Estado: RESUELTO** en el incremento prehumano del 2026-09-02. Las métricas vinculantes conservan todos los pares completos y el reporte agrega una sensibilidad separada que excluye pares donde cualquiera de los dos revisores declaró `possible_prior_exposure: true`, tanto para referencia como para salida. El reporte identifica los casos excluidos de esa sensibilidad; nunca borra el resultado vinculante.

La independencia también se controla a nivel de toda la ronda: un mismo ID no puede actuar como primario y secundario, y ningún adjudicador puede aparecer como revisor en otro caso. Las superposiciones se listan explícitamente y bloquean readiness aunque no coincidan dentro del mismo caso.

**Verificación:** tests cubren sensibilidad con exposición declarada, cruce primario/secundario entre casos y cruce revisor/adjudicador entre casos.

## Orden de resolución aplicado

1. Fase A/Fase B separadas.
2. Esquemas y completitud endurecidos.
3. Task precision y doble output review corregidos.
4. Readiness/`--require-validated` alineados con todos los gates.
5. Análisis de exposición y separación global de roles cerrados antes del primer contacto.

Los cinco P0 y el P1 están probados sin tocar `policy.py`, sin datos reales, servicios externos ni gasto. Estos cierres demuestran integridad metodológica del arnés, no validez agronómica.
