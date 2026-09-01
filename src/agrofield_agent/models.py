from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


EventType = Literal["flooding", "hail", "wind", "mixed", "none", "unknown"]


class FieldRecord(BaseModel):
    id: str
    name: str
    hectares: float
    crop: str = "soja"
    stage: str | None = None
    latitude: float
    longitude: float
    history: list[dict[str, Any]] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    weather: dict[str, Any] = Field(default_factory=dict)


class ObservationDraft(BaseModel):
    crop_stage: str | None = Field(
        default=None, description="Etapa fenológica explícita, por ejemplo V3 o R1"
    )
    event_type: EventType = "unknown"
    event_hours_ago: float | None = None
    access_safe: bool | None = None
    sample_points: int | None = None
    affected_area_pct: float | None = Field(default=None, ge=0, le=100)
    standing_water_pct: float | None = Field(default=None, ge=0, le=100)
    water_duration_hours: float | None = Field(default=None, ge=0)
    lodging_pct: float | None = Field(default=None, ge=0, le=100)
    stem_damage_pct: float | None = Field(default=None, ge=0, le=100)
    stand_count_per_m: float | None = Field(default=None, ge=0)
    general_condition: Literal["critical", "poor", "mixed", "good", "unknown"] = (
        "unknown"
    )
    notes: list[str] = Field(default_factory=list)
    evidence_quotes: dict[str, str] = Field(
        default_factory=dict,
        description="Fragmento literal que respalda cada campo no nulo",
    )
    uncertainties: list[str] = Field(default_factory=list)


class StructuredObservation(ObservationDraft):
    field_id: str
    raw_text: str
    provider: str


class ProviderTelemetry(BaseModel):
    provider: str
    model: str
    latency_ms: float
    input_tokens: int | None = None
    output_tokens: int | None = None
    request_id: str | None = None


class OfficialAlert(BaseModel):
    title: str
    url: str
    snippet: str
    published_date: str | None = None
    score: float | None = None


class TaskProposal(BaseModel):
    id: str
    title: str
    priority: Literal["urgent", "high", "medium", "low"]
    due_hours: int
    rationale: str
    requires_approval: bool = True
    status: Literal["pending", "approved", "rejected"] = "pending"


class AnalysisRequest(BaseModel):
    field_id: str
    raw_text: str = Field(min_length=5, max_length=8000)
    use_tavily: bool = False


class AnalysisResponse(BaseModel):
    id: str
    field: FieldRecord
    observation: StructuredObservation
    status: Literal["blocked", "review_ready"]
    missing_critical: list[str]
    followup_questions: list[str]
    priority_score: float
    rationale: list[str]
    proposed_tasks: list[TaskProposal]
    official_alerts: list[OfficialAlert]
    telemetry: ProviderTelemetry
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ApprovalRequest(BaseModel):
    reviewer: str = Field(min_length=2, max_length=120)
    decision_note: str = Field(default="", max_length=1000)


class AuditEvent(BaseModel):
    id: int
    event_type: str
    entity_id: str
    payload: dict[str, Any]
    created_at: str
