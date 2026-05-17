"""Seed the ``symbols`` table from ``config/watchlist.json``.

Idempotent: re-running does not duplicate or modify existing rows.

Run from repo root::

    PYTHONPATH=apps/api:. python scripts/seed_symbols.py
"""

from __future__ import annotations

import sys

from sqlalchemy import select

from app.core.logging import get_logger, setup_logging
from app.db.session import SessionLocal
from app.models import Symbol
from scripts.watchlist_loader import load_watchlist as _load_watchlist

setup_logging("INFO")
log = get_logger("seed_symbols")


def main() -> int:
    symbols = _load_watchlist()
    db = SessionLocal()
    try:
        inserted = 0
        for spec in symbols:
            existing = db.scalar(select(Symbol).where(Symbol.ticker == spec["ticker"]))
            if existing is not None:
                log.info("symbol_exists", ticker=spec["ticker"])
                continue
            db.add(Symbol(**spec))
            inserted += 1
            log.info("symbol_inserted", ticker=spec["ticker"])
        db.commit()
        log.info("seed_complete", inserted=inserted, total=len(symbols))
        return 0
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        log.error("seed_failed", error=str(exc))
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
