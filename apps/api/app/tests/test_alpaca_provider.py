"""Unit tests for AlpacaMarketDataProvider with a mocked HTTP transport."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import httpx
import pytest

from app.providers.market_data.alpaca import AlpacaMarketDataProvider
from app.providers.market_data.base import MarketDataProviderError


def _client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler), base_url="https://data.alpaca.markets")


class TestAuth:
    def test_missing_keys_raises(self):
        with pytest.raises(MarketDataProviderError):
            AlpacaMarketDataProvider(api_key_id="", api_secret_key="")


class TestGetBars:
    def test_happy_path(self):
        def handler(request: httpx.Request) -> httpx.Response:
            # Verify auth headers are set
            assert request.headers["APCA-API-KEY-ID"] == "key"
            assert request.headers["APCA-API-SECRET-KEY"] == "secret"
            assert "/v2/stocks/AAPL/bars" in str(request.url)
            assert "timeframe=1Min" in str(request.url)
            payload = {
                "bars": [
                    {
                        "t": "2026-05-13T13:30:00Z",
                        "o": 185.10,
                        "h": 185.40,
                        "l": 184.80,
                        "c": 185.20,
                        "v": 12345,
                        "n": 87,
                        "vw": 185.15,
                    }
                ],
                "next_page_token": None,
            }
            return httpx.Response(200, json=payload)

        provider = AlpacaMarketDataProvider(
            api_key_id="key",
            api_secret_key="secret",
            client=_client(handler),
        )
        bars = provider.get_bars("AAPL", timeframe="1m")
        assert len(bars) == 1
        b = bars[0]
        assert b.open == Decimal("185.10")
        assert b.high == Decimal("185.40")
        assert b.volume == 12345
        assert b.trade_count == 87
        # 13:30 UTC on a weekday is regular session
        assert b.session == "regular"

    def test_400_raises_provider_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(400, json={"message": "bad symbol"})

        provider = AlpacaMarketDataProvider(
            api_key_id="key",
            api_secret_key="secret",
            client=_client(handler),
        )
        with pytest.raises(MarketDataProviderError):
            provider.get_bars("???", timeframe="1m")

    def test_empty_response(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"bars": None, "next_page_token": None})

        provider = AlpacaMarketDataProvider(
            api_key_id="key",
            api_secret_key="secret",
            client=_client(handler),
        )
        assert provider.get_bars("AAPL") == []

    def test_limit_uses_asc_sort_and_chronological_order(self):
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            payload = {
                "bars": [
                    {
                        "t": "2026-05-15T19:00:00Z",
                        "o": 1,
                        "h": 1,
                        "l": 1,
                        "c": 1,
                        "v": 1,
                    },
                    {
                        "t": "2026-05-15T20:00:00Z",
                        "o": 2,
                        "h": 2,
                        "l": 2,
                        "c": 2,
                        "v": 1,
                    },
                ],
            }
            return httpx.Response(200, json=payload)

        provider = AlpacaMarketDataProvider(
            api_key_id="key",
            api_secret_key="secret",
            client=_client(handler),
        )
        bars = provider.get_bars("AAPL", timeframe="1m", limit=2)
        assert "sort=asc" in captured["url"]
        assert bars[0].timestamp < bars[1].timestamp
        assert bars[0].open == Decimal("1")

    def test_5m_maps_to_alpaca_timeframe(self):
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            return httpx.Response(200, json={"bars": []})

        provider = AlpacaMarketDataProvider(
            api_key_id="key",
            api_secret_key="secret",
            client=_client(handler),
        )
        provider.get_bars("AAPL", timeframe="5m")
        assert "timeframe=5Min" in captured["url"]
