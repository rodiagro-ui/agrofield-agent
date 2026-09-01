from pathlib import Path

import pytest

from agrofield_agent.repository import Repository


def test_task_can_only_be_decided_once(tmp_path: Path):
    repo = Repository(tmp_path / "db.sqlite3")
    repo.initialize()
    with repo.connect() as connection:
        connection.execute(
            "INSERT INTO tasks (id, analysis_id, field_id, payload_json, status, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("t1", "a1", "f1", '{"id":"t1","status":"pending"}', "pending", "now"),
        )
    decided = repo.decide_task("t1", "approved", "Ana", "Revisado")
    assert decided["status"] == "approved"
    with pytest.raises(ValueError):
        repo.decide_task("t1", "rejected", "Ana", "Cambio")
