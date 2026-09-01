from __future__ import annotations

from uuid import uuid4

from agrofield_agent.models import FieldRecord, StructuredObservation, TaskProposal


QUESTION_BY_FIELD = {
    "crop_stage": "¿Confirmás el estado fenológico de la soja (por ejemplo V3 o R1)?",
    "event_type": "¿El evento fue lluvia/anegamiento, granizo, viento o una combinación?",
    "event_hours_ago": "¿Cuántas horas pasaron desde el evento?",
    "access_safe": "¿El acceso al lote es seguro y transitable?",
    "sample_points": "¿Cuántos puntos representativos recorriste y con qué patrón?",
    "affected_area_pct": "¿Qué porcentaje aproximado del lote está afectado?",
    "standing_water_pct": "¿Qué porcentaje conserva agua parada?",
    "water_duration_hours": "¿Cuántas horas lleva el cultivo con agua parada o suelo saturado?",
    "lodging_pct": "¿Qué porcentaje presenta vuelco o acame?",
    "stem_damage_pct": "¿Qué porcentaje de plantas tiene tallos quebrados, cortados o golpeados?",
    "stand_count_per_m": "¿Cuál fue el stand en plantas por metro en varios puntos?",
}


def critical_fields(observation: StructuredObservation) -> list[str]:
    common = [
        "crop_stage",
        "event_type",
        "event_hours_ago",
        "access_safe",
        "sample_points",
        "affected_area_pct",
    ]
    raw = observation.raw_text.lower()
    mixed_has_flooding = observation.event_type == "mixed" and any(
        token in raw for token in ("aneg", "agua parada", "inund", "encharc")
    )
    mixed_has_physical_damage = observation.event_type == "mixed" and any(
        token in raw for token in ("granizo", "pedrada", "viento", "volcado", "acame", "tumbad")
    )
    if observation.event_type == "flooding" or mixed_has_flooding:
        common.extend(["standing_water_pct", "water_duration_hours", "stand_count_per_m"])
    if observation.event_type in {"hail", "wind"} or mixed_has_physical_damage:
        common.extend(["lodging_pct", "stem_damage_pct", "stand_count_per_m"])
    return list(dict.fromkeys(common))


def missing_critical_fields(observation: StructuredObservation) -> list[str]:
    missing: list[str] = []
    for name in critical_fields(observation):
        value = getattr(observation, name)
        if value is None or (name == "event_type" and value == "unknown"):
            missing.append(name)
    return missing


def _weather_number(field: FieldRecord, key: str) -> float:
    value = field.weather.get(key)
    return float(value) if isinstance(value, (int, float)) else 0.0


def priority(field: FieldRecord, observation: StructuredObservation) -> tuple[float, list[str]]:
    score = 10.0
    reasons: list[str] = []
    if observation.event_hours_ago is not None:
        recency = max(0.0, 20.0 - observation.event_hours_ago / 3)
        score += recency
        reasons.append(f"Evento reciente: hace {observation.event_hours_ago:g} h.")
    if observation.affected_area_pct is not None:
        contribution = min(25.0, observation.affected_area_pct * 0.35)
        score += contribution
        reasons.append(f"Área afectada declarada: {observation.affected_area_pct:g}%.")
    if observation.water_duration_hours is not None:
        score += min(18.0, observation.water_duration_hours * 0.6)
        reasons.append(f"Agua/saturación declarada durante {observation.water_duration_hours:g} h.")
    damage = max(observation.lodging_pct or 0, observation.stem_damage_pct or 0)
    if damage:
        score += min(18.0, damage * 0.3)
        reasons.append(f"Daño físico máximo observado: {damage:g}%.")
    rain = _weather_number(field, "precipitation_mm_72h")
    if rain:
        score += min(10.0, rain / 20)
        reasons.append(f"Lluvia contextual de 72 h: {rain:g} mm.")
    if field.risk_flags:
        score += min(10.0, len(field.risk_flags) * 4)
        reasons.append("Antecedentes: " + "; ".join(field.risk_flags) + ".")
    if observation.access_safe is False:
        score = max(score, 92.0)
        reasons.insert(0, "Acceso inseguro: escalar sin ingresar al lote.")
    return round(min(score, 100.0), 1), reasons


def propose_tasks(
    field: FieldRecord,
    observation: StructuredObservation,
    missing: list[str],
    score: float,
) -> list[TaskProposal]:
    if observation.access_safe is False:
        return [
            TaskProposal(
                id=str(uuid4()),
                title=f"Escalar acceso inseguro en {field.name}",
                priority="urgent",
                due_hours=1,
                rationale="No continuar la recorrida hasta que una persona responsable confirme condiciones seguras.",
            )
        ]
    if missing:
        return [
            TaskProposal(
                id=str(uuid4()),
                title=f"Completar {len(missing)} controles críticos en {field.name}",
                priority="high" if score >= 60 else "medium",
                due_hours=6 if score >= 60 else 24,
                rationale="La evidencia actual no permite cerrar la revisión sin inventar datos.",
            )
        ]

    tasks = [
        TaskProposal(
            id=str(uuid4()),
            title=f"Revisar evidencia post-evento de {field.name}",
            priority="urgent" if score >= 80 else "high" if score >= 60 else "medium",
            due_hours=2 if score >= 80 else 8 if score >= 60 else 24,
            rationale="Paquete completo listo para revisión del asesor; no implica tratamiento automático.",
        )
    ]
    if observation.event_type in {"hail", "mixed"}:
        tasks.append(
            TaskProposal(
                id=str(uuid4()),
                title=f"Programar control de rebrote en {field.name}",
                priority="medium",
                due_hours=120,
                rationale="El daño por granizo requiere una evaluación diferida del rebrote antes de decisiones irreversibles.",
            )
        )
    elif observation.event_type == "flooding":
        tasks.append(
            TaskProposal(
                id=str(uuid4()),
                title=f"Revisar persistencia de agua en {field.name}",
                priority="high" if (observation.water_duration_hours or 0) >= 24 else "medium",
                due_hours=12,
                rationale="Actualizar duración y extensión del anegamiento con la misma referencia de muestreo.",
            )
        )
    return tasks


def evaluate_policy(
    field: FieldRecord, observation: StructuredObservation
) -> tuple[str, list[str], list[str], float, list[str], list[TaskProposal]]:
    missing = missing_critical_fields(observation)
    score, rationale = priority(field, observation)
    questions = [QUESTION_BY_FIELD[name] for name in missing]
    status = "blocked" if missing else "review_ready"
    tasks = propose_tasks(field, observation, missing, score)
    return status, missing, questions, score, rationale, tasks
