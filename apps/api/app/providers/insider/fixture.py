"""Fixture-backed insider (Form 4 style) provider."""

from __future__ import annotations

import json
from pathlib import Path

from app.core.logging import get_logger
from app.schemas.insider import InsiderResponse

log = get_logger("fixture_insider")


class FixtureInsiderProvider:
    name = "fixture"

    def __init__(self, fixtures_dir: str | Path) -> None:
        self.fixtures_dir = Path(fixtures_dir)

    def get_insider(self, symbol: str) -> InsiderResponse | None:
        symbol_u = symbol.upper()
        path = self.fixtures_dir / f"insider_{symbol_u}.json"
        if not path.exists():
            log.warning("insider_fixture_missing", ticker=symbol_u, path=str(path))
            return None
        try:
            raw = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            log.error("insider_fixture_invalid", ticker=symbol_u, error=str(exc))
            return None
        return InsiderResponse.model_validate(raw)
