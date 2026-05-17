"""Institutional holdings (SEC Form 13F-HR style) endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Symbol
from app.providers.institutional.base import InstitutionalProvider
from app.schemas.institutional import InstitutionalResponse
from app.services.institutional_service import (
    fetch_institutional,
    get_institutional_provider,
)

router = APIRouter(prefix="/tickers", tags=["institutional"])


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


@router.get("/{ticker}/institutional", response_model=InstitutionalResponse)
def get_institutional(
    ticker: str,
    db: Annotated[Session, Depends(get_db)],
    provider: Annotated[InstitutionalProvider, Depends(get_institutional_provider)],
) -> InstitutionalResponse:
    t = _normalize_ticker(ticker)
    symbol = _load_symbol(db, t)
    data = fetch_institutional(provider, t)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No institutional holdings data for {t}",
        )
    return data.model_copy(
        update={
            "ticker": symbol.ticker,
            "company_name": symbol.company_name,
        }
    )
