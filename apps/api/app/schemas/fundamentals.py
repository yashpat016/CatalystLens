"""Pydantic schemas for quarterly fundamentals and earnings calendar."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ReportTime = Literal["bmo", "amc", "dmh", "unknown"]


class QuarterlyPeriod(BaseModel):
    """One reported fiscal quarter with EPS, revenue, and margin breakdown."""

    model_config = ConfigDict(from_attributes=True)

    fiscal_year: int
    fiscal_quarter: int = Field(ge=1, le=4)
    period_end: date
    report_date: date | None = None
    report_time: ReportTime = "unknown"

    eps_actual: Decimal | None = None
    eps_estimate: Decimal | None = None
    eps_surprise_pct: Decimal | None = None
    beat: bool | None = None

    revenue: Decimal | None = None
    revenue_estimate: Decimal | None = None
    revenue_surprise_pct: Decimal | None = None

    gross_margin_pct: Decimal | None = None
    operating_margin_pct: Decimal | None = None
    net_margin_pct: Decimal | None = None

    # Context chart: stock vs fundamentals (same fiscal quarter)
    quarter_end_price: Decimal | None = None
    free_cash_flow: Decimal | None = None
    total_debt: Decimal | None = None


class UpcomingEarnings(BaseModel):
    """Next scheduled earnings release for the ticker."""

    report_date: date
    report_time: ReportTime = "unknown"
    fiscal_year: int
    fiscal_quarter: int = Field(ge=1, le=4)
    eps_estimate: Decimal | None = None
    revenue_estimate: Decimal | None = None
    analyst_count: int | None = None
    days_until: int | None = None


class FundamentalsResponse(BaseModel):
    """Full fundamentals payload for a ticker."""

    ticker: str
    company_name: str | None = None
    currency: str = "USD"
    periods: list[QuarterlyPeriod]
    upcoming_earnings: UpcomingEarnings | None = None
