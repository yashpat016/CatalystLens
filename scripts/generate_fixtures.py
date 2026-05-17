"""Generate deterministic OHLCV fixture data for AAPL, TSLA, NVDA.

Produces one JSON file per ticker at ``settings.fixtures_dir`` with:

  - ``bars_1m``: every minute from 04:00 to 20:00 ET for the last
    ``MINUTE_DAYS`` US weekdays (sessions labelled correctly).
  - ``bars_1d``: one bar per US weekday for the last ``DAILY_DAYS`` weekdays.

The walk is seeded by ``(ticker, calendar_day)`` so each day's bars are
reproducible. Re-running the script regenerates the files; values do not change
within a given calendar day.

Run inside the api container:

    docker compose exec api python -m scripts.generate_fixtures
"""

from __future__ import annotations

import json
import math
import random
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.core.time import NY_TZ
from app.metrics.session import classify_session

setup_logging("INFO")
log = get_logger("generate_fixtures")

MINUTE_DAYS = 5  # weekdays of 1-minute bars
DAILY_DAYS = 30  # weekdays of daily bars

# Starting prices for the synthetic random walk. These are NOT fetched from a live
# feed — they only control the rough level of the demo chart. Re-tune when real
# prices drift far from what users expect (e.g. post-split NVDA ~$130–$250 range).
TICKERS: dict[str, dict] = {
    "AAPL": {
        "anchor_price": 298.00,
        "target_close": 298.00,
        "vol_sigma": 0.0012,
        "base_volume": 80_000,
    },
    "TSLA": {
        "anchor_price": 340.00,
        "target_close": 340.00,
        "vol_sigma": 0.0028,
        "base_volume": 120_000,
    },
    "NVDA": {
        "anchor_price": 228.00,
        "target_close": 228.00,
        "vol_sigma": 0.0022,
        "base_volume": 95_000,
    },
}


def _last_weekdays(n: int, reference: date) -> list[date]:
    """Return the last ``n`` weekdays ending at ``reference`` (inclusive if weekday)."""
    out: list[date] = []
    cur = reference
    while len(out) < n:
        if cur.weekday() < 5:
            out.append(cur)
        cur -= timedelta(days=1)
    return list(reversed(out))


def _seed(ticker: str, day: date) -> int:
    """Deterministic seed from ticker + ISO date."""
    return abs(hash((ticker, day.isoformat()))) & 0x7FFFFFFF


def _generate_day_minute_bars(
    ticker: str,
    cfg: dict,
    day: date,
    open_price: float,
) -> tuple[list[dict], float]:
    """Generate 1-minute bars for one weekday (04:00 -> 20:00 ET).

    Returns ``(bars, last_close_price)``.
    """
    rng = random.Random(_seed(ticker, day))
    bars: list[dict] = []

    # 16 hours x 60 minutes = 960 minute bars
    start_local = datetime.combine(day, time(4, 0), tzinfo=NY_TZ)
    end_local = datetime.combine(day, time(20, 0), tzinfo=NY_TZ)

    price = open_price
    t = start_local
    while t < end_local:
        ts_utc = t.astimezone(timezone.utc)
        sess = classify_session(ts_utc)

        sigma = cfg["vol_sigma"]
        step = rng.gauss(0.0, sigma) * price
        new_price = price + step
        intra_range = abs(rng.gauss(0.0, sigma / 1.5)) * price
        hi = max(price, new_price) + intra_range
        lo = min(price, new_price) - intra_range
        lo = max(lo, 0.01)

        if sess == "regular":
            vol = int(rng.uniform(0.5, 1.6) * cfg["base_volume"])
        elif sess in ("premarket", "afterhours"):
            vol = int(rng.uniform(0.05, 0.30) * cfg["base_volume"])
        else:
            vol = 0  # outside trading hours -- shouldn't happen in this range

        bars.append(
            {
                "timestamp": ts_utc.isoformat().replace("+00:00", "Z"),
                "open": round(price, 2),
                "high": round(hi, 2),
                "low": round(lo, 2),
                "close": round(new_price, 2),
                "volume": vol,
                "session": sess,
            }
        )
        price = new_price
        t += timedelta(minutes=1)

    return bars, price


def _generate_daily_bars(ticker: str, cfg: dict, days: list[date]) -> list[dict]:
    """Generate one daily bar per weekday."""
    rng = random.Random(_seed(ticker, days[0]) ^ 0xD41D)
    bars: list[dict] = []
    price = cfg["anchor_price"]
    daily_sigma = cfg["vol_sigma"] * math.sqrt(390.0)  # rough day-vol

    for d in days:
        change = rng.gauss(0.0, daily_sigma) * price
        new_price = max(0.01, price + change)
        hi = max(price, new_price) * (1 + abs(rng.gauss(0, daily_sigma / 2)))
        lo = min(price, new_price) * (1 - abs(rng.gauss(0, daily_sigma / 2)))
        vol = int(rng.uniform(0.6, 1.4) * cfg["base_volume"] * 390)

        # Daily bar timestamp = market open in UTC (09:30 ET).
        ts_local = datetime.combine(d, time(9, 30), tzinfo=NY_TZ)
        ts_utc = ts_local.astimezone(timezone.utc)
        bars.append(
            {
                "timestamp": ts_utc.isoformat().replace("+00:00", "Z"),
                "open": round(price, 2),
                "high": round(hi, 2),
                "low": round(lo, 2),
                "close": round(new_price, 2),
                "volume": vol,
                "session": "regular",
            }
        )
        price = new_price

    return bars


def _rescale_to_target_close(bars: list[dict], target_close: float) -> list[dict]:
    """Scale OHLC so the last bar's close matches ``target_close`` (shape preserved)."""
    if not bars or target_close <= 0:
        return bars
    last_close = float(bars[-1]["close"])
    if last_close <= 0:
        return bars
    factor = target_close / last_close
    for b in bars:
        for key in ("open", "high", "low", "close"):
            b[key] = round(float(b[key]) * factor, 2)
    return bars


def main() -> int:
    out_dir = Path(settings.fixtures_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    today_et = datetime.now(NY_TZ).date()
    # If today is a weekend, use the most recent Friday.
    while today_et.weekday() >= 5:
        today_et -= timedelta(days=1)

    minute_days = _last_weekdays(MINUTE_DAYS, today_et)
    daily_days = _last_weekdays(DAILY_DAYS, today_et)

    for ticker, cfg in TICKERS.items():
        # Walk price across days for the minute bars so closes/opens connect.
        bars_1m: list[dict] = []
        price = cfg["anchor_price"]
        for d in minute_days:
            day_bars, price = _generate_day_minute_bars(ticker, cfg, d, price)
            bars_1m.extend(day_bars)

        bars_1d = _generate_daily_bars(ticker, cfg, daily_days)

        target = cfg.get("target_close")
        if target is not None:
            bars_1m = _rescale_to_target_close(bars_1m, float(target))
            bars_1d = _rescale_to_target_close(bars_1d, float(target))

        payload = {
            "ticker": ticker,
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "bars_1m": bars_1m,
            "bars_1d": bars_1d,
        }
        path = out_dir / f"bars_{ticker}.json"
        path.write_text(json.dumps(payload))
        log.info(
            "fixtures_written",
            ticker=ticker,
            path=str(path),
            bars_1m=len(bars_1m),
            bars_1d=len(bars_1d),
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
