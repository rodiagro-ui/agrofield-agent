from pathlib import Path

from fastapi.testclient import TestClient

from agrofield_agent.app import PROJECT_ROOT, create_app
from agrofield_agent.config import Settings
from agrofield_agent.repository import Repository


def test_api_vertical_slice(tmp_path: Path):
    settings = Settings(
        provider="local",
        database_path=tmp_path / "test.sqlite3",
        nebius_api_key=None,
        nebius_base_url="https://example.invalid/v1",
        nebius_model="test",
        tavily_api_key=None,
        tavily_include_domains=("inta.gob.ar",),
    )
    repository = Repository(settings.database_path, PROJECT_ROOT / "fixtures" / "fields.json")
    client = TestClient(create_app(settings, repository))
    assert client.get("/health").json() == {
        "status": "ok",
        "provider": "local",
        "tavily_configured": False,
    }
    fields = client.get("/api/fields").json()
    assert len(fields) == 4
    response = client.post(
        "/api/analyze",
        json={
            "field_id": "lote-bajo",
            "raw_text": "Soja V3. Tormenta hace 18 horas, acceso seguro. Hay agua parada en 35% del lote.",
            "use_tavily": False,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "blocked"
    assert "sample_points" in body["missing_critical"]
    task = body["proposed_tasks"][0]
    approved = client.post(
        f"/api/tasks/{task['id']}/approve",
        json={"reviewer": "Asesor demo", "decision_note": "Completar muestreo"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
