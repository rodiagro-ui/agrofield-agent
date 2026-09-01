from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from agrofield_agent.config import Settings
from agrofield_agent.models import FieldRecord, OfficialAlert, StructuredObservation


@dataclass
class TavilyAlertProvider:
    settings: Settings

    async def search(
        self, field: FieldRecord, observation: StructuredObservation
    ) -> list[OfficialAlert]:
        if not self.settings.tavily_api_key or observation.event_type == "none":
            return []
        query = (
            f"alerta oficial reciente soja {observation.event_type} "
            "monitoreo de lotes Argentina"
        )
        payload = {
            "query": query,
            "search_depth": "basic",
            "max_results": 3,
            "topic": "general",
            "country": "argentina",
            "time_range": "month",
            "include_answer": False,
            "include_domains": list(self.settings.tavily_include_domains),
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://api.tavily.com/search",
                headers={"Authorization": f"Bearer {self.settings.tavily_api_key}"},
                json=payload,
            )
            response.raise_for_status()
        alerts: list[OfficialAlert] = []
        for item in response.json().get("results", []):
            host = (urlparse(item.get("url", "")).hostname or "").lower()
            if not any(
                host == allowed or host.endswith(f".{allowed}")
                for allowed in self.settings.tavily_include_domains
            ):
                continue
            score = item.get("score")
            if score is not None and score < 0.5:
                continue
            alerts.append(
                OfficialAlert(
                    title=item.get("title", "Alerta oficial"),
                    url=item["url"],
                    snippet=item.get("content", "")[:700],
                    published_date=item.get("published_date"),
                    score=score,
                )
            )
        return alerts
