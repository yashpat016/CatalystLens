"""OHLCV aggregation helpers for fixture and resampling paths."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from app.schemas.bar import Bar


def aggregate_minutes(bars: list[Bar], interval_minutes: int) -> list[Bar]:
    if not bars or interval_minutes < 2:
        return bars

    bucket: list[Bar] = []
    out: list[Bar] = []
    current_start: datetime | None = None

    def flush() -> None:
        if not bucket:
            return
        first, last = bucket[0], bucket[-1]
        out.append(
            Bar(
                timestamp=first.timestamp,
                open=first.open,
                high=max(b.high for b in bucket),
                low=min(b.low for b in bucket),
                close=last.close,
                volume=sum(b.volume for b in bucket),
                vwap=None,
                trade_count=None,
                session=first.session,
            )
        )
        bucket.clear()

    def bucket_start(ts: datetime) -> datetime:
        minute = (ts.minute // interval_minutes) * interval_minutes
        return ts.replace(minute=minute, second=0, microsecond=0)

    for b in bars:
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


def aggregate_monthly(bars_daily: list[Bar]) -> list[Bar]:
    if not bars_daily:
        return []
    bucket: list[Bar] = []
    out: list[Bar] = []
    current_key: tuple[int, int] | None = None

    def flush() -> None:
        if not bucket:
            return
        first, last = bucket[0], bucket[-1]
        out.append(
            Bar(
                timestamp=first.timestamp,
                open=first.open,
                high=max(b.high for b in bucket),
                low=min(b.low for b in bucket),
                close=last.close,
                volume=sum(b.volume for b in bucket),
                vwap=None,
                trade_count=None,
                session=first.session,
            )
        )
        bucket.clear()

    for b in bars_daily:
        ts = b.timestamp if b.timestamp.tzinfo else b.timestamp.replace(tzinfo=timezone.utc)
        key = (ts.year, ts.month)
        if current_key is None:
            current_key = key
        if key != current_key:
            flush()
            current_key = key
        bucket.append(b)
    flush()
    return out
