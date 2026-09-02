# Estado saneado de outreach — 2026-09-02

> Registro operativo posterior al freeze `1.2.1-authorized-prehuman`. No forma parte de ese freeze, no cambia sus hashes y no contiene nombres, correos, organizaciones, localidades ni otra PII.

## Conteos verificables

- Invitaciones de entrevista enviadas: **5/5** (`I01`–`I05`), según parte del usuario.
- Invitaciones de revisión enviadas: **3/3** (`AR01`, `AR02`, `AA01`), según parte del usuario.
- Aceptaciones preliminares verbales para entrevista: **5/5**, según parte del usuario.
- Roles profesionales confirmados preliminarmente por vía verbal: **`R01`, `R02` y `A01`**, según parte del usuario.
- Consentimientos informados escritos válidos: **0/5 entrevistas y ninguno de los tres roles**; no fueron reportados todavía.
- Entrevistas realizadas: **0**.
- Revisiones agronómicas: **0**.
- PII incorporada a Git: **0**.
- Datos agronómicos reales incorporados a la IA o a Git: **0**.
- Identificadores proporcionados transitoriamente a la IA para ejecutar el envío: **1 dirección de correo**, no reproducida ni persistida en el repositorio.

La invitación `I01` fue enviada individualmente por correo desde la cuenta del usuario, por instrucción expresa del usuario y con asistencia de la IA en la interfaz. El usuario informó después que envió los siete borradores restantes. Posteriormente informó que todas las personas confirmaron por llamada. No se registra aquí ninguna identidad, dirección, número, horario ni contenido de llamada. El envío de invitaciones y una confirmación verbal no constituyen consentimiento informado escrito, entrevista, revisión humana ni evidencia agronómica.

## Control de proceso

El usuario atestiguó el 2026-09-02, sin compartir PII adicional, que completó la configuración privada. La autorización vigente continúa siendo `AUTHORIZED_EMAIL_ONLY_PRIVATE_SETUP_ATTESTED`; el subestado operativo es `AWAITING_WRITTEN_CONSENT_BEFORE_DATA_COLLECTION`.

La atestación cubre los siete controles privados: responsable y contacto; clases de destinatarios; almacenamiento y acceso; retención; canal de derechos; `PR01` distinto de quien sanea; selección legítima y mapa privado de códigos. La IA no conoce sus valores.

Se conserva la desviación de control `DV-OUTREACH-001`: la invitación `I01` fue asistida antes de que la atestación anónima quedara documentada y una dirección real fue expuesta transitoriamente a la IA para ejecutarla. La atestación posterior cierra el bloqueo operativo, pero no borra el historial.

Mitigación vinculante:

1. todo correo futuro permitido, incluidos los recordatorios, es enviado únicamente por el usuario, sin compartir destinatarios con la IA;
2. no copiar al chat ni a Git identidades, direcciones, firmas, calendarios o respuestas crudas;
3. si una persona responde, enviar primero el aviso privado y obtener los consentimientos separados antes de entrevistar o revisar;
4. conservar el freeze prehumano vigente como snapshot histórico con `outreach_executed: false` y registrar la actividad posterior únicamente fuera de ese manifiesto.

Las llamadas entrantes reportadas se tratan solo como aceptación preliminar. Bajo el alcance vigente, seguimiento, consentimiento y recolección sustantiva continúan por correo. Una entrevista por llamada o videollamada exige una ampliación expresa del canal antes de comenzar. El texto operativo para convertir la aceptación preliminar en consentimiento escrito está en `post-acceptance-consent-pack.md`.

## Cupos agotados y próximo parte

Los cupos de invitación inicial están agotados: **5/5 entrevistas y 3/3 revisiones**. No se pueden sumar destinatarios sin una ampliación expresa. Como todas las personas confirmaron preliminarmente, el próximo paso no es un recordatorio: es enviar individualmente el aviso y obtener consentimiento escrito por correo. No se habilita ningún canal distinto de correo.

Después de actuar, el usuario informa únicamente:

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

Los conteos pueden actualizarse sin revelar quién ocupa cada código.
