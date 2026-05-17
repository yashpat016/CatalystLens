# Telegram alerts — institutional, price targets, X.com

Spec for **OpenClaw** (cron + Telegram) alongside CatalystLens on Oracle.

**Repo:** https://github.com/yashpat016/CatalystLens

---

## Goal

Send Telegram messages when:

1. **Institutional (13F)** — funds **increased / decreased / new / closed** positions vs prior disclosed quarter (with implied flow price when available).
2. **Analyst price targets** — PT **raised / lowered / initiated**, rating changes (Buy/Hold/Sell).
3. **X.com signal** — credible accounts posting about the same ticker (13F drops, large holder moves, PT changes) — **confirmation layer**, not sole source.

---

## Important: what 13F is (and is not)

| 13F gives you | 13F does NOT give you |
|---------------|------------------------|
| Quarter-end **positions** (shares, $ value) | Intraday trades |
| QoQ **Δ shares** → inferred buy/sell | **Price targets** |
| ~45 day lag after quarter end | Real-time news |

**Price targets** come from **analyst research** (upgrades/downgrades), Finviz, Benzinga, Bloomberg, or X posts — **separate pipeline**.

CatalystLens today:

| Data | API today | Live SEC |
|------|-----------|----------|
| Institutional 13F-style | `GET /api/tickers/{T}/institutional` | Fixture demo only |
| Insider Form 4 | `GET /api/tickers/{T}/insider` | Fixture + anchors |
| Price targets | **Not built yet** | Needs new provider |

---

## Message format (Telegram)

### Institutional (per ticker)

```
🏦 OSCR — Institutional (13F-style, QoQ)
Period: Q4'25 filed through 2026-02-14
Aggregate: net_buying | +1.2M shares QoQ

▲ Increased
• Vanguard Group — +450,000 sh (~$4.1M) @ ~$9.12 implied flow
• BlackRock — +120,000 sh @ ~$9.05

▼ Decreased
• State Street — −80,000 sh @ ~$9.20

Source: CatalystLens API / SEC 13F-HR (when live)
Fixture disclaimer if demo: synthetic fixture — verify on SEC
```

### Price target (per ticker) — **future / X-sourced**

```
📈 OSCR — Analyst PT
• Goldman Sachs: PT $14 → $18 (raised) | Overweight
• Morgan Stanley: initiated $12 | Equal-weight

Source: [X post URL] or Benzinga/Finnhub (when wired)
```

### X.com corroboration (optional footer)

```
🐦 X mentions (last 24h)
• @investingwithac — "OSCR 13F shows Vanguard adding…"
• @TheLongInvest — "Oscar institutional accumulation"

Links: …
```

---

## OpenClaw: what to build (phases)

### Phase A — Today (fixtures + curl)

1. Ensure CatalystLens API on VM: `http://127.0.0.1:8000`
2. Run digest script (see below) on cron.
3. OpenClaw sends script output to user's Telegram (channel already configured).

```bash
cd ~/CatalystLens
set -a && source .env && set +a
export PYTHONPATH=apps/api:.
python scripts/telegram_institutional_digest.py --telegram-format
```

Cron example (OpenClaw `cron` or system crontab):

```
0 8 * * 1-5  cd /home/ubuntu/CatalystLens && ./scripts/run_telegram_digest.sh
```

### Phase B — Live 13F (CatalystLens + SEC)

- [ ] `symbols.cik` + SEC 13F ingest (bulk or paid API)
- [ ] Store last two quarters per ticker; diff for alerts
- [ ] Alert only on **change** vs previous run (dedupe Telegram spam)

### Phase C — Price targets

- [ ] New API: `GET /api/tickers/{T}/analyst_targets` or `/signals`
- [ ] Sources (pick one):
  - Paid: Benzinga, Finnhub, Polygon analyst ratings
  - Free-ish: scrape from X with OpenClaw browser tool (fragile)
- [ ] Track: `firm`, `old_pt`, `new_pt`, `rating`, `date`, `direction` (raised|lowered|init)

### Phase D — X.com watchlist

Accounts to monitor (user-defined; examples):

