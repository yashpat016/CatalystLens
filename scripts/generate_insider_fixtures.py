"""Generate Form 4–style insider transaction fixtures (CEO/CFO focus).

CEO names come from ``ceo_name`` in ``config/watchlist.json``. Update that field
when leadership changes, then re-run this script.

    PYTHONPATH=apps/api:. python scripts/generate_insider_fixtures.py
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
from scripts.watchlist_loader import load_watchlist

ROOT = Path(__file__).resolve().parent.parent
ANCHORS_PATH = ROOT / "config" / "insider_anchors.json"

setup_logging("INFO")
log = get_logger("generate_insider_fixtures")

DATA_NOTES = [
    "Modeled after SEC Form 4 insider filings (demo fixture, not live EDGAR).",
    "CEO names are taken from config/watchlist.json (ceo_name) — update there after leadership changes.",
    "Highlights CEO and C-suite open-market buys/sells when present in fixture.",
    "Prices are approximate marks at transaction date for research UI only.",
]


def _q(x: float, places: int = 2) -> str:
    return str(Decimal(str(x)).quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP))


def load_anchors() -> dict[str, list[dict]]:
    if not ANCHORS_PATH.exists():
        return {}
    raw = json.loads(ANCHORS_PATH.read_text())
    out: dict[str, list[dict]] = {}
    for key, val in raw.items():
        if key.startswith("_") or not isinstance(val, list):
            continue
        out[key.upper()] = val
    return out


def _ceo_name(entry: dict) -> str:
    raw = (entry.get("ceo_name") or "").strip()
    if raw and raw != "—":
        return raw
    company = entry.get("company_name") or entry["ticker"]
    return f"{company} CEO"


def generate_for_ticker(
    entry: dict,
    rng: random.Random,
    anchors: dict[str, list[dict]],
) -> dict:
    ticker = entry["ticker"]
    today = date.today()
    # Keep synthetic prices in a plausible band; OSCR trades ~$10–20 (2025–26).
    if ticker == "OSCR":
        base_price = 12.0
    else:
        base_price = 50 + (hash(ticker) % 400)
    ceo = _ceo_name(entry)
    txs = []
    roles = [
        (ceo, "CEO"),
        ("Chief Financial Officer", "CFO"),
        ("Director", "Director"),
    ]
    for i in range(12):
        role_name, role = roles[i % 3]
        if role != "CEO" and rng.random() < 0.35:
            continue
        tx_date = today - timedelta(days=30 * i + rng.randint(0, 20))
        filing = tx_date + timedelta(days=rng.randint(1, 3))
        is_buy = rng.random() > 0.42 if role == "CEO" else rng.random() > 0.55
        tx_type = "buy" if is_buy else "sell"
        shares = rng.randint(500, 80_000) if role == "CEO" else rng.randint(200, 25_000)
        price = base_price * (1 + rng.uniform(-0.15, 0.2))
        value = shares * price
        txs.append(
            {
                "transaction_date": tx_date.isoformat(),
                "filing_date": filing.isoformat(),
                "insider_name": role_name,
                "role": role,
                "transaction_type": tx_type,
                "shares": shares,
                "price_usd": _q(price),
                "value_usd": _q(value),
                "shares_owned_after": shares * rng.randint(5, 40),
            }
        )
    anchored = anchors.get(ticker, [])
    if anchored:
        txs = anchored + txs
    txs.sort(key=lambda t: t["transaction_date"], reverse=True)

    notes = list(DATA_NOTES)
    if anchored:
        notes.insert(
            1,
            "Anchored events in config/insider_anchors.json (manually curated; verify on SEC EDGAR).",
        )

    return {
        "ticker": ticker,
        "source": "sec_form4_fixture",
        "data_as_of": today.isoformat(),
        "data_notes": notes,
        "transactions": txs,
    }


def main() -> int:
    out_dir = Path(settings.fixtures_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    entries = load_watchlist()
    anchors = load_anchors()
    for entry in entries:
        t = entry["ticker"]
        rng = random.Random(hash(t) & 0xFFFFFFFF)
        payload = generate_for_ticker(entry, rng, anchors)
        path = out_dir / f"insider_{t}.json"
        path.write_text(json.dumps(payload, indent=2))
        log.info("wrote_insider_fixture", ticker=t, ceo=_ceo_name(entry), path=str(path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
