"""Market data provider interface.

Every adapter implements ``get_bars`` and exposes a stable ``name`` attribute.
The rest of the backend talks to ``MarketDataProvider`` only -- never directly
to a vendor SDK.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from app.schemas.bar import Bar, Timeframe


class MarketDataProviderError(Exception):
    """Base class for provider errors. Wraps upstream HTTP / parse failures."""


@runtime_checkable
class MarketDataProvider(Protocol):
    """A source of normalized OHLCV bars."""

    name: str

    def get_bars(
        self,
        symbol: str,
        *,
        timeframe: Timeframe = "1m",
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> list[Bar]:
        """Return bars for ``symbol``, optionally bounded by ``[start, end)``.

        Implementations should return bars in ascending timestamp order. When
        ``limit`` is set, the most recent ``limit`` bars within the range are
        returned.
        """
        ...
