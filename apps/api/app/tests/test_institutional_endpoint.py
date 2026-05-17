"""Tests for GET /api/tickers/{ticker}/institutional."""

from __future__ import annotations

import json
from datetime import date, timedelta

from app.models import Symbol


def _seed_symbol(db_session, ticker: str = "AAPL") -> None:
    db_session.add(
        Symbol(
            ticker=ticker,
            exchange="NASDAQ",
            company_name="Apple Inc.",
            active=True,
        )
    )
    db_session.commit()


def _write_institutional(directory, ticker: str) -> None:
    period_end = date(2025, 3, 31)
    filed = period_end + timedelta(days=45)
    payload = {
        "ticker": ticker,
        "company_name": "Apple Inc.",
        "source": "fixture_sec_13f_hr",
        "data_as_of": period_end.isoformat(),
        "filed_through": filed.isoformat(),
        "data_notes": ["Test fixture."],
        "aggregate_flow": "net_buying",
        "net_shares_change_qoq": 12_500_000,
        "net_value_change_usd": "2850000000",
        "holders": [
            {
                "manager_name": "Vanguard Group Inc",
                "cik": "0000102909",
                "shares": 1_350_000_000,
                "market_value_usd": "308000000000",
                "shares_change_qoq": 8_000_000,
                "value_change_usd": "1824000000",
                "activity": "increased",
                "implied_position_price_usd": "228.15",
                "implied_flow_price_usd": "228.00",
                "pct_of_outstanding": "8.882",
                "filing_date": (filed - timedelta(days=3)).isoformat(),
            }
        ],
        "quarter_history": [],
    }
    (directory / f"institutional_{ticker}.json").write_text(json.dumps(payload))


class TestInstitutionalEndpoint:
    def test_happy_path(self, client, db_session, fixtures_tmp_dir):
        _seed_symbol(db_session)
        _write_institutional(fixtures_tmp_dir, "AAPL")
        from app.main import app
        from app.services.institutional_service import get_institutional_provider
        from app.providers.institutional.fixture import FixtureInstitutionalProvider

        app.dependency_overrides[get_institutional_provider] = lambda: FixtureInstitutionalProvider(
            fixtures_dir=fixtures_tmp_dir
        )
        try:
            resp = client.get("/api/tickers/AAPL/institutional")
        finally:
            app.dependency_overrides.pop(get_institutional_provider, None)

        assert resp.status_code == 200
        body = resp.json()
        assert body["ticker"] == "AAPL"
        assert body["aggregate_flow"] == "net_buying"
        assert len(body["holders"]) == 1
        assert body["holders"][0]["implied_flow_price_usd"] == "228.00"
        assert body["data_notes"]

    def test_unknown_ticker_404(self, client, db_session):
        _seed_symbol(db_session)
        resp = client.get("/api/tickers/ZZZZ/institutional")
        assert resp.status_code == 404

    def test_missing_fixture_404(self, client, db_session, fixtures_tmp_dir):
        _seed_symbol(db_session)
        from app.main import app
        from app.services.institutional_service import get_institutional_provider
        from app.providers.institutional.fixture import FixtureInstitutionalProvider

        app.dependency_overrides[get_institutional_provider] = lambda: FixtureInstitutionalProvider(
            fixtures_dir=fixtures_tmp_dir
        )
        try:
            resp = client.get("/api/tickers/AAPL/institutional")
        finally:
            app.dependency_overrides.pop(get_institutional_provider, None)
        assert resp.status_code == 404
