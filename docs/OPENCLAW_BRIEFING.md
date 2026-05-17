# CatalystLens — OpenClaw / Oracle briefing

Copy this file (or sections) to OpenClaw via Telegram when deploying or maintaining the app on Oracle Cloud.

**Public repo:** https://github.com/yashpat016/CatalystLens  
**Owner:** yashpat016  
**Purpose:** Research terminal (watchlist charts, fundamentals, 13F-style institutional, Form 4–style insider). Not trading signals.

---

## 1. What OpenClaw should know

- CatalystLens runs **beside** OpenClaw on the same Oracle VM — separate processes.
- **Do not** commit `.env` or paste Alpaca secrets into chat, skills, or `openclaw.json`.
- GitHub repo is **public** — code is visible; **API keys are not in git**.
- Expose UI via **Tailscale Serve** (loopback + tailnet), not public `0.0.0.0:3000` on the internet.
- OpenClaw can: clone repo, edit files, run docker/uvicorn, curl `http://127.0.0.1:8000/api/...`, cron digest scripts.

---

## 2. API keys & secrets (Alpaca)

### What they are

| Variable | Purpose |
|----------|---------|
| `MARKET_DATA_PROVIDER` | `alpaca` (live bars) or `fixture` (offline JSON, no keys) |
| `ALPACA_API_KEY_ID` | Alpaca **Key ID** (public-ish identifier) |
| `ALPACA_API_SECRET_KEY` | Alpaca **Secret** — treat like a password |
| `ALPACA_DATA_BASE_URL` | `https://data.alpaca.markets` (market data, not paper trading URL) |

Get keys: https://app.alpaca.markets → Paper (or Live) → API Keys.

### Where they live

- **ONLY** in `.env` at repo root on each machine (Mac, Oracle VM).
- **NOT** in GitHub (`.env` is gitignored).
- **`.env.example`** on GitHub has **empty** placeholders — safe.

### On Oracle — create secrets on the server

```bash
cd ~
git clone https://github.com/yashpat016/CatalystLens.git
cd CatalystLens
cp .env.example .env
chmod 600 .env
nano .env   # human pastes keys — NEVER commit, NEVER log in chat
```

Example `.env` (user fills real values):

