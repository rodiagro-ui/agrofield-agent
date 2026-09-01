# Revisiones humanas

Directorio intencionalmente vacío de etiquetas humanas al 2026-09-01. El estado sigue siendo `NOT_AUTHORIZED` y hay 0 entrevistas, 0 referencias y 0 revisiones de salida reales.

No agregar nombres, iniciales, empleadores, establecimientos ni coordenadas. Cada archivo debe usar un `reviewer_id` aleatorio y seguir las plantillas de `../../templates/`.

Convención sugerida:

```text
case-annotations-R01.jsonl
case-annotations-R02.jsonl
output-reviews-R01.jsonl
output-reviews-R02.jsonl
adjudications.jsonl
interviews.jsonl
```

Una IA puede verificar formato, pero su salida no cuenta como revisión humana ni como adjudicación agronómica.

No copiar aquí las plantillas. Los registros estructuralmente incompletos son ignorados, contados como inválidos y bloquean el gate final. Los archivos Fase A (`case-annotations-*`) y Fase B (`output-reviews-*`) deben permanecer separados; cada salida se vincula al hash de la anotación Fase A del mismo revisor.
