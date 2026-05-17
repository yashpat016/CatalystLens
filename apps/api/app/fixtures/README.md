# Bar fixtures

`bars_{TICKER}.json` files in this directory are produced at runtime by
`scripts/generate_fixtures.py` (run via `make seed`). They are intentionally
not checked into version control -- regenerating is fast and the content
shifts with the trading calendar.

Layout of each file:

```json
{
  "ticker": "AAPL",
  "generated_at": "2026-05-13T03:48:21Z",
  "bars_1m": [{"timestamp": "...", "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 0, "session": "regular"}],
  "bars_1d": [...]
}
```

`FixtureMarketDataProvider` (see `app/providers/market_data/fixture.py`) reads
from these files when `MARKET_DATA_PROVIDER=fixture` (the default).
