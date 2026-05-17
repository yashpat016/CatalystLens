"""Fixture-backed fundamentals provider."""

from __future__ import annotations

import json
from pathlib import Path

from app.core.logging import get_logger
from app.schemas.fundamentals import FundamentalsResponse

log = get_logger("fixture_fundamentals")


class FixtureFundamentalsProvider:
    name = "fixture"

    def __init__(self, fixtures_dir: str | Path) -> None:
        self.fixtures_dir = Path(fixtures_dir)

    def get_fundamentals(self, symbol: str) -> FundamentalsResponse | None:
        symbol_u = symbol.upper()
        path = self.fixtures_dir / f"fundamentals_{symbol_u}.json"
        if not path.exists():
            log.warning("fundamentals_fixture_missing", ticker=symbol_u, path=str(path))
            return None
        try:
            raw = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            log.error("fundamentals_fixture_invalid", ticker=symbol_u, error=str(exc))
            return None
        return FundamentalsResponse.model_validate(raw)
