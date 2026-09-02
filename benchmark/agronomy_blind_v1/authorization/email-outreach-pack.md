# Paquete operativo de correo — validación humana V1

> **Estado:** autorizado el 2026-09-02 para envío exclusivo por el usuario humano. No pegar nombres, direcciones, firmas, respuestas ni notas crudas en Git o en conversaciones con IA.

## 1. Gate privado antes del primer correo

Completar fuera del repositorio:

- [ ] responsable, contacto y domicilio aplicable;
- [ ] destinatarios o clases de destinatarios;
- [ ] almacenamiento privado y personas con acceso;
- [ ] eliminación: 30 días después del freeze humano final o, si no hay freeze, no más tarde del 31/12/2026;
- [ ] canal para acceso, rectificación, retiro y supresión;
- [ ] `PR01` distinto de la persona que sanea;
- [ ] hasta cinco destinatarios legítimos de entrevista y tres de revisión;
- [ ] mapa privado entre personas y códigos aleatorios, sin iniciales.

Si falta un punto, no enviar todavía. La IA no necesita ni debe recibir la información completada.

## 2. Cupos y registro privado

Usar esta estructura únicamente en una copia privada, nunca dentro del repositorio:

| Slot | Finalidad | Estado permitido |
|---|---|---|
| `I01`–`I05` | Invitación para entrevista | no enviado / enviado / aceptó / rechazó / sin respuesta / retiró |
| `AR01` | Candidato a revisor primario `R01` | no enviado / enviado / aceptó / rechazó / sin respuesta / retiró |
| `AR02` | Candidato a revisor secundario `R02` | no enviado / enviado / aceptó / rechazó / sin respuesta / retiró |
| `AA01` | Candidato a adjudicador `A01` | no enviado / enviado / aceptó / rechazó / sin respuesta / retiró |

No exceder 5 invitaciones de entrevista ni 3 de revisión. Puede enviarse un único recordatorio después de 3 días hábiles. Si menos de 3 entrevistas o los tres roles independientes no quedan cubiertos, detenerse y solicitar una ampliación; no sumar contactos por cuenta propia.

## 3. Correo inicial — entrevista

**Asunto:** Invitación breve sobre recorridas de soja después de tormentas

```text
Hola:

Estoy validando cómo se organiza una recorrida de soja después de lluvia fuerte, granizo o viento, y qué información suele faltar entre quien observa y quien decide.

Busco conversar entre 25 y 35 minutos con personas adultas que hayan participado directamente en ese flujo. No necesito nombres de clientes, establecimientos, coordenadas, superficies, importes ni decisiones comerciales. La participación es voluntaria, no remunerada y no se graba. Podés omitir preguntas o terminar en cualquier momento. Primero preguntaré por el proceso real; recién al final describiré un prototipo no prescriptivo.

Si te interesa, respondeme por este correo y te enviaré el alcance, el aviso de privacidad y las opciones de consentimiento antes de coordinar. No hace falta compartir ningún dato operativo en esta respuesta.

[FIRMA PRIVADA DEL USUARIO]
```

## 4. Correo inicial — revisión agronómica

Elegir un único rol por destinatario y reemplazar `[ROL]` y `[CARGA]` privadamente:

| Rol | Carga prevista después del piloto |
|---|---|
| `R01` | Referencia ciega y revisión de salida de 30 casos sintéticos, por bloques. |
| `R02` | Segunda referencia y revisión de salida de 10 casos prefijados. |
| `A01` | Adjudicación de 30 referencias después de congelar y medir el desacuerdo. |

**Asunto:** Invitación a revisión ciega de casos sintéticos de recorrida pos-evento

```text
Hola:

Estoy preparando una evaluación ciega de un sistema que estructura notas de recorridas de soja posteriores a lluvia, granizo o viento. Busco un/a profesional agronómico/a para el rol [ROL]. La carga prevista es: [CARGA]. Antes de confirmar habrá un piloto de formato que no usa casos evaluados.

Los casos son completamente sintéticos. No se solicita diagnóstico, prescripción ni información de clientes. No se revela proveedor, modelo, métricas ni split; las respuestas se producen independientemente y solo podrían usarse en el futuro de forma anónima o agregada, con consentimiento y una autorización de publicación separada. La participación es voluntaria, no remunerada y puede retirarse antes del freeze.

Si te interesa recibir el protocolo completo y el consentimiento, respondeme por este correo. No hace falta enviar matrícula, empleador ni datos de clientes.

[FIRMA PRIVADA DEL USUARIO]
```

## 5. Recordatorio único

Enviar solo después de 3 días hábiles y una sola vez:

```text
Hola. Cierro este mensaje para no insistir: ¿querés que te envíe el protocolo de la entrevista/revisión de AgroField? Si no respondés, no volveré a contactarte por este estudio. Gracias.
```

Ante un rechazo o retiro:

```text
Gracias por avisar. No habrá nuevos contactos por este estudio. El material identificable y todo registro aún no congelado asociado a tu código se eliminarán conforme al aviso de privacidad, si corresponde.
```

## 6. Respuesta después de una aceptación inicial

Antes de recolectar cualquier respuesta sustantiva, enviar el addendum privado completo y el guion de `../protocol/consent-and-privacy.md`. Registrar cada alcance por separado. No agruparlos en un único “acepto”.

Para entrevistas:

```text
Comprendí finalidad, carácter voluntario, destinatarios, retención y derechos: SÍ / NO.
Acepto participar: SÍ / NO.
Acepto uso de conclusiones agregadas en una posible publicación futura: SÍ / NO.
Acepto un escenario reescrito y anonimizado: SÍ / NO.
Acepto una cita anónima saneada: SÍ / NO.
Autorizo grabación: NO.
```

Para revisores:

```text
Acepto participar: SÍ / NO.
Acepto un posible uso futuro de resultados anónimos y agregados: SÍ / NO.
Confirmo que revisaré independientemente antes de ver respuestas ajenas: SÍ / NO.
Declaro posible exposición previa a AgroField o a estos casos: SÍ / NO.
```

Un `NO` a participar detiene el proceso. La negativa a cita o escenario no invalida los demás alcances. El uso futuro sigue bloqueado hasta una autorización expresa de publicación del usuario.

## 7. Único parte operativo que puede volver a la IA

Después de completar el setup y actuar, informar solo conteos y códigos no identificables:

```text
CONFIGURACIÓN PRIVADA COMPLETA. No comparto PII.
Invitaciones de entrevista enviadas: [0–5]/5.
Invitaciones de revisión enviadas: [0–3]/3.
Aceptaciones de entrevista: [conteo].
Roles de revisión confirmados por código: [ninguno / R01 / R02 / A01].
Retiros o rechazos: [conteo].
Datos reales enviados a IA o Git: 0.
```

No enviar nombres, emails, firmas, organizaciones, localidades, calendarios, notas crudas ni capturas. Los registros saneados se incorporarán más adelante mediante las plantillas y la doble revisión `DS01` → `PR01`.
