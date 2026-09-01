# Paquete de autorización y validación humana

> **Estado: `NOT_AUTHORIZED`.** Estos documentos no autorizan contactar personas, recolectar datos reales ni iniciar revisiones. Hace falta una respuesta expresa del usuario al alcance de `authorization-request.md`.

## Propósito

Preparar una validación humana defendible sin introducir datos personales en Git y sin contaminar las etiquetas con la salida del sistema. El objetivo es obtener:

- 3–5 entrevistas consentidas y anonimizadas sobre el flujo real;
- 30 anotaciones agronómicas primarias;
- 10 segundas anotaciones independientes;
- revisiones de todas las tareas propuestas;
- acuerdo entre revisores antes de adjudicar;
- una referencia adjudicada y congelada.

## Alcance preparado, no ejecutado

- Hasta 5 invitaciones privadas a asesores, productores o scouts para conseguir 3–5 entrevistas.
- Hasta 3 invitaciones privadas a profesionales agronómicos: dos revisores independientes y, preferentemente, un adjudicador distinto.
- Mensajes uno a uno por canales aprobados; sin scraping, campañas masivas, publicaciones públicas ni más de un recordatorio.
- Entrevistas sin grabación por defecto.
- El usuario conserva identidades, datos de contacto y notas crudas en un espacio privado fuera del repositorio.
- El repositorio recibe únicamente registros saneados con IDs aleatorios.

La autorización de este paquete no incluye Nebius, Tavily, pagos, publicación, despliegue, video ni submission.

## Archivos

| Archivo | Función |
|---|---|
| `authorization-request.md` | Alcance exacto que el usuario puede aprobar o modificar. |
| `contact-and-review-plan.md` | Perfiles, canales, roles, asignación y cronograma. |
| `invitation-and-consent-scripts.md` | Invitaciones, recordatorio único y guiones de consentimiento. |
| `privacy-controls.md` | Flujo de datos, minimización, retiro, retención y controles. |
| `execution-checklist.md` | Gates verificables desde autorización hasta freeze final. |
| `preflight-findings.md` | Riesgos técnicos que deben cerrarse antes de la ronda ciega. |

## Gates antes del primer contacto

- [ ] Autorización humana expresa registrada en la conversación.
- [ ] Canales y máximo de destinatarios aprobados.
- [ ] El usuario acepta ser custodio de identidades o designa uno fuera de Git.
- [ ] Se completan privadamente responsable, contacto, domicilio, destinatarios y plazo de retención del aviso de privacidad.
- [ ] Se confirma grabación `NO` y compensación `NO`, o se obtiene una autorización separada.

## Gates antes de la primera revisión de casos

- [ ] Al menos dos revisores agronómicos independientes confirmados.
- [ ] Roles `R01`, `R02`, `A01`, `PR01` y coordinador asignados por código.
- [x] Hallazgos P0 de `preflight-findings.md` resueltos y probados localmente.
- [x] Generador de paquete Fase A sin salida del sistema implementado y separado de Fase B.
- [ ] Alias y mapa de sistemas guardados fuera de Git.
- [ ] Rúbrica y archivos de la ronda vueltos a congelar si cambiaron.

## Regla de veracidad

Una IA puede preparar formularios, validar esquema, calcular métricas y verificar hashes. No puede figurar como entrevistado, revisor, adjudicador ni revisión de privacidad humana.
