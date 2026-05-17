"""Fundamentals provider interface."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.schemas.fundamentals import FundamentalsResponse


class FundamentalsProviderError(Exception):
    """Base class for fundamentals provider errors."""


@runtime_checkable
class FundamentalsProvider(Protocol):
    name: str

    def get_fundamentals(self, symbol: str) -> FundamentalsResponse | None:
        """Return fundamentals for ``symbol``, or ``None`` if unavailable."""
        ...
