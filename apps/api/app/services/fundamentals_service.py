"""Fundamentals service layer."""

from __future__ import annotations

from datetime import date

from app.core import config as config_module
from app.providers.fundamentals.fixture import FixtureFundamentalsProvider
from app.schemas.fundamentals import FundamentalsResponse, UpcomingEarnings


def get_fundamentals_provider():
    """FastAPI dependency: resolve the active fundamentals provider."""
    return FixtureFundamentalsProvider(fixtures_dir=config_module.settings.fixtures_dir)


def fetch_fundamentals(provider, ticker: str) -> FundamentalsResponse | None:
    raw = provider.get_fundamentals(ticker)
    if raw is None:
        return None
    return _enrich_upcoming(raw)


def _enrich_upcoming(data: FundamentalsResponse) -> FundamentalsResponse:
    """Compute ``days_until`` on upcoming earnings relative to today (UTC date)."""
    if data.upcoming_earnings is None:
        return data
    today = date.today()
    ue = data.upcoming_earnings
    days = (ue.report_date - today).days
    enriched = ue.model_copy(update={"days_until": days})
    return data.model_copy(update={"upcoming_earnings": enriched})
