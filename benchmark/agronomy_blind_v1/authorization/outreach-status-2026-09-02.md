# Estado saneado de outreach — 2026-09-02

> Registro operativo posterior al freeze `1.2.1-authorized-prehuman`. No forma parte de ese freeze, no cambia sus hashes y no contiene nombres, correos, organizaciones, localidades ni otra PII.

## Conteos verificables

- Invitaciones de entrevista enviadas: **5/5** (`I01`–`I05`), según parte del usuario.
- Invitaciones de revisión enviadas: **3/3** (`AR01`, `AR02`, `AA01`), según parte del usuario.
- Aceptaciones: **0 confirmadas**.
- Entrevistas realizadas: **0**.
- Revisiones agronómicas: **0**.
- PII incorporada a Git: **0**.
- Datos agronómicos reales incorporados a la IA o a Git: **0**.
- Identificadores proporcionados transitoriamente a la IA para ejecutar el envío: **1 dirección de correo**, no reproducida ni persistida en el repositorio.

La invitación `I01` fue enviada individualmente por correo desde la cuenta del usuario, por instrucción expresa del usuario y con asistencia de la IA en la interfaz. El usuario informó después que envió los siete borradores restantes. No se registra aquí ninguna identidad ni dirección. El envío de invitaciones no constituye entrevista, consentimiento, revisión humana ni evidencia agronómica.

## Control de proceso

El usuario atestiguó el 2026-09-02, sin compartir PII adicional, que completó la configuración privada. El estado operativo vigente es `AUTHORIZED_EMAIL_ONLY_PRIVATE_SETUP_ATTESTED`.

La atestación cubre los siete controles privados: responsable y contacto; clases de destinatarios; almacenamiento y acceso; retención; canal de derechos; `PR01` distinto de quien sanea; selección legítima y mapa privado de códigos. La IA no conoce sus valores.

Se conserva la desviación de control `DV-OUTREACH-001`: la invitación `I01` fue asistida antes de que la atestación anónima quedara documentada y una dirección real fue expuesta transitoriamente a la IA para ejecutarla. La atestación posterior cierra el bloqueo operativo, pero no borra el historial.

Mitigación vinculante:

1. todo correo futuro permitido, incluidos los recordatorios, es enviado únicamente por el usuario, sin compartir destinatarios con la IA;
2. no copiar al chat ni a Git identidades, direcciones, firmas, calendarios o respuestas crudas;
3. si una persona responde, enviar primero el aviso privado y obtener los consentimientos separados antes de entrevistar o revisar;
4. conservar el freeze prehumano vigente como snapshot histórico con `outreach_executed: false` y registrar la actividad posterior únicamente fuera de ese manifiesto.

## Cupos agotados y próximo parte

Los cupos de invitación inicial están agotados: **5/5 entrevistas y 3/3 revisiones**. No se pueden sumar destinatarios sin una ampliación expresa. Para cada correo sin respuesta puede enviarse un único recordatorio después de tres días hábiles; no se habilita ningún canal distinto de correo ni un segundo recordatorio.

Después de actuar, el usuario informa únicamente:

```text
ACTUALIZACIÓN SANEADA. No comparto PII adicional.
Invitaciones de entrevista enviadas: 5/5.
Invitaciones de revisión enviadas: 3/3.
Aceptaciones de entrevista: [conteo].
Roles de revisión confirmados por código: [ninguno / R01 / R02 / A01].
Retiros o rechazos: [conteo].
PII incorporada a Git: 0.
Datos agronómicos reales enviados a IA o Git: 0.
```

Los conteos pueden actualizarse sin revelar quién ocupa cada código.
