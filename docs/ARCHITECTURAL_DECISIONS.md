# Architectural Decision Records

> **Purpose**: Prevent future Hermes instances from re-litigating settled choices. Every major architectural decision is recorded here with context, rationale, and consequences.

---

## ADR-001: Append-Only Recommendation Ledger

- **Date**: 2026-06-25
- **Status**: Accepted

**Context**: Tracking the lifecycle of trade theses (THE PLAY) required a persistence mechanism. Initial proposals involved retroactively scanning `stories.json` to build a ledger.

**Decision**: Append a single JSONL line at `data/recommendation_ledger.jsonl` inside `telegram_broadcast.py` upon successful `send_telegram()`. No retroactive scanning.

**Rationale**: Retroactive state-scanning introduces looping overhead and risk of `AttributeError` crashes if schemas change. Writing at dispatch time makes the broadcast engine the immutable system of record. JSONL enables append-only writes without loading the full file.

**Consequences**: Every HIGH/ELEVATED conviction trade thesis that reaches Telegram is automatically tracked. Historical theses from before this ADR are not retroactively captured.

---

## ADR-002: Upstream Ticker & Source Normalization

- **Date**: 2026-06-25
- **Status**: Accepted

**Context**: The pipeline was passing through single-character source artifacts (`"T"`) and unformatted ticker symbols, corrupting frontend presentation.

**Decision**: Ticker formatting (uppercase, `$`/`#` stripping, canonical set validation) and source validation (intercepting `"t"`/`"T"`/`"UNKNOWN"`) are enforced inside `contradiction_synthesizer.py` rather than patched at broadcast or frontend.

**Rationale**: Data must be clean when it enters state (`all_stories`). Patching display logic hides the problem; fixing at ingestion ensures all downstream consumers (frontend, Telegram, future API) receive pristine data.

**Consequences**: Adds ~30 lines of validation to the synthesizer. Any new data source must pass these normalization gates.

---

## ADR-003: Destination Framing for Narrative Taxonomies

- **Date**: 2026-06-25
- **Status**: Accepted

**Context**: Initial narrative labels used legacy source-state framing (e.g., `CRITICAL_RESOURCE_CONTROL`, `DOLLAR_DECLINE`).

**Decision**: Transitioned all narrative display names to institutional terminal-state framing (e.g., *Energy Sovereignty*, *Sovereign Liquidity Migration*).

**Rationale**: Institutional traders bet on the destination, not the catalyst. Aligns visual taxonomy with the $6.5T Narrative Market Capitalization denominator. Internal IDs (`critical_resource_control`, `dollar_decline`) remain unchanged for code stability.

**Consequences**: All user-facing labels (website, Telegram, dossiers) use destination framing. Internal code references retain legacy IDs.

---

## ADR-004: Capital Volume Estimation Hierarchy

- **Date**: 2026-06-25
- **Status**: Accepted

**Context**: `capital_volume_usd` was being forced to 0 because the pipeline only accepted actual AUM data (which `market_prices.json` doesn't contain). This broke the leaderboard, sidebar, and Signal Pulse displays.

**Decision**: Implemented a 4-tier estimation hierarchy in `contradiction_synthesizer.py`:
1. CFTC net positioning × contract notional → HIGH confidence
2. Ticker price move × ETF AUM / market cap proxy → MEDIUM
3. Article-described capital rotation → LOW
4. 0 only if no basis → NONE

**Rationale**: Waiting for AUM data that doesn't exist produces broken displays. A transparent estimation hierarchy with confidence markers preserves trust while restoring functionality.

**Consequences**: New `capital_flow_confidence` and `estimation_method` fields added to story schema. $500B sanity cap prevents hallucinated overflows.

---

## ADR-005: Narrative Market Capitalization as Primary Size Metric

- **Date**: 2026-06-25
- **Status**: Accepted

**Context**: The platform had no way to answer "how big is this narrative economy?" — a fundamental question for allocation decisions.

**Decision**: Built `fetch_narrative_cap.py` to compute deterministic NMC from observable market data (yfinance). Equity market caps and ETF total assets, scaled by purity weights. No LLM estimation.

**Rationale**: Observable market data is auditable. LLM estimates are not. NMC provides the static denominator against which dynamic flow estimates gain meaning.

**Consequences**: `data/narrative_graph.json` and `data/narrative_cap.json` updated daily at 07:00 Kyiv. Frontend and Telegram formats now show "Capital in Play: $X.XT."

---

## ADR-006: Static Site with GCS as Deployment Target

- **Date**: 2026-06-18 (retroactively recorded)
- **Status**: Accepted

**Context**: The website needed to be fast, cheap, and globally available without server-side rendering.

**Decision**: `build_frontend.py` compiles a single static HTML file with all data embedded at build time. Deployed to GCS with CDN. Zero runtime JavaScript fetches.

**Rationale**: Eliminates server costs, cold starts, and API latency. Data freshness is maintained by the 10-minute pipeline cycle rather than real-time requests.

**Consequences**: Static model limits interactive features. Acceptable for current scale (600 stories). Directory-based data loading will be needed beyond ~3,000 stories.

---

*Last updated: 2026-06-25. New architectural decisions must be added as dated ADR entries with context, decision, rationale, and consequences.*
