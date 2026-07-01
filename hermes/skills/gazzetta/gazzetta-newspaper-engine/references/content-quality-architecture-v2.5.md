# Content Quality Architecture — v2.5.0 (June 2026)

## DeepSeek Prompt v2.2

### Materiality Gate (new)
Before scoring contradiction_gap, DeepSeek must ask: does this news event have a plausible causal connection to the assets tracked for this narrative? If unrelated (e.g., local crime story vs broad ETF, cultural article vs commodity prices), set gap to 0-10 and reality to "No material connection between this event and the tracked assets."

### Full-Range Scoring Guide
Replace binary "70+ if contradiction, <30 if aligned" with:
- 0-20: Narrative and price action fully aligned, or NO MATERIAL CONNECTION
- 21-40: Minor tension, mostly aligned
- 41-60: Moderate contradiction, mixed signals
- 61-80: Significant contradiction, narrative under pressure
- 81-100: Extreme contradiction, large price moves (2%+ broad indices, 5%+ sector ETFs)

Score MUST reflect price move MAGNITUDE, not just direction. A 0.4% ETF dip is 10-20, not 85.

### Headline Diversity
Forbid repeating the same verb (Fails, Ignores, Contradicts, Defies) more than once per batch. Require at least 3 different headline patterns per 10 stories. Acceptable patterns: direct statements, contrast pairs, questions, numeric hooks.

### Source Citation
they_say must begin with source name and colon: "Reuters reports: ..." or "SCMP claims: ..."

## Capital Volume from Real Data

### market_reality.py AUM Fetch
`fetch_yahoo()` now attempts `fast_info.total_assets` for every ticker. Stored as `"aum"` field in the price dict. Falls back gracefully if unavailable.

### assemble_story() AUM Computation
Sums AUM of all narrative tickers from market data. Uses computed AUM if >0; falls back to LLM estimate; then 0. This replaces LLM-hallucinated capital_volume_usd ($50M, $100B guesses) with real ETF AUM data.

### pick_market_context() Expansion
- All 4 narrative tickers sent (was 2-3)
- AUM appended to each ticker line: `FXI: $33.30 (-1.04%) AUM=$8,500,000,000`
- Benchmark context (SPY, QQQ, VIX) appended to every analysis for regime awareness

## Quality Gates

### Narrative Cap (merge_stories)
MAX_PER_NARRATIVE = 50. After dedup, stories are capped at 50 per container. Fixes China overweight (130/200 → 50/400).

### Reality Text Dedup (merge_stories)
Stories with identical reality text (first 120 chars) are deduplicated. The story with higher contradiction_gap is kept. Fixes same-data recycling where one price move appears in dozens of stories.

## Source Attribution on Cards

### build_frontend.py Template
Story cards now display feed_source when non-empty:
```javascript
(s.feed_source ? '<span class="...">via '+(s.feed_source||'')+'</span>' : '')
```
Rendered in the metadata row alongside container title and time-ago.

### extract_domain() Expansion
Domain mapping expanded from 5 to 15 entries covering all 7 RSS feed domains. Generic fallback strips TLD and capitalizes parts instead of raw `domain.upper()`.

## Pipeline Order Fix

gen_flows now runs BEFORE build_frontend (was after). Fixes one-cycle-stale flows data in the compiled HTML.

New order: ingestion → market_data → synthesis → gen_flows → build_frontend → test_platform → telegram_post → deploy

## Telegram Fixes

- Broken link: `/stories.html#story-ID` → `https://www.lagazzettadikyiv.com` (site is single-page, no story anchors)
- Freshness: `FRESHNESS_HOURS = 2` → `48` (was posting 0 stories every cycle)
- Idempotency via posted_stories.jsonl unchanged

## Governor Deploy Fix

- gcloud path: `/usr/bin/gcloud` absolute (systemd PATH doesn't include gcloud)
- Error tolerance: `;` instead of `&&` before CDN invalidation, `; true` at end
- Result: deploy now reports OK instead of FAIL(1) every cycle