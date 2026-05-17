"""Unit tests for FixtureMarketDataProvider."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.providers.market_data.fixture import FixtureMarketDataProvider


def write_fixture(tmp_path: Path, ticker: str, bars_1m: list[dict], bars_1d: list[dict] | None = None) -> Path:
    payload = {"ticker": ticker, "bars_1m": bars_1m, "bars_1d": bars_1d or []}
    path = tmp_path / f"bars_{ticker}.json"
    path.write_text(json.dumps(payload))
    return path


def make_bar_dict(
    ts: datetime, *, o: float = 100, h: float = 101, low: float = 99, c: float = 100.5, v: int = 1000, session: str = "regular"
) -> dict:
    return {
        "timestamp": ts.isoformat().replace("+00:00", "Z"),
        "open": o,
        "high": h,
        "low": low,
        "close": c,
        "volume": v,
        "session": session,
    }


class TestFixtureProvider:
    def test_missing_file_returns_empty(self, tmp_path):
        provider = FixtureMarketDataProvider(fixtures_dir=tmp_path)
        assert provider.get_bars("AAPL") == []

    def test_invalid_json_returns_empty(self, tmp_path):
        (tmp_path / "bars_AAPL.json").write_text("not json")
        provider = FixtureMarketDataProvider(fixtures_dir=tmp_path)
        assert provider.get_bars("AAPL") == []

    def test_reads_1m_bars(self, tmp_path):
        ts = datetime(2026, 5, 13, 13, 30, tzinfo=timezone.utc)
        write_fixture(tmp_path, "AAPL", [make_bar_dict(ts)])
        provider = FixtureMarketDataProvider(fixtures_dir=tmp_path)
        bars = provider.get_bars("AAPL", timeframe="1m")
        assert len(bars) == 1
        assert bars[0].timestamp == ts

    def test_case_insensitive_ticker(self, tmp_path):
        ts = datetime(2026, 5, 13, 13, 30, tzinfo=timezone.utc)
        write_fixture(tmp_path, "AAPL", [make_bar_dict(ts)])
        provider = FixtureMarketDataProvider(fixtures_dir=tmp_path)
        assert len(provider.get_bars("aapl")) == 1

    def test_start_end_filter(self, tmp_path):
        bars = [
            make_bar_dict(datetime(2026, 5, 13, 13, 30, tzinfo=timezone.utc)),
            make_bar_dict(datetime(2026, 5, 13, 13, 31, tzinfo=timezone.utc)),
            make_bar_dict(datetime(2026, 5, 13, 13, 32, tzinfo=timezone.utc)),
        ]
        write_fixture(tmp_path, "AAPL", bars)
        provider = FixtureMarketDataProvider(fixtures_dir=tmp_path)
        out = provider.get_bars(
            "AAPL",
            start=datetime(2026, 5, 13, 13, 31, tzinfo=timezone.utc),
            end=datetime(2026, 5, 13, 13, 32, tzinfo=timezone.utc),
        )
        assert len(out) == 1
        assert out[0].timestamp.minute == 31

    def test_limit_keeps_most_recent(self, tmp_path):
        bars = [
            make_bar_dict(datetime(2026, 5, 13, 13, 30 + i, tzinfo=timezone.utc))
            for i in range(5)
        ]
        write_fixture(tmp_path, "AAPL", bars)
        provider = FixtureMarketDataProvider(fixtures_dir=tmp_path)
        out = provider.get_bars("AAPL", limit=2)
        assert len(out) == 2
        # the last two minutes (34, 33) should be returned in chronological order
        assert out[0].timestamp.minute == 33
        assert out[1].timestamp.minute == 34

    def test_5m_aggregation_groups_correctly(self, tmp_path):
        # Five consecutive 1m bars in the same 5-minute bucket plus one new one.
        # Volume should sum, high/low should aggregate.
        base = datetime(2026, 5, 13, 13, 30, tzinfo=timezone.utc)
        bars = [
            make_bar_dict(base.replace(minute=30), o=100, h=101, low=99, c=100, v=1000),
            make_bar_dict(base.replace(minute=31), o=100, h=102, low=99, c=101, v=1100),
            make_bar_dict(base.replace(minute=32), o=101, h=103, low=100, c=102, v=900),
            make_bar_dict(base.replace(minute=33), o=102, h=104, low=101, c=103, v=1200),
            make_bar_dict(base.replace(minute=34), o=103, h=105, low=102, c=104, v=800),
            make_bar_dict(base.replace(minute=35), o=104, h=106, low=103, c=105, v=700),
        ]
        write_fixture(tmp_path, "AAPL", bars)
        provider = FixtureMarketDataProvider(fixtures_dir=tmp_path)
        out = provider.get_bars("AAPL", timeframe="5m")
        # First bucket: minutes 30-34 (5 bars). Second bucket: minute 35.
        assert len(out) == 2
        first = out[0]
        assert first.volume == 1000 + 1100 + 900 + 1200 + 800
        assert int(first.high) == 105
        assert int(first.low) == 99
        # open from first bar, close from last bar in bucket
        assert int(first.open) == 100
        assert int(first.close) == 104

    def test_reads_1d_bars(self, tmp_path):
        ts = datetime(2026, 5, 13, 13, 30, tzinfo=timezone.utc)
        write_fixture(
            tmp_path,
            "AAPL",
            bars_1m=[],
            bars_1d=[make_bar_dict(ts, v=100_000_000)],
        )
        provider = FixtureMarketDataProvider(fixtures_dir=tmp_path)
        bars = provider.get_bars("AAPL", timeframe="1d")
        assert len(bars) == 1
        assert bars[0].volume == 100_000_000