| Account | Focus |
|---------|--------|
| @TheLongInvest | Long-term / 13F commentary |
| @investingwithac | Institutional flow posts |
| @CNBC | Breaking news (noisy) |
| @fundstrat (Tom Lee) | Macro / crypto / BMNR narratives |

**Do not** rely on X alone for 13F numbers — use SEC or CatalystLens API, use X as **secondary**.

OpenClaw standing order idea:

> Daily 8am ET: For each watchlist ticker, curl CatalystLens institutional, diff QoQ increases/decreases, search X for `"{TICKER} 13F" OR "{TICKER} institutional"` from last 24h, merge into one Telegram message. Flag PT raise/lower if found in X text or analyst API.

---

## API fields to use (institutional)

From `GET /api/tickers/OSCR/institutional`:

```json
{
  "aggregate_flow": "net_buying",
  "net_shares_change_qoq": 1200000,
  "holders": [
    {
      "manager_name": "Vanguard Group Inc",
      "activity": "increased",
      "shares_change_qoq": 450000,
      "implied_flow_price_usd": "9.12",
      "market_value_usd": "..."
    }
  ],
  "quarter_history": [...]
}
```

**Alert rules:**

- `activity` in `increased` | `new` → bullish institutional line
- `activity` in `decreased` | `closed` → bearish institutional line
- `|shares_change_qoq|` above threshold (e.g. 50k) to reduce noise
- Mention `implied_flow_price_usd` when present (not cost basis)

---

## Price target alert rules (when implemented)

| Event | Telegram line |
|-------|----------------|
| PT raised | `Firm: $12 → $16 (raised)` |
| PT lowered | `Firm: $20 → $15 (lowered)` |
| Initiated | `Firm: initiated $14 | Buy` |
| Downgrade | `Firm: Buy → Hold` |

Always include **prior quarter PT** if known (store state in `.local/pt_state.json` on VM).

---

## Secrets

| Secret | For |
|--------|-----|
| Alpaca `.env` | Price charts only |
| SEC User-Agent email | EDGAR (no key) |
| X API bearer token | Optional X search (if user adds) |
| Telegram | OpenClaw already has channel config |

**Never** commit X or Alpaca secrets to GitHub.

---

## Copy-paste for OpenClaw (Telegram)

```
NEW TASK: CatalystLens watchlist Telegram alerts

1) INSTITUTIONAL (13F QoQ)
- For each ticker in config/watchlist.json, GET http://127.0.0.1:8000/api/tickers/{T}/institutional
- Compare holders with activity: increased/new vs decreased/closed
- Report prior quarter context from quarter_history[] and net_shares_change_qoq
- Include implied_flow_price_usd when set (label as implied, not exact trade price)
- Today data may be FIXTURE — say so until live SEC is wired

2) PRICE TARGETS (not in API yet)
- Search X.com last 24h for: "{TICKER} price target", "{TICKER} PT raised", "{TICKER} upgrade"
- Watch accounts: @TheLongInvest @investingwithac (user may add more in config/x_watchlist.json)
- Parse posts for: firm name, old PT → new PT, raised/lowered/initiated
- Send separate 📈 section per ticker; store last seen PT in ~/CatalystLens/.local/pt_state.json to only alert on CHANGE

3) TELEGRAM FORMAT
- One message per ticker OR one daily digest — user preference: daily digest 8am ET weekdays
- Use templates in docs/TELEGRAM_ALERTS.md
- Do not send on weekends unless filing dropped

4) RUN SCRIPT
cd ~/CatalystLens && python scripts/telegram_institutional_digest.py

5) STYLING/UI is separate — this task is data alerts only

Read: docs/TELEGRAM_ALERTS.md, docs/ROADMAP.md
```

---

## Product note (dashboard, not alerts)

Long-term UI ideas (do not clutter ticker page):

- “Institutional flow” chip: net buying / selling this quarter
- “PT consensus” row when analyst API exists
- X “buzz” sidebar — top 3 posts — link out only

See OPENCLAW_BRIEFING §10 for influencer tracking ideas.
