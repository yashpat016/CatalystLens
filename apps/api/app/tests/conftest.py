"""Shared pytest fixtures.

Sprint 1 uses an in-memory SQLite database for endpoint tests so the suite is
fast and self-contained. The production deployment uses Postgres; the schema
is portable enough that this is safe for the tables we have today
(``symbols`` + ``market_bars``). When Postgres-specific features arrive in
later sprints the conftest will switch to a per-test transactional fixture
against a real Postgres container.
"""

from __future__ import annotations

import json
from collections.abc import Generator
from pathlib import Path  # noqa: F401  -- re-exported helper API

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base


@pytest.fixture(scope="function")
def test_engine():
    # StaticPool keeps the in-memory database alive across all sessions in this
    # process; otherwise SQLAlchemy hands out fresh connections (each with its
    # own empty in-memory DB) and the schema vanishes between queries.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    TestSession = sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def fixtures_tmp_dir(tmp_path: Path) -> Path:
    """A temp directory the fixture provider will be pointed at via DI override."""
    return tmp_path


@pytest.fixture(scope="function")
def client(db_session, fixtures_tmp_dir) -> Generator[TestClient, None, None]:
    """A FastAPI TestClient with DB + market-data-provider dependencies overridden."""
    from app.db.session import get_db
    from app.main import app
    from app.providers.market_data.fixture import FixtureMarketDataProvider
    from app.services.fundamentals_service import get_fundamentals_provider
    from app.services.institutional_service import get_institutional_provider
    from app.services.market_data_service import get_market_data_provider

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass  # session lifecycle owned by the db_session fixture

    def _override_provider():
        return FixtureMarketDataProvider(fixtures_dir=fixtures_tmp_dir)

    def _override_fundamentals_provider():
        from app.providers.fundamentals.fixture import FixtureFundamentalsProvider

        return FixtureFundamentalsProvider(fixtures_dir=fixtures_tmp_dir)

    def _override_institutional_provider():
        from app.providers.institutional.fixture import FixtureInstitutionalProvider

        return FixtureInstitutionalProvider(fixtures_dir=fixtures_tmp_dir)

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_market_data_provider] = _override_provider
    app.dependency_overrides[get_fundamentals_provider] = _override_fundamentals_provider
    app.dependency_overrides[get_institutional_provider] = _override_institutional_provider
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()


def write_fixture_bars(
    directory: Path,
    ticker: str,
    bars_1m: list[dict],
    bars_1d: list[dict] | None = None,
) -> Path:
    """Helper for tests that need to lay down a fixture JSON file."""
    payload = {"ticker": ticker, "bars_1m": bars_1m, "bars_1d": bars_1d or []}
    path = directory / f"bars_{ticker}.json"
    path.write_text(json.dumps(payload))
    return path