```env
MARKET_DATA_PROVIDER=alpaca
ALPACA_API_KEY_ID=PASTE_KEY_ID_HERE
ALPACA_API_SECRET_KEY=PASTE_SECRET_HERE
ALPACA_DATA_BASE_URL=https://data.alpaca.markets
DATABASE_URL=sqlite:////home/ubuntu/CatalystLens/.local/catalystlens.db
FIXTURES_DIR=/home/ubuntu/CatalystLens/apps/api/app/fixtures
API_BASE_URL_INTERNAL=http://127.0.0.1:8000
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

**Rotate keys** if they were ever pasted in chat or committed by mistake.

### Fixture mode (no keys)

```env
MARKET_DATA_PROVIDER=fixture
```

Charts use bundled JSON under `apps/api/app/fixtures/` — good for demos on a locked-down VM.

### Verify Alpaca after setup

```bash
cd ~/CatalystLens
set -a && source .env && set +a
export PYTHONPATH=apps/api:.
python scripts/verify_alpaca.py
```

---

## 3. Repo layout (markdown & config)

```
CatalystLens/
├── README.md                 # Setup, charts, Alpaca, troubleshooting
├── docs/
│   ├── ROADMAP.md            # Done vs pending, SEC/EDGAR plan, OSCR anchor
│   └── OPENCLAW_BRIEFING.md  # This file
├── config/
│   ├── watchlist.json        # Tickers + company_name + ceo_name
│   └── insider_anchors.json  # Real insider events (e.g. OSCR Bertolini buy)
├── .env.example              # Template — no secrets
├── .gitignore                # Ignores .env, node_modules, .next, .local/
├── docker-compose.yml        # postgres, redis, api, web
├── Makefile                  # make up, seed, test
├── scripts/
│   ├── run_local.sh          # Dev stack Mac
│   ├── seed_symbols.py
│   ├── generate_*_fixtures.py
│   └── verify_alpaca.py
├── apps/
│   ├── api/                  # FastAPI
│   │   ├── app/
│   │   │   ├── routers/      # tickers, fundamentals, institutional, insider
│   │   │   ├── providers/    # alpaca, fixture, insider, institutional
│   │   │   └── fixtures/     # JSON demo data
│   │   └── alembic/
│   └── web/                  # Next.js 14
│       └── src/
│           ├── app/          # pages
│           └── components/   # charts, panels
└── catalystlens_ai_agent_master_plan.md  # Original product plan
```

---

## 4. Deploy commands (Oracle VM)

### Prerequisites

```bash
sudo apt update && sudo apt install -y git docker.io docker-compose-plugin
sudo usermod -aG docker $USER
# log out/in once for docker group
```

### Clone & env

```bash
git clone https://github.com/yashpat016/CatalystLens.git
cd CatalystLens
cp .env.example .env
chmod 600 .env
# EDIT .env with Alpaca keys (user only, not OpenClaw in public channel)
```

### Docker (recommended)

```bash
cd ~/CatalystLens
docker compose up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python -m scripts.seed_symbols
docker compose exec api python -m scripts.generate_fundamentals_fixtures
docker compose exec api python -m scripts.generate_institutional_fixtures
docker compose exec api python -m scripts.generate_insider_fixtures
```

### Health checks

```bash
curl -s http://127.0.0.1:8000/api/health
curl -s http://127.0.0.1:3000/api/health    # Next proxy to API
curl -s "http://127.0.0.1:8000/api/tickers/OSCR/bars?timeframe=1d&limit=5"
curl -s http://127.0.0.1:8000/api/tickers/OSCR/insider | head -c 400
```

### Tailscale Serve (expose UI on tailnet only)

```bash
# Example: proxy local web to tailnet (adjust per OpenClaw tailscale docs)
tailscale serve --bg http://127.0.0.1:3000
```

User opens UI from tailnet, not public IP.

### Restart after code pull

```bash
cd ~/CatalystLens
git pull
docker compose down
docker compose up -d --build
```

---

## 5. API endpoints (for OpenClaw cron / skills)

```
GET  /api/health
GET  /api/tickers/{TICKER}/summary
GET  /api/tickers/{TICKER}/bars?timeframe=1m|5m|1h|1d|1mo&limit=N
GET  /api/tickers/{TICKER}/fundamentals
GET  /api/tickers/{TICKER}/institutional
GET  /api/tickers/{TICKER}/insider
```

Watchlist tickers: AAPL TSLA NVDA ETH BTC JD BMNR OSCR BABA NVO QS ADUR ASTS HIMS NBIS ZETA SOFI IREN

Example cron idea: morning message with OSCR/AAPL insider + summary via curl + format.

---

## 6. TODO / pending (priority order)

### High — live SEC data

- [ ] Add `symbols.cik` column + `scripts/seed_cik_from_sec.py`
- [ ] `EdgarInsiderProvider` — Form 4 from data.sec.gov, cache in DB
- [ ] Env: `SEC_INSIDER_PROVIDER=edgar|fixture`
- [ ] UI: "View on SEC" links; stop relying on fake fixture trades for CEO

### Medium — hosting / prod

- [ ] `docs/oracle-deploy.md` — Tailscale + compose prod
- [ ] Next.js production build in Docker (`next build` / `next start`)
- [ ] OpenClaw cron: watchlist digest via local API

### Medium — institutional (13F)

- [ ] Live 13F is hard on free EDGAR (aggregate all funds) — bulk job or paid API
- [ ] Or keep `institutional_*` fixtures for now

### Low — chart polish

- [ ] Two-click Fib on chart
- [ ] Live earnings (not fixture fundamentals)

### Done (reference)

- [x] Alpaca bars + pagination + multi-year daily
- [x] Timeframes 1m 5m 1h 1D 1M, Fib manual, MA SMA/WMA
- [x] Linked price/volume, Yahoo link
- [x] Fundamentals 5y comparison grid
- [x] Insider/institutional demo fixtures
- [x] `ceo_name` in watchlist; OSCR Mark Bertolini anchor ($11.92 buy 2026-04-06)
- [x] Next.js `/api` proxy (fixes CORS on 127.0.0.1:3000)

Full detail: `docs/ROADMAP.md`

---

## 7. Maintainer commands (after config edits)

```bash
# CEO name change in config/watchlist.json
PYTHONPATH=apps/api:. python scripts/generate_insider_fixtures.py

# Real insider event in config/insider_anchors.json (then regenerate)
PYTHONPATH=apps/api:. python scripts/generate_insider_fixtures.py

# Watchlist change
PYTHONPATH=apps/api:. python scripts/seed_symbols.py
```

---

## 8. Rules for OpenClaw

1. Never `git add .env` or print secret key values.
2. Never post Alpaca secret in Telegram/Discord/logs.
3. Prefer `curl` to `127.0.0.1:8000` from the same VM as the API.
4. Public repo clone is fine; secrets are always manual on-server `.env`.
5. For OSCR CEO: **Mark Bertolini** (`config/watchlist.json`); anchored buy in `config/insider_anchors.json`.

---

## 9. One-message summary for Telegram

> CatalystLens: public repo github.com/yashpat016/CatalystLens — research UI for my watchlist. Clone on Oracle, create chmod 600 `.env` with Alpaca KEY+SECRET (not in git). `docker compose up -d`, health at :8000. UI :3000 via Tailscale only. Read README.md + docs/ROADMAP.md + docs/OPENCLAW_BRIEFING.md. TODO: live SEC Form 4, CIK seed, prod Next build. Do not expose or log API secrets.
