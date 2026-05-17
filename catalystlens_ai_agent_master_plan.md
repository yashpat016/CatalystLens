# CatalystLens: AI Agent Development Brief

Version: 0.1  
Purpose: Give AI coding sub-agents a clear, scoped, testable plan for building a market event, liquidity, and research intelligence product.

---

## 1. Product Summary

CatalystLens is a market intelligence dashboard for active traders and investors. It connects price movement, volume behavior, liquidity, market events, filings, earnings, fundamentals, and user-written theses into one intuitive research workflow.

The product should not be positioned as an automated trading bot or buy/sell signal generator. It should be positioned as a research and analytics terminal.

Core product promise:

> Know what moved a ticker, when it moved, what event likely triggered it, how volume and liquidity behaved, and what facts support or weaken the user's thesis.

Core user question:

> What changed, how did the market react, and what should I investigate next?

---

## 2. Product Boundaries

### Build This

- Market event timeline
- Price and volume dashboard
- Relative volume analytics
- VWAP and anchored VWAP
- Catalyst/event detection
- Earnings and SEC filing tracking
- Estimated buy/sell volume when trade and quote data are available
- User watchlists
- User ticker tags
- User thesis notes
- Source-backed AI question answering
- Alerts for events and abnormal market reactions
- Fundamental summary views

### Do Not Build Initially

- Automated trading execution
- Broker order placement
- Personalized buy/sell recommendations
- Options strategy recommendations
- Promises of profit
- Paywall bypassing
- Social media scraping that violates platform terms
- A mobile app before the web app works
- A full Bloomberg clone

### Compliance-Safe Product Language

Use language like:

- "market event analytics"
- "source-backed research"
- "volume and catalyst intelligence"
- "watchlist monitoring"
- "educational market context"

Avoid language like:

- "AI tells you what to buy"
- "guaranteed signals"
- "profit predictor"
- "personalized trading advice"
- "automated money machine"

---

## 3. Target User

Primary user:

- Active retail trader or serious investor
- Tracks watchlists daily
- Watches earnings, SEC filings, analyst changes, macro events, and news
- Wants a better explanation of movement than standard chart apps provide

Secondary user:

- Swing trader tracking setups
- Small-cap catalyst trader
- Earnings trader
- Biotech catalyst trader
- Research-heavy investor monitoring fundamentals and event risk

---

## 4. Core Workflow

The core workflow is:

1. User adds tickers to a watchlist.
2. System ingests market data, events, filings, earnings, and fundamentals.
3. System normalizes events into a single event model.
4. System overlays events on the ticker chart.
5. System calculates market reaction metrics around each event.
6. User tags a ticker with a thesis, such as "possible bounce" or "watching earnings reaction."
7. User asks questions like:
   - "Why did this move today?"
   - "What changed since earnings?"
   - "Is this move supported by volume?"
   - "What would need to happen for a bounce?"
   - "What are the next catalysts?"
8. System answers using source-backed facts and clearly states uncertainty.
9. User receives alerts when events or market behavior match their watch criteria.

---

## 5. High-Level Architecture

Recommended first stack:

```text
Frontend:
  Next.js
  React
  TypeScript
  Lightweight Charts
  Apache ECharts, later if needed

Backend:
  FastAPI
  Python
  Pydantic
  SQLAlchemy
  Alembic

Database:
  PostgreSQL first
  TimescaleDB or ClickHouse later for tick-scale data

Queue and cache:
  Redis
  RQ, Celery, or Arq

LLM layer:
  Retrieval-augmented summarization
  Source-grounded answers
  No direct trade advice

Deployment:
  Docker Compose first
  VPS or small cloud instance
  Managed Postgres later
```

Initial deployment should be simple. Do not over-engineer with Kubernetes early.

---

## 6. Recommended Repository Structure

```text
catalystlens/
  README.md
  docs/
    product_spec.md
    metrics.md
    event_taxonomy.md
    data_sources.md
    compliance_boundaries.md
    api_contracts.md
    agent_briefs.md
  apps/
    web/
      package.json
      src/
        app/
        components/
        lib/
        types/
    api/
      pyproject.toml
      app/
        main.py
        core/
        db/
        models/
        schemas/
        routers/
        services/
        workers/
        providers/
        metrics/
        ai/
        tests/
  infra/
    docker-compose.yml
    Dockerfile.api
    Dockerfile.web
    nginx/
  scripts/
    seed_symbols.py
    backfill_bars.py
    backfill_events.py
  notebooks/
    research_volume_metrics.ipynb
  .env.example
```

---

## 7. Development Methodology

Use a vertical-slice approach.

A vertical slice means one thin but complete flow from data ingestion to UI display. This is better than building ten disconnected modules that do not talk to each other.

### Build Order

1. One ticker page with price chart and basic volume.
2. Event ingestion and event markers on chart.
3. Event impact calculations.
4. Watchlist and alerts.
5. User tags and thesis notes.
6. Source-backed AI question answering.
7. Tick-level trade/quote analytics.
8. Advanced liquidity and flow views.
9. Paid subscriptions.

### Engineering Rule

Every module should have:

- Clear input contract
- Clear output contract
- Tests for core calculations
- Error handling
- Logging
- Small, replaceable data provider adapter

Do not let API provider logic leak all over the codebase. Wrap each provider in an adapter.

---

## 8. Milestone Plan

## Milestone 1: Ticker Page V1

Goal:

Build a web page where the user can search a ticker and view basic market data.

Features:

- Ticker search
- 1-minute OHLCV chart
- Daily OHLCV chart
- Basic volume bars
- VWAP
- Session labels:
  - premarket
  - regular market
  - after-hours

Backend tasks:

- Create symbols table
- Create market_bars table
- Create market data provider interface
- Implement one provider adapter
- Add endpoint: `GET /api/tickers/{ticker}/bars`
- Add endpoint: `GET /api/tickers/{ticker}/summary`

Frontend tasks:

- Create ticker page route
- Render chart
- Render volume bars
- Render VWAP line
- Show ticker header

Acceptance criteria:

- User can open `/ticker/AAPL`
- Chart loads without manual refresh
- VWAP calculation is tested
- Timezone is consistent and displayed as ET for US equities

---

## Milestone 2: Events and Catalyst Timeline

Goal:

Normalize events from different sources and show them on the chart.

