"""Application settings.

All configuration is loaded from environment variables (with optional ``.env``
support for local development). Settings are kept boring and explicit so the
provider/data-source plumbing stays inspectable.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


_APP_DIR = Path(__file__).resolve().parent.parent  # apps/api/app
_REPO_ROOT = _APP_DIR.parent.parent.parent  # monorepo root (catalystLens/)


def _discover_env_files() -> tuple[str, ...]:
    """Load repo-root ``.env`` first, then ``apps/api/.env`` if present."""
    candidates = (_REPO_ROOT / ".env", _APP_DIR.parent / ".env")
    return tuple(str(p) for p in candidates if p.is_file())


class Settings(BaseSettings):
    """Runtime configuration for the API."""

    # --- Database / cache ---
    database_url: str = Field(
        default="postgresql+psycopg://catalystlens:catalystlens@postgres:5432/catalystlens",
        description="SQLAlchemy URL for the primary database.",
    )
    redis_url: str = Field(default="redis://redis:6379/0")

    # --- Logging ---
    log_level: str = Field(default="INFO")

    # --- Market data provider ---
    market_data_provider: str = Field(
        default="fixture",
        description="Which MarketDataProvider implementation to use ('fixture' or 'alpaca').",
    )
    alpaca_api_key_id: str = Field(default="")
    alpaca_api_secret_key: str = Field(default="")
    alpaca_data_base_url: str = Field(default="https://data.alpaca.markets")

    # --- Fixtures ---
    fixtures_dir: str = Field(
        default=str(_APP_DIR / "fixtures"),
        description="Directory containing fixture JSON files.",
    )

    # --- CORS ---
    cors_allow_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        description="Allowed browser origins for direct API calls (proxy bypass).",
    )

    model_config = SettingsConfigDict(
        env_file=_discover_env_files() or (".env",),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
