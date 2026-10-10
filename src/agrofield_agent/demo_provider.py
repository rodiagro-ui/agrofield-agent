"""Budgeted Nemotron provider for a public demo; never enabled by default.

Every note still goes through the guarded single-request contract (one POST, no
retry, closed schema, literal evidence). This module only adds what a shared URL
needs: a persistent spend ledger with a hard total cap, a daily request cap and a
rate limit. The ledger is an application-side estimate, not a provider invoice;
the account-level stop on Token Factory remains the real backstop.
"""
from __future__ import annotations

import os
import sqlite3
import time
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING
from pathlib import Path
from typing import Any, Callable

import httpx

from agrofield_agent.config import Settings
from agrofield_agent.models import ObservationDraft, ProviderTelemetry
from agrofield_agent.semantic_verifier import VerifiedExtractionProvider
from agrofield_agent.nebius_smoke import (
    MONEY_QUANTUM,
    ContractViolation,
    PreflightBlocked,
    SmokeHarnessError,
    SmokePlan,
    UpstreamRequestFailure,
    _bounded_int_env,
    _money,
    _required_decimal_env,
    _validate_plan,
    execute_one_request,
    preflight,
)

DEMO_PROVIDER = "nebius-demo"
DEMO_CONFIRMATION_PHRASE = "RUN_PUBLIC_NEMOTRON_DEMO"


class DemoLimitReached(SmokeHarnessError):
    """A demo limit stopped the request before any network access."""

    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class DemoLimits:
    total_budget_usd: Decimal
    daily_requests: int
    requests_per_minute: int

    def __post_init__(self) -> None:
        if self.total_budget_usd <= 0:
            raise PreflightBlocked("demo total budget must be positive")
        if not 1 <= self.daily_requests <= 5000:
            raise PreflightBlocked("demo daily request cap must be between 1 and 5000")
        if not 1 <= self.requests_per_minute <= 60:
            raise PreflightBlocked("demo per-minute cap must be between 1 and 60")


def _units(amount: Decimal) -> int:
    """Whole 1e-8 USD units, rounded up so the ledger never undercounts."""
    return int((amount / MONEY_QUANTUM).to_integral_value(rounding=ROUND_CEILING))


def _usd(units: int) -> Decimal:
    return Decimal(units) * MONEY_QUANTUM


