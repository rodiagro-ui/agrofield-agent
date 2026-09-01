# Dataset card — conjunto candidato

## Estado

- Versión: `1.0.0-candidate`
- Casos: 30
- Desarrollo: 20
- Holdout: 10
- Doble revisión requerida: 10
- Casos vinculados al fixture original: 12
- Casos nuevos: 18
- Revisiones humanas completadas: **0**

El archivo `cases.jsonl` es un conjunto sintético para preparar y probar el protocolo. No es todavía el benchmark agronómico congelado.

## Cobertura intencional

- anegamiento, granizo, viento, eventos mixtos y ausencia explícita de daño;
- omisión de estado, muestreo, duración, área y seguridad;
- acceso inseguro y estimaciones desde camino/entrada;
- coma decimal, números en palabras y conversión días→horas;
- negaciones, ceros explícitos, contradicciones y autocorrecciones orales;
- atribución de porcentajes a área, vuelco, tallos y agua;
- intento de prompt injection y autoridad falsa;
- metadata que no debe completar una observación ausente;
- notas completas y casos con múltiples omisiones.

## Split

`bfv1-001` a `bfv1-020` forman desarrollo. `bfv1-021` a `bfv1-030` forman el holdout candidato.

Casos prefijados para doble revisión:

`bfv1-003`, `bfv1-007`, `bfv1-011`, `bfv1-014`, `bfv1-016`, `bfv1-019`, `bfv1-023`, `bfv1-025`, `bfv1-028`, `bfv1-030`.

El coordinador debe ocultar el split en los paquetes mostrados a revisores.

## Privacidad

Todos los escenarios fueron escritos como ficción. Los nombres siguen el patrón `Campo sintético NNN`; superficie y clima son ficticios; `0.0, 0.0` es un sentinel técnico y no una ubicación agronómica. No hay textos copiados de comunicaciones, nombres, empresas o establecimientos.

Antes de publicar, se debe volver a ejecutar el control de privacidad y considerar hacer opcionales las coordenadas en el esquema para eliminar incluso el sentinel.

## Referencia candidata

`candidate_reference` es una anotación provisional del equipo que permite desarrollar el evaluador. No equivale a ground truth. Debe reemplazarse por referencia adjudicada a partir de revisiones humanas, preservando la referencia candidata para auditar cambios.

## Amenazas a la validez

1. Los autores del sistema también diseñaron los candidatos.
2. El lenguaje puede favorecer o castigar patrones conocidos del extractor local.
3. El holdout está visible y no es secreto; su protección es procedimental.
4. Los criterios de prioridad todavía no fueron calibrados con consecuencias reales.
5. Las fuentes técnicas orientan la plausibilidad, pero no validan etiquetas individuales.

Por estas razones, cualquier métrica calculada antes de la revisión debe incluir `reference_status: provisional_candidate_reference`.

## Fuentes orientativas

- [Iowa State — Crop Scouting Basics](https://crops.extension.iastate.edu/encyclopedia/crop-scouting-basics)
- [Iowa State — Early Season Hail Damage](https://crops.extension.iastate.edu/post/early-season-hail-damage)
- [Nebraska Extension — Flooding and Ponding in Soybeans](https://cropwatch.unl.edu/2018/flooding-and-ponding-soybeans/)
- [Nebraska Extension — Survival in Saturated and Flooded Soils](https://cropwatch.unl.edu/corn-and-soybean-survival-saturated-and-flooded-soils/)

Estas fuentes no deben usarse para inferir presencia, rendimiento o tratamiento en un caso individual.
