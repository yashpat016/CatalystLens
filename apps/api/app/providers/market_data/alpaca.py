"""Alpaca market-data adapter.

Hits the public Alpaca Market Data v2 endpoint
``GET https://data.alpaca.markets/v2/stocks/{symbol}/bars``. This adapter is
*dormant* unless both ``ALPACA_API_KEY_ID`` and ``ALPACA_API_SECRET_KEY`` are
present in the environment; constructing it without keys raises
``MarketDataProviderError`` so a misconfigured deployment fails loudly instead
of silently returning empty data.

Sprint 1 ships a unit test against a mocked HTTP transport; there is no live
integration test in CI.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.metrics.session import classify_session
from app.providers.market_data.base import MarketDataProviderError
from app.schemas.bar import Bar, Timeframe

log = get_logger("alpaca_provider")

_TIMEFRAME_MAP = {
    "1m": "1Min",
    "5m": "5Min",
    "1h": "1Hour",
    "1d": "1Day",
    "1mo": "1Month",
}

_MAX_PAGE = 10_000


def _calendar_days_for_range(timeframe: Timeframe, *, limit: int | None) -> int:
    """How far back to request so ``limit`` bars can be satisfied."""
    lim = limit or _MAX_PAGE
    if timeframe == "1mo":
        return min(365 * 25, max(365 * 8, int(lim * 31) + 90))
    if timeframe == "1d":
        return min(365 * 8, max(400, int(lim * 1.55) + 60))
    if timeframe == "1h":
        return min(365 * 3, max(90, int(lim / 6.5) + 30))
    if timeframe == "5m":
        return min(400, max(60, int(lim / 78) + 14))
    # 1m
    return min(30, max(7, int(lim / 250) + 3))


def _default_range(
    timeframe: Timeframe,
    *,
    limit: int | None,
) -> tuple[datetime, datetime]:
    """Alpaca returns empty ``bars`` without ``start``/``end``; pick a sensible window."""
    end = datetime.now(timezone.utc)
    days = _calendar_days_for_range(timeframe, limit=limit)
    start = end - timedelta(days=days)
    return start, end


class AlpacaMarketDataProvider:
    name = "alpaca"

    def __init__(
        self,
        *,
        api_key_id: str | None = None,
        api_secret_key: str | None = None,
        base_url: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key_id = (
            settings.alpaca_api_key_id if api_key_id is None else api_key_id
        )
        self.api_secret_key = (
            settings.alpaca_api_secret_key if api_secret_key is None else api_secret_key
        )
        self.base_url = (base_url or settings.alpaca_data_base_url).rstrip("/")

        if not self.api_key_id or not self.api_secret_key:
            raise MarketDataProviderError(
                "AlpacaMarketDataProvider requires ALPACA_API_KEY_ID and "
                "ALPACA_API_SECRET_KEY to be set."
            )

        self._client = client or httpx.Client(
            base_url=self.base_url,
            timeout=httpx.Timeout(30.0),
        )
        self._auth_headers = {
            "APCA-API-KEY-ID": self.api_key_id,
            "APCA-API-SECRET-KEY": self.api_secret_key,
            "Accept": "application/json",
        }

    def get_bars(
        self,
        symbol: str,
        *,
        timeframe: Timeframe = "1m",
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> list[Bar]:
        alpaca_tf = _TIMEFRAME_MAP.get(timeframe)
        if alpaca_tf is None:
            raise MarketDataProviderError(f"Unsupported timeframe: {timeframe}")

        if start is None and end is None:
            start, end = _default_range(timeframe, limit=limit)

        target = min(limit or _MAX_PAGE, _MAX_PAGE)
        params: dict[str, str | int] = {
            "timeframe": alpaca_tf,
            "feed": "iex",
            "sort": "asc",
        }
        if start is not None:
            params["start"] = start.isoformat().replace("+00:00", "Z")
        if end is not None:
            params["end"] = end.isoformat().replace("+00:00", "Z")

        all_raw: list[dict] = []
        page_token: str | None = None

        while len(all_raw) < target:
            page_params = dict(params)
            if page_token:
                page_params["page_token"] = page_token
            else:
                page_params["limit"] = min(_MAX_PAGE, target - len(all_raw))

            try:
                response = self._client.get(
                    f"/v2/stocks/{symbol.upper()}/bars",
                    params=page_params,
                    headers=self._auth_headers,
                )
            except httpx.HTTPError as exc:
                log.error("alpaca_http_error", error=str(exc), symbol=symbol)
                raise MarketDataProviderError(str(exc)) from exc

            if response.status_code != 200:
                log.error(
                    "alpaca_bad_status",
                    status=response.status_code,
                    body=response.text[:512],
                    symbol=symbol,
                )
                raise MarketDataProviderError(
                    f"Alpaca returned {response.status_code}: {response.text[:200]}"
                )

            payload = response.json()
            batch: list[dict] = list(payload.get("bars") or [])
            all_raw.extend(batch)
            page_token = payload.get("next_page_token")
            if not page_token or not batch:
                break

        if limit is not None and len(all_raw) > limit:
            all_raw = all_raw[-limit:]

        return [self._normalize(b) for b in all_raw]

    @staticmethod
    def _normalize(raw: dict) -> Bar:
        ts = datetime.fromisoformat(str(raw["t"]).replace("Z", "+00:00"))
        return Bar(
            timestamp=ts,
            open=Decimal(str(raw["o"])),
            high=Decimal(str(raw["h"])),
            low=Decimal(str(raw["l"])),
            close=Decimal(str(raw["c"])),
            volume=int(raw["v"]),
            vwap=Decimal(str(raw["vw"])) if "vw" in raw and raw["vw"] is not None else None,
            trade_count=int(raw["n"]) if "n" in raw and raw["n"] is not None else None,
            session=classify_session(ts),
        )
