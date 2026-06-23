# QUANT AUDIT REPORT — Data Integrity & Capital Flow Accuracy
## La Gazzetta di Kyiv — Portfolio Manager Review
**Date: 2026-06-22 | Auditor: Subagent (Portfolio Manager / Quant)**

---

## EXECUTIVE SUMMARY

**Data Trustworthiness Rating: 2/10**

The data pipeline contains **14 distinct discrepancies** spanning every layer from source scripts to live site. The most critical finding: **capital volume numbers are entirely manufactured** (every story gets a flat $100M hallucinated by the LLM), and the primary capital computation engine (`calculate_capital.py`) **never executes** in the production pipeline. The live site's "Capital Flows" table is a count × $100M multiplication with no real data backing.

---

## P0 — CRITICAL: Pipeline Execution Gaps

### 1. `calculate_capital.py` NEVER runs in production
**Severity: P0 | Category: Dead pipeline step**

The governor pipeline (`governor.py` lines 462-471) defines 8 STEPS:
```
ingestion → market_data → synthesis → gen_flows → build_frontend → test_platform → telegram_post → deploy
```

`calculate_capital.py` is NOT among them. Neither is `classify_stories.py` nor `update_narratives.py`. These are **dead code** — they exist on disk but never execute.

**Consequence in data (every story):**
```
capital_at_stake_usd = 0     // ← should be computed by calculate_capital.py
capital_base_usd = 0         // ← should be set from asset_base
data_fidelity = "TIER_3"     // ← should be TIER_1/2/3 per narrative
narrative_alpha = {}         // ← empty/missing
```

### 2. Supporting market data files are missing or stubs
**Severity: P0 | Category: Broken dependency chain**

Files that `calculate_capital.py` depends on:
| File | Status | Content |
|------|--------|---------|
| `data/cftc_cot.json` | EXISTS | **STUB** — `"source": "CFTC COT (stub — API key not configured)", "positions": []` |
| `data/fred_macro.json` | MISSING | Does not exist |
| `data/coingecko_data.json` | MISSING | Does not exist |

Even if `calculate_capital.py` ran, it would fall back to $50M for ALL narratives (line 123 of calculate_capital.py) and produce garbage results.

---

## P1 — CRITICAL: Manufactured & Identical Capital Numbers

### 3. ALL stories have identical capital_volume_usd = $100M (manufactured)
**Severity: P1 | Category: Data fabrication**

**Evidence:**
- 189/191 stories: `capital_volume_usd = 100,000,000` (= $0.1B)
- 2/191 stories: `capital_volume_usd = 0` (the 2 where LLM followed prompt instructions)
- **0 stories have any other value**
- Capital flow amounts are just `count × $0.1B` = count × 100M

**Root cause:** `contradiction_synthesizer.py` line 416:
```python
capital_volume_usd = int(computed_aum) if computed_aum > 0 else (llm_volume if llm_volume > 0 else 0)
```
- `computed_aum` = 0 because `market_prices.json` has NO `aum` field for any ticker (0 of 31 tickers)
- `llm_volume` = 100,000,000 because LLM hallucinates this default value since prompt says "omit if not provided"
- The LLM ignores the instruction and fabricates $100M

**Result: Live Capital Flows table is `count × $0.1B`:**  
| Narrative | Shown | Computation |
|-----------|-------|-------------|
| Rate Cycle | $4.0B, 40 stories | 40 × $0.1B |
| Energy Sovereignty | $2.8B, 29 stories | 29 × $0.1B - 1 story with $0 |
| Tech Convergence | $2.2B, 22 stories | 22 × $0.1B |
| Space Economy | $1.7B, 18 stories | 18 × $0.1B - 1 story with $0 |
| AI Chips | $1.4B, 14 stories | 14 × $0.1B |
| All others | n × $0.1B | n × $0.1B |

### 4. Contradiction Gaps are flat — 98.9% of stories at gap=15
**Severity: P1 | Category: No variance / Data quality**

- 189/191 stories (98.95%): `contradiction_gap = 15`
- 1/191 stories: gap=65
- 1/191 stories: gap=70
- **Only 2 stories have any meaningful differentiation**

This is statistically impossible for any real contradiction analysis system. The LLM produces a flat 15 for every story regardless of content. The frontend's gap-based filtering (highlighting gap ≥ 40) shows only 2 stories, with 189 invisible.

