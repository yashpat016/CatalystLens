# CatalystLens — Roadmap & discussion log

Living document for what we built, what we talked about, and what is **still pending**.  
Last updated: 2026-05-17.

For day-to-day setup, see [README.md](../README.md).

---

## What the app is today

| Area | Status | Notes |
|------|--------|--------|
| Watchlist + ticker pages | Done | `config/watchlist.json` |
| Price/volume charts (linked) | Done | lightweight-charts |
| Timeframes | Done | 1m, 5m, 1h, 1D, 1M |
| Alpaca live bars | Done | `MARKET_DATA_PROVIDER=alpaca` |
| Daily history depth | Done | Paginated Alpaca + ~6yr window (restart API after changes) |
| Fib retracement | Done | User-entered high/low |
| Moving averages | Done | SMA/WMA, period in bars |
| Yahoo Finance link | Done | Ticker header |
| Fundamentals (~5y) | Done | Fixtures + comparison grid |
| Institutional (13F-style) | Demo | Fixtures only |
| Insider (Form 4-style) | Demo | Fixtures + `ceo_name` + optional anchors |
| SEC/EDGAR live | **Pending** | Design below |

---

## Conversation summary (chronological)

### Research terminal scope

- Not trading signals — context for watchlist names (portfolio tickers: AAPL, TSLA, NVDA, OSCR, SOFI, etc.).
- Fundamentals and 13F panels are **synthetic fixtures** until live data is wired.

### Market data (Alpaca)

- Fixed: Friday bars missing (`sort=desc` + reverse, higher limit).
- Fixed: CORS / empty chart when using `127.0.0.1:3000` (Next.js `/api` proxy).
- Fixed: Daily chart only ~1 year (400-day window → paginated multi-year fetch).

### Charts UX

- Replaced congested quarterly bar lists with line charts + quarter window (8Q/12Q/20Q).
- Fib: moved from auto high/low → **manual High $ / Low $** (+ “Fill from chart range”).
- Autoscale: default visible window per timeframe (e.g. 252 days on 1D), not squashed full series.
- Requested: 1h, 1D, 1M timeframes — implemented (labeled 1h, 1D, 1M).

### Insider / CEO data

