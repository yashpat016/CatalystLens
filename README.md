# CatalystLens

Research terminal for watchlist tickers: linked price/volume charts, fundamentals comparisons, institutional (13F-style) holdings, and insider (Form 4–style) activity. **Not trading signals** — context for your own decisions.

**Roadmap & pending work:** [docs/ROADMAP.md](docs/ROADMAP.md)

Stack: **FastAPI** (`apps/api`) + **Next.js 14** (`apps/web`) + SQLite (local) or Postgres (Docker).

---

## Quick start (local, no Docker)

### 1. Environment

```bash
cp .env.example .env
# Edit .env — for live charts set:
#   MARKET_DATA_PROVIDER=alpaca
#   ALPACA_API_KEY_ID=...
#   ALPACA_API_SECRET_KEY=...
```

Never commit `.env` (it is gitignored).

### 2. One-command dev stack

```bash
./scripts/run_local.sh
```

This bootstraps the DB, runs tests, starts:

| Service | URL |
|---------|-----|
| Web UI | http://127.0.0.1:3000 |
| API | http://127.0.0.1:8000 |
| API docs | http://127.0.0.1:8000/docs |

Open a ticker: http://127.0.0.1:3000/ticker/AAPL

### 3. Manual restart (API + web only)

If you already ran setup once:

```bash
# From repo root
kill $(lsof -ti :8000) 2>/dev/null; kill $(lsof -ti :3000) 2>/dev/null

set -a && source .env && set +a
export DATABASE_URL="${DATABASE_URL:-sqlite:///$(pwd)/.local/catalystlens.db}"
export FIXTURES_DIR="${FIXTURES_DIR:-$(pwd)/apps/api/app/fixtures}"
export PYTHONPATH="$(pwd)/apps/api"

# API
cd apps/api && source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 &

# Web (separate terminal)
cd apps/web
rm -rf .next   # if pages are blank/500 after code changes
export API_BASE_URL_INTERNAL=http://127.0.0.1:8000
npm run dev -- -p 3000 -H 127.0.0.1
```

Hard refresh the browser: **Cmd+Shift+R**.

---

## Docker

```bash
cp .env.example .env
make up      # build, migrate, seed fixtures
make down    # stop
make test    # API + web tests
```

Web: http://localhost:3000 · API: http://localhost:8000

---

## Watchlist

Edit `config/watchlist.json` (optional `ceo_name` per ticker for insider fixtures), then re-seed:

```bash
# Local
PYTHONPATH=apps/api:. python scripts/seed_symbols.py

# Docker
make seed
```

`make seed` also regenerates bar, fundamentals, institutional, and insider fixtures.

---

## Price chart

### Timeframes

| Button | Data | Typical window |
|--------|------|----------------|
| **1m** | 1-minute bars | ~2 weeks |
| **5m** | 5-minute bars | ~months |
| **1h** | Hourly bars | ~months |
| **1D** | Daily bars | ~5+ years (Alpaca IEX; paginated) |
| **1M** | Monthly bars | ~10 years |

Default on load: **1D**. Footer shows bar count and date range (e.g. `1374 bars · Nov 2020 → May 2026`).

- **Pan/zoom** on price or volume — both panels stay linked.
- **Autoscale**: opens on a sensible window (e.g. 252 daily bars ≈ 1 trading year). Scroll left for older history.

### Fibonacci retracement

1. Enable **Fib retracement**.
2. Enter **High $** and **Low $** (your swing top and bottom).
3. Lines and a level table appear (0% = high, 100% = low).

**Fill from chart range** copies min/max of loaded bars — optional shortcut only.

### Moving averages

- Toggle **Moving average**.
- **SMA** (simple) or **WMA** (weighted).
- **Period** = number of **bars** on the current timeframe (20 on 1D = 20 days; 20 on 1m = 20 minutes).

### VWAP

Blue line = session-reset VWAP (typical-price approximation from bar data).

### Yahoo Finance

**Yahoo Finance ↗** in the ticker header opens the Yahoo quote page (BTC → `BTC-USD`, ETH → `ETH-USD`).

---

## Other panels (demo fixtures)

