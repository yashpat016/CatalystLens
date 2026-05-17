"""Pydantic schemas for ticker summary responses."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.schemas.bar import SessionLabel


class TickerSummary(BaseModel):
    """Top-of-page snapshot for a ticker.

    Sprint 1 leaves ``relative_volume`` and ``latest_event`` as ``None`` -- these
    are wired up in later sprints. The fields are present in the schema so the
    frontend can rely on a stable contract.
    """

    model_config = ConfigDict(from_attributes=True)

    ticker: str
    company_name: str | None
    exchange: str | None
    price: Decimal | None
    change_pct: Decimal | None
    volume: int | None
    relative_volume: Decimal | None = None
    session: SessionLabel
    last_bar_time: datetime | None
    latest_event: dict | None = None
