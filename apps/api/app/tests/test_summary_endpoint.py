"""Tests for the GET /api/tickers/{ticker}/summary endpoint."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from app.models import Symbol


def _seed_symbol(db_session, ticker: str = "AAPL") -> None:
    db_session.add(
        Symbol(
            ticker=ticker,
            exchange="NASDAQ",
            company_name="Apple Inc.",
            sector="Technology",
            industry="Consumer Electronics",
            active=True,
        )
    )
    db_session.commit()


def _bar(ts: datetime, *, open_: float, close: float, volume: int, session: str = "regular") -> dict:
    return {
        "timestamp": ts.isoformat().replace("+00:00", "Z"),
        "open": open_,
        "high": max(open_, close) + 0.5,
        "low": min(open_, close) - 0.5,
        "close": close,
        "volume": volume,
        "session": session,
    }


class TestSummaryEndpoint:
    def test_unknown_ticker_returns_404(self, client, db_session, fixtures_tmp_dir):
        _seed_symbol(db_session, "AAPL")
        resp = client.get("/api/tickers/ZZZZ/summary")
        assert resp.status_code == 404

    def test_basic_shape(self, client, db_session, fixtures_tmp_dir):
        _seed_symbol(db_session, "AAPL")
        # One bar today, regular session
        ts = datetime(2026, 5, 13, 14, 0, tzinfo=timezone.utc)
        bars = [_bar(ts, open_=100.0, close=101.0, volume=1000)]
        (fixtures_tmp_dir / "bars_AAPL.json").write_text(
            json.dumps({"ticker": "AAPL", "bars_1m": bars, "bars_1d": []})
        )
        resp = client.get("/api/tickers/AAPL/summary")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ticker"] == "AAPL"
        assert body["company_name"] == "Apple Inc."
        assert body["exchange"] == "NASDAQ"
        assert body["session"] == "regular"
        # Sprint 1 doesn't populate these yet
        assert body["relative_volume"] is None
        assert body["latest_event"] is None

    def test_change_pct_uses_prior_session_close(self, client, db_session, fixtures_tmp_dir):
        _seed_symbol(db_session, "AAPL")
        # Two days of bars. Prior day final regular close at 100, today's close at 110.
        prior_day = [
            _bar(datetime(2026, 5, 12, 19, 59, tzinfo=timezone.utc), open_=99, close=100, volume=1000)
        ]
        today = [
            _bar(datetime(2026, 5, 13, 14, 0, tzinfo=timezone.utc), open_=105, close=110, volume=2000)
        ]
        (fixtures_tmp_dir / "bars_AAPL.json").write_text(
            json.dumps({"ticker": "AAPL", "bars_1m": prior_day + today, "bars_1d": []})
        )
        resp = client.get("/api/tickers/AAPL/summary")
        assert resp.status_code == 200
        body = resp.json()
        # (110 - 100) / 100 * 100 = 10.0
        assert float(body["change_pct"]) == 10.0

    def test_empty_fixture_returns_null_price(self, client, db_session, fixtures_tmp_dir):
        _seed_symbol(db_session, "AAPL")
        resp = client.get("/api/tickers/AAPL/summary")
        assert resp.status_code == 200
        body = resp.json()
        assert body["price"] is None
        assert body["volume"] is None
        assert body["session"] == "closed"
