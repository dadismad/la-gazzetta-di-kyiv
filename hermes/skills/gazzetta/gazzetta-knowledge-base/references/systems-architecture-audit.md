# Systems Architecture Audit — lagazzettadikyiv.com

Consolidated architecture map, critical rendering path, data quality diagnostics, and SPOF mapping. Discovered during June 2026 architecture review.

## Architecture Map

```
SQLite DB (gazzetta.db) ← 3 ingestion paths:
  ├── Telegram Monitor → intel_to_stories.py
  ├── OSINT Collector → fetch_intel.py → approve_draft.py
  └── Manual drafts

  └── db_to_json.py → data/stories.json + data/flows.json
        ↓
  build_site.py → site/ (static HTML/JS/CSS)
        ↓
  shipit.sh (8 stages) → gsutil rsync → GCS bucket
        ↓
  verify_reality.py → post-deploy audit
```

**Frontend architecture:** Vanilla JS, no framework. Content rendered entirely client-side via `app.js boot()`.

## Critical Frontend Rendering Path

```
STEP 1: DNS (2ms) → TCP (29ms) → TLS (95ms)
STEP 2: HTML download (TTFB 269ms, 22.5KB — 19.4% inline SVGs, 0 story cards)
STEP 3: ⚠️ render-blocking: Google Fonts CSS (external, cross-origin)
STEP 4: ⚠️ render-blocking: styles.css (74KB — full design system)
STEP 5: <body> parsed — empty containers + loading skeletons visible
STEP 6: ⚠️ render-blocking: i18n.js (3.4KB) + app.js (129KB)
         → NO async/defer — blocks HTML parsing
STEP 7: boot() starts → sequential chain:

  a. await i18nReady (poll 50ms, timeout 5s)
  b. wireCollapsibleContainers() + wireCardDelegation()
  c. renderAnchor() + renderTrackRecord()
  d. updateMasthead()
  e. ⚠️ await fetchFlows()           — 1st HTTP round-trip
  f. ⚠️ await market_prices.json     — 2nd HTTP round-trip
  g. ⚠️ await living_stories.json    — 3rd HTTP round-trip
  h. ⚠️ await stories.json (1.5MB)   — 4th HTTP round-trip
  i. appendStoryCard() × 245         — DOM manipulation
  j. updateCumulativeStats() + populateSidebar()
  k. setTimeout → populateTeasers()  — MORE fetches

FIRST CONTENTFUL PAINT: ~300ms (masthead only)
FIRST MEANINGFUL PAINT: ~2-5s on 4G (story cards visible)
TIME TO INTERACTIVE: ~5-8s
```

## Data Quality Diagnostic

Run this one-liner to baseline production data health:

```bash
curl -s https://www.lagazzettadikyiv.com/data/stories.json | python3 -c "
import json,sys
d=json.load(sys.stdin)
ss=d.get('stories',[])
print(f'Stories: {len(ss)}')
print(f'Generated: {d.get(\"generated_at\")}')
print(f'Total amount_b: \${sum(float(s.get(\"amount_b\",0) or 0) for s in ss):,.0f}')
print(f'Confidence values: {sorted(set(s.get(\"confidence_pct\",0) for s in ss))}')
print(f'Flows in stories.json: {len(d.get(\"flows\",[]))}')
print(f'Sources: {sorted(set(s.get(\"source\",\"\") for s in ss))}')
# Flag zero amounts
zero_count = sum(1 for s in ss if not s.get('amount_b') or s.get('amount_b')==0)
if zero_count > len(ss)*0.1:
    print(f'⚠️  WARNING: {zero_count}/{len(ss)} stories have amount_b=0')
flat_conf = len(set(s.get('confidence_pct',0) for s in ss))
if flat_conf <= 3:
    print(f'⚠️  WARNING: Only {flat_conf} unique confidence values (pipeline stuck)')
"
```

**Known data pipeline failure modes:**

