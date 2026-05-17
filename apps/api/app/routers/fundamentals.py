"""Fundamentals and earnings calendar endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Symbol
from app.providers.fundamentals.base import FundamentalsProvider
from app.schemas.fundamentals import FundamentalsResponse
from app.services.fundamentals_service import fetch_fundamentals, get_fundamentals_provider

router = APIRouter(prefix="/tickers", tags=["fundamentals"])


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


@router.get("/{ticker}/fundamentals", response_model=FundamentalsResponse)
def get_fundamentals(
    ticker: str,
    db: Annotated[Session, Depends(get_db)],
    provider: Annotated[FundamentalsProvider, Depends(get_fundamentals_provider)],
) -> FundamentalsResponse:
    t = _normalize_ticker(ticker)
    symbol = _load_symbol(db, t)
    data = fetch_fundamentals(provider, t)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No fundamentals data for {t}",
        )
    return data.model_copy(
        update={
            "ticker": symbol.ticker,
            "company_name": symbol.company_name,
        }
    )
