"""Form 4–style insider transaction fixtures (demo / research UI)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

InsiderTransactionType = Literal["buy", "sell", "award", "gift"]


class InsiderTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_date: date
    filing_date: date
    insider_name: str
    role: str = Field(description="e.g. CEO, CFO, Director")
    transaction_type: InsiderTransactionType
    shares: int = Field(ge=0)
    price_usd: Decimal | None = None
    value_usd: Decimal | None = None
    shares_owned_after: int | None = None


class InsiderResponse(BaseModel):
    ticker: str
    company_name: str | None = None
    source: str = "sec_form4_fixture"
    data_as_of: date
    data_notes: list[str] = Field(default_factory=list)
    transactions: list[InsiderTransaction]
