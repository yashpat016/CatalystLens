"""Insider transaction service layer."""

from __future__ import annotations

from app.core import config as config_module
from app.providers.insider.fixture import FixtureInsiderProvider
from app.schemas.insider import InsiderResponse


def get_insider_provider() -> FixtureInsiderProvider:
    s = config_module.settings
    return FixtureInsiderProvider(fixtures_dir=s.fixtures_dir)


def fetch_insider(provider: FixtureInsiderProvider, ticker: str) -> InsiderResponse | None:
    return provider.get_insider(ticker)