Event types:

- SEC filing
- earnings
- guidance
- analyst rating
- dividend
- split
- offering
- halt/resume
- FDA/regulatory
- macro event
- news headline

Backend tasks:

- Create events table
- Create data_sources table
- Create raw_ingest table
- Create event provider interface
- Implement SEC filing ingest
- Implement earnings calendar ingest
- Add endpoint: `GET /api/tickers/{ticker}/events`
- Add endpoint: `GET /api/events/{event_id}`

Frontend tasks:

- Add event markers to chart
- Add event rail below chart
- Add event detail drawer
- Add event type filters

Acceptance criteria:

- Events are displayed chronologically
- Event markers align to chart timestamps
- Clicking a marker opens event details
- Raw source URL is stored when available

---

## Milestone 3: Event Impact Metrics

Goal:

For each event, calculate how the market reacted.

Metrics:

- Return after 1 minute
- Return after 5 minutes
- Return after 15 minutes
- Return after 60 minutes
- Daily return after event
- Relative volume during reaction window
- Dollar volume
- VWAP distance
- Anchored VWAP from event timestamp
- Benchmark-adjusted return, if benchmark data exists

Backend tasks:

- Create event_impact_metrics table
- Implement event window slicing
- Implement returns calculation
- Implement relative volume calculation
- Implement anchored VWAP calculation
- Add endpoint: `GET /api/events/{event_id}/impact`

Frontend tasks:

- Show market reaction panel
- Show event impact table
- Plot anchored VWAP from event
- Show simple labels, such as:
  - "abnormal volume"
  - "weak reaction"
  - "strong continuation"
  - "failed breakout"

Acceptance criteria:

- Every supported event has impact metrics
- Metrics are recalculated when new bars arrive
- Unit tests cover event window slicing and VWAP

---

## Milestone 4: Volume Flow V1

Goal:

Make volume more useful than a normal volume bar.

V1 metrics:

- Total volume
- Dollar volume
- Cumulative volume
- Relative volume by time of day
- VWAP
- Anchored VWAP
- Volume spike detection

Backend tasks:

- Implement time-of-day baseline volume model
- Implement relative volume calculation
- Implement abnormal volume score
- Add endpoint: `GET /api/tickers/{ticker}/volume-profile`

Frontend tasks:

- Add volume flow panel
- Show RVOL gauge
- Show cumulative volume vs average line
- Show volume spike labels

Acceptance criteria:

- User can identify abnormal participation
- Relative volume is calculated against comparable intraday time windows
- Pre-market and regular session are not mixed unless explicitly requested

---

## Milestone 5: Trade and Quote Flow V2

Goal:

Estimate buyer-initiated and seller-initiated volume using trades and quotes.

This milestone requires data with trades and bid/ask quotes.

Metrics:

- Estimated buy volume
- Estimated sell volume
- Cumulative volume delta
- Spread
- Effective spread
- Trade size buckets
- Large print detection
- Order book imbalance, if depth data exists

Trade classification logic:

```text
midpoint = (bid + ask) / 2

if trade_price > midpoint:
    inferred_side = "buy"
elif trade_price < midpoint:
    inferred_side = "sell"
else:
    inferred_side = "ambiguous"
```

Optional fallback:

```text
If trade is at midpoint, use tick rule:
  price higher than previous trade -> buy
  price lower than previous trade -> sell
  unchanged -> ambiguous
```

Backend tasks:

- Create trades table
- Create quotes table
- Implement trade classification
- Implement CVD
- Implement spread metrics
- Add endpoint: `GET /api/tickers/{ticker}/flow`

Frontend tasks:

- Add estimated buy/sell volume bars
- Add CVD chart
- Add spread chart
- Add liquidity warning labels

Acceptance criteria:

- The UI clearly says "estimated" buy/sell volume
- Ambiguous trades are tracked, not silently forced into buy/sell
- Unit tests cover classification logic

---

## Milestone 6: User Watchlists, Tags, and Theses

Goal:

Allow users to save tickers, tag them, and write a thesis.

Features:

- Watchlist creation
- Add/remove tickers
- Tags:
  - possible bounce
  - earnings watch
  - dilution risk
  - biotech catalyst
  - long-term research
  - short-term momentum
- User notes
- Thesis status:
  - watching
  - active
  - invalidated
  - resolved

Backend tasks:

- Create users table
- Create watchlists table
- Create watchlist_tickers table
- Create user_tags table
- Create user_theses table
- Add CRUD endpoints

Frontend tasks:

- Watchlist sidebar
- Ticker tag editor
- Thesis note panel
- Thesis status selector

Acceptance criteria:

- User can tag a ticker and save a note
- Tags appear on ticker page
- Tag history is not lost when ticker is removed from watchlist

---

## Milestone 7: Source-Backed AI Ask Panel

Goal:

User can ask questions about a ticker and get grounded answers.

Example questions:

- "Why did this move today?"
- "What changed since the last earnings report?"
- "Is this move supported by volume?"
- "What would need to happen for a bounce?"
- "What are the next catalysts?"
- "What are the biggest risks to this thesis?"

Answer format:

```markdown
## Answer

### Known facts
...

### Market reaction
...

### Possible interpretations
...

### What would strengthen the thesis
...

### What would weaken the thesis
...

### Missing data
...

### Confidence
Low / Medium / High

### Sources
- Source 1
- Source 2
```

Rules:

- Do not give direct buy/sell advice
- Do not invent facts
- Cite events, filings, fundamentals, and market metrics
- State uncertainty clearly
- Prefer "conditions" over predictions

Bad:

```text
This stock will bounce.
```

Good:

```text
A bounce thesis becomes stronger if price reclaims anchored VWAP from the earnings timestamp, seller-initiated volume fades, and no new negative filings appear.
```

Backend tasks:

- Create retrieval service
- Collect relevant events, filings, bars, metrics, fundamentals, and user thesis
- Generate grounded answer
- Store question and answer
- Add endpoint: `POST /api/tickers/{ticker}/ask`

Frontend tasks:

- Add ask panel
- Add suggested questions
- Show answer with source list
- Show confidence and missing data

Acceptance criteria:

- Answer includes source references
- Answer refuses unsupported prediction requests
- Answer uses user's thesis context when available

---

## Milestone 8: Alerts

Goal:

