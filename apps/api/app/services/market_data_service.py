"""Service layer for market data.

Resolves the configured ``MarketDataProvider`` and exposes business operations
the routers need (fetching bars + building a ticker summary). Routers should
never instantiate providers directly.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.core import config as config_module
from app.core.logging import get_logger
from app.providers.market_data.base import MarketDataProvider, MarketDataProviderError
from app.providers.market_data.fixture import FixtureMarketDataProvider
from app.schemas.bar import Bar, Timeframe

log = get_logger("market_data_service")


def get_market_data_provider() -> MarketDataProvider:
    """FastAPI dependency that resolves the active market-data provider.

    Falls back to the fixture provider if ``alpaca`` is requested but keys are
    missing -- the app stays runnable and the operator sees a loud warning.
    Tests override this via ``app.dependency_overrides``.
    """
    s = config_module.settings  # re-read each call so tests can mutate settings
    name = s.market_data_provider.lower()
    if name == "alpaca":
        try:
            from app.providers.market_data.alpaca import AlpacaMarketDataProvider

            return AlpacaMarketDataProvider()
        except MarketDataProviderError as exc:
            log.warning("alpaca_unavailable_falling_back_to_fixture", error=str(exc))
    return FixtureMarketDataProvider(fixtures_dir=s.fixtures_dir)


def fetch_bars(
    provider: MarketDataProvider,
    ticker: str,
    *,
    timeframe: Timeframe = "1m",
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int | None = None,
) -> list[Bar]:
    return provider.get_bars(
        ticker, timeframe=timeframe, start=start, end=end, limit=limit
    )


def build_summary_from_bars(bars_1m: list[Bar]) -> dict[str, Optional[object]]:
    """Derive the ticker-summary numeric block from a list of 1-minute bars.

    Returns a dict with keys: ``price``, ``change_pct``, ``volume``, ``session``,
    ``last_bar_time``. Returns ``None`` for each field when ``bars_1m`` is empty.
    """
    if not bars_1m:
        return {
            "price": None,
            "change_pct": None,
            "volume": None,
            "session": "closed",
            "last_bar_time": None,
        }

    latest = bars_1m[-1]
    # All bars for the latest UTC date — used for the day's running volume.
    latest_day = latest.timestamp.date()
    day_bars = [b for b in bars_1m if b.timestamp.date() == latest_day]
    day_volume = sum(b.volume for b in day_bars)

    # For change_pct, use the most recent regular-session close of the *previous*
    # trading day if available. That matches how trading apps show "% change".
    prior_regular = [
        b
        for b in bars_1m
        if b.timestamp.date() < latest_day and b.session == "regular"
    ]
    if prior_regular:
        prior_close = prior_regular[-1].close
        change_pct: Decimal | None = (
            (latest.close - prior_close) / prior_close * Decimal(100)
            if prior_close != 0
            else None
        )
    else:
        # Fall back to "today's open vs. now" so the UI has something honest.
        first_today = day_bars[0]
        change_pct = (
            (latest.close - first_today.open) / first_today.open * Decimal(100)
            if first_today.open != 0
            else None
        )

    if change_pct is not None:
        change_pct = change_pct.quantize(Decimal("0.0001"))

    return {
        "price": latest.close,
        "change_pct": change_pct,
        "volume": day_volume,
        "session": latest.session,
        "last_bar_time": latest.timestamp,
    }
