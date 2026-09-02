# Paquete de autorización y validación humana

> **Estado: `AUTHORIZED_EMAIL_ONLY_PENDING_PRIVATE_SETUP`.** El usuario autorizó el alcance limitado el 2026-09-02. Solo el usuario puede enviar los correos y custodiar identidades. No se debe enviar el primer mensaje hasta completar privadamente el addendum y los controles pendientes. Ver `authorization-decision-2026-09-02.md`.

## Propósito

Preparar una validación humana defendible sin introducir datos personales en Git y sin contaminar las etiquetas con la salida del sistema. El objetivo es obtener:

- 3–5 entrevistas consentidas y anonimizadas sobre el flujo real;
- 30 anotaciones agronómicas primarias;
- 10 segundas anotaciones independientes;
- revisiones de todas las tareas propuestas;
- acuerdo entre revisores antes de adjudicar;
- una referencia adjudicada y congelada.

## Alcance autorizado, todavía no ejecutado

- Hasta 5 invitaciones privadas a asesores, productores o scouts para conseguir 3–5 entrevistas.
- Hasta 3 invitaciones privadas a profesionales agronómicos: dos revisores independientes y un adjudicador distinto.
- Mensajes uno a uno exclusivamente por correo; sin scraping, campañas masivas, publicaciones públicas ni más de un recordatorio.
- Entrevistas sin grabación y sin compensación.
- El usuario conserva identidades, datos de contacto y notas crudas en un espacio privado fuera del repositorio.
- El repositorio recibe únicamente registros saneados con IDs aleatorios.

La autorización de este paquete no incluye Nebius, Tavily, pagos, publicación, despliegue, video ni submission.

## Archivos

| Archivo | Función |
|---|---|
| `authorization-request.md` | Alcance exacto que el usuario puede aprobar o modificar. |
| `authorization-decision-2026-09-02.md` | Decisión registrada, límites y exclusiones vigentes. |
| `contact-and-review-plan.md` | Perfiles, canales, roles, asignación y cronograma. |
| `invitation-and-consent-scripts.md` | Invitaciones, recordatorio único y guiones de consentimiento. |
| `email-outreach-pack.md` | Correos finales y checklist privado para ejecutar sin compartir PII. |
| `privacy-controls.md` | Flujo de datos, minimización, retiro, retención y controles. |
| `execution-checklist.md` | Gates verificables desde autorización hasta freeze final. |
| `preflight-findings.md` | Riesgos técnicos que deben cerrarse antes de la ronda ciega. |

## Gates antes del primer contacto

- [x] Autorización humana expresa registrada en la conversación y en el repositorio sin PII.
- [x] Correo y máximos de 5 + 3 destinatarios aprobados.
- [x] El usuario es remitente y custodio privado.
- [ ] Se completan privadamente responsable, contacto, domicilio, destinatarios y plazo de retención del aviso de privacidad.
- [x] Grabación `NO` y compensación `NO`.

## Gates antes de la primera revisión de casos

- [ ] Dos revisores agronómicos independientes y un adjudicador globalmente distinto confirmados.
- [ ] Roles `R01`, `R02`, `A01`, `PR01` y coordinador asignados por código.
- [x] Hallazgos P0 de `preflight-findings.md` resueltos y probados localmente.
- [x] P1 de exposición previa e independencia global de roles resuelto y probado localmente.
- [x] Generador de paquete Fase A sin salida del sistema implementado y separado de Fase B.
- [ ] Alias y mapa de sistemas guardados fuera de Git.
- [ ] Rúbrica y archivos de la ronda vueltos a congelar si cambiaron.

## Regla de veracidad

Una IA puede preparar formularios, validar esquema, calcular métricas y verificar hashes. No puede enviar las invitaciones, conocer destinatarios ni figurar como entrevistado, revisor, adjudicador o revisión de privacidad humana.