---

## P1 — DATA INCONSISTENCIES

### 5. `containers` section vs `all_stories` — two different universes
**Severity: P1 | Category: Dual data structure divergence**

The `stories.json` file has TWO story data structures that are completely disconnected:

| Narrative | containers.stories | all_stories.narrative_id | Delta |
|-----------|------------------|------------------------|-------|
| dollar_decline | **50** | 2 | -48 |
| energy_sovereignty | **34** | 29 | -5 |
| deglobalization | **50** | 2 | -48 |
| china_ascent | **0** | 1 | +1 |
| space_economy | **1** | 18 | +17 |
| gene_editing | **4** | 2 | -2 |
| tech_convergence | **51** | 22 | -29 |
| wealthy_sports | **2** | 1 | -1 |
| ai_chips | **1** | 14 | +13 |
| crypto_reserve | **0** | 10 | +10 |
| rate_cycle | **0** | 40 | +40 |
| commodity_supercycle | **0** | 9 | +9 |
| **Total** | **193** | **191** | **+2 to 191** |

The `containers` section is stale legacy data; `all_stories` is the modern structure. `build_frontend.py` correctly reads `all_stories`, but `generate_flows.py` reads `containers` (wrong). The test suite (`test_platform.py`) validates `containers` structure but not `all_stories`.

### 6. 41 stories (21%) are "unassigned"
**Severity: P1 | Category: 21% orphan data**

`classify_stories.py` exists to fix this but never runs. With 41 unassigned stories, the capital flows table is missing 21% of the data.

### 7. Live site contradicts `containers` data for capital flows
**Severity: P1 | Category: Display-data mismatch**

Live site claims:
- Rate Cycle: 40 stories → containers says 0
- Commodity Supercycle: 9 stories → containers says 0
- AI Chips: 14 stories → containers says 1
- Dollar Decline: 2 stories → containers says 50

The live table uses `all_stories.narrative_id` counts (from `build_frontend.py`). `containers` counts are completely wrong. A reader cross-referencing "stories by container" on another page would see totally different numbers.

### 8. Tiers are wrong — BREAKING/ACTIVE never materialize
**Severity: P1 | Category: Broken classification**

- 186 stories: "DEVELOPING" (should include 2 gap=65/70 stories that should be BREAKING per the gap_to_tier threshold)
- 5 stories: "ALIGNED" (from old archived script `intel_to_stories.py`)
- 0 stories: "BREAKING" or "ACTIVE"
- 0 stories: "SETTLING" (which calculate_capital.py would assign)

The "ALIGNED" tier is deprecated from archived scripts that no longer run. Tiers are frozen since no pipeline step updates them.

---

## P2 — PIPELINE DATA LINEAGE BREAKS

### 9. `generate_flows.py` reads wrong data structure
**Severity: P2 | Category: Incorrect data source**

`generate_flows.py` reads from the **legacy `containers` dict** (line 74), NOT from `all_stories`. This produces narrative_flows from the stale containers section, not from properly tagged stories. Although this script runs with `critical=False` (non-fatal), its output (`flows.json`) is still deployed.

### 10. `classify_stories.py`, `calculate_capital.py`, `update_narratives.py` all missing from pipeline
**Severity: P2 | Category: Missing pipeline steps**

All three scripts exist on disk but are excluded from the governor's `STEPS` array. They have no trigger point. Any data they would produce is absent.

### 11. `market_prices.json` lacks AUM field
**Severity: P2 | Category: API data loss**

`contradiction_synthesizer.py` tries to compute capital_volume from `prices[ticker]["aum"]`, but `market_prices.json` has **0 out of 31** tickers with an `aum` field. The market data fetcher (`fetch_yahoo` in `market_reality.py`) calls `fi.total_assets` but the result is either None or not persisted.

### 12. `backfill_narrative_ids.py` was a one-time script that hardcodes circular data
**Severity: P2 | Category: Historical script residue**

Line 61: `hydrated_story["capital_at_stake_usd"] = hydrated_story.get("capital_volume_usd", 0)`

This mirrors the LLM-hallucinated $100M into `capital_at_stake_usd`. Running this after `contradiction_synthesizer` would propagate the fake volume to the stake field. Since `calculate_capital.py` never runs afterward, the fake value persists.

---

## P3 — MONITORING & TESTING GAPS

