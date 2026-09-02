# Paquete posterior a la aceptación — consentimiento escrito

> **Estado operativo:** listo para envío individual por el usuario humano. Este archivo no forma parte del freeze `1.2.1-authorized-prehuman`, no contiene PII y no amplía la autorización existente.

## 1. Punto de partida verificable

El 2026-09-02 el usuario informó, sin compartir identidades ni contenido agronómico, que las cinco personas invitadas a entrevista confirmaron verbalmente su interés y que quedaron cubiertos en principio los tres roles profesionales `R01`, `R02` y `A01`.

Estas confirmaciones son **aceptaciones preliminares verbales**. No equivalen a consentimiento informado escrito, entrevista realizada, designación definitiva de revisor, etiqueta humana ni evidencia agronómica. Hasta recibir por correo las respuestas obligatorias de este paquete:

- entrevistas con consentimiento válido: **0/5**;
- roles de revisión con consentimiento válido: **ninguno**;
- entrevistas realizadas: **0**;
- revisiones humanas: **0**;
- `benchmark_validated`: **false**.

Las llamadas entrantes reportadas se limitaron a la confirmación preliminar. No registrar ni incorporar su contenido, identidad, número, horario o metadatos. Bajo el alcance vigente, el consentimiento y cualquier recolección sustantiva continúan limitados al correo; una entrevista por llamada o videollamada requiere una ampliación expresa del canal antes de realizarla.

## 2. Gate privado antes de enviar

El usuario debe completar en cada correo, fuera de Git y sin mostrar esos valores a la IA:

- `[RESPONSABLE, CONTACTO Y DOMICILIO APLICABLE]`;
- `[CLASES DE DESTINATARIOS]`;
- `[ALMACENAMIENTO PRIVADO Y PERSONAS CON ACCESO]`;
- `[CANAL PRIVADO PARA EJERCER DERECHOS]`;
- firma privada del remitente.

La retención acordada es: eliminar los originales 30 días después del freeze humano final o, si ese freeze no ocurre, no más tarde del 31/12/2026. No adjuntar casos, formularios ni preguntas sustantivas al correo de consentimiento.

Enviar cada mensaje por separado. No usar CC/CCO grupal. El usuario es el único remitente y custodio de las respuestas identificables.

## 3. Correo para cada entrevista (`I01`–`I05`)

**Asunto:** Consentimiento escrito para entrevista sobre recorridas pos-evento

```text
Hola:

Gracias por confirmar verbalmente tu interés. Antes de coordinar o responder preguntas sustantivas, necesito dejar por escrito el alcance y tus decisiones de consentimiento.

FINALIDAD
Comprender cómo se organiza una recorrida de soja después de lluvia fuerte, granizo o viento, qué información suele faltar y qué controles debería tener un prototipo no prescriptivo. La participación es voluntaria, no remunerada y no se graba.

RESPONSABLE Y CONTACTO
[RESPONSABLE, CONTACTO Y DOMICILIO APLICABLE]

QUÉ SE SOLICITARÁ
Una entrevista de 25–35 minutos sobre el proceso de trabajo. No se necesitan nombres de clientes, establecimientos, coordenadas, superficies o importes exactos, matrículas, contratos, teléfonos, decisiones comerciales, imágenes ni documentos privados. Podés omitir cualquier pregunta o retirarte antes del freeze humano.

TRATAMIENTO Y DESTINATARIOS
Las notas crudas y tu identidad quedarán bajo custodia privada del responsable. [CLASES DE DESTINATARIOS]. La IA y el repositorio solo podrán recibir un registro reescrito, saneado, codificado y aprobado por una segunda revisión de privacidad. No se publicará nada sin una autorización separada del responsable del proyecto.

ALMACENAMIENTO, RETENCIÓN Y DERECHOS
[ALMACENAMIENTO PRIVADO Y PERSONAS CON ACCESO]. Los originales se eliminarán 30 días después del freeze humano final o, si no ocurre, no más tarde del 31/12/2026. Podés solicitar acceso, rectificación, retiro o supresión antes del freeze mediante [CANAL PRIVADO PARA EJERCER DERECHOS]. Después de una eventual publicación pública no puede garantizarse la eliminación de copias de terceros; hoy no hay publicación autorizada.

Respondé copiando estas seis líneas y marcando una sola opción en cada una. No incluyas todavía información de campo:

1. Comprendí finalidad, carácter voluntario, destinatarios, retención y derechos: SÍ / NO.
2. Acepto participar: SÍ / NO.
3. Acepto que conclusiones anónimas y agregadas puedan proponerse para una publicación futura, sujeta a autorización separada del proyecto: SÍ / NO.
4. Acepto que una experiencia pueda convertirse en un escenario reescrito, sintético y anonimizado: SÍ / NO.
5. Acepto una posible cita anónima saneada: SÍ / NO.
6. Autorizo grabación: NO.

Solo las respuestas SÍ en 1 y 2 habilitan la participación. Las opciones 3, 4 y 5 son independientes y pueden ser NO sin afectar la entrevista. Una respuesta SÍ no autoriza publicación por sí sola.

[FIRMA PRIVADA DEL USUARIO]
```

## 4. Correo para cada rol agronómico

Reemplazar `[ROL]` y `[CARGA]` privadamente con una sola fila:

| Rol | Carga posterior al piloto |
|---|---|
| `R01` | Referencia ciega y revisión de salida de 30 casos sintéticos, en bloques y con Fase A bloqueada antes de Fase B. |
| `R02` | Segunda referencia y revisión de salida independiente de los 10 casos prefijados. |
| `A01` | Adjudicación de las 30 referencias después de congelar y medir el desacuerdo; no revisa salidas del sistema. |