Notify users when relevant events or abnormal market reactions happen.

Alert types:

- New SEC filing
- Earnings released
- Guidance changed
- Analyst rating changed
- Offering detected
- Halt/resume detected
- RVOL above threshold
- Price crosses anchored VWAP from event
- CVD flips positive or negative
- Tagged ticker receives new event
- Thesis invalidation condition triggered

Delivery channels:

- Email
- Discord webhook
- Telegram bot
- Browser notification later
- SMS much later

Backend tasks:

- Create alert_rules table
- Create alert_deliveries table
- Implement alert evaluator
- Implement email delivery
- Implement Discord webhook delivery
- Add endpoint: `POST /api/alerts/rules`
- Add endpoint: `GET /api/alerts/history`

Frontend tasks:

- Alert rule builder
- Alert history page
- Alert status badges

Acceptance criteria:

- Alerts are not duplicated excessively
- Alert delivery failures are logged
- User can pause/delete rules

---

## 9. Data Source Strategy

Use provider adapters. The app should not care whether the data comes from Alpaca, FMP, Polygon, Databento, Benzinga, SEC, or another provider.

### Provider Interface Pattern

```python
class MarketDataProvider:
    def get_bars(self, symbol: str, start: datetime, end: datetime, timeframe: str):
        raise NotImplementedError

    def get_trades(self, symbol: str, start: datetime, end: datetime):
        raise NotImplementedError

    def get_quotes(self, symbol: str, start: datetime, end: datetime):
        raise NotImplementedError
```

```python
class EventProvider:
    def get_events(self, symbol: str, start: datetime, end: datetime):
        raise NotImplementedError
```

```python
class FundamentalsProvider:
    def get_company_profile(self, symbol: str):
        raise NotImplementedError

    def get_financials(self, symbol: str):
        raise NotImplementedError
```

### V1 Data Sources

Start with only a few:

- Market bars provider
- SEC EDGAR for filings
- One earnings/calendar provider
- One fundamentals provider

### Later Data Sources

- Trade and quote data provider
- News provider
- Analyst ratings provider
- FDA calendar provider
- Offerings/dilution provider
- Macro calendar provider
- Transcript provider

---

## 10. Paywall-Blocked Content Methodology

Do not bypass paywalls. Instead, model source availability honestly.

### Access Levels

```text
full_text
licensed_full_text
headline_and_snippet
metadata_only
paywall_blocked
source_unavailable
manual_user_import
```

### Source Object

```json
{
  "source": "Example News Source",
  "url": "https://example.com/article",
  "access_level": "headline_and_snippet",
  "paywall_status": "blocked",
  "raw_text_available": false,
  "summary_method": "metadata_only",
  "confidence_penalty": 0.25
}
```

### Fallback Order

1. Use licensed API source if available.
2. Use official source, such as SEC, company investor relations, press release, FDA, exchange notice, or earnings transcript.
3. Use headline, timestamp, ticker tags, and snippet only.
4. Allow user to paste or upload text they have access to.
5. Mark source as unavailable and reduce confidence.

### UI Copy

Use:

```text
Paywall-limited source. We only have headline, timestamp, source, and ticker tags. Confidence reduced.
```

Do not use:

```text
We bypassed the paywall.
```

---

## 11. Core Data Model

### data_sources

```text
id
name
source_type
auth_type
base_url
license_notes
enabled
created_at
updated_at
```

### raw_ingest

```text
id
source_id
source_event_id
fetched_at
payload_json
payload_hash
status
error_message
```

### symbols

```text
id
ticker
exchange
cik
company_name
sector
industry
active
created_at
updated_at
```

### market_bars

```text
id
symbol_id
timestamp
timeframe
open
high
low
close
volume
vwap
trade_count
session
created_at
```

### trades

```text
id
symbol_id
timestamp
price
size
exchange
conditions
bid
ask
midpoint
inferred_side
side_confidence
created_at
```

### quotes

```text
id
symbol_id
timestamp
bid
ask
bid_size
ask_size
spread
created_at
```

### events

```text
id
symbol_id
event_type
event_time
source_id
title
summary
url
access_level
confidence
raw_ingest_id
created_at
updated_at
```

### event_impact_metrics

```text
id
event_id
window
return_pct
benchmark_adjusted_return_pct
sector_adjusted_return_pct
volume
dollar_volume
relative_volume
buy_volume
sell_volume
cvd_change
spread_change
vwap_distance
anchored_vwap_reclaimed
confidence
created_at
updated_at
```

### fundamentals

```text
id
symbol_id
period
fiscal_year
fiscal_quarter
revenue
gross_margin
operating_income
net_income
eps
cash
debt
free_cash_flow
shares_outstanding
created_at
updated_at
```

### users

```text
id
email
name
created_at
updated_at
```

### watchlists

```text
id
user_id
name
created_at
updated_at
```

### watchlist_tickers

```text
id
watchlist_id
symbol_id
created_at
```

### user_tags

```text
id
user_id
symbol_id
tag
created_at
```

### user_theses

```text
id
user_id
symbol_id
title
body
timeframe
status
created_at
updated_at
```

### user_questions

```text
id
user_id
symbol_id
question
answer
citations_json
confidence
created_at
```

### alert_rules

```text
id
user_id
symbol_id
rule_type
params_json
enabled
created_at
updated_at
```

### alert_deliveries

```text
id
alert_rule_id
event_id
status
channel
payload_json
sent_at
error_message
```

---

## 12. Useful Metrics

## Price Metrics

- Current price
- Percent change
- Gap percent
- Intraday high/low
- Distance from previous close
- Distance from VWAP
- Distance from anchored VWAP
- Benchmark-adjusted return
- Sector-adjusted return

## Volume Metrics

- Total volume
- Dollar volume
- Cumulative volume
- Relative volume
- Relative dollar volume
- Volume spike score
- Volume by session
- Volume by price level
- Average volume by time of day

## Flow Metrics

- Estimated buy volume
- Estimated sell volume
- Buy/sell imbalance
- Cumulative volume delta
- Ambiguous trade volume
- Large trade count
- Large trade volume
- Aggressive flow change after event

## Liquidity Metrics

- Bid/ask spread
- Effective spread
- Spread z-score
- Top-of-book depth
- Depth imbalance
- Liquidity gap detection
- Halt/resume status

