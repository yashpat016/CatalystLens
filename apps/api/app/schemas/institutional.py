"""Pydantic schemas for institutional holdings derived from SEC Form 13F-HR.

Form 13F reports quarter-end positions (shares + market value), not trade-level
buys/sells. QoQ share changes imply net institutional flow with a lag (~45 days).
``implied_*_price`` fields are derived proxies (value ÷ shares), not reported
cost basis.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

HolderActivity = Literal["new", "increased", "decreased", "closed", "unchanged"]
AggregateFlow = Literal["net_buying", "net_selling", "mixed", "unchanged"]


class InstitutionalHolder(BaseModel):
    """One institutional manager's position in the issuer for a 13F reporting period."""

    model_config = ConfigDict(from_attributes=True)

    manager_name: str
    cik: str | None = None
    shares: int = Field(ge=0)
    market_value_usd: Decimal
    shares_change_qoq: int | None = None
    value_change_usd: Decimal | None = None
    activity: HolderActivity = "unchanged"
    # Quarter-end mark: market_value / shares at filing date (not acquisition cost).
    implied_position_price_usd: Decimal | None = None
    # Rough flow proxy: value_change / shares_change when the manager added or trimmed.
    implied_flow_price_usd: Decimal | None = None
    pct_of_outstanding: Decimal | None = Field(
        default=None,
        description="Holder's shares as % of issuer shares outstanding (when known).",
    )
    filing_date: date | None = None


class InstitutionalQuarterSummary(BaseModel):
    """Aggregate institutional footprint for one reported quarter."""

    model_config = ConfigDict(from_attributes=True)

    period_end: date
    filed_through: date
    holder_count: int = Field(ge=0)
    total_shares: int = Field(ge=0)
    total_market_value_usd: Decimal
    net_shares_change_qoq: int | None = None
    net_value_change_usd: Decimal | None = None
    aggregate_flow: AggregateFlow = "unchanged"


class InstitutionalResponse(BaseModel):
    """Institutional holdings and inferred QoQ flow for a ticker."""

    ticker: str
    company_name: str | None = None
    source: str = Field(
        default="sec_13f_hr",
        description="Data lineage label (e.g. sec_13f_hr, fixture).",
    )
    data_as_of: date = Field(description="Quarter-end date of the latest 13F snapshot.")
    filed_through: date = Field(description="Latest manager filing date included.")
    data_notes: list[str] = Field(
        default_factory=list,
        description="Human-readable caveats about SEC 13F limitations.",
    )
    aggregate_flow: AggregateFlow = "unchanged"
    net_shares_change_qoq: int | None = None
    net_value_change_usd: Decimal | None = None
    holders: list[InstitutionalHolder]
    quarter_history: list[InstitutionalQuarterSummary] = Field(default_factory=list)
