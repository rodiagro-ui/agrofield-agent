from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    provider: str
    database_path: Path
    nebius_api_key: str | None
    nebius_base_url: str
    nebius_model: str
    tavily_api_key: str | None
    tavily_include_domains: tuple[str, ...]

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        domains = os.getenv(
            "TAVILY_INCLUDE_DOMAINS",
            "inta.gob.ar,smn.gob.ar,senasa.gob.ar,crops.extension.iastate.edu,extension.umn.edu",
        )
        return cls(
            provider=os.getenv("AGROFIELD_PROVIDER", "local").lower(),
            database_path=Path(os.getenv("AGROFIELD_DB_PATH", "agrofield.sqlite3")),
            nebius_api_key=os.getenv("NEBIUS_API_KEY") or None,
            nebius_base_url=os.getenv(
                "NEBIUS_BASE_URL",
                "https://api.tokenfactory.us-central1.nebius.com/v1",
            ).rstrip("/"),
            nebius_model=os.getenv(
                "NEBIUS_MODEL", "nvidia/nemotron-3-super-120b-a12b"
            ),
            tavily_api_key=os.getenv("TAVILY_API_KEY") or None,
            tavily_include_domains=tuple(
                item.strip().lower() for item in domains.split(",") if item.strip()
            ),
        )