## Event Metrics

- Event type
- Event timestamp quality
- Event source quality
- Event uniqueness
- Price reaction windows
- Volume reaction windows
- Flow reaction windows
- Confidence score
- Competing event count

## Fundamental Metrics

- Revenue growth
- Gross margin
- Operating margin
- Net margin
- EPS trend
- Free cash flow trend
- Cash runway estimate, when applicable
- Debt trend
- Share count trend
- Dilution risk
- Guidance revision
- Analyst estimate revision

---

## 13. Event Confidence Methodology

Event confidence should not pretend to prove causation. It should estimate whether an event is likely related to a market move.

### Inputs

- Timestamp quality
- Source quality
- Event uniqueness
- Abnormal price move
- Abnormal volume move
- Flow change
- Liquidity change
- Number of competing events

### Example Formula

```text
confidence =
    timestamp_quality * 0.25
  + source_quality * 0.15
  + event_uniqueness * 0.20
  + abnormal_move_score * 0.20
  + abnormal_volume_score * 0.15
  + flow_confirmation * 0.05
```

### Confidence Labels

```text
0.00 - 0.39: Low
0.40 - 0.69: Medium
0.70 - 1.00: High
```

### Wording Rules

Use:

- "likely associated with"
- "reaction window suggests"
- "possibly triggered by"
- "confidence: medium"

Avoid:

- "this definitely caused"
- "guaranteed reason"
- "the market moved because of this and nothing else"

---

## 14. Event Timeline Design

The event timeline should be a first-class UI element.

Example:

```text
09:30:00  Market open
09:31:18  8-K filed
09:32:04  News headline published
09:33:12  Volume spike begins
09:33:48  Spread widens
09:35:00  Price breaks premarket high
09:37:30  CVD turns positive
10:00:00  Analyst rating update
```

Each event card should show:

- Timestamp
- Source
- Event type
- Title
- Short summary
- Related ticker
- Source URL
- Access level
- Confidence
- Reaction metrics
- Missing data

---

## 15. AI Agent Team Structure

Use specialized sub-agents. Do not ask one agent to build the whole product.

Recommended agents:

1. Product Architect Agent
2. Backend API Agent
3. Database Schema Agent
4. Market Data Agent
5. Event/Catalyst Agent
6. Volume Metrics Agent
7. Fundamentals Agent
8. Frontend Charting Agent
9. AI/RAG Answering Agent
10. Alerts Agent
11. DevOps Agent
12. QA/Test Agent
13. Compliance and Copy Agent
14. Growth/Landing Page Agent

Each agent should produce small, reviewable changes.

---

# 16. Sub-Agent Briefs

## 16.1 Product Architect Agent

### Mission

Keep the product coherent. Convert fuzzy trading ideas into clear user workflows, API contracts, data models, and acceptance criteria.

### Responsibilities

- Maintain product spec
- Define user stories
- Define feature priority
- Protect scope
- Ensure all agents follow shared architecture
- Review whether features support core product promise

### Deliverables

- `docs/product_spec.md`
- `docs/roadmap.md`
- `docs/user_stories.md`
- Updated acceptance criteria for each milestone

### Prompt

```text
You are the Product Architect Agent for CatalystLens.

Your job is to convert the product idea into clear user stories, feature boundaries, and acceptance criteria.

Product promise:
A source-backed market event and liquidity intelligence dashboard that helps users understand what moved a ticker, when it moved, how the market reacted, and what facts support or weaken a user's thesis.

Constraints:
- Do not design trading execution.
- Do not create buy/sell recommendation flows.
- Keep V1 narrow and shippable.
- Prefer one working vertical slice over many disconnected features.

Task:
Create or update docs/product_spec.md with:
1. Core user workflows
2. V1 feature list
3. Explicit non-goals
4. Acceptance criteria
5. Risks and open questions
```

---

## 16.2 Backend API Agent

### Mission

Build clean backend endpoints and service boundaries.

### Responsibilities

- FastAPI app structure
- REST endpoints
- Pydantic schemas
- Service layer
- Error handling
- Logging
- API tests

### Deliverables

- `apps/api/app/main.py`
- `apps/api/app/routers/`
- `apps/api/app/schemas/`
- `apps/api/app/services/`
- API tests

### Prompt

```text
You are the Backend API Agent for CatalystLens.

Build FastAPI endpoints for the current milestone.

Rules:
- Use Pydantic schemas for request/response validation.
- Keep router logic thin.
- Put business logic in services.
- Use SQLAlchemy models from the database layer.
- Include tests.
- Do not add authentication unless explicitly assigned.
- Do not hardcode provider-specific logic inside routers.

Current task:
Implement endpoints for ticker bars and ticker events:
- GET /api/tickers/{ticker}/summary
- GET /api/tickers/{ticker}/bars
- GET /api/tickers/{ticker}/events
- GET /api/events/{event_id}

Include response schemas, service functions, and tests.
```

---

## 16.3 Database Schema Agent

### Mission

Design normalized, migration-safe schemas.

### Responsibilities

- SQLAlchemy models
- Alembic migrations
- Index design
- Foreign keys
- Data integrity
- Timezone-safe timestamps

### Deliverables

- `apps/api/app/models/`
- `apps/api/alembic/versions/`
- `docs/schema.md`

### Prompt

```text
You are the Database Schema Agent for CatalystLens.

Design PostgreSQL tables and SQLAlchemy models for market data, events, users, watchlists, tags, theses, and alerts.

Rules:
- Use timezone-aware timestamps.
- Use indexes for ticker/time queries.
- Use foreign keys where appropriate.
- Keep raw provider payloads in raw_ingest, not scattered across domain tables.
- Write Alembic migrations.
- Include a docs/schema.md explanation.

Current task:
Create models and migrations for:
- data_sources
- raw_ingest
- symbols
- market_bars
- events
- event_impact_metrics
```

---

## 16.4 Market Data Agent

### Mission

Ingest and normalize market bars, trades, and quotes.

### Responsibilities

- Provider adapter interface
- Bar ingestion
- Trade ingestion later
- Quote ingestion later
- Timezone normalization
- Duplicate handling
- Missing data detection

### Deliverables

- `apps/api/app/providers/market_data/base.py`
- `apps/api/app/providers/market_data/{provider}.py`
- `apps/api/app/services/market_data_service.py`
- Ingestion scripts
- Tests

