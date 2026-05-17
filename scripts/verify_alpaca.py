"""Verify Alpaca market-data credentials and print a sample bar.

Usage (from repo root)::

    PYTHONPATH=apps/api:. python scripts/verify_alpaca.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "apps", "api"))
sys.path.insert(0, ROOT)

from app.core import config as config_module
from app.providers.market_data.alpaca import AlpacaMarketDataProvider
from app.providers.market_data.base import MarketDataProviderError


def main() -> int:
    config_module.get_settings.cache_clear()
    s = config_module.get_settings()

    if not s.alpaca_api_key_id:
        print("FAIL: ALPACA_API_KEY_ID is empty in .env")
        return 1
    if not s.alpaca_api_secret_key:
        print("FAIL: ALPACA_API_SECRET_KEY is empty in .env")
        print("  Open https://app.alpaca.markets → Paper → API Keys")
        print("  Copy the Secret Key into .env (never paste it in chat).")
        return 1

    try:
        provider = AlpacaMarketDataProvider()
    except MarketDataProviderError as exc:
        print(f"FAIL: {exc}")
        return 1

    bars = provider.get_bars("AAPL", timeframe="1d", limit=3)
    if not bars:
        print("FAIL: Alpaca returned no bars (check plan/feed limits).")
        return 1

    latest = bars[-1]
    print("OK: Alpaca market data works.")
    print(f"  Provider: {provider.name}")
    print(f"  Base URL: {provider.base_url}")
    print(f"  Latest AAPL 1d bar: {latest.timestamp.date()} close={latest.close}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
