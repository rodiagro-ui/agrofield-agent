from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from agrofield_agent.config import Settings
from agrofield_agent.demo_provider import (
    DEMO_PROVIDER,
    DemoLimitReached,
    demo_provider_from_env,
)
from agrofield_agent.models import AnalysisRequest, ApprovalRequest
from agrofield_agent.nebius_smoke import (
    ContractViolation,
    UpstreamRequestFailure,
    provider_for_application,
)
from agrofield_agent.orchestrator import Orchestrator
from agrofield_agent.repository import Repository
from agrofield_agent.services.extraction import (
    ExtractionProvider,
    LocalExtractionProvider,
)
from agrofield_agent.services.tavily import TavilyAlertProvider


PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parents[1]


def create_app(
    settings: Settings | None = None,
    repository: Repository | None = None,
    extraction_provider: ExtractionProvider | None = None,
) -> FastAPI:
    settings = settings or Settings.from_env()
    repository = repository or Repository(
        settings.database_path, PACKAGE_ROOT / "data" / "fields.json"
    )
    repository.initialize()
    if extraction_provider is None:
        extraction_provider = (
            demo_provider_from_env(settings)
            if settings.provider == DEMO_PROVIDER
            else provider_for_application(settings)
        )
    alerts = TavilyAlertProvider(settings)
    orchestrator = Orchestrator(repository, extraction_provider, alerts)
    # Explicit, user-requested and labeled by its telemetry; never a silent fallback.
    local_orchestrator = Orchestrator(repository, LocalExtractionProvider(), alerts)

    app = FastAPI(
        title="AgroField Agent",
        version="0.1.0",
        description="Post-event soybean scouting evidence coordinator",
    )
    app.mount("/static", StaticFiles(directory=PACKAGE_ROOT / "static"), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def index() -> str:
        return (PACKAGE_ROOT / "templates" / "index.html").read_text(encoding="utf-8")

    @app.get("/health")
    async def health() -> dict[str, str | bool]:
        return {
            "status": "ok",
            "provider": settings.provider,
            "tavily_configured": bool(settings.tavily_api_key),
            "recording_mode": settings.recording_mode,
        }

    @app.get("/api/runtime")
    async def runtime() -> dict:
        """Public, credential-free description of the extraction engine in use."""
        budget = getattr(extraction_provider, "budget", None)
        return {
            "provider": settings.provider,
            "model": settings.nebius_model if settings.provider != "local"
            else "deterministic-es-v0.1",
            "nemotron_runtime": settings.provider != "local",
            "demo_budget": budget() if callable(budget) else None,
        }

    @app.get("/api/fields")
    async def fields():
        return repository.list_fields()

    @app.get("/api/fields/{field_id}")
    async def field(field_id: str):
        item = repository.get_field(field_id)
        if not item:
            raise HTTPException(status_code=404, detail="Unknown field")
        return item

    @app.post("/api/analyze")
    async def analyze(
        request: AnalysisRequest,
        engine: Literal["default", "local"] = Query(default="default"),
    ):
        chosen = local_orchestrator if engine == "local" else orchestrator
        try:
            return await chosen.analyze(
                request.field_id, request.raw_text, request.use_tavily
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Unknown field") from exc
        except DemoLimitReached as exc:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": str(exc),
                    "failure_code": exc.code,
                    "automatic_retry": False,
                    "local_engine_available": True,
                },
            )
        except (ContractViolation, UpstreamRequestFailure) as exc:
            return JSONResponse(
                status_code=503,
                content={
                    "detail": str(exc),
                    "failure_code": exc.code,
                    "safe_diagnostics": exc.diagnostics,
                    "automatic_retry": False,
                },
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.post("/api/tasks/{task_id}/approve")
    async def approve(task_id: str, request: ApprovalRequest):
        try:
            task = repository.decide_task(
                task_id, "approved", request.reviewer, request.decision_note
            )
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        if not task:
            raise HTTPException(status_code=404, detail="Unknown task")
        return task

    @app.post("/api/tasks/{task_id}/reject")
    async def reject(task_id: str, request: ApprovalRequest):
        try:
            task = repository.decide_task(
                task_id, "rejected", request.reviewer, request.decision_note
            )
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        if not task:
            raise HTTPException(status_code=404, detail="Unknown task")
        return task

    @app.get("/api/audit")
    async def audit(limit: int = Query(default=30, ge=1, le=200)):
        return repository.list_audit(limit)

    return app


app = create_app()
