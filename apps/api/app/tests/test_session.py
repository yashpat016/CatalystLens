"""Unit tests for US-equities session classification.

Sprint 1 deliberately ignores holidays -- only weekend + clock-time logic is
tested here. The DST-transition tests verify that the ET window is correctly
anchored regardless of how UTC is moving underneath it.
"""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from app.metrics.session import classify_session

NY = ZoneInfo("America/New_York")


def at_et(year: int, month: int, day: int, hour: int, minute: int = 0) -> datetime:
    """Build a UTC datetime that corresponds to a specific NY local time."""
    return datetime(year, month, day, hour, minute, tzinfo=NY).astimezone(timezone.utc)


class TestSessionBoundaries:
    def test_premarket_starts_at_4am_et(self):
        assert classify_session(at_et(2026, 5, 13, 4, 0)) == "premarket"

    def test_premarket_before_4am_is_closed(self):
        assert classify_session(at_et(2026, 5, 13, 3, 59)) == "closed"

    def test_regular_starts_at_930_et(self):
        assert classify_session(at_et(2026, 5, 13, 9, 30)) == "regular"

    def test_just_before_open_is_premarket(self):
        assert classify_session(at_et(2026, 5, 13, 9, 29)) == "premarket"

    def test_regular_just_before_close(self):
        assert classify_session(at_et(2026, 5, 13, 15, 59)) == "regular"

    def test_afterhours_starts_at_4pm_et(self):
        assert classify_session(at_et(2026, 5, 13, 16, 0)) == "afterhours"

    def test_afterhours_ends_at_8pm_et(self):
        # 20:00 ET is the first minute of "closed".
        assert classify_session(at_et(2026, 5, 13, 20, 0)) == "closed"

    def test_just_before_8pm_is_afterhours(self):
        assert classify_session(at_et(2026, 5, 13, 19, 59)) == "afterhours"


class TestWeekends:
    def test_saturday_is_closed(self):
        # 2026-05-16 is a Saturday in NY.
        ts = at_et(2026, 5, 16, 10, 0)
        assert classify_session(ts) == "closed"

    def test_sunday_is_closed(self):
        ts = at_et(2026, 5, 17, 13, 0)
        assert classify_session(ts) == "closed"


class TestDST:
    def test_spring_forward_regular_session(self):
        # 2026 spring DST: March 8. 10:00 ET that day should still be regular.
        ts = at_et(2026, 3, 9, 10, 0)  # Monday after spring DST
        assert classify_session(ts) == "regular"

    def test_fall_back_regular_session(self):
        # 2026 fall DST: November 1 (Sunday). Monday Nov 2 should classify normally.
        ts = at_et(2026, 11, 2, 10, 0)
        assert classify_session(ts) == "regular"

    def test_premarket_anchored_to_et_through_dst(self):
        # 8:00 ET in March (DST) and 8:00 ET in January (EST) are both premarket.
        assert classify_session(at_et(2026, 3, 9, 8, 0)) == "premarket"
        assert classify_session(at_et(2026, 1, 5, 8, 0)) == "premarket"


class TestNaiveDatetimes:
    def test_naive_is_treated_as_utc(self):
        # Mon Jan 5 2026 14:30 UTC == 09:30 EST (regular open).
        naive = datetime(2026, 1, 5, 14, 30)
        assert classify_session(naive) == "regular"
