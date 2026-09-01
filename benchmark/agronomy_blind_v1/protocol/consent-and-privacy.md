# Consentimiento, privacidad y anonimización

## Alcance

Este protocolo cubre entrevistas breves con asesores/productores y la eventual transformación de experiencias en escenarios sintéticos. No autoriza recolectar datos operativos reales dentro del repositorio.

No sustituye asesoramiento legal. Si una organización exige su propio consentimiento o acuerdo de confidencialidad, prevalece ese instrumento.

## Guion de consentimiento

Leer antes de comenzar:

> Estamos evaluando un prototipo que ayuda a detectar información faltante en recorridas de soja posteriores a eventos meteorológicos. La conversación dura aproximadamente 25–35 minutos. Participar es voluntario; puede omitir cualquier pregunta o terminar en cualquier momento. No necesitamos nombres, clientes, establecimientos, coordenadas, matrículas, teléfonos ni datos comerciales precisos. No grabaremos audio o video salvo autorización separada. Las conclusiones se usarán de forma agregada. Un escenario solo podrá incorporarse al repositorio público si fue reescrito, anonimizado y usted autoriza ese uso. El prototipo no emite prescripciones agronómicas.

Registrar únicamente:

- `participant_id`: código aleatorio como `P01`; nunca iniciales.
- rol: `asesor`, `productor`, `scout`, `otro`.
- experiencia en banda: `0-4`, `5-9`, `10-19`, `20+` años.
- zona amplia opcional: provincia o región; nunca localidad pequeña.
- `consent_aggregated_insights`: `yes/no`.
- `consent_sanitized_scenario`: `yes/no`.
- `consent_anonymous_quote`: `yes/no`.
- `recording_authorized`: `yes/no`; el valor por defecto es `no`.

Si cualquiera de los dos primeros consentimientos necesarios es `no`, no incorporar material al paquete.

## Datos prohibidos en el repositorio

- nombre, iniciales, correo, teléfono, usuario de mensajería o firma;
- establecimiento, empresa, cliente, contratista o matrícula;
- coordenadas, polígonos, rutas precisas o identificadores catastrales;
- fechas y horarios exactos vinculables a un evento privado;
- imágenes con rostros, patentes, marcas de agua, metadatos GPS o cartelería;
- rendimientos, costos, dosis, contratos o superficies exactas de una operación real;
- notas de voz o texto copiadas literalmente desde comunicaciones privadas;
- credenciales, tokens o identificadores de solicitudes.

## Transformación obligatoria

1. Trabajar con el insumo original fuera del repositorio, en un espacio controlado por el usuario.
2. Reescribir la situación; no pegar el texto original.
3. Sustituir lotes por IDs como `campo-sintetico-07`.
4. Redondear tiempos a horas relativas y superficies a bandas o porcentajes ficticios plausibles.
5. Eliminar coordenadas; los fixtures técnicos usan `0.0, 0.0` para señalar que no representan una ubicación real.
6. Generalizar combinaciones raras que permitan reidentificar el caso.
7. Ejecutar una revisión humana de privacidad independiente del autor.
8. Registrar solo `privacy_review_status: passed`, el ID del revisor y la fecha; nunca su identidad.

## Regla de citas

Las citas literales públicas están desactivadas por defecto. Aun con autorización, una cita debe revisarse para eliminar datos indirectamente identificables. Es preferible publicar una paráfrasis marcada como tal.

## Retiro y retención

Antes del freeze, un participante puede pedir retirar su material mediante su `participant_id`. Después del freeze público no puede garantizarse retirar copias de terceros; esto debe explicarse antes de aceptar uso público.

Los registros originales no deben versionarse. El proyecto conserva solamente formularios saneados y el resultado agregado necesario para reproducir el análisis.

## Checklist de privacidad

- [ ] Consentimiento registrado por alcance.
- [ ] No existe nombre o inicial.
- [ ] No existe establecimiento o cliente.
- [ ] No existe coordenada o ubicación precisa.
- [ ] No existe fecha privada exacta.
- [ ] El texto fue reescrito, no copiado.
- [ ] Se eliminaron metadatos de imágenes/archivos.
- [ ] Segunda revisión de privacidad aprobada.
