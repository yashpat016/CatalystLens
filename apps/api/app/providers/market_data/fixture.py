"""Fixture-backed MarketDataProvider.

Reads ``bars_{TICKER}.json`` files produced by ``scripts/generate_fixtures.py``
and serves them as ``Bar`` instances. Supports on-the-fly 5-minute aggregation
from 1-minute bars so the API contract can offer all three timeframes without
storing them.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from app.core.logging import get_logger
from app.providers.market_data.bar_aggregate import aggregate_minutes, aggregate_monthly
from app.schemas.bar import Bar, Timeframe

log = get_logger("fixture_provider")


class FixtureMarketDataProvider:
    name = "fixture"

    def __init__(self, fixtures_dir: str | Path) -> None:
        self.fixtures_dir = Path(fixtures_dir)

    # ------------------------------------------------------------------ public

    def get_bars(
        self,
        symbol: str,
        *,
        timeframe: Timeframe = "1m",
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> list[Bar]:
        symbol_u = symbol.upper()
        path = self.fixtures_dir / f"bars_{symbol_u}.json"
        if not path.exists():
            log.warning("fixture_missing", ticker=symbol_u, path=str(path))
            return []

        try:
            raw = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            log.error("fixture_invalid_json", ticker=symbol_u, error=str(exc))
            return []

        bars_1m = self._parse_bars(raw.get("bars_1m", []))
        bars_1d = self._parse_bars(raw.get("bars_1d", []))

        if timeframe == "1m":
            bars = bars_1m
        elif timeframe == "1d":
            bars = bars_1d if bars_1d else bars_1m
        elif timeframe == "5m":
            bars = self._aggregate_to_5m(bars_1m)
        elif timeframe == "1h":
            bars = aggregate_minutes(bars_1m, 60)
        elif timeframe == "1mo":
            bars = aggregate_monthly(bars_1d if bars_1d else bars_1m)
        else:
            return []

        bars = self._filter_range(bars, start=start, end=end)
        if limit is not None and len(bars) > limit:
            bars = bars[-limit:]
        return bars

    # ----------------------------------------------------------------- helpers

    @staticmethod
    def _parse_bars(raw: list[dict]) -> list[Bar]:
        return [Bar.model_validate(item) for item in raw]

    @staticmethod
    def _filter_range(
        bars: list[Bar], *, start: datetime | None, end: datetime | None
    ) -> list[Bar]:
        if start is None and end is None:
            return bars
        out: list[Bar] = []
        for b in bars:
            ts = b.timestamp
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if start is not None and ts < start:
                continue
            if end is not None and ts >= end:
                continue
            out.append(b)
        return out

    @staticmethod
    def _aggregate_to_5m(bars_1m: list[Bar]) -> list[Bar]:
        """Collapse consecutive 1-minute bars into 5-minute bars.

        Groups by floor(timestamp, 5 min). High/low/volume aggregate as you'd
        expect; open = first.open, close = last.close, session = first.session.
        Resets across day boundaries are implicit because timestamps are
        wall-clock UTC.
        """
        if not bars_1m:
            return []
        bucket: list[Bar] = []
        out: list[Bar] = []

        def flush() -> None:
            if not bucket:
                return
            first = bucket[0]
            last = bucket[-1]
            high = max(b.high for b in bucket)
            low = min(b.low for b in bucket)
            volume = sum(b.volume for b in bucket)
            out.append(
                Bar(
                    timestamp=first.timestamp,
                    open=first.open,
                    high=high,
                    low=low,
                    close=last.close,
                    volume=volume,
                    vwap=None,
                    trade_count=None,
                    session=first.session,
                )
            )
            bucket.clear()

        def bucket_start(ts: datetime) -> datetime:
            # Floor minute to nearest 5-minute multiple.
            minute = (ts.minute // 5) * 5
            return ts.replace(minute=minute, second=0, microsecond=0)

        current_start: datetime | None = None
        for b in bars_1m:
            ts = b.timestamp if b.timestamp.tzinfo else b.timestamp.replace(tzinfo=timezone.utc)
            this_start = bucket_start(ts)
            if current_start is None:
                current_start = this_start
            if this_start != current_start:
                flush()
                current_start = this_start
            bucket.append(b)
        flush()
        return out
