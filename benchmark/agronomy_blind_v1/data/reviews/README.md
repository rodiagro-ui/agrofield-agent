# Revisiones humanas

Directorio intencionalmente vacío de etiquetas humanas al 2026-09-02. El contacto por correo está `AUTHORIZED_EMAIL_ONLY_PENDING_PRIVATE_SETUP`, pero todavía hay 0 personas contactadas, 0 entrevistas, 0 referencias, 0 revisiones de salida y 0 adjudicaciones reales. La autorización no convierte ninguna plantilla o fixture en evidencia humana.

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