### Prompt

```text
You are the Market Data Agent for CatalystLens.

Build a provider-agnostic market data ingestion layer.

Rules:
- Use adapter interfaces.
- Normalize all timestamps to UTC in storage.
- Return ET display metadata for US equities when needed.
- Do not mix provider-specific fields into domain models.
- Store raw payloads in raw_ingest.
- Include tests for parsing, duplicates, and missing bars.

Current task:
Implement a market data provider interface and one concrete adapter for 1-minute OHLCV bars.
Store normalized bars in market_bars.
```

---

## 16.5 Event/Catalyst Agent

### Mission

Ingest market catalysts and normalize them into a unified event timeline.

### Responsibilities

- Event taxonomy
- SEC filing ingestion
- Earnings calendar ingestion
- Event deduplication
- Event source quality scoring
- Event confidence inputs

### Deliverables

- `docs/event_taxonomy.md`
- `apps/api/app/providers/events/base.py`
- `apps/api/app/providers/events/sec.py`
- `apps/api/app/providers/events/earnings.py`
- `apps/api/app/services/event_service.py`
- Event tests

### Prompt

```text
You are the Event/Catalyst Agent for CatalystLens.

Build the event ingestion and normalization system.

Rules:
- Normalize all event types into the events table.
- Keep raw provider payloads in raw_ingest.
- Deduplicate events by ticker, timestamp, source, title, and event type.
- Preserve source URL when available.
- Track access_level and confidence.
- Do not claim causation. Only store event facts and calculated association metrics.

Current task:
Implement SEC filing and earnings event ingestion. Then expose normalized events for a ticker.
```

---

## 16.6 Volume Metrics Agent

### Mission

Create metrics that reveal participation, abnormal volume, and later buyer/seller aggression.

### Responsibilities

- VWAP
- Anchored VWAP
- Relative volume
- Dollar volume
- Volume spike detection
- Estimated buy/sell volume later
- CVD later
- Unit tests for calculations

### Deliverables

- `docs/metrics.md`
- `apps/api/app/metrics/volume.py`
- `apps/api/app/metrics/vwap.py`
- `apps/api/app/metrics/flow.py`
- Tests

### Prompt

```text
You are the Volume Metrics Agent for CatalystLens.

Build calculation functions for volume and flow analytics.

Rules:
- Functions should be pure where possible.
- Use explicit inputs and outputs.
- Include tests with synthetic data.
- Clearly label estimated metrics as estimated.
- Do not call estimated buy/sell volume actual buy/sell volume.

Current task:
Implement:
- VWAP
- anchored VWAP
- cumulative volume
- dollar volume
- relative volume by time of day
- volume spike score

Return structured metric objects that the API can serialize.
```

---

## 16.7 Fundamentals Agent

### Mission

Build company fundamental summaries and risk flags.

### Responsibilities

- Financial statement ingestion
- SEC XBRL mapping later
- Revenue/margin/cash/debt/share trends
- Dilution risk detection
- Fundamental summary generation
- Missing data indicators

### Deliverables

- `apps/api/app/providers/fundamentals/base.py`
- `apps/api/app/providers/fundamentals/{provider}.py`
- `apps/api/app/services/fundamentals_service.py`
- `docs/fundamentals.md`
- Tests

### Prompt

```text
You are the Fundamentals Agent for CatalystLens.

Build the company fundamentals layer.

Rules:
- Prefer source-backed numeric data.
- Track period, fiscal year, and fiscal quarter.
- Do not compare periods unless units and periods are consistent.
- Store missing fields as null, not fake zeroes.
- Include data quality warnings.

Current task:
Implement a fundamentals provider interface and normalized storage for:
- revenue
- gross margin
- operating income
- net income
- EPS
- cash
- debt
- free cash flow
- shares outstanding
```

---

## 16.8 Frontend Charting Agent

### Mission

Build the intuitive visual interface.

### Responsibilities

- Ticker page
- Candlestick chart
- Volume bars
- VWAP and anchored VWAP
- Event markers
- Event rail
- Volume flow panel
- Responsive layout

### Deliverables

- `apps/web/src/app/ticker/[ticker]/page.tsx`
- `apps/web/src/components/charts/`
- `apps/web/src/components/events/`
- `apps/web/src/components/volume/`
- TypeScript types

### Prompt

```text
You are the Frontend Charting Agent for CatalystLens.

Build a clear, intuitive ticker page.

Rules:
- Use TypeScript.
- Keep API calls in data hooks or server components, not buried inside low-level chart components.
- Chart components should accept typed props.
- Event markers must be clickable.
- Use plain labels that explain what metrics mean.
- Do not overload the first screen with every possible metric.

Current task:
Create a ticker page with:
- header summary
- candlestick chart
- volume bars
- VWAP line
- event markers
- event rail
- event details drawer
```

---

## 16.9 AI/RAG Answering Agent

### Mission

Build source-backed question answering over ticker data, events, fundamentals, metrics, and user thesis notes.

### Responsibilities

- Retrieval context assembly
- Prompt templates
- Citation handling
- Refusal logic for unsupported advice
- Answer confidence
- Missing data section

### Deliverables

- `apps/api/app/ai/context_builder.py`
- `apps/api/app/ai/prompts.py`
- `apps/api/app/ai/answer_service.py`
- `docs/ai_answering.md`
- Tests for prompt safety and answer structure

### Prompt

```text
You are the AI/RAG Answering Agent for CatalystLens.

Build a source-backed answer service for ticker-specific questions.

Rules:
- Do not provide direct buy/sell advice.
- Do not invent facts.
- Always separate known facts, interpretation, missing data, and confidence.
- Use user's saved thesis when available.
- Cite source events, filings, fundamentals, and metrics.
- Prefer conditional language.

Current task:
Implement POST /api/tickers/{ticker}/ask.
Input:
- ticker
- user_id optional
- question

The service should gather:
- recent events
- event impact metrics
- recent bars and volume metrics
- fundamentals
- user tags and thesis

Return a structured answer with:
- known_facts
- market_reaction
- interpretations
- thesis_strengtheners
- thesis_weakeners
- missing_data
- confidence
- citations
```

---

## 16.10 Alerts Agent

### Mission

Build event and market reaction alerts.

