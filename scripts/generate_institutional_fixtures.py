"""Generate deterministic institutional (13F-style) fixtures for every watchlist ticker.

Produces ``institutional_{TICKER}.json``. Run::

    PYTHONPATH=apps/api:. python scripts/generate_institutional_fixtures.py
"""

from __future__ import annotations

import json
import random
import sys
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from scripts.fixture_profiles import institutional_profile
from scripts.watchlist_loader import load_watchlist

setup_logging("INFO")
log = get_logger("generate_institutional_fixtures")

DATA_NOTES = [
    "Source model: SEC Form 13F-HR (quarterly institutional holdings).",
    "Filings lag the quarter end by up to ~45 days; this is not real-time flow.",
    "SEC filings report shares and market value at quarter end, not trade tickets.",
    "implied_position_price_usd = market_value ÷ shares (quarter-end mark, not cost basis).",
    "implied_flow_price_usd = value_change ÷ shares_change when a manager added or trimmed.",
    "Demo fixture — not sourced from live SEC filings.",
]

MANAGERS = [
    ("Vanguard Group Inc", "0000102909"),
    ("BlackRock Inc.", "0001364742"),
    ("State Street Corp", "0000093751"),
    ("Fidelity Management & Research Co LLC", "0000315066"),
    ("Geode Capital Management, L.L.C.", "0001214717"),
    ("Morgan Stanley", "0000895421"),
    ("JPMorgan Chase & Co", "0000019617"),
    ("Bank of America Corp /DE/", "0000070858"),
    ("Northern Trust Corp", "0000073124"),
    ("Goldman Sachs Group Inc", "0000886982"),
    ("Norges Bank", "0001383445"),
    ("Capital Research Global Investors", "0001113169"),
]


def _q(x: float, places: int = 2) -> str:
    return str(Decimal(str(x)).quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP))


def _last_quarter_end(today: date) -> date:
    month = today.month
    q_end_month = ((month - 1) // 3) * 3
    if q_end_month == 0:
        return date(today.year - 1, 12, 31)
    return date(today.year, q_end_month, 1) - timedelta(days=1)


def _activity(shares_change: int, prev_shares: int) -> str:
    if prev_shares == 0 and shares_change > 0:
        return "new"
    if shares_change > 0:
        return "increased"
    if shares_change < 0:
        return "decreased"
    if prev_shares > 0 and shares_change == -prev_shares:
        return "closed"
    return "unchanged"


def _aggregate_flow(net_change: int) -> str:
    if net_change > 0:
        return "net_buying"
    if net_change < 0:
        return "net_selling"
    return "unchanged"


def _generate_holders(
    ticker: str, cfg: dict, period_end: date, filed_through: date
) -> tuple[list[dict], dict]:
    rng = random.Random(abs(hash((ticker, period_end.isoformat()))) & 0x7FFFFFFF)
    price = cfg["base_price"] * (1 + rng.uniform(-0.04, 0.06))
    total_out = max(int(cfg["total_shares_out_m"] * 1_000_000), 1)
    inst_target = max(int(total_out * cfg["institutional_pct"] / 100), 1)

    weights = [rng.uniform(0.6, 1.4) for _ in MANAGERS[:10]]
    w_sum = sum(weights)
    holders: list[dict] = []
    allocated = 0

    for i, (name, cik) in enumerate(MANAGERS[:10]):
        if i == 9:
            shares = max(inst_target - allocated, 0)
        else:
            shares = int(inst_target * (weights[i] / w_sum))
            allocated += shares

        prev_shares = int(shares * rng.uniform(0.88, 1.12))
        shares_change = shares - prev_shares
        value = shares * price
        value_change = shares_change * price * rng.uniform(0.95, 1.05)
        activity = _activity(shares_change, prev_shares)

        implied_position = price
        implied_flow = None
        if shares_change != 0:
            implied_flow = abs(value_change / shares_change)

        holders.append(
            {
                "manager_name": name,
                "cik": cik,
                "shares": shares,
                "market_value_usd": _q(value, 0),
                "shares_change_qoq": shares_change,
                "value_change_usd": _q(value_change, 0),
                "activity": activity,
                "implied_position_price_usd": _q(implied_position),
                "implied_flow_price_usd": _q(implied_flow) if implied_flow is not None else None,
                "pct_of_outstanding": _q(shares / total_out * 100, 3),
                "filing_date": (filed_through - timedelta(days=rng.randint(0, 12))).isoformat(),
            }
        )

    holders.sort(key=lambda h: int(h["shares"]), reverse=True)
    net_change = sum(h["shares_change_qoq"] for h in holders)
    net_value = sum(float(h["value_change_usd"]) for h in holders)
    summary = {
        "net_shares_change_qoq": net_change,
        "net_value_change_usd": _q(net_value, 0),
        "aggregate_flow": _aggregate_flow(net_change),
        "total_shares": sum(h["shares"] for h in holders),
        "total_market_value_usd": _q(sum(float(h["market_value_usd"]) for h in holders), 0),
    }
    return holders, summary


def _quarter_history(ticker: str, cfg: dict, latest_end: date) -> list[dict]:
    history: list[dict] = []
    end = latest_end
    for _ in range(4):
        filed = end + timedelta(days=45)
        holders, summary = _generate_holders(ticker, cfg, end, filed)
        history.append(
            {
                "period_end": end.isoformat(),
                "filed_through": filed.isoformat(),
                "holder_count": len(holders),
                "total_shares": summary["total_shares"],
                "total_market_value_usd": summary["total_market_value_usd"],
                "net_shares_change_qoq": summary["net_shares_change_qoq"],
                "net_value_change_usd": summary["net_value_change_usd"],
                "aggregate_flow": summary["aggregate_flow"],
            }
        )
        if end.month <= 3:
            end = date(end.year - 1, 12, 31)
        else:
            end = date(end.year, end.month - 3, 1) - timedelta(days=1)
            if end.month not in (3, 6, 9, 12):
                end = date(end.year, ((end.month - 1) // 3) * 3 + 1, 1) - timedelta(days=1)
    return list(reversed(history))


def build_payload(ticker: str, cfg: dict, today: date) -> dict:
    period_end = _last_quarter_end(today)
    filed_through = period_end + timedelta(days=42)
    holders, summary = _generate_holders(ticker, cfg, period_end, filed_through)
    return {
        "ticker": ticker,
        "company_name": cfg["company_name"],
        "source": "fixture_sec_13f_hr",
        "data_as_of": period_end.isoformat(),
        "filed_through": filed_through.isoformat(),
        "data_notes": DATA_NOTES,
        "aggregate_flow": summary["aggregate_flow"],
        "net_shares_change_qoq": summary["net_shares_change_qoq"],
        "net_value_change_usd": summary["net_value_change_usd"],
        "holders": holders,
        "quarter_history": _quarter_history(ticker, cfg, period_end),
    }


def main() -> int:
    out_path = Path(settings.fixtures_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    today = date.today()

    for entry in load_watchlist():
        ticker = entry["ticker"]
        cfg = institutional_profile(ticker, entry["company_name"])
        payload = build_payload(ticker, cfg, today)
        path = out_path / f"institutional_{ticker}.json"
        path.write_text(json.dumps(payload, indent=2))
        log.info("wrote_institutional_fixture", ticker=ticker, path=str(path))

    return 0


if __name__ == "__main__":
    sys.exit(main())