- **OSCR CEO** was wrong (Mario Schlosser → **Mark Bertolini**).
- Fix: `ceo_name` in `config/watchlist.json`, regenerate insider fixtures.
- User noted Bertolini **bought** around **~$10.85** in 2026:
  - Public Form 4 reporting (Apr 2026) shows **open-market purchase of 1M shares at $11.92** on **2026-04-06** (plus separate PSU/tax-related activity same week).
  - Anchored in `config/insider_anchors.json` at $11.92 until live EDGAR is integrated; **verify on SEC** if you remember $10.85 (may be a different lot, average, or date).
  - SEC references: [Bertolini ownership](https://www.sec.gov/cgi-bin/own-disp?CIK=0001352552&action=getowner), [OSCR Form 4 index](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001568651&type=4).

### Hosting (Oracle Cloud + OpenClaw)

- CatalystLens can run **alongside** OpenClaw on the same free ARM VM.
- Do **not** embed inside the gateway — pair them: Tailscale Serve, local API, optional OpenClaw cron calling `http://127.0.0.1:8000/api/...`.
- Production: `next build` + `next start` on VPS (Docker web still uses dev mode).

### SEC / EDGAR integration (discussed, not built)

See [SEC/EDGAR integration plan](#secedgar-integration-plan) below.

---

## OSCR — Mark Bertolini anchor (fixture)

Until live Form 4 parsing ships, the **real** CEO buy is seeded from:

- **File:** `config/insider_anchors.json`
- **Event:** 2026-04-06, Mark Bertolini, CEO, buy, 1,000,000 sh @ **$11.92** (SEC-reported open market)

Regenerate fixtures after editing anchors:

```bash
PYTHONPATH=apps/api:. python scripts/generate_insider_fixtures.py
```

To add your **~$10.85** recollection as a separate anchor row (if you confirm date/shares from a filing), edit that JSON and re-run the script.

---

## SEC/EDGAR integration plan

### Principles

1. **Backend only** — browser never calls `data.sec.gov` (no CORS).
2. **User-Agent** — `CatalystLens/0.1 (your@email.com)` per [SEC developer FAQ](https://www.sec.gov/os/webmaster-faq#developers).
3. **Rate limit** — ≤10 req/s; cache aggressively.
4. **CIK required** — ticker → 10-digit CIK via [company_tickers.json](https://www.sec.gov/files/company_tickers.json).

### Phase 1 — CIK mapping (pending)

- [ ] Alembic migration: `symbols.cik` (nullable string, 10 digits).
- [ ] `scripts/seed_cik_from_sec.py` — map watchlist tickers to CIK.
- [ ] Handle ADRs (BABA, NVO); mark crypto (BTC, ETH) as no SEC.

### Phase 2 — Live Form 4 / insider (pending) — **do this first**

- [ ] `InsiderProvider` protocol + `EdgarInsiderProvider`.
- [ ] Flow: `CIK → submissions JSON → filter form 4/4/A → download XML → parse transactions`.
- [ ] Map to existing `InsiderResponse` / `InsiderTransaction` schemas.
- [ ] DB cache table + TTL (e.g. 6h) or nightly `scripts/sync_insider_form4.py`.
- [ ] Env: `SEC_INSIDER_PROVIDER=edgar|fixture`.
- [ ] UI: link “View on SEC” per filing; show `source: sec_edgar`.
- [ ] Library choice: **edgartools** (fast prototype) or **httpx + XML** (fewer deps).

**Outcome:** CEO names and trades (including Bertolini buys) come from filings, not `watchlist.json`.

### Phase 3 — Live 13F / institutional (pending) — harder

13F is filed by **managers**, not issuers. “Who owns OSCR?” requires aggregating many 13Fs.

Options:

- [ ] **A.** Nightly bulk SEC job + local DB (heavy, free).
- [ ] **B.** Paid API (e.g. sec-api.io) — faster.
- [ ] **C.** Keep fixtures for 13F; only Form 4 live in v1.

- [ ] Env: `SEC_INSTITUTIONAL_PROVIDER=fixture|edgar|sec_api`.

### Phase 4 — Telegram alerts (OpenClaw) — partial

- [x] Spec: `docs/TELEGRAM_ALERTS.md` + `config/x_watchlist.json`
- [x] Script: `scripts/telegram_institutional_digest.py` (13F-style from API)
- [ ] OpenClaw cron → forward digest to Telegram (weekdays 8am ET)
- [ ] Dedupe: only alert when QoQ holder list **changes** vs last run
- [ ] **Price targets:** analyst API or X parse; PT raised/lowered/initiated
- [ ] **X.com:** search + influencer accounts from `config/x_watchlist.json`
- [ ] Store PT state in `.local/pt_state.json` on VM (gitignored)

### Phase 5 — Ops (pending)

- [ ] OpenClaw cron: daily insider digest via local API.
- [ ] `docs/oracle-deploy.md` — Tailscale, compose prod, env secrets.
- [ ] Rotate Alpaca/SEC keys; never commit `.env`.

---

## Chart / API backlog (pending)

| Item | Priority | Notes |
|------|----------|--------|
| Live EDGAR Form 4 | High | Replaces fixtures + anchors |
| CIK on symbols | High | Prerequisite |
| Production Next build in Docker | Medium | Oracle / always-on |
| Live 13F institutional | Medium–Low | Bulk or paid API |
| Telegram institutional + PT alerts | Medium | OpenClaw + `TELEGRAM_ALERTS.md` |
| Analyst price targets API | Medium | Not in 13F; separate provider |
| Manual “Fit 1Y” zoom preset | Low | Partially covered by 1D default 252 bars |
| Click-two-points Fib on chart | Low | Alternative to numeric high/low |
| Earnings live (not fixture) | Low | Separate from SEC |
| Tests for `EdgarInsiderProvider` | Medium | Mock HTTP |

---

## Done checklist (for reference)

- [x] Institutional 13F-style fixtures + panel
- [x] Alpaca provider + verify script
- [x] Linked price/volume charts
- [x] Watchlist expansion + seed
- [x] Fundamentals 5y + dual-axis comparison grid
- [x] Quarterly line charts (less congestion)
- [x] Fib manual high/low
- [x] Timeframes 1m/5m/1h/1D/1M
- [x] Chart autoscale / default visible range
- [x] MA SMA/WMA
- [x] Yahoo Finance link
- [x] Insider fixtures + CEO from watchlist `ceo_name`
- [x] OSCR Bertolini anchor (SEC $11.92 Apr 2026)
- [x] README.md
- [x] Next.js API proxy + CORS fix
- [x] Alpaca pagination / multi-year daily

---

## Key files

| Purpose | Path |
|---------|------|
| Watchlist + CEO names | `config/watchlist.json` |
| Real insider events (manual) | `config/insider_anchors.json` |
| Regenerate insider fixtures | `scripts/generate_insider_fixtures.py` |
| Alpaca market data | `apps/api/app/providers/market_data/alpaca.py` |
| Chart timeframes (web) | `apps/web/src/lib/chartLimits.ts` |
| Insider API | `GET /api/tickers/{ticker}/insider` |
| Institutional API | `GET /api/tickers/{ticker}/institutional` |

---

## How to pick up work

1. **Quick win:** Run insider generator after editing `insider_anchors.json` / `ceo_name`.
2. **High value:** Phase 1 + 2 EDGAR (CIK + Form 4) — insider panel becomes trustworthy.
3. **Hosting:** Oracle + OpenClaw per README “Hosting” section when you want 24/7 access.

Questions to decide before coding EDGAR:

- **edgartools** vs raw XML?
- **Form 4 only** for v1 (recommended)?
- Your **SEC User-Agent email** for `.env`.
