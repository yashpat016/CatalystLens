"""Time utilities.

CatalystLens stores everything in UTC and displays ET for US equities. These
helpers centralise the conversion + parsing rules so timezone bugs do not leak
into the rest of the code.
"""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

NY_TZ = ZoneInfo("America/New_York")
UTC = timezone.utc


def now_utc() -> datetime:
    """Current time as a timezone-aware UTC datetime."""
    return datetime.now(tz=UTC)


def ensure_utc(dt: datetime) -> datetime:
    """Return ``dt`` as a timezone-aware UTC datetime.

    Naive datetimes are assumed to already be UTC. Timezone-aware datetimes
    are converted to UTC.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def to_et(dt: datetime) -> datetime:
    """Convert a datetime (naive or aware) to America/New_York."""
    return ensure_utc(dt).astimezone(NY_TZ)


def parse_iso(value: str) -> datetime:
    """Parse an ISO-8601 datetime string. ``Z`` suffix is accepted.

    Returns a timezone-aware UTC datetime. Raises ``ValueError`` on bad input.
    """
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    return ensure_utc(dt)
