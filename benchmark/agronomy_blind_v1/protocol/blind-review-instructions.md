# Instrucciones de revisión ciega

## Roles

- **Coordinador:** genera paquetes, asigna IDs y conserva el mapa proveedor→alias fuera de los formularios.
- **Revisor primario:** anota todos los casos.
- **Revisor secundario:** anota solo los 10 casos `double_review_required`.
- **Adjudicador:** resuelve desacuerdos después de calcular métricas independientes.

Para el benchmark validado, el adjudicador debe usar un ID distinto de los revisores del caso. Si por limitación operativa una persona ocupa ambos roles, se documenta como limitación y el gate permanece cerrado.

## Condición de ciego

La revisión usa dos paquetes que nunca comparten archivo.

**Fase A — referencia:**

- ID de caso y texto de la nota;
- contexto sintético del lote sin ubicación;
- rúbrica de campos, omisiones y prioridad.

No incluye ninguna salida, alias o dato del sistema. Al finalizar, se valida el formulario y se calcula el hash canónico de esa anotación.

**Fase B — salida:**

- ID de caso, nota y el mismo contexto sintético;
- campos extraídos y sus citas;
- omisiones y preguntas;
- estado `blocked/review_ready`;
- prioridad y justificación textual;
- tareas propuestas;
- alertas externas con fuente/fecha, si existieran.

Cada formulario Fase B debe copiar `reference_packet_id` y `reference_lock_sha256` de la anotación Fase A del mismo revisor. Un hash ausente o distinto invalida el registro.

Debe excluir:

- proveedor, modelo y endpoint;
- latencia, tokens, costo y request ID;
- referencia candidata o adjudicada;
- split `development/holdout`;
- respuestas de otros revisores;
- nombre del sistema si se compara con otro baseline.

Los alias de sistema se generan de forma aleatoria y estable por corrida, por ejemplo `system-k7`. No usar siempre `A=AgroField`.

## Procedimiento

1. Confirmar consentimiento del revisor para publicar resultados anonimizados.
2. Asignar un `reviewer_id` aleatorio; no usar iniciales.
3. Completar experiencia en banda y rol, sin empleador.
4. Recibir únicamente el paquete Fase A.
5. Anotar referencia campo por campo, citas, omisiones y prioridad; completar fecha y control de privacidad.
6. Validar, bloquear y calcular el hash canónico de la anotación Fase A.
7. Recibir recién entonces el paquete Fase B y vincular el hash anterior.
8. Evaluar la salida sin intentar adivinar el proveedor.
9. Etiquetar **todas** las tareas; una lista parcial invalida el caso.
10. Registrar errores E1–E8 y severidad; bloquear Fase B.
11. Recibir las 30 primarias y las 10 secundarias completas antes de calcular acuerdo.
12. Recién después comparar revisores y adjudicar sin sobrescribir registros.

## Reglas contra contaminación

- No modificar extractor, `policy.py`, prompt, fixtures o umbrales durante una ronda abierta.
- No mostrar resultados agregados hasta recibir ambos archivos de los casos dobles.
- Si el formato falla, corregir el formato sin revelar la respuesta esperada y registrar el incidente.
- Si un revisor reconoce un caso, marcar `possible_prior_exposure: true`.
- El holdout se evalúa una sola vez por versión congelada.

## Criterio de completitud

Una revisión es completa cuando usa esquema `1.1.0-candidate`, IDs no-placeholder, asignación `primary/secondary`, fecha ISO, consentimiento, `privacy_check: passed`, los 11 campos con evidencia literal para cada valor no nulo, omisiones, prioridad, todas las tareas, preguntas de utilidad y errores estructurados. Un comentario libre o una plantilla sin completar no cuenta.

## Resultado honesto

Si el acuerdo es bajo, se publica el desacuerdo y se revisa la definición del problema. No se elimina un revisor, caso o categoría porque perjudique la métrica.
