# Paquete de entrevistas por correo — trabajo de campo V1

> **Estado:** borrador local listo. No enviar hasta confirmar el alcance de evidencia de cada participante. Solo el usuario humano envía y custodia respuestas. Este archivo no autoriza llamadas, grabaciones, publicación ni servicios pagos.

## Gate anterior al primer cuestionario

Para cada persona, el custodio verifica privadamente:

1. consentimiento escrito obligatorio válido;
2. `consent_aggregated_insights: true`;
3. `consent_sanitized_scenario: true`;
4. ningún retiro posterior;
5. código privado aleatorio asignado, sin iniciales.

Una persona puede participar aunque rechace un uso opcional, pero su entrevista no debe incorporarse al benchmark si faltan los alcances 2 o 3 exigidos por el evaluador. No enviar a la IA la matriz individual de consentimientos.

El diseño usa dos correos para mantener el orden neutral: primero el episodio real y sus contraejemplos; solo después se presenta el concepto. Enviar uno a uno, sin CC/CCO grupal y sin adjuntos.

## Correo A — episodio y proceso, sin presentar AgroField

**Asunto:** Entrevista escrita — recorrida posterior a un evento meteorológico

```text
Hola:

Gracias por participar. Esta es la primera parte de la entrevista escrita. Busco comprender un episodio real y el proceso de trabajo; todavía no voy a presentar el prototipo.

Por favor, respondé debajo de cada número con tus propias palabras. Para proteger la privacidad, no incluyas nombres de personas, clientes, empresas o establecimientos; coordenadas o localidades pequeñas; fechas exactas; superficies, rendimientos, costos, dosis o contratos exactos; ni copies mensajes privados. Podés usar roles y rangos, omitir cualquier pregunta o retirarte.

1. Pensá en la última mañana posterior a lluvia fuerte, granizo o viento en la que hubo que decidir qué lotes revisar. ¿Qué ocurrió desde el primer aviso hasta que se tomó o postergó una decisión?

2. ¿Qué rol detectó el evento, quién observó en campo y qué rol decidió el orden de recorrida? No indiques nombres.

3. ¿Qué información ya existía antes de salir y por qué canales llegó? ¿Qué dato faltó, llegó ambiguo o hubo que confirmar?

4. ¿Cómo comprobaron que la observación representaba al lote y no solamente a la entrada o a un punto problemático? Indicá recorrida, cantidad aproximada de puntos o tipo de medición, usando rangos.

5. ¿Qué decisión se postergó y por qué? ¿Fue necesario pedir otro mensaje, regresar al lote o enviar a otra persona?

6. ¿Qué registro quedó después y quién podía auditarlo por rol?

7. Elegí una opción por línea:
   - frecuencia: casi nunca / algunas veces por campaña / mensualmente en campaña / semanalmente en campaña;
   - consecuencia habitual de un dato faltante: solo otro mensaje / más de 30 minutos / recorrida extra / riesgo de decisión prematura / otra;
   - personas que suelen intervenir: 1 / 2–3 / 4+.

8. ¿Qué observaciones son indispensables después de anegamiento? ¿Y después de granizo o viento? ¿Qué dato nunca debería inferirse si nadie lo observó?

9. ¿Qué hace que un lote tenga prioridad sobre otro? ¿Qué información externa reciente podría cambiar el orden de visita sin demostrar por sí sola qué ocurre dentro del lote?

10. Contame un contraejemplo: ¿cuándo este problema no existe, el proceso actual alcanza o una herramienta nueva agregaría más fricción que valor?

No hace falta responder todo en una sola sesión. No enviar fotos, audios ni documentos.

[FIRMA PRIVADA DEL USUARIO]
```

## Clarificación neutral opcional

Después de recibir el Correo A puede enviarse una sola ronda de aclaraciones. Usar preguntas como:

```text
Gracias. Para entender el proceso sin completar información por mi cuenta:

- Cuando decís “[PARÁFRASIS BREVE]”, ¿qué ocurrió inmediatamente después?
- ¿Cómo supieron eso y qué evidencia quedó?
- ¿Podés expresarlo como rango o categoría, sin datos identificables?
- ¿Recordás un caso en que ocurrió lo contrario?

No incluyas nombres, ubicaciones precisas, cifras comerciales exactas ni mensajes copiados.
```

No sugerir una respuesta, no corregir agronomía y no mencionar métricas, alertas, IA o bloqueos en esta etapa.

## Correo B — prueba neutral del concepto

Enviar solo después de cerrar el Correo A y cualquier aclaración.

**Asunto:** Entrevista escrita — segunda y última parte

```text
Hola:

Gracias. Esta es la segunda y última parte.

Concepto neutral: un sistema estructura una nota de recorrida, muestra la frase que respalda cada dato, pregunta por controles faltantes, ordena tareas y exige aprobación humana antes de una decisión. No diagnostica ni prescribe.

1. ¿Qué parte sería útil y por qué?
2. ¿Qué parte sería inútil, molesta o duplicaría algo que ya funciona?
3. ¿En qué situación un bloqueo por información faltante sería incorrecto?
4. ¿Qué error destruiría tu confianza en el sistema?
5. ¿Qué tendría que medir una prueba para que consideres creíble el resultado?
6. ¿En qué superficie de trabajo tendría más sentido: campo, escritorio, correo o mensajería? ¿Por qué?
7. Si este problema no merece una herramienta nueva, ¿cuál es la razón principal?

Mantené las mismas precauciones de privacidad de la primera parte. No enviar fotos, audios, documentos ni datos identificables.

[FIRMA PRIVADA DEL USUARIO]
```

## Saneamiento y revisión privada

Por cada entrevista completada:

1. conservar correos y mapa de identidad únicamente en el espacio privado declarado;
2. asignar `P01`–`P05` sin relación visible con nombre o iniciales;
3. `DS01` reescribe y resume; nunca copia frases de los correos;
4. usar bandas de experiencia, frecuencia, consecuencia y cantidad de personas;
5. eliminar organizaciones, localidades pequeñas, fechas exactas y combinaciones singulares;
6. `PR01`, distinto de `DS01`, realiza la segunda revisión;
7. solo con `privacy_review_status: passed` crear el JSON saneado;
8. ejecutar el escaneo de privacidad antes de incorporar cualquier archivo al repositorio.

El JSON debe seguir `../templates/interview-record.template.json`. `workflow_summary`, `missing_information_summary` y `counterevidence_summary` deben ser resúmenes sustantivos reescritos. Una respuesta vacía, una cita copiada o una plantilla sin completar no cuenta.

## Parte saneado posterior

No compartir respuestas crudas. Informar únicamente:

```text
ENTREVISTAS V1 — ACTUALIZACIÓN SANEADA. No comparto PII.
Correo A completado: [0–5]/5.
Correo B completado: [0–5]/5.
Entrevistas retiradas o no utilizables: [conteo].
Registros saneados por DS01: [conteo].
Registros aprobados por PR01: [conteo].
Roles agregados: asesor [n], productor [n], scout [n], otro [n].
Bandas de experiencia agregadas: 0–4 [n], 5–9 [n], 10–19 [n], 20+ [n].
PII enviada a la IA o Git: 0.
Notas o citas crudas enviadas a la IA o Git: 0.
```

Las entrevistas siguen siendo exploratorias; cinco respuestas no constituyen una muestra representativa. No afirmar impacto, ahorro o adopción sin medición independiente.