**Asunto:** Consentimiento escrito — rol [ROL] en revisión agronómica ciega

```text
Hola:

Gracias por confirmar verbalmente tu interés en el rol [ROL]. Antes del piloto o de acceder a casos, necesito dejar por escrito el protocolo y tus decisiones de consentimiento.

FINALIDAD Y CARGA
Evaluar de forma ciega y reproducible un sistema que estructura notas sintéticas de recorridas de soja posteriores a lluvia, granizo o viento. Tu carga prevista es: [CARGA]. Habrá primero un piloto de formato que no usa casos evaluados.

RESPONSABLE Y CONTACTO
[RESPONSABLE, CONTACTO Y DOMICILIO APLICABLE]

DATOS Y LÍMITES
Los casos son sintéticos. No se solicita diagnóstico, prescripción, matrícula, empleador ni información de clientes. No compartas nombres, establecimientos, coordenadas, imágenes, documentos privados o datos operativos reales. La participación es voluntaria, no remunerada y sin grabación.

CEGUERA E INDEPENDENCIA
No se revelarán proveedor, modelo, salida, métricas, respuestas ajenas ni split cuando puedan sesgar tu fase. No converses los casos con los otros roles. `R01`, `R02` y `A01` deben ser personas distintas. Una posible exposición previa no te excluye automáticamente, pero debe declararse para el análisis de sensibilidad.

TRATAMIENTO, RETENCIÓN Y DERECHOS
Tu identidad y consentimiento quedarán bajo custodia privada del responsable. [CLASES DE DESTINATARIOS]. [ALMACENAMIENTO PRIVADO Y PERSONAS CON ACCESO]. Al repositorio solo llegará una revisión codificada y sin PII. Los originales se eliminarán 30 días después del freeze humano final o, si no ocurre, no más tarde del 31/12/2026. Podés solicitar acceso, rectificación, retiro o supresión antes del freeze mediante [CANAL PRIVADO PARA EJERCER DERECHOS]. No existe autorización actual de publicación.

Respondé copiando estas cinco líneas y marcando una sola opción en cada una. No adjuntes todavía revisiones ni contenido agronómico:

1. Comprendí finalidad, carga, carácter voluntario, destinatarios, retención y derechos: SÍ / NO.
2. Acepto participar en el rol [ROL]: SÍ / NO.
3. Confirmo que trabajaré independientemente antes de ver respuestas ajenas: SÍ / NO.
4. Declaro posible exposición previa a AgroField o a estos casos: SÍ / NO.
5. Acepto que resultados anónimos y agregados puedan proponerse para una publicación futura, sujeta a autorización separada del proyecto: SÍ / NO.

Solo las respuestas SÍ en 1, 2 y 3 habilitan el rol. La línea 4 debe responderse con veracidad: un SÍ se conserva para sensibilidad y no es rechazo automático. La línea 5 es opcional; un NO no invalida la revisión. Ninguna respuesta autoriza publicación por sí sola.

[FIRMA PRIVADA DEL USUARIO]
```

## 5. Validación privada de cada respuesta

El custodio registra fuera de Git:

1. código del slot y fecha de respuesta;
2. copia íntegra del aviso enviado y de la respuesta recibida;
3. resultado de cada alcance, sin condensarlo en un “acepto” general;
4. versión del texto de consentimiento: `post-acceptance-consent-pack-v1`;
5. retiro, restricción u observación, si existe;
6. confirmación de que no se recibió contenido sustantivo antes del consentimiento.

No reenviar respuestas, capturas, firmas, cabeceras, direcciones ni calendario a la IA. Si una persona responde `NO` a una condición obligatoria, detener su participación y reportar solo el conteo. Si responde de manera ambigua, pedir aclaración por correo; no inferir consentimiento.

## 6. Parte saneado para volver a la IA

Cuando estén procesadas las respuestas, informar únicamente:

```text
CONSENTIMIENTOS V1 — ACTUALIZACIÓN SANEADA. No comparto PII.
Entrevistas con consentimiento escrito obligatorio válido: [0–5]/5.
Roles con consentimiento escrito obligatorio válido: [ninguno / R01 / R02 / A01].
Consentimientos ambiguos o incompletos: [conteo].
Retiros o rechazos acumulados: [conteo].
Contenido sustantivo recogido antes del consentimiento: 0.
PII incorporada a Git o enviada a la IA: 0.
Datos agronómicos reales enviados a Git o a la IA: 0.
```

No incluir quién aceptó cada alcance opcional. Esos permisos se conservan privadamente y solo se consultan si más adelante existe una autorización separada de publicación.

## 7. Gate de avance

| Condición | Estado actual | Habilita |
|---|---:|---|
| 3–5 consentimientos escritos de entrevista | 0/5 | Recolección por el canal autorizado |
| Consentimiento escrito e independencia de `R01` | pendiente | Piloto de Fase A de `R01` |
| Consentimiento escrito e independencia de `R02` | pendiente | Piloto de Fase A de `R02` |
| Consentimiento escrito e independencia de `A01` | pendiente | Preparación; la adjudicación espera desacuerdo congelado |
| Canal de llamada/videollamada ampliado | no autorizado | Entrevistas sin grabación por ese canal |

No enviar casos a revisores ni iniciar entrevistas hasta que el gate correspondiente esté completo. No ejecutar Nemotron/Tavily, generar costos, publicar, desplegar, subir video o registrar una submission: ninguna de esas acciones está autorizada.
