# Controles de privacidad y manejo de datos

## Principio rector

Recolectar lo mínimo, separar identidad de contenido y hacer que el repositorio nunca necesite datos personales. Estos controles reducen riesgo; no constituyen una garantía jurídica absoluta ni asesoramiento legal.

La guía oficial argentina indica que, al tratar datos personales, deben informarse de forma clara finalidad, consecuencias, destinatarios y responsable, además de permitir el ejercicio de derechos. También recomienda que los datos sean adecuados, pertinentes, no excesivos y eliminados cuando dejan de ser necesarios. Fuentes: [derechos sobre datos personales — AAIP](https://www.argentina.gob.ar/aaip/datospersonales/derechos), [política de privacidad — AAIP](https://www.argentina.gob.ar/aaip/politica-de-privacidad-de-la-aaip), [Ley 25.326 actualizada](https://www.argentina.gob.ar/normativa/nacional/64790/actualizacion).

## Flujo permitido

```text
identidad/contacto ──> mapa privado del usuario ──X──> Git
                              │
                              └── ID aleatorio
                                      │
nota cruda privada ──> reescritura + minimización ──> revisión PR01
                                                        │
                                                        └── registro saneado en Git
```

## Inventario y ubicación

| Dato | Ubicación | Acceso | ¿Git? |
|---|---|---|---:|
| Nombre, contacto, consentimiento identificable | Espacio privado del custodio | `RC01`/`DS01` | No |
| Mapa identidad ↔ ID | Espacio privado separado | `DS01` | No |
| Nota cruda de entrevista | Espacio privado, sin audio por defecto | `F01`/`DS01` | No |
| Registro reescrito | Área de saneamiento | `DS01`/`PR01` | Solo tras `passed` |
| Anotación de caso sintético | Archivo por ID | Coordinador/revisor | Sí, tras control |
| Alias ↔ proveedor | Espacio privado del coordinador | Coordinador | No |
| Métricas agregadas/hashes | Repositorio | Equipo/público futuro | Sí |

La ruta ignorada `benchmark/agronomy_blind_v1/private/` es defensa adicional, no el almacenamiento recomendado. Los datos identificables deben mantenerse fuera del repositorio completo, no solo fuera del índice de Git.

## Minimización obligatoria

- IDs aleatorios; nunca iniciales.
- Rol y experiencia por banda.
- Región amplia opcional; omitir si vuelve singular a la persona.
- Frecuencia, tiempo y consecuencia por bandas.
- Sin nombres, establecimientos, clientes, empresas, matrículas ni contratistas.
- Sin coordenadas, polígonos, localidad pequeña, rutas o fechas privadas exactas.
- Sin superficies, rendimientos, costos, dosis o contratos reales exactos.
- Sin texto copiado de WhatsApp, email o audio.
- Sin imágenes o archivos con metadatos.
- Sin datos sensibles; si aparecen, detener y eliminar del registro de trabajo.

## Grabación y servicios externos

- Grabación por defecto: `NO`.
- Una grabación exige nueva autorización específica, finalidad, retención y ubicación.
- No usar transcripción automática, formularios públicos ni almacenamiento externo no declarado bajo el alcance inicial.
- Si se propone Zoom, Meet, Google Forms u otro proveedor, informar previamente destinatarios/transferencias y pedir autorización separada.

## Retención propuesta

- Contactos que rechazan o no responden: eliminar del registro operativo del estudio al cerrar la invitación, salvo agenda personal legítima del usuario fuera del proyecto.
- Mapa de IDs y notas crudas: eliminar 30 días después del freeze humano final o, si no hay freeze, a más tardar el 31/12/2026.
- Registros saneados: conservar solo para los alcances consentidos y versionar cualquier retiro previo al freeze.
- Grabaciones: no existen bajo el alcance recomendado.

El plazo exacto y el responsable se completan privadamente antes del contacto. Si una obligación aplicable exige otro plazo, detenerse y obtener asesoramiento competente.

## Retiro, acceso, rectificación y supresión

El custodio conserva el único mapa entre persona e ID para atender solicitudes. Antes del freeze, una persona puede retirar usos futuros y pedir corrección o supresión del material identificable/saneado asociado. Después de una publicación, no puede garantizarse eliminar copias de terceros; debe explicarse antes de consentir uso público.

## Revisión de privacidad en dos personas

1. `DS01` reescribe y minimiza.
2. `PR01`, distinto del autor, busca identificadores directos e indirectos.
3. Solo `privacy_review_status: passed` entra al repositorio.
4. `PR01` queda registrado por código y fecha, no por identidad.

## Control antes de cada commit

- Revisar manualmente `git diff --cached`.
- Confirmar que no hay archivos en rutas privadas ni nombres de contactos.
- Buscar emails, teléfonos, coordenadas y claves con herramientas locales; un escaneo automático no reemplaza la revisión humana.
- Verificar que cualquier cita sea paráfrasis o tenga consentimiento y saneamiento explícitos.
- Si hay duda de reidentificación, excluir el material.

## Incidente

Ante un dato real en Git o un paquete compartido incorrectamente:

1. detener distribución y nuevos commits;
2. identificar alcance sin copiar el dato a otros canales;
3. avisar al usuario/custodio;
4. retirar el archivo de la superficie compartida mediante un procedimiento autorizado;
5. evaluar notificación a la persona y obligaciones aplicables;
6. documentar el incidente sin reproducir el dato;
7. reanudar solo después de un nuevo control de privacidad.

No reescribir historia pública ni borrar material sin autorización y verificación exacta del objetivo.