### Responsibilities

- Alert rule model
- Alert evaluator
- Event alert triggers
- Market metric triggers
- Delivery channels
- Deduplication
- Failure handling

### Deliverables

- `apps/api/app/services/alerts_service.py`
- `apps/api/app/workers/alert_worker.py`
- `apps/api/app/providers/notifications/`
- Tests

### Prompt

```text
You are the Alerts Agent for CatalystLens.

Build alert rules and delivery for watchlist events and market reactions.

Rules:
- Alerts must be deduplicated.
- Delivery failures must be logged.
- Users must be able to pause rules.
- Do not send repeated spam for the same event.
- Include source/event links when available.

Current task:
Implement alerts for:
- new SEC filing
- new earnings event
- RVOL above threshold
- tagged ticker has new event

Delivery:
- email stub
- Discord webhook implementation
```

---

## 16.11 DevOps Agent

### Mission

Make the app easy to run, test, and deploy.

### Responsibilities

- Docker Compose
- Environment variables
- Database migrations
- Worker process
- Logging
- Health checks
- Basic CI

### Deliverables

- `docker-compose.yml`
- `Dockerfile.api`
- `Dockerfile.web`
- `.env.example`
- `Makefile`
- GitHub Actions workflow later

### Prompt

```text
You are the DevOps Agent for CatalystLens.

Make the project runnable by a developer with one command.

Rules:
- Use Docker Compose first.
- Include Postgres and Redis.
- Include API and web services.
- Include migration command.
- Include .env.example.
- Do not introduce Kubernetes.

Current task:
Create local development infrastructure with:
- api
- web
- postgres
- redis
- worker

Add Makefile commands:
- make up
- make down
- make logs
- make migrate
- make test
```

---

## 16.12 QA/Test Agent

### Mission

Prevent the product from lying with confidence.

### Responsibilities

- Unit tests
- Integration tests
- Calculation tests
- Timezone tests
- API tests
- Data quality tests
- Synthetic market data fixtures

### Deliverables

- `apps/api/app/tests/`
- `apps/web/src/tests/`
- `docs/testing.md`
- Synthetic fixtures

### Prompt

```text
You are the QA/Test Agent for CatalystLens.

Build tests for all critical calculations and API behavior.

Rules:
- Focus heavily on time, timezone, market session, and event window bugs.
- Use synthetic data where exact expected outputs are known.
- Test missing data and provider failure behavior.
- Test that AI answers include required sections.

Current task:
Create tests for:
- VWAP
- anchored VWAP
- relative volume
- event window slicing
- event impact returns
- trade side classification
- API error responses
```

---

## 16.13 Compliance and Copy Agent

### Mission

Keep product language clear, honest, and safe.

### Responsibilities

- Compliance boundaries
- Disclaimers
- UI copy
- Landing page claims
- AI refusal language
- Paywall limitations copy

### Deliverables

- `docs/compliance_boundaries.md`
- `docs/copy_guidelines.md`
- Suggested disclaimers
- Landing page copy review

### Prompt

```text
You are the Compliance and Copy Agent for CatalystLens.

Review product language and AI answer behavior.

Rules:
- Do not allow promises of profit.
- Do not allow direct personalized buy/sell advice.
- Do not call inferred data certain.
- Do not imply paywall bypassing.
- Prefer source-backed, educational, conditional language.

Current task:
Write docs/compliance_boundaries.md and docs/copy_guidelines.md.
Include:
- approved language
- prohibited language
- AI answer rules
- paywall blocked content rules
- disclaimer examples
```

---

## 16.14 Growth/Landing Page Agent

### Mission

Create a clear landing page and beta signup flow.

### Responsibilities

- Positioning
- Landing page copy
- Pricing experiments
- Waitlist form
- Beta user feedback questions

### Deliverables

- `docs/landing_page.md`
- `apps/web/src/app/page.tsx`
- Waitlist form

### Prompt

```text
You are the Growth/Landing Page Agent for CatalystLens.

Create a landing page for beta users.

Rules:
- Do not promise profits.
- Do not sell the app as a trading bot.
- Emphasize catalyst timeline, volume flow, source-backed research, and watchlist alerts.
- Keep copy specific and practical.

Current task:
Create landing page copy and a simple waitlist form.

Target headline direction:
"See what moved your watchlist and how the market reacted."
```

---

# 17. Shared Coding Standards

## Backend

- Use type hints.
- Use Pydantic schemas.
- Keep routers thin.
- Keep provider adapters isolated.
- Write tests for calculations.
- Avoid global mutable state.
- Log provider failures.
- Store raw provider payloads.
- Normalize timestamps to UTC.
- Convert to display timezone at the edge.

## Frontend

- Use TypeScript.
- Keep chart components prop-driven.
- Separate API fetching from display components.
- Use loading, empty, and error states.
- Do not hide missing data.
- Prefer explanatory labels.

## Data

- Never store fake zeroes for missing values.
- Preserve source timestamp and ingestion timestamp.
- Track provider and source URL.
- Track access level.
- Track confidence.
- Track raw payload hash for deduplication.

## AI

- Never answer from vibes.
- Use context builder.
- Include missing data.
- Include confidence.
- Include source references.
- Avoid predictions stated as fact.

---

# 18. API Contract Drafts

## GET /api/tickers/{ticker}/summary

Response:

```json
{
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "exchange": "NASDAQ",
  "price": 185.12,
  "change_pct": 1.24,
  "volume": 42100000,
  "relative_volume": 1.8,
  "session": "regular",
  "latest_event": {
    "id": "evt_123",
    "event_type": "earnings",
    "title": "Q2 earnings released",
    "event_time": "2026-05-13T13:30:00Z",
    "confidence": 0.91
  }
}
```

## GET /api/tickers/{ticker}/bars

Query params:

```text
timeframe=1m|5m|1d
start=ISO datetime
end=ISO datetime
```

Response:

```json
{
  "ticker": "AAPL",
  "timeframe": "1m",
  "bars": [
    {
      "timestamp": "2026-05-13T13:30:00Z",
      "open": 184.1,
      "high": 184.9,
      "low": 183.8,
      "close": 184.7,
      "volume": 123456,
      "vwap": 184.42,
      "session": "regular"
    }
  ]
}
```

## GET /api/tickers/{ticker}/events

