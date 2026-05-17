"""US-equities session classification.

CatalystLens distinguishes premarket, regular, after-hours and closed time
windows so volume comparisons and event windows stay honest. Sprint 1 omits the
holiday calendar -- only weekends and clock time are considered. Holidays will
be added with a real exchange calendar in a later sprint.
"""

from __future__ import annotations

from datetime import datetime, time

from app.core.time import to_et

PREMARKET_OPEN = time(4, 0)
REGULAR_OPEN = time(9, 30)
REGULAR_CLOSE = time(16, 0)
AFTERHOURS_CLOSE = time(20, 0)

SessionLabel = str  # one of "premarket" | "regular" | "afterhours" | "closed"


def classify_session(ts_utc: datetime, *, exchange: str = "XNAS") -> SessionLabel:
    """Classify a UTC timestamp as premarket | regular | afterhours | closed.

    ``exchange`` is accepted for forward-compat; Sprint 1 only handles US
    equities and uses the same windows regardless.
    """
    et = to_et(ts_utc)

    # Weekend = closed (no holiday calendar in Sprint 1).
    if et.weekday() >= 5:
        return "closed"

    t = et.time()
    if PREMARKET_OPEN <= t < REGULAR_OPEN:
        return "premarket"
    if REGULAR_OPEN <= t < REGULAR_CLOSE:
        return "regular"
    if REGULAR_CLOSE <= t < AFTERHOURS_CLOSE:
        return "afterhours"
    return "closed"