| Panel | Source | Notes |
|-------|--------|--------|
| Fundamentals | `fundamentals_{TICKER}.json` | ~5y quarterly; comparison grid + line charts |
| Institutional | `institutional_{TICKER}.json` | 13F-style QoQ flow (not live SEC) |
| Insider | `insider_{TICKER}.json` | Form 4–style CEO/C-suite buys & sells (demo; CEO from `ceo_name` in watchlist) |

Regenerate fixtures:

```bash
PYTHONPATH=apps/api:. python scripts/generate_fundamentals_fixtures.py
PYTHONPATH=apps/api:. python scripts/generate_institutional_fixtures.py
PYTHONPATH=apps/api:. python scripts/generate_insider_fixtures.py
```

After a CEO change, update `ceo_name` in `config/watchlist.json` (and `apps/web/src/data/watchlist.json`), then re-run `generate_insider_fixtures.py`.

---

## Market data providers

| `MARKET_DATA_PROVIDER` | Behavior |
|------------------------|----------|
| `fixture` | JSON under `apps/api/app/fixtures/` — no API keys |
| `alpaca` | Live bars from [Alpaca Market Data](https://alpaca.markets/) (IEX feed on free tier) |

Alpaca keys in `.env`:

```env
MARKET_DATA_PROVIDER=alpaca
ALPACA_API_KEY_ID=...
ALPACA_API_SECRET_KEY=...
ALPACA_DATA_BASE_URL=https://data.alpaca.markets
```

Verify Alpaca:

```bash
PYTHONPATH=apps/api:. python scripts/verify_alpaca.py
```

---

## Troubleshooting

### “No bars in range” / empty chart

1. **API running?** `curl http://127.0.0.1:8000/api/health` → `{"status":"ok",...}`
2. **Proxy working?** `curl http://127.0.0.1:3000/api/health` → same JSON (use **127.0.0.1:3000**, not only localhost, if you hit CORS issues before the proxy fix).
3. **Restart API** after changing `.env` or Alpaca code — old process keeps old behavior.
4. **Unknown ticker?** Run `seed_symbols.py` for your watchlist.
5. **Fixture mode?** Run `make seed` or `generate_fixtures.py`.

### Chart only shows ~1 year on daily

Usually an **old API process** (400-day window). Restart API (see above). After fix, AAPL daily should reach ~2020 on Alpaca IEX.

### Blank / 500 ticker page

```bash
rm -rf apps/web/.next
# restart web dev server
```

### Daily history shorter than expected

Alpaca free **IEX** data has limits; paginated requests return the maximum available (often ~5–6 years for large caps). Premium feeds may extend history.

---

## API (selected)

```
GET /api/health
GET /api/tickers/{ticker}/summary
GET /api/tickers/{ticker}/bars?timeframe=1m|5m|1h|1d|1mo&limit=...
GET /api/tickers/{ticker}/fundamentals
GET /api/tickers/{ticker}/institutional
GET /api/tickers/{ticker}/insider
```

---

## Tests

```bash
# API
cd apps/api && PYTHONPATH=. pytest app/tests -q

# Web
cd apps/web && npm run test:run
```

---

## Hosting on Oracle Cloud + OpenClaw (optional)

Run CatalystLens **alongside** OpenClaw on the same free ARM instance — separate processes, not inside the gateway:

- CatalystLens: `docker compose` or `run_local.sh` on loopback (`127.0.0.1:3000` / `:8000`).
- Expose UI via **Tailscale Serve** (same pattern as OpenClaw docs) — avoid opening public HTTP if the VCN is locked down.
- OpenClaw cron/skills can call `http://127.0.0.1:8000/api/...` for watchlist digests.

Use production Next (`next build` + `next start`) on a VPS; the default Docker web service uses `npm run dev` for development.

---

## Project layout

```
apps/api/          FastAPI, providers, fixtures, Alembic
apps/web/          Next.js UI, charts (lightweight-charts)
config/            watchlist.json
scripts/           seed, fixtures, run_local.sh, verify_alpaca.py
docker-compose.yml
```

---

## Disclaimer

Fundamentals, institutional, and insider sections use **synthetic fixtures** unless you wire live data sources. Price data depends on your configured market provider. This is a research UI, not financial advice.
