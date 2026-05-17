"""MarketBar model: OHLCV bars for a symbol at a given timeframe."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.symbol import Symbol


# Allowed values, also exposed as a tuple for validation by Pydantic schemas.
TIMEFRAMES: tuple[str, ...] = ("1m", "5m", "1d")
SESSIONS: tuple[str, ...] = ("premarket", "regular", "afterhours", "closed")


class MarketBar(Base):
    __tablename__ = "market_bars"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol_id: Mapped[int] = mapped_column(
        ForeignKey("symbols.id", ondelete="CASCADE"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(8), nullable=False)
    open: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    vwap: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    trade_count: Mapped[int | None] = mapped_column(Integer)
    session: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    symbol: Mapped["Symbol"] = relationship(back_populates="bars")

    __table_args__ = (
        UniqueConstraint(
            "symbol_id", "timeframe", "timestamp", name="uq_market_bars_symbol_tf_ts"
        ),
        Index(
            "ix_market_bars_symbol_tf_ts_desc",
            "symbol_id",
            "timeframe",
            "timestamp",
        ),
    )

    def __repr__(self) -> str:  # pragma: no cover - debug only
        return (
            f"<MarketBar sym={self.symbol_id} tf={self.timeframe} "
            f"ts={self.timestamp.isoformat()} c={self.close}>"
        )
