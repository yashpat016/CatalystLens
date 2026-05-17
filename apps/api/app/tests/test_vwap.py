"""Unit tests for VWAP and rolling VWAP."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.metrics.vwap import rolling_vwap, typical_price, vwap
from app.schemas.bar import Bar


def make_bar(
    *,
    ts: datetime | None = None,
    o: float = 100.0,
    h: float = 101.0,
    low: float = 99.0,
    c: float = 100.5,
    v: int = 1000,
    session: str = "regular",
) -> Bar:
    return Bar(
        timestamp=ts or datetime(2026, 5, 13, 13, 30, tzinfo=timezone.utc),
        open=Decimal(str(o)),
        high=Decimal(str(h)),
        low=Decimal(str(low)),
        close=Decimal(str(c)),
        volume=v,
        vwap=None,
        trade_count=None,
        session=session,  # type: ignore[arg-type]
    )


class TestTypicalPrice:
    def test_simple_average(self):
        bar = make_bar(h=10, low=4, c=7)
        assert typical_price(bar) == Decimal(7)

    def test_handles_decimals(self):
        bar = make_bar(h=101.50, low=99.50, c=100.50)
        # (101.5 + 99.5 + 100.5) / 3 = 100.5
        assert typical_price(bar) == Decimal("100.5")


class TestVwap:
    def test_empty_returns_none(self):
        assert vwap([]) is None

    def test_single_bar_with_volume(self):
        bar = make_bar(h=10, low=4, c=7, v=100)
        # typical price = 7; weighted vwap with single bar = 7
        assert vwap([bar]) == Decimal(7)

    def test_zero_volume_bars_are_ignored(self):
        b1 = make_bar(h=10, low=4, c=7, v=0)
        b2 = make_bar(h=12, low=8, c=10, v=200)
        # b1 ignored, b2 contributes (typical_price=10, weight=200)
        assert vwap([b1, b2]) == Decimal(10)

    def test_all_zero_volume_returns_none(self):
        bars = [make_bar(v=0) for _ in range(5)]
        assert vwap(bars) is None

    def test_weighted_mean_is_correct(self):
        # Two bars: tp=10 weight 100, tp=20 weight 300
        # vwap = (10*100 + 20*300) / (100+300) = 7000/400 = 17.5
        b1 = make_bar(h=10, low=10, c=10, v=100)
        b2 = make_bar(h=20, low=20, c=20, v=300)
        assert vwap([b1, b2]) == Decimal("17.5")


class TestRollingVwap:
    def test_empty_returns_empty(self):
        assert rolling_vwap([]) == []

    def test_aligned_to_input_length(self):
        bars = [make_bar(c=100, v=100) for _ in range(5)]
        out = rolling_vwap(bars)
        assert len(out) == 5

    def test_monotonic_growth_with_constant_price(self):
        bars = [make_bar(h=100, low=100, c=100, v=1000) for _ in range(3)]
        out = rolling_vwap(bars)
        assert out == [Decimal(100), Decimal(100), Decimal(100)]

    def test_resets_on_session_change(self):
        # Two premarket bars at price 100, then regular session at price 200.
        # With reset_on='session', the regular-session running VWAP starts fresh at 200.
        b_pre1 = make_bar(h=100, low=100, c=100, v=100, session="premarket")
        b_pre2 = make_bar(h=100, low=100, c=100, v=100, session="premarket")
        b_reg = make_bar(h=200, low=200, c=200, v=100, session="regular")
        out = rolling_vwap([b_pre1, b_pre2, b_reg], reset_on="session")
        assert out[0] == Decimal(100)
        assert out[1] == Decimal(100)
        assert out[2] == Decimal(200)  # reset, not the cumulative mean of 100/100/200

    def test_no_reset_keeps_running_total(self):
        b_pre = make_bar(h=100, low=100, c=100, v=100, session="premarket")
        b_reg = make_bar(h=200, low=200, c=200, v=100, session="regular")
        out = rolling_vwap([b_pre, b_reg], reset_on=None)
        # cumulative: (100*100 + 200*100) / 200 = 150
        assert out[1] == Decimal(150)

    def test_emits_none_until_first_positive_volume(self):
        b1 = make_bar(c=100, v=0)
        b2 = make_bar(c=100, v=100)
        out = rolling_vwap([b1, b2])
        assert out[0] is None
        assert out[1] == Decimal(100)
