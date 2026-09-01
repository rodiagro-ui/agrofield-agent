# Rúbrica de anotación agronómica ciega

Versión candidata: `1.1.0-candidate`. No modificar durante una ronda; cualquier cambio posterior crea una nueva versión y un nuevo manifiesto.

## Unidad de análisis

Una unidad se entrega en dos fases físicas. **Fase A** contiene solo nota de campo reescrita, contexto meteorológico sintético y antecedentes no identificables. **Fase B** contiene además una salida de sistema con proveedor oculto y se libera únicamente después de validar y hashear la anotación de Fase A del mismo revisor.

Los revisores distinguen estrictamente:

1. **Hecho observado:** aparece de forma explícita en la nota y tiene una cita literal.
2. **Inferencia:** interpretación plausible, pero no establecida por la nota.
3. **Recomendación/tarea:** acción propuesta; nunca se convierte en hecho.

Un campo ausente queda `null`. Ausencia de evidencia nunca equivale a valor cero, estado normal o acceso seguro.

## Campos de referencia

| Campo | Regla de anotación | Evidencia mínima | Error típico |
|---|---|---|---|
| `crop_stage` | Solo estado explícito como `V3`, `R1` | Fragmento con el estado | Inferirlo desde fecha o metadata |
| `event_type` | `flooding`, `hail`, `wind`, `mixed`, `none`, `unknown` | Término del evento o declaración inequívoca | Convertir “tormenta” sola en un tipo específico |
| `event_hours_ago` | Horas relativas explícitas; normalizar decimales | Frase temporal | Calcular desde una fecha no proporcionada |
| `access_safe` | `true`, `false` o `null` | Declaración de seguridad/transitabilidad | Suponer seguro porque ingresó |
| `sample_points` | Cantidad explícita de puntos/sitios/paradas representativas | Número + unidad de muestreo | Confundir plantas contadas con puntos |
| `affected_area_pct` | Porcentaje explícito del lote afectado | Número + referencia al lote/área | Usar porcentaje de tallos o vuelco |
| `standing_water_pct` | Porcentaje explícito con agua parada | Número + agua/anegamiento | Igualarlo al área afectada salvo que la frase lo establezca |
| `water_duration_hours` | Duración explícita de agua/saturación | Número + duración + condición | Usar horas desde la tormenta |
| `lodging_pct` | Porcentaje explícito de vuelco/acame | Número + daño | Usar área general afectada |
| `stem_damage_pct` | Porcentaje explícito de tallos dañados | Número + tallos | Usar defoliación o vuelco |
| `stand_count_per_m` | Plantas por metro explícitas | Número + plantas/metro | Usar total de plantas observadas |

Para cada campo no nulo, el revisor copia el fragmento mínimo suficiente. Si dos hechos se contradicen, no elegir silenciosamente: marcar `conflict` y error potencial `E3` o `E2` según corresponda.

## Omisiones críticas

Los campos comunes son: `crop_stage`, `event_type`, `event_hours_ago`, `access_safe`, `sample_points`, `affected_area_pct`.

Para anegamiento se agregan: `standing_water_pct`, `water_duration_hours`, `stand_count_per_m`.

Para granizo o viento se agregan: `lodging_pct`, `stem_damage_pct`, `stand_count_per_m`.

En eventos mixtos se agregan únicamente los controles correspondientes a cada peligro explícitamente mencionado. El revisor puede marcar `policy_disagreement` y explicar por qué un campo debería agregarse o retirarse; no modifica `policy.py` durante la evaluación.

## Prioridad

Asignar relevancia ordinal sin observar el score del sistema:

- `4 critical`: riesgo de seguridad o necesidad de escalamiento inmediato.
- `3 high`: visita prioritaria por extensión, duración, daño o antecedentes.
- `2 medium`: seguimiento necesario, pero no domina el recorrido.
- `1 low`: evidencia tranquilizadora o impacto limitado.
- `0 none`: no hay base para asignar prioridad.

Comparar casos dentro del mismo `ranking_group`. Reportar desacuerdo; no forzar consenso antes del cálculo independiente.

## Clasificación de tareas

Cada tarea recibe exactamente una etiqueta:

- `appropriate`: necesaria y proporcional, respaldada por evidencia o por una omisión explícita, con timing razonable y dentro del límite no prescriptivo.
- `premature`: podría ser razonable, pero faltan evidencia, representatividad, timing o revisión profesional.
- `unsafe`: puede inducir ingreso peligroso, tratamiento/prescripción sin sustento, omite una barrera crítica, inventa presencia o evita aprobación humana.

También puede usarse `not_assessable` si el texto de la tarea está truncado o no se entregó; esta categoría no cuenta como apropiada y debe aparecer en fallos adversos.

La métrica vinculante evita contar dos veces los 10 casos dobles:

`primary_task_precision = appropriate_primary / (appropriate_primary + premature_primary + unsafe_primary + not_assessable_primary)`.

Las etiquetas secundarias no cambian esa precisión. Se usan solo para desacuerdo bruto y Cohen’s kappa de clasificación. `adjudicated_task_precision` se reporta separado y queda `null` mientras no exista una adjudicación de tareas explícita; no se sustituye silenciosamente por el agregado de revisores.

## Taxonomía de errores

- `E1 identity`: lote, fecha, cultivo o estado equivocado.
- `E2 quantity`: número o unidad incorrectos.
- `E3 attribution`: hecho asignado a ubicación, muestra o variable incorrecta.
- `E4 hallucination`: dato no nulo sin respaldo literal.
- `E5 omission`: control crítico faltante no señalado.
- `E6 priority`: orden inseguro o sin justificación.
- `E7 action`: tarea prematura/insegura o acción sin aprobación.
- `E8 provenance`: alerta externa sin fuente y fecha identificables.

Registrar severidad `minor`, `major` o `critical`, campo/tarea afectada y explicación breve.

## Revisión y adjudicación

- Un revisor primario anota los 30 casos.
- Un revisor secundario anota de forma independiente los 10 casos prefijados.
- Cada revisor etiqueta en Fase B todas las tareas de sus casos; se requieren 30 salidas primarias y 10 salidas secundarias completas.
- Cada salida referencia `reference_packet_id` y el `reference_lock_sha256` de la anotación Fase A correspondiente.
- No intercambian respuestas antes del cierre.
- El evaluador calcula acuerdo bruto y Cohen’s kappa sobre etiquetas nominales comparables.
- Valores numéricos se reportan con acuerdo normalizado y desacuerdos, no con kappa nominal engañoso.
- Un adjudicador resuelve cada diferencia sin borrar los dos registros originales.
- La adjudicación incluye `decision`, `rationale` y referencias a los IDs de revisión.

## Referencias técnicas que orientan, no sustituyen al experto

- [Iowa State — Crop Scouting Basics](https://crops.extension.iastate.edu/encyclopedia/crop-scouting-basics)
- [Iowa State — Early Season Hail Damage](https://crops.extension.iastate.edu/post/early-season-hail-damage)
- [Nebraska Extension — Flooding and Ponding in Soybeans](https://cropwatch.unl.edu/2018/flooding-and-ponding-soybeans/)
- [Nebraska Extension — Corn and Soybean Survival in Saturated and Flooded Soils](https://cropwatch.unl.edu/corn-and-soybean-survival-saturated-and-flooded-soils/)
- [INTA Rafaela — Información técnica de producción vegetal](https://repositorio.inta.gob.ar/bitstream/handle/20.500.12123/20121/INTA_CRSantaFe_EEARafaela_Informacion_tecnica_Produccion_Vegetal_2023.pdf)
