# Solicitud de autorización expresa

> Solicitud histórica satisfecha el 2026-09-02 con alcance limitado a correo. La decisión vigente está en `authorization-decision-2026-09-02.md`; este archivo se conserva como plantilla y no amplía esa autorización.

## Alcance recomendado

Se solicita autorización únicamente para preparar y ejecutar validación humana bajo estas condiciones:

1. El usuario envía invitaciones privadas, o designa explícitamente otro remitente humano.
2. Máximo inicial: 5 personas para entrevistas y 3 profesionales agronómicos para revisión/adjudicación.
3. Canales permitidos: correo, WhatsApp o LinkedIn, siempre uno a uno y solo si el usuario los aprueba.
4. Un único recordatorio, no antes de 3 días hábiles; silencio posterior equivale a cierre del contacto.
5. Participación voluntaria, sin compensación y sin grabación por defecto.
6. Identidades, contactos, consentimientos identificables y notas crudas quedan bajo custodia privada del usuario, fuera del repositorio.
7. La IA recibe únicamente registros anonimizados y saneados con códigos como `P01`, `R01` y `A01`.
8. Antes de revisar casos se corrigen los bloqueos P0 de `preflight-findings.md`.
9. No se publican nombres, citas literales, audios, coordenadas, establecimientos ni datos operativos reales.
10. La autorización puede revocarse para contactos futuros en cualquier momento.

## Decisiones que no están incluidas

Esta autorización no permite:

- llamadas a Nebius o Tavily;
- uso de créditos o cualquier gasto;
- publicación del repositorio o datos;
- despliegue, video o submission;
- contacto masivo, scraping o publicación de convocatorias;
- grabación de audio/video;
- compensación a participantes;
- prescripciones o decisiones agronómicas reales.

Cada elemento requiere una autorización separada si llegara a ser necesario.

## Respuesta exacta sugerida

El usuario puede autorizar el alcance recomendado respondiendo:

```text
AUTORIZO VALIDACIÓN HUMANA AGROFIELD V1.
Entrevistas: autoricé hasta 5 invitaciones para obtener 3–5 entrevistas.
Revisión: autoricé hasta 3 invitaciones a profesionales agronómicos para cubrir R01, R02 y A01.
Canales autorizados: [correo / WhatsApp / LinkedIn; eliminar los no autorizados].
Remitente de los contactos: [yo / otra persona humana designada privadamente].
Custodio privado de identidades y notas crudas: [yo / persona designada privadamente].
Grabación: NO.
Compensación: NO.
La IA y el repositorio recibirán solo registros saneados y anonimizados.
No autorizo Nebius, Tavily, gastos, publicación, despliegue, video ni submission.
```

Si el usuario modifica un límite, prevalece su respuesta. Una respuesta genérica como “seguí” no se interpreta como autorización para contactar personas o tratar datos reales.

## Información privada necesaria antes de enviar

El custodio debe completar fuera de Git el addendum del guion de consentimiento:

- identidad del responsable del tratamiento;
- medio de contacto y domicilio aplicable;
- destinatarios o clases de destinatarios;
- ubicación privada de almacenamiento;
- fecha o evento límite de retención;
- procedimiento de acceso, rectificación, retiro y supresión.

No colocar esos datos identificatorios en archivos versionados.