### 13. `test_platform.py` has no capital validation
**Severity: P3 | Category: Test coverage gap**

The test suite checks:
- Container structure ✓
- Story_id uniqueness ✓
- Tags index validity ✓
- Required field presence ✓

**Does NOT check:**
- Capital_volume_usd sanity (all identical = FAIL, but no alert)
- Capital_at_stake_usd > 0
- Narrative_alpha existence
- Contradiction_gap distribution (98% at 15 is suspicious)
- Story count vs claimed count

The test would **PASS** even with all capital data at $0 or all identical.

### 14. `quality_gate.py` has insufficient alerting
**Severity: P3 | Category: Weak SLA monitoring**

The quality gate checks 4 metrics but only alerts when ALL 4 fail for 3 consecutive cycles. Metric (c) "capital volumes not all identical" IS currently failing (only 1 distinct value), but since other metrics likely pass (e.g., recency), the alert never fires.

### 15. `math_sanity_check.json` is a useless stub
**Severity: P3 | Category: Misleading validation**

Content: `{"math_sanity_passed": true, "vectors_tested": 6, "vectors_passed": 6}` — but no actual math vectors are defined. This is a hardcoded pass.

---

## DETAILED DATA FLOW MAP

```
SOURCE SCRIPTS                          DATA FILES                    DESTINATION
────────────────────────────────────────────────────────────────────────────────

ingestion_triage.py  ───→  SQLite DB  ───→  (Raw news items)
                                                      ↓
contradiction_synthesizer.py  ───→  market_prices.json  [NO AUM DATA]
       ↓ LLM hallucinates $100M           ↓ computed_aum=0 for all
       ↓ capital_volume_usd=100000000     ↓ falls through to LLM estimate
       ↓ contradiction_gap=15 (98.9%)     ↓ LLM output has no real AUM
                                                      ↓
                                   stories.json
                                   ├── containers [LEGACY, stale data]
                                   ├── all_stories [ACTIVE, 191 stories]
                                   │    ├── capital_volume_usd=100M (189/191)
                                   │    ├── capital_at_stake_usd=0 (191/191)
                                   │    ├── contradiction_gap=15 (189/191)
                                   │    └── narrative_alpha=empty [NEVER COMPUTED]
                                   └── tags_index
                                                      ↓
calculate_capital.py  → DOES NOT RUN (missing from STEPS)
classify_stories.py   → DOES NOT RUN (missing from STEPS)
update_narratives.py  → DOES NOT RUN (missing from STEPS)
                                                      ↓
build_frontend.py  ───→  index.html (570KB SPA)
       ├── Capital Flows table = sum(capital_volume_usd)/1e9 per narrative_id
       │                              = count × $100M / 1e9
       │                              = count × $0.1B
       └── Stream tab = all_stories[0:200], grouped by narrative_id
                                                      ↓
generate_flows.py  ───→  flows.json [reads containers dict, not all_stories]
                                                      ↓
                     GCS deploy → www.lagazzettadikyiv.com
```

---

## RECOMMENDED FIXES (by priority)

| Priority | Fix | Impact |
|----------|-----|--------|
| **P0** | Add `calculate_capital.py` to governor STEPS between synthesis and gen_flows | Restores capital_at_stake, narrative_alpha, materiality gate |
| **P0** | Fix `market_reality.py` to persist `aum` field in market_prices.json | Enables real capital volume computation |
| **P0** | Add CFTC/FRED/CoinGecko data pipelines or remove stubs | Unblocks real TIER_1/2 capital bases |
| **P1** | Add LLM prompt guard: require capital_volume_usd=0 when no AUM available | Stops $100M hallucination |
| **P1** | Delete or sync the legacy `containers` section to match `all_stories` | Eliminates dual-universe confusion |
| **P1** | Add `classify_stories.py` to pipeline after synthesis | Fixes 41 unassigned stories (21%) |
| **P2** | Fix `generate_flows.py` to read from `all_stories`, not `containers` | Corrects flows.json data |
| **P2** | Add `capital_volume_usd` variance check to `test_platform.py` | Catches flat-line data |
| **P3** | Lower quality_gate.py alert threshold from 4/4 to 2/4 failures | Earlier detection of data degradation |
| **P3** | Add real math validation to `math_sanity_check.json` or remove it | Removes false sense of security |
