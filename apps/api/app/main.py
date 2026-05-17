"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.routers import fundamentals, health, insider, institutional, tickers

setup_logging(settings.log_level)


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application."""

    app = FastAPI(
        title="CatalystLens API",
        version="0.1.0",
        description="Market event and liquidity intelligence backend.",
        docs_url="/docs",
        redoc_url=None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api")
    app.include_router(tickers.router, prefix="/api")
    app.include_router(fundamentals.router, prefix="/api")
    app.include_router(institutional.router, prefix="/api")
    app.include_router(insider.router, prefix="/api")

    return app


app = create_app()