Response:

```json
{
  "ticker": "AAPL",
  "events": [
    {
      "id": "evt_123",
      "event_type": "sec_filing",
      "event_time": "2026-05-13T13:31:18Z",
      "title": "8-K filed",
      "summary": "Company filed a current report.",
      "source": "SEC EDGAR",
      "url": "https://example.com",
      "access_level": "full_text",
      "confidence": 0.95
    }
  ]
}
```

## GET /api/events/{event_id}/impact

Response:

```json
{
  "event_id": "evt_123",
  "ticker": "AAPL",
  "event_time": "2026-05-13T13:31:18Z",
  "metrics": [
    {
      "window": "5m",
      "return_pct": 1.2,
      "benchmark_adjusted_return_pct": 1.0,
      "volume": 982300,
      "relative_volume": 4.3,
      "dollar_volume": 181234000,
      "vwap_distance_pct": 0.7,
      "confidence": 0.82
    }
  ]
}
```

## POST /api/tickers/{ticker}/ask

Request:

```json
{
  "user_id": "user_123",
  "question": "What would need to happen for a bounce?"
}
```

Response:

```json
{
  "ticker": "AAPL",
  "question": "What would need to happen for a bounce?",
  "answer": {
    "known_facts": ["..."],
    "market_reaction": ["..."],
    "interpretations": ["..."],
    "thesis_strengtheners": ["..."],
    "thesis_weakeners": ["..."],
    "missing_data": ["..."],
    "confidence": "medium"
  },
  "citations": [
    {
      "type": "event",
      "id": "evt_123",
      "label": "Q2 earnings released"
    }
  ]
}
```

---

# 19. Core Calculation Specs

## VWAP

Formula:

```text
VWAP = sum(price * volume) / sum(volume)
```

For OHLCV bars, use typical price if trade-level data is not available:

```text
typical_price = (high + low + close) / 3
bar_vwap_approx = sum(typical_price * volume) / sum(volume)
```

Label approximate VWAP clearly if calculated from bars rather than trades.

## Anchored VWAP

Same as VWAP, but start calculation at an anchor timestamp.

Common anchors:

- Market open
- Earnings release
- SEC filing
- News headline
- Halt resume
- User-defined timestamp

## Relative Volume

Basic formula:

```text
relative_volume = current_cumulative_volume / average_cumulative_volume_for_same_time
```

Important:

- Compare same session type to same session type.
- Do not compare premarket volume to full-day volume.
- Use a rolling historical baseline, such as 20 prior trading days.

## Event Return

Formula:

```text
return_pct = (price_at_window_end - price_at_event) / price_at_event * 100
```

If price_at_event is unavailable, use nearest next available bar and mark lower timestamp quality.

## Benchmark-Adjusted Return

Formula:

```text
adjusted_return = ticker_return - benchmark_return
```

Potential benchmarks:

- SPY for broad market
- QQQ for tech-heavy names
- Sector ETF later

## Trade Side Classification

Quote rule:

```text
midpoint = (bid + ask) / 2

if trade_price > midpoint:
    buyer_initiated
elif trade_price < midpoint:
    seller_initiated
else:
    ambiguous
```

Fallback tick rule:

```text
if trade_price > previous_trade_price:
    buyer_initiated
elif trade_price < previous_trade_price:
    seller_initiated
else:
    ambiguous
```

Always track ambiguity.

## Cumulative Volume Delta

Formula:

```text
CVD = cumulative_sum(estimated_buy_volume - estimated_sell_volume)
```

Label as estimated.

---

# 20. UI Design Requirements

## Ticker Header

Show:

- Ticker
- Company name
- Current price
- Percent change
- Volume
- Relative volume
- Catalyst status
- Risk flags

Example:

```text
XYZ  $12.44  +8.2%  RVOL 6.4x  Catalyst: Earnings Beat  Risk: Offering history
```

## Main Chart

Must show:

- Candles
- Volume
- VWAP
- Anchored VWAP
- Event markers

## Event Rail

Must show:

- Event timestamp
- Type icon or label
- Title
- Source
- Confidence
- Market reaction preview

## Volume Flow Panel

V1:

- Cumulative volume vs average
- RVOL gauge
- Dollar volume
- Spike markers

V2:

- Estimated buy volume
- Estimated sell volume
- CVD
- Spread
- Liquidity warnings

## Ask Panel

Suggested questions:

- Why is this moving today?
- What changed since the last event?
- Is the move supported by volume?
- What would strengthen a bounce thesis?
- What would weaken the thesis?
- What are the next catalysts?

---

# 21. Testing Checklist

## Backend Tests

- Symbol lookup
- Market bar ingestion
- Duplicate bar handling
- Missing bar handling
- Event ingestion
- Event deduplication
- Event impact windows
- VWAP
- Anchored VWAP
- Relative volume
- Trade side classification
- CVD
- API response validation
- Provider error handling

## Frontend Tests

- Ticker page renders loading state
- Ticker page renders error state
- Chart receives correct data shape
- Event marker click opens drawer
- Empty event list displays properly
- Ask panel handles pending answer

## AI Tests

- Answer contains required sections
- Answer includes citations
- Answer states missing data
- Answer refuses direct buy/sell request
- Answer does not claim certainty when confidence is low

## Timezone Tests

- US market open converted correctly
- Premarket identified correctly
- Regular session identified correctly
- After-hours identified correctly
- Event timestamp aligns with chart marker

---

# 22. Observability and Operations

Track:

- Last successful ingest per provider
- Provider latency
- Provider failure rate
- API quota usage
- Missing data count
- Duplicate event rate
- Event classification accuracy
- Alert delivery latency
- Alert failure rate
- AI answer citation coverage
- User watchlist count
- Events viewed per user
- Alerts clicked
- Tagged ticker retention

Admin/debug pages later:

- Provider status
- Ingest logs
- Event deduplication view
- Failed alerts
- Data freshness dashboard

---

# 23. Security and Secrets

Rules:

- Do not commit API keys.
- Use `.env.example` with placeholder values.
- Use environment variables for provider keys.
- Do not log secrets.
- Do not expose raw provider credentials to frontend.
- Rate-limit expensive endpoints.
- Validate ticker input.
- Sanitize user notes before rendering.

---

# 24. First Sprint Task List

## Sprint 1 Goal

