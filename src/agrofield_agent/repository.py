from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agrofield_agent.models import AnalysisResponse, AuditEvent, FieldRecord


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Repository:
    def __init__(self, database_path: Path, seed_path: Path | None = None) -> None:
        self.database_path = database_path
        self.seed_path = seed_path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS fields (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    field_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    analysis_id TEXT NOT NULL,
                    field_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    reviewer TEXT,
                    decision_note TEXT,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
        if not self.list_fields() and self.seed_path and self.seed_path.exists():
            seeds = json.loads(self.seed_path.read_text(encoding="utf-8"))
            with self.connect() as connection:
                for item in seeds:
                    field = FieldRecord.model_validate(item)
                    connection.execute(
                        "INSERT INTO fields (id, name, payload_json) VALUES (?, ?, ?)",
                        (field.id, field.name, field.model_dump_json()),
                    )
                connection.execute(
                    "INSERT INTO audit_events (event_type, entity_id, payload_json, created_at) VALUES (?, ?, ?, ?)",
                    ("demo_seeded", "workspace", json.dumps({"fields": len(seeds)}), _now()),
                )

    def list_fields(self) -> list[FieldRecord]:
        if not self.database_path.exists():
            return []
        with self.connect() as connection:
            rows = connection.execute("SELECT payload_json FROM fields ORDER BY name").fetchall()
        return [FieldRecord.model_validate_json(row["payload_json"]) for row in rows]

    def get_field(self, field_id: str) -> FieldRecord | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM fields WHERE id = ?", (field_id,)
            ).fetchone()
        return FieldRecord.model_validate_json(row["payload_json"]) if row else None

    def save_analysis(self, analysis: AnalysisResponse) -> None:
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO analyses (id, field_id, payload_json, created_at) VALUES (?, ?, ?, ?)",
                (analysis.id, analysis.field.id, analysis.model_dump_json(), analysis.created_at),
            )
            for task in analysis.proposed_tasks:
                connection.execute(
                    """INSERT INTO tasks
                    (id, analysis_id, field_id, payload_json, status, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        task.id,
                        analysis.id,
                        analysis.field.id,
                        task.model_dump_json(),
                        task.status,
                        analysis.created_at,
                    ),
                )
            connection.execute(
                "INSERT INTO audit_events (event_type, entity_id, payload_json, created_at) VALUES (?, ?, ?, ?)",
                (
                    "analysis_created",
                    analysis.id,
                    json.dumps(
                        {
                            "field_id": analysis.field.id,
                            "status": analysis.status,
                            "provider": analysis.telemetry.provider,
                            "missing_critical": analysis.missing_critical,
                        }
                    ),
                    analysis.created_at,
                ),
            )

    def decide_task(
        self, task_id: str, status: str, reviewer: str, decision_note: str
    ) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT payload_json, status FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
            if not row:
                return None
            if row["status"] != "pending":
                raise ValueError("Task has already been decided")
            payload = json.loads(row["payload_json"])
            payload["status"] = status
            updated_at = _now()
            connection.execute(
                """UPDATE tasks SET payload_json = ?, status = ?, reviewer = ?,
                decision_note = ?, updated_at = ? WHERE id = ?""",
                (json.dumps(payload), status, reviewer, decision_note, updated_at, task_id),
            )
            connection.execute(
                "INSERT INTO audit_events (event_type, entity_id, payload_json, created_at) VALUES (?, ?, ?, ?)",
                (
                    f"task_{status}",
                    task_id,
                    json.dumps({"reviewer": reviewer, "decision_note": decision_note}),
                    updated_at,
                ),
            )
        return payload

    def list_audit(self, limit: int = 50) -> list[AuditEvent]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM audit_events ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [
            AuditEvent(
                id=row["id"],
                event_type=row["event_type"],
                entity_id=row["entity_id"],
                payload=json.loads(row["payload_json"]),
                created_at=row["created_at"],
            )
            for row in rows
        ]
