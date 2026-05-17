"""Deterministic demo profiles for fundamentals and 13F fixtures per ticker."""

from __future__ import annotations

import random


def _rng(ticker: str, salt: str) -> random.Random:
    return random.Random(abs(hash((ticker.upper(), salt))) & 0x7FFFFFFF)


def fundamentals_profile(ticker: str, company_name: str) -> dict:
    """Build generator config for ``generate_fundamentals_fixtures``."""
    t = ticker.upper()
    rng = _rng(t, "fundamentals")

    if t in ("ETH", "BTC"):
        return {
            "company_name": company_name,
            "base_eps": 0.0,
            "base_revenue_b": 0.05,
            "base_stock_price": 3500.0 if t == "BTC" else 3200.0,
            "base_debt_b": 0.0,
            "gross_margin": 0.0,
            "oper_margin": 0.0,
            "net_margin": 0.0,
        }

    tier = rng.random()
    if tier < 0.25:
        rev = rng.uniform(35.0, 130.0)
        eps = rng.uniform(1.2, 5.5)
        price = rng.uniform(80.0, 350.0)
        debt = rev * rng.uniform(0.4, 1.2)
        gm, om, nm = (
            rng.uniform(38.0, 52.0),
            rng.uniform(22.0, 38.0),
            rng.uniform(18.0, 32.0),
        )
    elif tier < 0.65:
        rev = rng.uniform(1.5, 30.0)
        eps = rng.uniform(0.05, 2.5)
        price = rng.uniform(12.0, 180.0)
        debt = rev * rng.uniform(0.2, 0.9)
        gm, om, nm = (
            rng.uniform(25.0, 65.0),
            rng.uniform(5.0, 25.0),
            rng.uniform(-5.0, 20.0),
        )
    else:
        rev = rng.uniform(0.15, 4.0)
        eps = rng.uniform(-0.8, 0.9)
        price = rng.uniform(3.0, 45.0)
        debt = rev * rng.uniform(0.1, 0.6)
        gm, om, nm = (
            rng.uniform(15.0, 55.0),
            rng.uniform(-15.0, 12.0),
            rng.uniform(-25.0, 8.0),
        )

    return {
        "company_name": company_name,
        "base_eps": round(eps, 2),
        "base_revenue_b": round(rev, 2),
        "base_stock_price": round(price, 2),
        "base_debt_b": round(debt, 2),
        "gross_margin": round(gm, 1),
        "oper_margin": round(om, 1),
        "net_margin": round(nm, 1),
    }


def institutional_profile(ticker: str, company_name: str) -> dict:
    """Build generator config for ``generate_institutional_fixtures``."""
    t = ticker.upper()
    rng = _rng(t, "institutional")

    if t in ("ETH", "BTC"):
        return {
            "company_name": company_name,
            "base_price": 65000.0 if t == "BTC" else 3500.0,
            "total_shares_out_m": 0.02,
            "institutional_pct": 12.0,
        }

    cap_tier = rng.random()
    if cap_tier < 0.25:
        shares_m = rng.uniform(8000, 25000)
        inst_pct = rng.uniform(55.0, 72.0)
        price = rng.uniform(80.0, 350.0)
    elif cap_tier < 0.65:
        shares_m = rng.uniform(400, 8000)
        inst_pct = rng.uniform(38.0, 62.0)
        price = rng.uniform(10.0, 120.0)
    else:
        shares_m = rng.uniform(50, 600)
        inst_pct = rng.uniform(22.0, 48.0)
        price = rng.uniform(3.0, 40.0)

    return {
        "company_name": company_name,
        "base_price": round(price, 2),
        "total_shares_out_m": round(shares_m, 1),
        "institutional_pct": round(inst_pct, 1),
    }
