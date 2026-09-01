# Instrucciones de revisión ciega

## Roles

- **Coordinador:** genera paquetes, asigna IDs y conserva el mapa proveedor→alias fuera de los formularios.
- **Revisor primario:** anota todos los casos.
- **Revisor secundario:** anota solo los 10 casos `double_review_required`.
- **Adjudicador:** resuelve desacuerdos después de calcular métricas independientes.

Una persona puede cumplir más de un rol solo si no ve las respuestas ajenas antes de cerrar su propia revisión.

## Condición de ciego

El paquete mostrado al revisor incluye:

- ID de caso y texto de la nota;
- contexto sintético del lote sin ubicación;
- campos extraídos y sus citas;
- omisiones y preguntas;
- estado `blocked/review_ready`;
- prioridad y justificación textual;
- tareas propuestas;
- alertas externas con fuente/fecha, si existieran.

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
4. Revisar la nota antes de la salida.
5. Anotar referencia campo por campo y omisiones.
6. Evaluar la salida sin intentar adivinar el proveedor.
7. Etiquetar todas las tareas.
8. Registrar errores E1–E8 y severidad.
9. Bloquear el archivo y calcular su SHA-256.
10. Recién después comparar revisores y adjudicar.

## Reglas contra contaminación

- No modificar extractor, `policy.py`, prompt, fixtures o umbrales durante una ronda abierta.
- No mostrar resultados agregados hasta recibir ambos archivos de los casos dobles.
- Si el formato falla, corregir el formato sin revelar la respuesta esperada y registrar el incidente.
- Si un revisor reconoce un caso, marcar `possible_prior_exposure: true`.
- El holdout se evalúa una sola vez por versión congelada.

## Criterio de completitud

Una revisión es completa cuando incluye los 11 campos de extracción, omisiones, prioridad, todas las tareas, preguntas de utilidad y cualquier error detectado. Un comentario libre no reemplaza etiquetas estructuradas.

## Resultado honesto

Si el acuerdo es bajo, se publica el desacuerdo y se revisa la definición del problema. No se elimina un revisor, caso o categoría porque perjudique la métrica.