class SpendLedger:
    """SQLite ledger: reserve the cost ceiling first, settle with reported usage."""

    def __init__(self, path: Path, clock: Callable[[], float] = time.time) -> None:
        self.path = path
        self._clock = clock
        path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS nebius_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at REAL NOT NULL,
                    day TEXT NOT NULL,
                    cost_units INTEGER NOT NULL,
                    status TEXT NOT NULL
                )"""
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, timeout=10, isolation_level=None)

    def _day(self, moment: float) -> str:
        return datetime.fromtimestamp(moment, timezone.utc).strftime("%Y-%m-%d")

    def reserve(self, ceiling_usd: Decimal, limits: DemoLimits) -> int:
        now = self._clock()
        with closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                spent, today, last_minute = connection.execute(
                    """SELECT COALESCE(SUM(cost_units), 0),
                              COALESCE(SUM(day = ?), 0),
                              COALESCE(SUM(created_at > ?), 0)
                       FROM nebius_requests""",
                    (self._day(now), now - 60),
                ).fetchone()
                if spent + _units(ceiling_usd) > _units(limits.total_budget_usd):
                    raise DemoLimitReached(
                        "The demo's Nemotron budget is exhausted",
                        code="demo_budget_exhausted",
                    )
                if today >= limits.daily_requests:
                    raise DemoLimitReached(
                        "The demo's daily Nemotron request cap was reached",
                        code="demo_daily_cap_reached",
                    )
                if last_minute >= limits.requests_per_minute:
                    raise DemoLimitReached(
                        "Too many Nemotron requests in the last minute; retry shortly",
                        code="demo_rate_limited",
                    )
                cursor = connection.execute(
                    "INSERT INTO nebius_requests (created_at, day, cost_units, status) "
                    "VALUES (?, ?, ?, 'reserved')",
                    (now, self._day(now), _units(ceiling_usd)),
                )
                connection.execute("COMMIT")
                return int(cursor.lastrowid)
            except BaseException:
                connection.execute("ROLLBACK")
                raise

    def settle(self, reservation: int, status: str, cost_usd: Decimal | None = None) -> None:
        """Record the outcome; without reported usage the reserved ceiling stays."""
        with closing(self._connect()) as connection:
            if cost_usd is None:
                connection.execute(
                    "UPDATE nebius_requests SET status = ? WHERE id = ?",
                    (status, reservation),
                )
            else:
                connection.execute(
                    "UPDATE nebius_requests SET status = ?, cost_units = ? WHERE id = ?",
                    (status, _units(cost_usd), reservation),
                )

    def summary(self, limits: DemoLimits) -> dict[str, Any]:
        now = self._clock()
        with closing(self._connect()) as connection:
            total, spent, today, accepted = connection.execute(
                """SELECT COUNT(*), COALESCE(SUM(cost_units), 0),
                          COALESCE(SUM(day = ?), 0), COALESCE(SUM(status = 'accepted'), 0)
                   FROM nebius_requests""",
                (self._day(now),),
            ).fetchone()
        budget = _units(limits.total_budget_usd)
        return {
            "requests_total": total,
            "requests_accepted": accepted,
            "requests_today": today,
            "daily_request_cap": limits.daily_requests,
            "requests_per_minute_cap": limits.requests_per_minute,
            "estimated_spend_usd": _money(_usd(spent)),
            "total_budget_usd": _money(limits.total_budget_usd),
            "estimated_remaining_usd": _money(_usd(max(budget - spent, 0))),
            "basis": "application_estimate_from_reported_tokens_not_an_invoice",
        }


def _usage_cost(diagnostics: dict[str, Any], plan: SmokePlan) -> Decimal | None:
    prompt, completion = diagnostics.get("prompt_tokens"), diagnostics.get("completion_tokens")
    if not isinstance(prompt, int) or not isinstance(completion, int):
        return None
    return (
        Decimal(prompt) * plan.input_price_per_million
        + Decimal(completion) * plan.output_price_per_million
    ) / Decimal(1_000_000)


@dataclass
class BudgetedNebiusExtractionProvider:
    """Many guarded single requests, each admitted by the spend ledger first."""

    plan: SmokePlan
    api_key: str = field(repr=False)
    ledger: SpendLedger
    limits: DemoLimits
    transport: httpx.AsyncBaseTransport | None = None

    async def extract(self, raw_text: str) -> tuple[ObservationDraft, ProviderTelemetry]:
        _, estimate = preflight(raw_text, self.plan)
        reservation = self.ledger.reserve(estimate.estimated_cost_ceiling_usd, self.limits)
        try:
            result = await execute_one_request(
                raw_text, self.plan, self.api_key, transport=self.transport
            )
        except ContractViolation as exc:
            self.ledger.settle(
                reservation, "contract_rejected", _usage_cost(exc.diagnostics, self.plan)
            )
            raise
        except UpstreamRequestFailure:
            self.ledger.settle(reservation, "upstream_failed")
            raise
        except BaseException:
            self.ledger.settle(reservation, "error")
            raise
        self.ledger.settle(
            reservation, "accepted", Decimal(result["estimated_usage_cost_usd"])
        )
        return (
            ObservationDraft.model_validate(result["observation"]),
            ProviderTelemetry.model_validate(result["telemetry"]),
        )

    def admit(self, ceiling_usd: Decimal) -> Callable[[str, Decimal | None], None]:
        """Reserve a second request (the verifier) on the same ledger and caps."""
        reservation = self.ledger.reserve(ceiling_usd, self.limits)
        return lambda status, cost: self.ledger.settle(reservation, status, cost)

    def budget(self) -> dict[str, Any]:
        return {
            "provider": DEMO_PROVIDER,
            "model": self.plan.model,
            "input_price_per_million_usd": str(self.plan.input_price_per_million),
            "output_price_per_million_usd": str(self.plan.output_price_per_million),
            "automatic_retries": 0,
            **self.ledger.summary(self.limits),
        }


def demo_provider_from_env(
    settings: Settings, *, transport: httpx.AsyncBaseTransport | None = None
) -> BudgetedNebiusExtractionProvider | VerifiedExtractionProvider:
    """Build the demo provider or refuse to start; every guard is mandatory."""
    if os.getenv("AGROFIELD_NEBIUS_DEMO_CONFIRMATION") != DEMO_CONFIRMATION_PHRASE:
        raise PreflightBlocked(
            "public demo mode blocked; set AGROFIELD_NEBIUS_DEMO_CONFIRMATION="
            f"{DEMO_CONFIRMATION_PHRASE} only after the owner approves a budget"
        )
    if not settings.nebius_api_key:
        raise PreflightBlocked("NEBIUS_API_KEY is required for public demo mode")
    plan = SmokePlan(
        model=settings.nebius_model,
        base_url=settings.nebius_base_url,
        max_completion_tokens=_bounded_int_env("NEBIUS_MAX_COMPLETION_TOKENS", 1024),
        prompt_token_budget=_bounded_int_env("NEBIUS_PROMPT_TOKEN_BUDGET", 16384),
        input_price_per_million=_required_decimal_env("NEBIUS_INPUT_PRICE_PER_MILLION"),
        output_price_per_million=_required_decimal_env("NEBIUS_OUTPUT_PRICE_PER_MILLION"),
        max_cost_usd=_required_decimal_env("NEBIUS_MAX_COST_USD"),
        reasoning_effort=os.getenv("NEBIUS_REASONING_EFFORT", "none").lower(),
    )
    _validate_plan(plan)
    limits = DemoLimits(
        total_budget_usd=_required_decimal_env("AGROFIELD_DEMO_TOTAL_BUDGET_USD"),
        daily_requests=_bounded_int_env("AGROFIELD_DEMO_DAILY_REQUESTS", 200),
        requests_per_minute=_bounded_int_env("AGROFIELD_DEMO_REQUESTS_PER_MINUTE", 6),
    )
    ledger_path = Path(
        os.getenv("AGROFIELD_DEMO_LEDGER_PATH")
        or settings.database_path.with_name("nebius-demo-ledger.sqlite3")
    )
    provider = BudgetedNebiusExtractionProvider(
        plan=plan,
        api_key=settings.nebius_api_key,
        ledger=SpendLedger(ledger_path),
        limits=limits,
        transport=transport,
    )
    verifier_model = os.getenv("AGROFIELD_VERIFIER_MODEL", "").strip()
    if not verifier_model:
        return provider
    # Optional second pass: its own model and prices, the same cap, the same
    # ledger and caps (each verification is one more admitted request).
    verifier_plan = SmokePlan(
        model=verifier_model,
        base_url=settings.nebius_base_url,
        max_completion_tokens=plan.max_completion_tokens,
        prompt_token_budget=plan.prompt_token_budget,
        input_price_per_million=_required_decimal_env("NEBIUS_VERIFIER_INPUT_PRICE_PER_MILLION"),
        output_price_per_million=_required_decimal_env("NEBIUS_VERIFIER_OUTPUT_PRICE_PER_MILLION"),
        max_cost_usd=plan.max_cost_usd,
    )
    _validate_plan(verifier_plan)
    return VerifiedExtractionProvider(
        inner=provider,
        plan=verifier_plan,
        api_key=settings.nebius_api_key,
        transport=transport,
        admit=provider.admit,
    )
