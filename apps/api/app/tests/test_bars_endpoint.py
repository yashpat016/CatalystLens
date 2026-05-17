"""Tests for the GET /api/tickers/{ticker}/bars endpoint."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from app.models import Symbol


def _seed_symbol(db_session, ticker: str = "AAPL") -> None:
    sym = Symbol(
        ticker=ticker,
        exchange="NASDAQ",
        company_name=f"{ticker} Test Co.",
        active=True,
    )
    db_session.add(sym)
    db_session.commit()


def _write_bars_fixture(fixtures_tmp_dir, ticker: str, n: int = 3) -> None:
    bars = []
    for i in range(n):
        ts = datetime(2026, 5, 13, 13, 30 + i, tzinfo=timezone.utc)
        bars.append(
            {
                "timestamp": ts.isoformat().replace("+00:00", "Z"),
                "open": 100 + i,
                "high": 101 + i,
                "low": 99 + i,
                "close": 100.5 + i,
                "volume": 1000 + i * 100,
                "session": "regular",
            }
        )
    payload = {"ticker": ticker, "bars_1m": bars, "bars_1d": []}
    (fixtures_tmp_dir / f"bars_{ticker}.json").write_text(json.dumps(payload))


class TestBarsEndpoint:
    def test_happy_path(self, client, db_session, fixtures_tmp_dir):
        _seed_symbol(db_session)
        _write_bars_fixture(fixtures_tmp_dir, "AAPL")
        resp = client.get("/api/tickers/AAPL/bars?timeframe=1m")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ticker"] == "AAPL"
        assert body["timeframe"] == "1m"
        assert len(body["bars"]) == 3
        # Bars should round-trip through Pydantic with the expected shape
        assert "timestamp" in body["bars"][0]
        assert "open" in body["bars"][0]

    def test_lowercase_ticker_is_normalized(self, client, db_session, fixtures_tmp_dir):
        _seed_symbol(db_session)
        _write_bars_fixture(fixtures_tmp_dir, "AAPL")
        resp = client.get("/api/tickers/aapl/bars")
        assert resp.status_code == 200
        assert resp.json()["ticker"] == "AAPL"

    def test_unknown_ticker_returns_404(self, client, db_session, fixtures_tmp_dir):
        _seed_symbol(db_session, "AAPL")
        resp = client.get("/api/tickers/ZZZZ/bars")
        assert resp.status_code == 404
        assert "ZZZZ" in resp.json()["detail"]

    def test_bad_timeframe_returns_422(self, client, db_session, fixtures_tmp_dir):
        _seed_symbol(db_session)
        _write_bars_fixture(fixtures_tmp_dir, "AAPL")
        resp = client.get("/api/tickers/AAPL/bars?timeframe=2m")
        assert resp.status_code == 422

    def test_invalid_ticker_chars_returns_400(self, client, db_session, fixtures_tmp_dir):
        _seed_symbol(db_session)
        resp = client.get("/api/tickers/!!!/bars")
        # FastAPI may resolve path parameter; we expect either 400 or 404
        assert resp.status_code in (400, 404)

    def test_start_after_end_returns_400(self, client, db_session, fixtures_tmp_dir):
        _seed_symbol(db_session)
        _write_bars_fixture(fixtures_tmp_dir, "AAPL")
        resp = client.get(
            "/api/tickers/AAPL/bars",
            params={
                "timeframe": "1m",
                "start": "2026-05-13T15:00:00Z",
                "end": "2026-05-13T14:00:00Z",
            },
        )
        assert resp.status_code == 400

    def test_empty_when_no_fixture(self, client, db_session, fixtures_tmp_dir):
        _seed_symbol(db_session, "AAPL")
        # Symbol exists but fixture file is absent -- provider returns empty list.
        resp = client.get("/api/tickers/AAPL/bars")
        assert resp.status_code == 200
        assert resp.json()["bars"] == []
