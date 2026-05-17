"""Pydantic schema for normalized OHLCV bars.

The same shape is used by:
  - the metrics layer (input to VWAP / session / etc.)
  - provider adapters (output of ``get_bars``)
  - the API response (serialized to JSON)
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SessionLabel = Literal["premarket", "regular", "afterhours", "closed"]
Timeframe = Literal["1m", "5m", "1h", "1d", "1mo"]


class Bar(BaseModel):
    """One OHLCV bar, normalized."""

    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime = Field(description="Bar start time, timezone-aware UTC")
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int = Field(ge=0)
    vwap: Decimal | None = None
    trade_count: int | None = None
    session: SessionLabel


class BarsResponse(BaseModel):
    ticker: str
    timeframe: Timeframe
    bars: list[Bar]
