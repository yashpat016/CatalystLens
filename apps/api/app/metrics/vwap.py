"""VWAP and rolling VWAP for OHLCV bars.

When trade-level data is available the right denominator is total traded
volume; when only bars are available we use the typical-price approximation
``(high + low + close) / 3`` weighted by bar volume. The plan calls this out
explicitly -- VWAP from bars is an approximation and should be labelled as such
to the user when displayed.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from app.schemas.bar import Bar

THREE = Decimal(3)


def typical_price(bar: Bar) -> Decimal:
    """``(high + low + close) / 3``."""
    return (bar.high + bar.low + bar.close) / THREE


def vwap(bars: Iterable[Bar]) -> Decimal | None:
    """Single aggregate VWAP across ``bars``.

    Returns ``None`` when the total volume is zero (no useful weight). Zero-volume
    bars are skipped rather than counted -- they contribute no information.
    """
    pv = Decimal(0)
    v = 0
    for bar in bars:
        if bar.volume <= 0:
            continue
        pv += typical_price(bar) * Decimal(bar.volume)
        v += bar.volume
    if v == 0:
        return None
    return pv / Decimal(v)


def rolling_vwap(
    bars: list[Bar],
    *,
    reset_on: str | None = "session",
) -> list[Decimal | None]:
    """Running VWAP aligned to ``bars``.

    Parameters
    ----------
    bars
        Bars in chronological order.
    reset_on
        ``"session"`` (default): reset the running totals whenever the bar's
        ``session`` label changes (e.g. premarket -> regular). ``"day"``: reset
        on each calendar day in UTC. ``None``: never reset (single cumulative
        VWAP for the whole series).

    Returns
    -------
    list[Decimal | None]
        One value per input bar. ``None`` is emitted when no positive-volume
        bars have been seen yet in the current window.
    """
    out: list[Decimal | None] = []
    pv = Decimal(0)
    v = 0
    last_key: object = None

    for bar in bars:
        key: object
        if reset_on == "session":
            key = bar.session
        elif reset_on == "day":
            key = bar.timestamp.date()
        else:
            key = None  # never reset

        if reset_on is not None and key != last_key:
            pv = Decimal(0)
            v = 0
            last_key = key

        if bar.volume > 0:
            pv += typical_price(bar) * Decimal(bar.volume)
            v += bar.volume

        out.append(pv / Decimal(v) if v > 0 else None)

    return out
