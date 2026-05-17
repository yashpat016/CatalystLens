"""Tests for GET /api/tickers/{ticker}/fundamentals."""

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


def _write_fundamentals(directory, ticker: str) -> None:
    today = date.today()
    report = today + timedelta(days=14)
    payload = {
        "ticker": ticker,
        "company_name": "Apple Inc.",
        "currency": "USD",
        "periods": [
            {
                "fiscal_year": 2025,
                "fiscal_quarter": 1,
                "period_end": "2024-12-31",
                "report_date": "2025-01-30",
                "report_time": "amc",
                "eps_actual": "2.18",
                "eps_estimate": "2.10",
                "eps_surprise_pct": "3.81",
                "beat": True,
                "revenue": "124300000000",
                "revenue_estimate": "123500000000",
                "revenue_surprise_pct": "0.65",
                "gross_margin_pct": "46.2",
                "operating_margin_pct": "30.5",
                "net_margin_pct": "26.1",
            },
            {
                "fiscal_year": 2025,
                "fiscal_quarter": 2,
                "period_end": "2025-03-31",
                "report_date": "2025-05-01",
                "report_time": "amc",
                "eps_actual": "1.65",
                "eps_estimate": "1.62",
                "eps_surprise_pct": "1.85",
                "beat": True,
                "revenue": "95359000000",
                "revenue_estimate": "94500000000",
                "revenue_surprise_pct": "0.91",
                "gross_margin_pct": "47.1",
                "operating_margin_pct": "31.2",
                "net_margin_pct": "26.8",
                "quarter_end_price": "210.50",
                "free_cash_flow": "22000000000",
                "total_debt": "105000000000",
            },
        ],
        "upcoming_earnings": {
            "report_date": report.isoformat(),
            "report_time": "amc",
            "fiscal_year": 2025,
            "fiscal_quarter": 3,
            "eps_estimate": "1.72",
            "revenue_estimate": "98000000000",
            "analyst_count": 28,
        },
    }
    (directory / f"fundamentals_{ticker}.json").write_text(json.dumps(payload))


class TestFundamentalsEndpoint:
    def test_happy_path(self, client, db_session, fixtures_tmp_dir):
        _seed_symbol(db_session)
        _write_fundamentals(fixtures_tmp_dir, "AAPL")
        # Override fundamentals provider path via same fixtures dir
        from app.services.fundamentals_service import get_fundamentals_provider
        from app.main import app

        def _fund_provider():
            from app.providers.fundamentals.fixture import FixtureFundamentalsProvider

            return FixtureFundamentalsProvider(fixtures_dir=fixtures_tmp_dir)

        app.dependency_overrides[get_fundamentals_provider] = _fund_provider
        try:
            resp = client.get("/api/tickers/AAPL/fundamentals")
        finally:
            app.dependency_overrides.pop(get_fundamentals_provider, None)

        assert resp.status_code == 200
        body = resp.json()
        assert body["ticker"] == "AAPL"
        assert len(body["periods"]) == 2
        assert body["periods"][0]["beat"] is True
        assert body["upcoming_earnings"] is not None
        assert body["upcoming_earnings"]["days_until"] is not None
        assert body["upcoming_earnings"]["eps_estimate"] == "1.72"

    def test_unknown_ticker_404(self, client, db_session, fixtures_tmp_dir):
        _seed_symbol(db_session)
        resp = client.get("/api/tickers/ZZZZ/fundamentals")
        assert resp.status_code == 404

    def test_missing_fixture_404(self, client, db_session, fixtures_tmp_dir):
        _seed_symbol(db_session)
        from app.services.fundamentals_service import get_fundamentals_provider
        from app.main import app
        from app.providers.fundamentals.fixture import FixtureFundamentalsProvider

        app.dependency_overrides[get_fundamentals_provider] = lambda: FixtureFundamentalsProvider(
            fixtures_dir=fixtures_tmp_dir
        )
        try:
            resp = client.get("/api/tickers/AAPL/fundamentals")
        finally:
            app.dependency_overrides.pop(get_fundamentals_provider, None)
        assert resp.status_code == 404
