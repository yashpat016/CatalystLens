"""Ticker endpoints: summary + bars.

Sprint 1 surface area:

  GET /api/tickers/{ticker}/summary
  GET /api/tickers/{ticker}/bars?timeframe=1m|5m|1d&start=...&end=...&limit=...
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Symbol
from app.providers.market_data.base import MarketDataProvider
from app.schemas.bar import BarsResponse, Timeframe
from app.schemas.ticker import TickerSummary
from app.services.market_data_service import (
    build_summary_from_bars,
    fetch_bars,
    get_market_data_provider,
)

router = APIRouter(prefix="/tickers", tags=["tickers"])


def _normalize_ticker(ticker: str) -> str:
    t = ticker.strip().upper()
    if not t or not t.isascii() or not all(c.isalnum() or c in "-." for c in t):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ticker symbol.",
        )
    return t


def _load_symbol(db: Session, ticker: str) -> Symbol:
    sym = db.scalar(select(Symbol).where(Symbol.ticker == ticker))
    if sym is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown ticker: {ticker}",
        )
    return sym


@router.get("/{ticker}/summary", response_model=TickerSummary)
def get_summary(
    ticker: str,
    db: Annotated[Session, Depends(get_db)],
    provider: Annotated[MarketDataProvider, Depends(get_market_data_provider)],
) -> TickerSummary:
    t = _normalize_ticker(ticker)
    symbol = _load_symbol(db, t)

    bars = fetch_bars(provider, t, timeframe="1m", limit=2500)
    derived = build_summary_from_bars(bars)

    return TickerSummary(
        ticker=symbol.ticker,
        company_name=symbol.company_name,
        exchange=symbol.exchange,
        price=derived["price"],  # type: ignore[arg-type]
        change_pct=derived["change_pct"],  # type: ignore[arg-type]
        volume=derived["volume"],  # type: ignore[arg-type]
        relative_volume=None,
        session=derived["session"],  # type: ignore[arg-type]
        last_bar_time=derived["last_bar_time"],  # type: ignore[arg-type]
        latest_event=None,
    )


@router.get("/{ticker}/bars", response_model=BarsResponse)
def get_bars(
    ticker: str,
    db: Annotated[Session, Depends(get_db)],
    provider: Annotated[MarketDataProvider, Depends(get_market_data_provider)],
    timeframe: Timeframe = Query(default="1m"),
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1, le=10000),
) -> BarsResponse:
    t = _normalize_ticker(ticker)
    symbol = _load_symbol(db, t)

    if start is not None and end is not None and start >= end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="`start` must be earlier than `end`.",
        )

    bars = fetch_bars(provider, t, timeframe=timeframe, start=start, end=end, limit=limit)
    return BarsResponse(ticker=symbol.ticker, timeframe=timeframe, bars=bars)
