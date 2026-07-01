# Phase 3 Narrative Architecture (June 21, 2026)

## Current Pipeline (10 stages)
```
ingestion → market_data → synthesis → classify → calc_capital → gen_flows → build_frontend → test_platform → telegram_post → deploy
```

## Key Additions (Phase 1-3)

### 48-Field Story Schema
Deployed in `contradiction_synthesizer.py` `assemble_story()`. Key new fields: narrative_id, data_fidelity, capital_at_stake_usd, materiality_pass, contradiction_note, brief_review, implication_note, event_type, geopolitical_dimension, causal_chain. Dead fields removed: thesis, multi_persona.

### 12 Narratives (narratives.json)
`data/narratives.json` is the single source of truth. Contains: display_name, description, tickers, invalidation_threshold, status, strength_score, velocity, story_count, capital_total_usd. Update via `update_narratives.py` after each cycle.

### classify_stories.py
Runs between synthesis and calc_capital. Re-assigns narrative_id to all stories using keyword matching from narratives.json descriptions + seed keywords + ticker names. Catches stories that lost narrative_id during synthesis merge dedup. Must run every cycle.

### calculate_capital.py
Computes capital_at_stake_usd from real data: CFTC (21 markets, TIER_1), CoinGecko (20 assets, TIER_2), FRED (3 series, TIER_3). ETF-based narratives use story's capital_volume_usd as TIER_3 fallback. Materiality gate: capital_at_stake >= $50M AND contradiction_gap >= 40. Sets tier: BREAKING (gap>=65, material), ACTIVE (gap>=40, material), SETTLING (otherwise).

### CFTC Data (21 markets)
`fetch_cftc_cot.py` merges TWO reports:
- Legacy COT (`deacotYYYY.zip` → annual.txt): Bitcoin, S&P 500, Gold, Silver, WTI Crude, UST Bond (6 markets)
- Disaggregated COT (`fut_disagg_txt_YYYY.zip` → f_year.txt): Copper, Corn, Soybeans, Wheat, Coffee, Sugar, Cotton, Cocoa, Cattle, Hogs, Gasoline, Palladium, Platinum (15 markets)

CRITICAL: ALWAYS verify CFTC URLs, column names, and market names against live data before writing scripts. Analyst-provided schemas are frequently hallucinated. The Legacy archive uses column "Market and Exchange Names" (with spaces). The Disaggregated archive uses "Market_and_Exchange_Names" (with underscores) and "Swap__Positions_Short_All" (double underscore is REAL in the data).

### Data Collectors (cron)
- CoinGecko: */5 * * * * (bulk endpoint, 20 assets, no API key)
- FRED: 30 1 * * * (public CSV endpoint, no API key)
- CFTC: 30 21 * * 5 (weekly after COT release)

## Critical Operational Patterns

### File Ownership
ALL data files under /opt/gazzetta-di-kyiv/data/ and public/data/ must be owned by gazzetta:gazzetta. The systemd service runs as user 'gazzetta'. Files created by alexstocchi (interactive) will cause Permission denied errors. Fix: `sudo chown gazzetta:gazzetta <file>`.

### Python .pyc Cache
After editing governor.py on the VM, purge `__pycache__/governor.cpython-311.pyc`. The Python interpreter may use the stale .pyc instead of the new .py, causing pipeline stages to silently not appear.

### Two stories.json Paths
- `data/stories.json` — pipeline working copy (synthesis writes here, classify/calc_capital read+write here)
- `public/data/stories.json` — deployed copy (build_frontend reads here, copied during deploy)

Keep them in sync. After manual edits: `sudo cp data/stories.json public/data/stories.json && sudo chown gazzetta:gazzetta public/data/stories.json`.

### VM Deployment Pattern
1. scp file to /tmp/ on VM (alexstocchi user)
2. `sudo cp /tmp/file /opt/gazzetta-di-kyiv/scripts/file`
3. `sudo chown gazzetta:gazzetta /opt/gazzetta-di-kyiv/scripts/file`

### SSH f-string Escaping
NEVER pipe complex Python with nested quotes through SSH. Write the script to /tmp/check.py via heredoc or scp, then run it. Shell escaping with f-strings containing dict access is guaranteed to fail.

### Batch API Calls
- CoinGecko: `/simple/price?ids=bitcoin,ethereum,solana,...` (comma-separated, single call)
- yfinance: `yf.download("AAPL NVDA BTC-USD")` (space-separated, single call)
- FRED: `/fredgraph.csv?id=WALCL` (single call per series, no rate limit)

### Materiality Gate Design
The gate requires BOTH capital >= $50M AND gap >= 40 (AND, not OR). An OR gate lets high-gap immaterial stories through (the Logic Professor's original complaint). The AND gate correctly identifies only 8 of 314 stories as material — dollar_decline (6) and crypto_reserve (2). This IS correct behavior — most stories are noise.