| Symptom | Likely Root Cause | Fix |
|---------|-------------------|-----|
| All amount_b = $0 | `context_amount()` fallback in pipeline; scaling step in `db_to_json.py` losing amounts | Trace amount field through `db_to_json.py` → SQL query → DB |
| All confidence = 0 | `compute_confidence()` import failure or SQL null default | Check `import compute_confidence` from `generate_flows.py`; check DB default |
| All confidence flat (50/65/75) | Old flat defaults — `compute_confidence()` not being called | Run `db_to_json.py` v23+ which auto-computes; or `backfill_pace.py` + manual compute |
| Story count flat despite DB growing | `osint` exclusion filter in SQL (legacy) OR `pending_review` vs `pending` status mismatch | Check `WHERE` clause in `db_to_json.py`; check `gazzetta_product_factory.sh` query |
| flows.json separate from stories.json | `db_to_json.py` writes to separate files; frontend fetches both | Check `Has flows key` in stories.json — if False, 2nd HTTP fetch needed |

## Single Points of Failure (Ranked)

| # | SPOF | What Breaks | Recovery |
|---|------|-------------|----------|
| 1 | SQLite DB (gazzetta.db) | No stories flow to production | Restore from backup; none automated |
| 2 | db_to_json.py | Pipeline stops; no new JSON | Git checkout + manual run |
| 3 | GCS bucket (single backend) | Complete site blackout | No failover configured |
| 4 | Cron scheduler (single macOS process) | Pipeline stops silently; 12h+ outage possible | `cron-recovery-procedure.md` |
| 5 | boot() JS function (single entry point) | Null DOM element = complete frontend blank | Git rollback + null-guard fix |
| 6 | Hermes Agent (single automation orchestrator) | No pipeline, no cron, no deploy | Restart agent + restore cron jobs |

## Frontend Performance Baseline

| Metric | Current Value | Target (Lighthouse 90+) |
|--------|---------------|------------------------|
| First Contentful Paint | ~300ms (masthead) | < 1.0s |
| First Meaningful Paint | ~2-5s (4G) | < 1.5s |
| Largest Contentful Paint | ~3-6s | < 2.5s |
| Total JS Payload | 132.4KB (129KB app + 3.4KB i18n) | < 50KB per-page |
| Total CSS Payload | 74KB | < 30KB (inline critical) |
| JSON Payload (cold load) | ~1.77MB (stories 1.5MB + flows 215KB + prices 57KB) | < 200KB first load |
| Render-blocking requests | 4 (fonts CSS, styles.css, i18n.js, app.js) | 0 |
| Sequential fetches in boot() | 4-6 | 1 (Promise.all) |

## Known GCS Metrics (June 2026)

| Asset | Size | Cache Policy | Last Modified |
|-------|------|-------------|---------------|
| index.html | 22.5KB | max-age=0,must-revalidate | 2026-06-11 |
| app.1683dea1.js | 129KB | public, max-age=3600 | 2026-06-11 |
| styles.6e5321ba.css | 74KB | public, max-age=3600 | 2026-06-11 |
| i18n.7dcc40be.js | 3.4KB | public, max-age=3600 | 2026-06-11 |
| data/stories.json | 1.5MB | private, no-store | fresh |
| data/flows.json | 215KB | private, no-store | fresh |
| /ru/ | 404 | — | BROKEN |

## Boot Sequence Optimization Pattern

Replace sequential awaits with `Promise.all()`:

```javascript
// BEFORE (sequential waterfall):
await i18nReady();
await fetchFlows();
await fetchMarketPrices();
await fetchStories();

// AFTER (parallel — ~1 RTT instead of 4):
const [flowsData, pricesData, storiesData] = await Promise.all([
  fetchFlows(),
  fetchMarketPrices().catch(() => null),     // optional — never blocks
  getJSON(getDataPath(), null),
]);
```

Combine with:
- Inject hero stats (story count, capital tracked, model confidence) into HTML at **build time** → zero JS needed for above-fold stats
- Inject first 5 story cards as static HTML → first paint includes real content
- Add `defer` to all `<script>` tags → eliminates render blocking
- Self-host Google Fonts → eliminates cross-origin blocking request
