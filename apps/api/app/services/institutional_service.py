"""Institutional holdings service layer."""

from __future__ import annotations

from app.core import config as config_module
from app.providers.institutional.fixture import FixtureInstitutionalProvider
from app.schemas.institutional import InstitutionalResponse


def get_institutional_provider():
    """FastAPI dependency: resolve the active institutional provider."""
    return FixtureInstitutionalProvider(fixtures_dir=config_module.settings.fixtures_dir)


def fetch_institutional(provider, ticker: str) -> InstitutionalResponse | None:
    return provider.get_institutional(ticker)
