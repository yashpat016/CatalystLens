"""Institutional holdings provider interface."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.schemas.institutional import InstitutionalResponse


class InstitutionalProviderError(Exception):
    """Base class for institutional data provider errors."""


@runtime_checkable
class InstitutionalProvider(Protocol):
    name: str

    def get_institutional(self, symbol: str) -> InstitutionalResponse | None:
        """Return 13F-style holdings for ``symbol``, or ``None`` if unavailable."""
        ...
