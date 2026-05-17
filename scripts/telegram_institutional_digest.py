#!/usr/bin/env python3
"""Format institutional (13F-style) changes for Telegram / OpenClaw cron.

Uses CatalystLens API (fixture or live when available).

    python scripts/telegram_institutional_digest.py
    python scripts/telegram_institutional_digest.py --ticker OSCR
    API_BASE=http://127.0.0.1:8000 python scripts/telegram_institutional_digest.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WATCHLIST_PATH = ROOT / "config" / "watchlist.json"


def _api_base() -> str:
    return os.environ.get("API_BASE", "http://127.0.0.1:8000").rstrip("/")


def _fetch_institutional(ticker: str) -> dict | None:
    url = f"{_api_base()}/api/tickers/{ticker.upper()}/institutional"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"⚠️ {ticker}: HTTP {e.code}", file=sys.stderr)
        return None
    except OSError as e:
        print(f"⚠️ {ticker}: {e}", file=sys.stderr)
        return None


def _fmt_shares(n: int | None) -> str:
    if n is None:
        return "—"
    sign = "+" if n > 0 else ""
    return f"{sign}{n:,}"


def _format_ticker(data: dict) -> str:
    t = data.get("ticker", "?")
    flow = data.get("aggregate_flow", "unchanged")
    net = data.get("net_shares_change_qoq")
    as_of = data.get("data_as_of", "")
    filed = data.get("filed_through", "")
    is_fixture = data.get("source", "").endswith("fixture") or "fixture" in str(
        data.get("data_notes", [])
    ).lower()

    lines = [f"🏦 **{t}** — Institutional (13F-style QoQ)"]
    if as_of:
        lines.append(f"Period data as of {as_of} · filed through {filed}")
    lines.append(f"Aggregate: **{flow}** · net shares {_fmt_shares(net)}")
    if is_fixture:
        lines.append("⚠️ _Demo fixture — verify on SEC when live_")

    increased = []
    decreased = []
    for h in data.get("holders") or []:
        act = h.get("activity", "unchanged")
        name = h.get("manager_name", "?")
        delta = h.get("shares_change_qoq")
        flow_px = h.get("implied_flow_price_usd")
        px = f" @ ~${flow_px} implied" if flow_px else ""
        row = f"• {name} — {_fmt_shares(delta)} sh{px}"
        if act in ("increased", "new"):
            increased.append(row)
        elif act in ("decreased", "closed"):
            decreased.append(row)

    if increased:
        lines.append("\n▲ **Increased / New**")
        lines.extend(increased[:8])
    if decreased:
        lines.append("\n▼ **Decreased / Closed**")
        lines.extend(decreased[:8])

    lines.append("\n📈 _Price targets: not in API yet — use X search (see docs/TELEGRAM_ALERTS.md)_")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Institutional digest for Telegram")
    parser.add_argument("--ticker", help="Single ticker only")
    args = parser.parse_args()

    if args.ticker:
        tickers = [args.ticker.upper()]
    else:
        raw = json.loads(WATCHLIST_PATH.read_text())
        tickers = [e["ticker"].upper() for e in raw]

    print(f"📊 CatalystLens institutional digest · API {_api_base()}\n")
    any_ok = False
    for t in tickers:
        data = _fetch_institutional(t)
        if not data:
            continue
        any_ok = True
        print(_format_ticker(data))
        print()

    if not any_ok:
        print("No data — is the API running? curl http://127.0.0.1:8000/api/health")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
