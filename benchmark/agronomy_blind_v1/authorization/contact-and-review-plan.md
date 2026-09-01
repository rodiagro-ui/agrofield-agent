# Plan concreto de contacto y revisión

## Resultado buscado

En una ronda breve y auditable, obtener evidencia que pueda refutar o sostener la hipótesis del producto y convertir el conjunto candidato en una referencia humana adjudicada. El éxito no es “conseguir opiniones positivas”; es recibir etiquetas independientes y conservar desacuerdos.

## Muestra y perfiles

### Entrevistas: 3–5 completadas

Incluir personas adultas con experiencia directa en soja y recorridas posteriores a lluvia, granizo o viento:

- asesor/a agronómico/a;
- productor/a que decide recorridas;
- scout o encargado/a de campo que observa y reporta.

Buscar variación en rol y banda de experiencia. No pedir cliente, empresa, matrícula, localidad pequeña ni tamaño exacto de explotación.

No incluir a una persona que no pueda consentir, que quiera compartir datos identificables o que solo conozca el flujo de manera indirecta. Si menos de 3 de las 5 invitaciones se convierten en entrevistas, detenerse y pedir autorización para ampliar; no aumentar el cupo por cuenta propia.

### Revisión: mínimo 2, ideal 3 profesionales

- `R01`: profesional agronómico primario; anota los 30 casos y revisa todas sus salidas.
- `R02`: segundo profesional independiente; anota los 10 casos prefijados y revisa sus salidas.
- `A01`: adjudicador, idealmente un tercer profesional; firma una referencia final para los 30 casos después del cálculo de desacuerdo.

Una sola persona no puede producir una doble anotación independiente. Si solo hay dos profesionales, ambos pueden adjudicar conjuntamente después de bloquear sus revisiones, pero debe declararse la menor independencia. Los entrevistados y revisores deben ser personas distintas cuando sea posible; cualquier exposición previa se marca y se reporta.

## Canales y cadencia

Orden recomendado:

1. presentación cálida uno a uno dentro de la red profesional del usuario;
2. correo o WhatsApp privado a un contacto legítimo;
3. LinkedIn privado si no existe otro canal.

No usar listas compradas, scraping, grupos, mensajes masivos ni publicaciones abiertas bajo esta autorización. Enviar una invitación inicial y, si no hay respuesta, un único recordatorio después de 3 días hábiles. No insistir ante rechazo o silencio posterior.

## Responsabilidades

| Código | Responsable | Puede ver identidad | Entregable |
|---|---|---:|---|
| `OWNER` | Usuario humano | Sí | Autoriza alcance y uso posterior. |
| `RC01` | Coordinador humano de reclutamiento | Sí | Envía invitaciones y conserva el mapa privado. |
| `F01` | Facilitador humano | Solo si es necesario | Realiza entrevistas sin inducir. |
| `DS01` | Custodio humano de datos | Sí | Sanea notas y atiende retiro/supresión. |
| `PR01` | Revisor humano de privacidad | No necesita identidad | Segunda revisión del material saneado. |
| `R01` | Revisor agronómico primario | No | 30 anotaciones + 30 revisiones de salida. |
| `R02` | Revisor agronómico secundario | No | 10 anotaciones + 10 revisiones de salida. |
| `A01` | Adjudicador humano | No | 30 referencias finales y justificaciones. |
| `QA-AI` | IA | No | Esquema, métricas, errores y hashes; nunca etiquetas humanas. |

Una persona puede cubrir funciones humanas compatibles, salvo que comprometa independencia. `R01` y `R02` nunca ven respuestas ajenas antes del lock. `PR01` no debe ser quien redactó el escenario saneado. `QA-AI` no sustituye ningún rol humano.

## Secuencia por días relativos a la autorización

| Día | Acción | Gate de salida |
|---|---|---|
| D0 | Completar aviso privado, asignar roles por código y aprobar canales. | Alcance y responsable documentados fuera de Git. |
| D1 | Enviar invitaciones dentro de los cupos. | Registro privado de envío; cero PII en Git. |
| D2–D5 | Realizar 3–5 entrevistas de 25–35 minutos, sin grabar. | Consentimiento por alcance y notas crudas privadas. |
| D3–D6 | Sanear entrevistas y hacer segunda revisión de privacidad. | Solo registros `privacy_review_status: passed`. |
| D1–D4 | Resolver hallazgos P0 técnicos y generar materiales en dos fases. | Tests y prueba de ausencia de metadata/salida en referencia. |
| D4–D7 | `R01` y `R02` completan primero las referencias; se bloquean hashes. | 30 primarias y 10 dobles independientes. |
| D6–D9 | Entregar salidas ciegas y recoger clasificación de hechos, prioridad y tareas. | Todas las tareas etiquetadas. |
| D9 | Calcular desacuerdo y kappa antes de mostrar respuestas cruzadas. | Informe de acuerdo inmutable. |
| D9–D10 | `A01` adjudica los 30 casos sin borrar revisiones. | 30 referencias adjudicadas. |
| D10–D11 | Ejecutar métricas, privacidad, gates y nuevo freeze. | `--require-validated` y manifiesto humano válidos. |

El cronograma es una meta, no una presión sobre participantes. Si una revisión apresurada compromete calidad, se extiende sin abrir resultados parciales.

## Diseño de ciego en dos fases

### Fase A — referencia humana

Cada revisor ve solo:

- ID del caso;
- nota sintética;
- contexto sintético sin ubicación;
- rúbrica.

No ve salida, proveedor, alias, referencia candidata, split, score, tareas ni respuestas ajenas. El archivo se cierra y hashea antes de Fase B.

### Fase B — revisión de salida

Después del lock de Fase A, el revisor ve:

- salida con alias aleatorio;
- citas y omisiones;
- estado y prioridad;
- tareas;
- fuente/fecha de alertas externas si existieran.

No ve proveedor, modelo, split, referencia ni métricas. Los 10 dobles deben tener también dos revisiones de salida para calcular acuerdo de tareas.

## Reglas de decisión

- Entrevistas: si menos de 3 participantes reconocen costo operativo repetido, revisar o abandonar la hipótesis.
- Revisión: acuerdo bajo se publica; no se excluyen casos/revisores para mejorar números.
- Task precision final no mezcla ni duplica etiquetas secundarias: se reporta sobre una referencia primaria/adjudicada definida.
- Holdout no se usa para ajustar extractor, `policy.py`, prompt o umbrales.
- Ninguna salida humana autoriza una decisión agronómica real.
