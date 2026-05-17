"""Fixture-backed institutional (13F-style) provider."""

from __future__ import annotations

import json
from pathlib import Path

from app.core.logging import get_logger
from app.schemas.institutional import InstitutionalResponse

log = get_logger("fixture_institutional")


class FixtureInstitutionalProvider:
    name = "fixture"

    def __init__(self, fixtures_dir: str | Path) -> None:
        self.fixtures_dir = Path(fixtures_dir)

    def get_institutional(self, symbol: str) -> InstitutionalResponse | None:
        symbol_u = symbol.upper()
        path = self.fixtures_dir / f"institutional_{symbol_u}.json"
        if not path.exists():
            log.warning(
                "institutional_fixture_missing",
                ticker=symbol_u,
                path=str(path),
            )
            return None
        try:
            raw = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            log.error("institutional_fixture_invalid", ticker=symbol_u, error=str(exc))
            return None
        return InstitutionalResponse.model_validate(raw)
