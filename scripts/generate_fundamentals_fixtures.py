"""Generate deterministic fundamentals fixtures for every watchlist ticker.

Produces ``fundamentals_{TICKER}.json`` with 20 quarters (~5 years) + upcoming earnings.

Run from repo root::

    PYTHONPATH=apps/api:. python scripts/generate_fundamentals_fixtures.py
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
from scripts.fixture_profiles import fundamentals_profile
from scripts.watchlist_loader import load_watchlist

setup_logging("INFO")
log = get_logger("generate_fundamentals_fixtures")

QUARTERS_BACK = 20


def _q(x: float, places: int = 4) -> str:
    return str(Decimal(str(x)).quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP))


def _surprise_pct(actual: float, estimate: float) -> float | None:
    if estimate == 0:
        return None
    return round((actual - estimate) / abs(estimate) * 100, 2)


def _generate_periods(ticker: str, cfg: dict, today: date) -> list[dict]:
    rng = random.Random(abs(hash((ticker, "fundamentals"))) & 0x7FFFFFFF)
    periods: list[dict] = []

    year = today.year
    quarter = (today.month - 1) // 3
    if quarter == 0:
        quarter = 4
        year -= 1

    eps = cfg["base_eps"]
    rev_b = cfg["base_revenue_b"]
    stock = cfg.get("base_stock_price", 100.0)
    debt_b = cfg.get("base_debt_b", 50.0)

    for _ in range(QUARTERS_BACK):
        q_end_month = quarter * 3
        period_end = date(year, q_end_month, 28 if q_end_month == 2 else 30)
        if q_end_month == 6:
            period_end = date(year, 6, 30)
        if q_end_month == 9:
            period_end = date(year, 9, 30)
        if q_end_month == 12:
            period_end = date(year, 12, 31)
        if q_end_month == 3:
            period_end = date(year, 3, 31)

        report_date = period_end + timedelta(days=rng.randint(28, 45))
        report_time = rng.choice(["amc", "bmo"])

        eps_est = eps * (1 + rng.uniform(-0.03, 0.03))
        beat_roll = rng.random()
        if beat_roll > 0.35:
            eps_act = eps_est * (1 + rng.uniform(0.01, 0.08))
        else:
            eps_act = eps_est * (1 - rng.uniform(0.01, 0.06))

        rev_est = rev_b * (1 + rng.uniform(-0.02, 0.02))
        rev_act = (
            rev_est * (1 + rng.uniform(0.01, 0.04))
            if eps_act >= eps_est
            else rev_est * (1 - rng.uniform(0.01, 0.04))
        )
        rev_est = max(rev_est, 0.01)
        rev_act = max(rev_act, 0.01)

        gm = cfg["gross_margin"] + rng.uniform(-1.5, 1.5)
        om = cfg["oper_margin"] + rng.uniform(-1.0, 1.0)
        nm = cfg["net_margin"] + rng.uniform(-0.8, 0.8)

        stock_move = 1 + rng.uniform(-0.06, 0.10) * (1 if eps_act >= eps_est else -1)
        stock = max(stock * stock_move, 1.0)

        fcf_b = rev_act * rng.uniform(0.12, 0.28) * (1 if nm > 15 else 0.85)
        debt_b = max(debt_b * (1 + rng.uniform(-0.02, 0.04)), 0.5)

        periods.append(
            {
                "fiscal_year": year,
                "fiscal_quarter": quarter,
                "period_end": period_end.isoformat(),
                "report_date": report_date.isoformat(),
                "report_time": report_time,
                "eps_actual": _q(eps_act, 2),
                "eps_estimate": _q(eps_est, 2),
                "eps_surprise_pct": _q(_surprise_pct(eps_act, eps_est) or 0, 2),
                "beat": eps_act >= eps_est,
                "revenue": str(int(rev_act * 1_000_000_000)),
                "revenue_estimate": str(int(rev_est * 1_000_000_000)),
                "revenue_surprise_pct": _q(_surprise_pct(rev_act, rev_est) or 0, 2),
                "gross_margin_pct": _q(gm, 1),
                "operating_margin_pct": _q(om, 1),
                "net_margin_pct": _q(nm, 1),
                "quarter_end_price": _q(stock, 2),
                "free_cash_flow": str(int(fcf_b * 1_000_000_000)),
                "total_debt": str(int(debt_b * 1_000_000_000)),
            }
        )

        eps = eps_act * (1 + rng.uniform(-0.02, 0.06))
        rev_b = rev_act

        quarter -= 1
        if quarter == 0:
            quarter = 4
            year -= 1

    periods.reverse()
    return periods


def _upcoming(ticker: str, today: date, last_period: dict) -> dict:
    rng = random.Random(abs(hash((ticker, "upcoming"))) & 0x7FFFFFFF)
    days_ahead = rng.randint(7, 45)
    report_date = today + timedelta(days=days_ahead)

    last_eps = float(last_period["eps_actual"])
    last_rev = max(int(last_period["revenue"]) / 1_000_000_000, 0.01)

    fy = last_period["fiscal_year"]
    fq = last_period["fiscal_quarter"] + 1
    if fq > 4:
        fq = 1
        fy += 1

    return {
        "report_date": report_date.isoformat(),
        "report_time": rng.choice(["amc", "bmo"]),
        "fiscal_year": fy,
        "fiscal_quarter": fq,
        "eps_estimate": _q(last_eps * (1 + rng.uniform(0.02, 0.08)), 2),
        "revenue_estimate": str(
            int(max(last_rev * (1 + rng.uniform(0.01, 0.05)), 0.01) * 1_000_000_000)
        ),
        "analyst_count": rng.randint(8, 42),
    }


def main() -> int:
    out_path = Path(settings.fixtures_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    today = date.today()

    for entry in load_watchlist():
        ticker = entry["ticker"]
        cfg = fundamentals_profile(ticker, entry["company_name"])
        periods = _generate_periods(ticker, cfg, today)
        upcoming = _upcoming(ticker, today, periods[-1])
        payload = {
            "ticker": ticker,
            "company_name": cfg["company_name"],
            "currency": "USD",
            "periods": periods,
            "upcoming_earnings": upcoming,
        }
        path = out_path / f"fundamentals_{ticker}.json"
        path.write_text(json.dumps(payload, indent=2))
        log.info("fundamentals_written", ticker=ticker, path=str(path), periods=len(periods))
    return 0


if __name__ == "__main__":
    sys.exit(main())
