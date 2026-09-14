# Nebius live `/api/analyze` smoke — 2026-09-14

> Resultado: `LIVE_ROUTE_ONE_CONTRACT_VALIDATION_FAIL` (`event_type` evidence quote no literal)

Este registro documenta un intento real y controlado a través de la ruta de la
aplicación. No es una extracción Nemotron aceptada, no es una evaluación y no
demuestra inferencia completa; sí muestra que el flujo alcanzó el parser de
contrato y falló en una validación estricta de evidencias.

## Autorización y controles previos

El usuario autorizó exactamente:

- una solicitud API de AgroField, sin reintentos;
- el modelo `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`;
- hasta US$0,01 de crédito promocional y US$0 de cargo personal;
- crear y revocar una clave temporal solo para esta prueba;
- detenerse si faltaba crédito o aparecía un cobro;
- `STOP usage` activo.

Antes de ejecutar, la interfaz autenticada de Token Factory mostró:

- precio de Nano: US$0,06 por millón de tokens de entrada y US$0,24 por millón
  de salida;
- trial: US$1,00 disponible y 29 días restantes;
- saldo de cuenta: US$0,00;
- fallback post-trial: `Usage stops after the trial`.

El preflight conservador del perfil calculó US$0,00122880, por debajo del cap.
La clave temporal se inyectó en el entorno del proceso servidor y no se escribió
en `.env`, archivos, logs de la aplicación ni Git. Su valor sí quedó visible en
la sesión privada de automatización al copiarlo desde la interfaz; por eso la
revocación posterior era obligatoria. Tavily permaneció desactivado.

## Ejecución

Se inició el FastAPI real de AgroField en `127.0.0.1:8000` con:

- `AGROFIELD_PROVIDER=nebius`;
- Nano, 1.024 tokens máximos de salida y presupuesto conservador de 16.384
  tokens de prompt;
- `reasoning_effort: none` y pensamiento desactivado;
- herramienta obligatoria, una solicitud máxima por proceso y cero reintentos;
- SQLite temporal y una nota exclusivamente sintética;
- `use_tavily: false`.

El cliente local envió un único `POST /api/analyze`. La ruta respondió HTTP 503:

```json
{"detail":"non-literal evidence quote for: event_type"}
```

El estado indica que hubo un intento de salida modelada contra el contrato local:

- se alcanzó el validador de contrato;
- el modelo (o la infraestructura) devolvió un `event_type` sin cita literal;
- no se emitió un `ObservationDraft` válido para medir calidad.

No se obtuvo salida evaluable del `ObservationDraft`, ni uso de tokens detallado
ni costo estimado utilizable para benchmark en esa corrida.

## Limpieza y observaciones posteriores

Después del único intento:

- se cerró el proceso servidor y se comprobó que el puerto 8000 ya no escuchaba;
- se eliminó la base SQLite temporal;
- se limpió el portapapeles;
- se revocó la clave temporal con confirmación del usuario;
- la interfaz mostró vacía la lista de API keys;
- la consulta de uso inmediata no mostró cargo visible y mantuvo el trial
  `US$1,00` y saldo `US$0,00`.

La consulta de uso puede sufrir demora o redondeo; no demuestra cobro exacto cero,
sino ausencia de cargo visible inmediato.

## Estado de la autorización

La autorización de esta solicitud fue consumida. No queda autorización para otra
llamada de Nemotron ni de Tavily, ni para repetir la ruta real, hasta que el
usuario autorice explícitamente un nuevo presupuesto y una nueva clave.
