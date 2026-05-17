"""Bootstrap local SQLite DB + fixture files for dev without Docker.

Usage::

    export DATABASE_URL=sqlite:////tmp/catalystlens.db
    export FIXTURES_DIR=apps/api/app/fixtures
    PYTHONPATH=apps/api:. python scripts/bootstrap_local.py
"""

from __future__ import annotations

import os
import sys

# Ensure repo root is on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "apps", "api"))
sys.path.insert(0, ROOT)

os.environ.setdefault("DATABASE_URL", f"sqlite:///{ROOT}/.local/catalystlens.db")
os.environ.setdefault("FIXTURES_DIR", os.path.join(ROOT, "apps", "api", "app", "fixtures"))

from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core import config as config_module
from app.db.base import Base
import app.models  # noqa: F401
from app.models import Symbol


def main() -> int:
    config_module.get_settings.cache_clear()
    settings = config_module.get_settings()

    db_path = settings.database_url.replace("sqlite:///", "")
    if db_path and not db_path.startswith(":"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(settings.database_url, future=True)
    Base.metadata.create_all(engine)

    from scripts.watchlist_loader import load_watchlist

    with Session(engine) as db:
        for spec in load_watchlist():
            if db.scalar(select(Symbol).where(Symbol.ticker == spec["ticker"])) is None:
                db.add(Symbol(**spec, active=True))
        db.commit()

    print("DB ready:", settings.database_url)
    print("Fixtures dir:", settings.fixtures_dir)

    from scripts import (
        generate_fixtures,
        generate_fundamentals_fixtures,
        generate_institutional_fixtures,
    )

    generate_fixtures.main()
    generate_fundamentals_fixtures.main()
    generate_institutional_fixtures.main()
    print("Bootstrap complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
