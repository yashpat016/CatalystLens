"""Load ``config/watchlist.json`` for fixture generators and seed scripts."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WATCHLIST_PATH = ROOT / "config" / "watchlist.json"
# Keep in sync with apps/web/src/data/watchlist.json (web UI copy).


def load_watchlist() -> list[dict]:
    raw = json.loads(WATCHLIST_PATH.read_text())
    return [
        {
            "ticker": entry["ticker"].upper(),
            "exchange": entry.get("exchange"),
            "company_name": entry.get("company_name") or entry["ticker"],
            "ceo_name": entry.get("ceo_name"),
        }
        for entry in raw
    ]