A local app where `/ticker/AAPL` shows chart, volume, VWAP, and event rail placeholders.

Tasks:

1. Create repo structure.
2. Add Docker Compose with API, web, Postgres, Redis.
3. Add FastAPI skeleton.
4. Add Next.js skeleton.
5. Add SQLAlchemy and Alembic.
6. Create `symbols` and `market_bars` models.
7. Seed a few symbols.
8. Implement market bars provider stub using static fixture data.
9. Implement `/api/tickers/{ticker}/bars`.
10. Implement `/api/tickers/{ticker}/summary`.
11. Build ticker page.
12. Render chart and volume.
13. Implement VWAP calculation.
14. Add backend tests for VWAP and bars endpoint.
15. Add README instructions.

Acceptance criteria:

- `make up` starts the app.
- `/ticker/AAPL` renders chart data.
- Tests pass.
- No real provider key required for local demo.

---

# 25. Second Sprint Task List

## Sprint 2 Goal

Events appear on the chart and in the event rail.

Tasks:

1. Create `data_sources`, `raw_ingest`, and `events` models.
2. Add event taxonomy enum.
3. Implement event fixture provider.
4. Implement SEC provider stub or real minimal SEC fetcher.
5. Implement `/api/tickers/{ticker}/events`.
6. Add event markers to chart.
7. Add event rail.
8. Add event detail drawer.
9. Add event deduplication tests.
10. Add timestamp alignment tests.

Acceptance criteria:

- `/ticker/AAPL` shows at least one event marker.
- Clicking marker opens details.
- Events are sorted chronologically.
- Tests pass.

---

# 26. Third Sprint Task List

## Sprint 3 Goal

Clicking an event shows reaction metrics.

Tasks:

1. Create `event_impact_metrics` model.
2. Implement event window slicing.
3. Implement return calculations.
4. Implement relative volume baseline.
5. Implement anchored VWAP from event.
6. Implement `/api/events/{event_id}/impact`.
7. Add event impact panel.
8. Add tests with synthetic bars.

Acceptance criteria:

- Event detail drawer shows +5m, +15m, +60m reaction.
- Anchored VWAP appears after event.
- Relative volume is displayed.
- Tests pass.

---

# 27. Fourth Sprint Task List

## Sprint 4 Goal

User can tag a ticker, save a thesis, and ask a source-backed question.

Tasks:

1. Create simple user model.
2. Create watchlists.
3. Create tags.
4. Create theses.
5. Add UI for tagging ticker.
6. Add thesis notes panel.
7. Build AI context builder.
8. Implement answer service stub.
9. Implement `/api/tickers/{ticker}/ask`.
10. Add safe answer template.
11. Add tests for answer structure.

Acceptance criteria:

- User can save a thesis for a ticker.
- User can ask "Why is this moving?"
- Answer includes known facts, market reaction, missing data, confidence, and sources.
- System does not provide direct buy/sell recommendation.

---

# 28. Useful Agent Coordination Rules

Before any agent changes code, it should answer:

1. What files will I touch?
2. What contract am I implementing?
3. What tests will prove it works?
4. What assumptions am I making?
5. What should another agent avoid touching at the same time?

After any agent changes code, it should report:

1. Files changed
2. Commands run
3. Tests passed or failed
4. Known issues
5. Next recommended task

No agent should silently rewrite the architecture.

---

# 29. Master Prompt for Cursor/Codex

Use this to initialize a coding agent:

```text
You are working on CatalystLens, a market event and liquidity intelligence dashboard.

Core product:
A source-backed research dashboard that helps users understand what moved a ticker, when it moved, what event likely triggered it, how volume/liquidity reacted, and what facts support or weaken a user's thesis.

Important boundaries:
- Do not build trading execution.
- Do not provide direct buy/sell advice.
- Do not bypass paywalls.
- Do not call inferred buy/sell volume certain.
- Build source-backed analytics, not predictions stated as fact.

Engineering principles:
- Build vertical slices.
- Keep provider adapters isolated.
- Store raw provider payloads in raw_ingest.
- Normalize timestamps to UTC.
- Write tests for all calculations.
- Keep frontend chart components typed and prop-driven.
- Prefer simple Docker Compose over complex infrastructure.

Before coding:
1. Read docs/product_spec.md.
2. Read docs/metrics.md.
3. Read docs/event_taxonomy.md.
4. State the exact files you will modify.
5. State the tests you will add or run.

After coding:
1. Summarize files changed.
2. Explain the implementation.
3. Report tests run.
4. State any assumptions or limitations.
```

---

# 30. First Exact Commands for Local Project Setup

These are suggested commands, not gospel. Adjust for your environment.

```bash
mkdir -p catalystlens
cd catalystlens
mkdir -p docs apps/api apps/web infra scripts notebooks
```

Create backend:

```bash
cd apps/api
python -m venv .venv
. .venv/bin/activate
pip install fastapi uvicorn sqlalchemy alembic psycopg pydantic pytest httpx python-dotenv
```

Create frontend:

```bash
cd ../../apps
npx create-next-app@latest web --typescript --eslint --app
```

Add local infra:

```bash
cd ..
touch docker-compose.yml .env.example Makefile README.md
```

Again: do not blindly run commands. Understand the shape first.

---

# 31. Biggest Risks

## Data Licensing

Market data licensing can become expensive and restrictive. Design provider adapters so data sources can be swapped.

## False Causation

Markets move for multiple reasons. Use confidence and careful wording.

## Bad Timezones

Financial apps die by timestamp bugs. Store UTC, display ET for US equities, and test session boundaries.

## Fake Buy/Sell Volume

Trade direction is inferred unless the data explicitly provides aggressor side. Label it as estimated.

## Scope Creep

Do not build everything. Build a ticker page, events, impact metrics, tags, ask panel, and alerts.

## AI Hallucination

The AI layer must only summarize available context. It must say when data is missing.

---

# 32. What Success Looks Like

A useful V1 lets a user open a ticker and immediately see:

- What events happened
- Where those events occurred on the chart
- How price reacted
- Whether volume was abnormal
- Whether the move held or failed around VWAP
- What sources support the explanation
- What data is missing
- What upcoming events matter
- What would strengthen or weaken their saved thesis

If V1 does that, you have a real product foundation.

Everything else is garnish until this works.

