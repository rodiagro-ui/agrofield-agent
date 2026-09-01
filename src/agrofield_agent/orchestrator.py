from __future__ import annotations

from uuid import uuid4

from agrofield_agent.models import AnalysisResponse, StructuredObservation
from agrofield_agent.policy import evaluate_policy
from agrofield_agent.repository import Repository
from agrofield_agent.services.extraction import ExtractionProvider
from agrofield_agent.services.tavily import TavilyAlertProvider


class Orchestrator:
    def __init__(
        self,
        repository: Repository,
        extractor: ExtractionProvider,
        alerts: TavilyAlertProvider,
    ) -> None:
        self.repository = repository
        self.extractor = extractor
        self.alerts = alerts

    async def analyze(
        self, field_id: str, raw_text: str, use_tavily: bool = False
    ) -> AnalysisResponse:
        field = self.repository.get_field(field_id)
        if not field:
            raise KeyError(field_id)
        draft, telemetry = await self.extractor.extract(raw_text)
        observation = StructuredObservation(
            **draft.model_dump(),
            field_id=field_id,
            raw_text=raw_text,
            provider=telemetry.provider,
        )
        status, missing, questions, score, rationale, tasks = evaluate_policy(
            field, observation
        )
        official_alerts = await self.alerts.search(field, observation) if use_tavily else []
        if official_alerts:
            rationale.append(
                f"{len(official_alerts)} alerta(s) oficial(es) reciente(s) para revisar; no prueban presencia en el lote."
            )
            score = min(100.0, round(score + 3, 1))
        analysis = AnalysisResponse(
            id=str(uuid4()),
            field=field,
            observation=observation,
            status=status,
            missing_critical=missing,
            followup_questions=questions,
            priority_score=score,
            rationale=rationale,
            proposed_tasks=tasks,
            official_alerts=official_alerts,
            telemetry=telemetry,
        )
        self.repository.save_analysis(analysis)
        return analysis
