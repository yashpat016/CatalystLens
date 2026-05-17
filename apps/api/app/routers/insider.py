"""Insider transaction (Form 4 style) endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Symbol
from app.providers.insider.fixture import FixtureInsiderProvider
from app.schemas.insider import InsiderResponse
from app.services.insider_service import fetch_insider, get_insider_provider

router = APIRouter(prefix="/tickers", tags=["insider"])


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


@router.get("/{ticker}/insider", response_model=InsiderResponse)
def get_insider(
    ticker: str,
    db: Annotated[Session, Depends(get_db)],
    provider: Annotated[FixtureInsiderProvider, Depends(get_insider_provider)],
) -> InsiderResponse:
    t = _normalize_ticker(ticker)
    symbol = _load_symbol(db, t)
    data = fetch_insider(provider, t)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No insider transaction data for {t}",
        )
    return data.model_copy(
        update={
            "ticker": symbol.ticker,
            "company_name": symbol.company_name,
        }
    )
