from agrofield_agent.models import FieldRecord, StructuredObservation
from agrofield_agent.policy import evaluate_policy


FIELD = FieldRecord(
    id="x",
    name="Lote X",
    hectares=50,
    crop="soja",
    stage="V3",
    latitude=-33,
    longitude=-62,
    risk_flags=["drenaje lento"],
    weather={"precipitation_mm_72h": 120},
)


def observation(**overrides):
    data = dict(
        field_id="x",
        raw_text="nota",
        provider="local",
        crop_stage="V3",
        event_type="flooding",
        event_hours_ago=12,
        access_safe=True,
        sample_points=6,
        affected_area_pct=30,
        standing_water_pct=30,
        water_duration_hours=10,
        stand_count_per_m=11,
    )
    data.update(overrides)
    return StructuredObservation(**data)


def test_complete_observation_is_review_ready():
    status, missing, questions, score, reasons, tasks = evaluate_policy(FIELD, observation())
    assert status == "review_ready"
    assert missing == []
    assert questions == []
    assert score > 40
    assert tasks and all(task.requires_approval for task in tasks)


def test_missing_duration_blocks_decision():
    status, missing, questions, *_ = evaluate_policy(
        FIELD, observation(water_duration_hours=None)
    )
    assert status == "blocked"
    assert "water_duration_hours" in missing
    assert any("Cuántas horas" in question for question in questions)


def test_unsafe_access_forces_urgent_escalation():
    *_, score, reasons, tasks = evaluate_policy(
        FIELD, observation(access_safe=False, sample_points=None)
    )
    assert score >= 92
    assert tasks[0].priority == "urgent"
    assert "inseguro" in tasks[0].title.lower()


def test_wind_and_hail_mix_does_not_require_water_evidence():
    mixed = observation(
        raw_text="Viento y granizo con vuelco",
        event_type="mixed",
        standing_water_pct=None,
        water_duration_hours=None,
        lodging_pct=20,
        stem_damage_pct=5,
    )
    status, missing, *_ = evaluate_policy(FIELD, mixed)
    assert status == "review_ready"
    assert "water_duration_hours" not in missing
