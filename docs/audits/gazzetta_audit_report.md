# GAZZETTA DI KYIV — Content Quality Audit Report
**Date:** 2026-06-11 | **Analyst:** Hermes Agent

---

## 1. STORIES — Main Site (EN)

| Metric | Value |
|---|---|
| **Total stories** | **245** |
| Generated at | 2026-06-11T18:23:14 UTC |
| With `amount` | **0/245 (0%)** — No `amount` field on any story (capital flow amounts are in nested `capital_flow.amount_b`) |
| With `extracted_amount` | **0/245 (0%)** |
| With `pace_multiplier` | **245/245 (100%)** — All have pace in `capital_flow.pace_multiplier` or directly |
| With `paradigm_implications` | **245/245 (100%)** |
| With `tier` | **244/245 (99.6%)** |
| With `thesis` | **245/245 (100%)** |
| With `body`/`body_html` | **0/245 (0%)** — No body field exists; content lives in `thesis`, `they_say`, `reality` |
| With `headline` | **245/245 (100%)** |
| With `sector` | **244/245 (99.6%)** |
| With `horizon` | **245/245 (100%)** |
| With `confidence` | **245/245 (100%)** |
| Duplicate headlines | **0** — All unique |

### Tier Distribution
- **DEVELOPING:** 227 (92.7%)
- **ALIGNED:** 17 (6.9%)
- Missing: 1

### Sector Distribution
- **tech:** 69 (28.2%)
- **commodities:** 62 (25.3%)
- **defense:** 43 (17.6%)
- **equities:** 38 (15.5%)
- **crypto:** 23 (9.4%)
- **fixed_income:** 5 (2.0%)
- **fx:** 4 (1.6%)

### Pillar Distribution
- **multi_pillar:** 129 (52.7%)
- **china_ascendancy:** 50 (20.4%)
- **abundance_tech:** 27 (11.0%)
- **eu_fragmentation:** 21 (8.6%)
- **dollar_decline:** 11 (4.5%)
- **blockchain_agentic:** 7 (2.9%)

### Content Freshness
- **All null timestamps:** 245 (no published/created_at field on individual stories; only `generated_at` at file level)
- No future-dated entries detected
- Stories appear to be current OSINT pipeline output

---

## 2. LIVING STORIES

| Metric | Value |
|---|---|
| **Active stories** | **11** |
| Archived | 0 |
| Generated | 2026-06-05 (6 days old) |

### Field Coverage
- All 11 have `headline`, `sector`, `pillar`, `actors`, `status`
- **No `amount`, `pace_multiplier`, `paradigm_implications`, `tier`, `thesis`, `body`, `horizon`, `confidence`**
- 8 of 11 are >7 days old (last updated June 3-4)
- 6 are `new` (evolution_score=0.0, minimal evidence)
- 3 have `geopolitics` sector, 3 `macro`, 4 `tech`

---

## 3. FLOWS

| Metric | Value |
|---|---|
| **Total flows** | **199** |
| `total_flows_tracked` | 199 ✅ Matches |
| Generated at | 2026-06-11T18:23:14 UTC |
| Aggregate confidence | 52 |
| Direction | **Bullish** (inflow:outflow = 80:20) |

### Flow Field Coverage
- **asset_class:** 199/199 (100%)
- **direction:** 199/199 (100%)
- **confidence_pct:** 199/199 (100%)
- **name/flow_name:** 0/199 — No flow has a name field

### amount_b Analysis
- **Null:** 11/199 (5.5%) — Mostly in `fx` and `defense`
- **≤1.5 (generic/small):** 59/199 (29.6%)
- **Range:** 0.0000 – 300.0000
- **Mean:** 16.31

### Source Distribution
- **OSINT-sourced:** 191/199 (96.0%)
  - `osint_reuters_business`: 164
  - `osint_the_cradle`: 13
  - `osint_geopolitical_futures`: 8
  - `telegram_intel`: 8
  - `osint_federal_reserve`: 4
  - `osint_ecb_press`: 2
- **Non-OSINT:** 8 (telegram_intel)

### pace_multiplier Distribution
| Value | Count |
|---|---|
| 1.0 | 189 (95.0%) |
| 1.7 | 3 |
| 2.0 | 2 |
| 2.2 | 2 |
| 1.9 | 1 |
| 2.1 | 1 |
| 2.3 | 1 |

### Direction Distribution
- **Inflow:** 160 (80.4%)
- **Outflow:** 39 (19.6%)

### RU Flows
- **12 flows** (vs 199 EN)
- All have `amount_b` > 1.5 (mean: 66.0)
- Only 33% OSINT-sourced
- Confidence: 86 (higher than EN)

---

## 4. TRADES / TRACK RECORD

| Metric | Value |
|---|---|
| **Separate `trades.json` file** | ❌ **NOT FOUND** |
| **Trades in track_record.json** | **33** |
| Settled | 33 (100%) |
| Open | 0 |
| Win rate | **76%** (25 correct, 8 incorrect) |
| Total realized alpha | 25 |
| Avg correct PnL | +1.66% |
| Avg incorrect PnL | -0.9% |
| Success velocity | 1.3 |

### Trade Structure
Trades use different field naming from the audit spec:
- **No `entry`/`stop`/`target`** price fields
- Fields: `id`, `headline`, `date`, `direction`, `asset`, `conviction_pct`, `amount_b`, `narrative_sentiment`, `price_delta_pct`, `outcome`, `correct`, `settled`, `realized_pnl_pct`, `tier`
- Trades are outcome-based (correct/incorrect) rather than entry/stop/target based

---

## 5. SIGNAL ENDPOINT

| Metric | Value |
|---|---|
| **Signals claimed (total_signals)** | **245** |
| **Actual signals[] length** | **15** |
| **⚠ MISMATCH** | 245 ≠ 15 |
| Aggregate score | 67/100 |
| Generated at | 2026-06-11T18:23:22 UTC |

### Signal Structure
- Each signal has: `story_id`, `headline`, `score`, `tier`, `flow_alignment`, `contradiction`, `event_strength`, `asset_class`, `direction`
- All 15 are **HIGH CONVICTION** tier
- Scores range: 74-80
- **Story references:** 15/15 (100%)
- **Flow references:** 0/15
- **Trade references:** 0/15

### Signal Asset Distribution
- defense: 5 | crypto: 3 | tech: 4 | equities: 1 | commod: 1 | fixed_income: 1

---

## 6. EDITORIAL QUALITY

### Categorization
- ❌ **No stories have a `category` field** (geopolitics/markets/wealth/pleasure)
- Instead, stories use `sector` (tech, equities, commodities, crypto, defense, fx, fixed_income)
- The 4 expected editorial categories are **completely absent**

### INTEL/ALPHA Separation
- ❌ **No `INTEL` or `ALPHA` section identifiers found** on any story or flow
- Living stories use `sector: geopolitics` rather than section labels
- No formal INTEL/ALPHA content separation exists in the data

### Placeholder / Draft-Quality Content
- **211/245 stories** (86%) contain `correlation regime: tbd` in their `portfolio_implication` field
- All DEVELOPING-tier stories are **OSINT drafts** with thesis like "OSINT draft #359: ..."
- These are pipeline output awaiting editorial review — not live published content

### Localization
- **EN:** 245 stories (main), 11 living stories
- **RU:** 82 stories (translated subset) — headline example: "Иран наносит удар по Кувейту"
- Both EN and RU sites have independent generation timestamps

---

## 7. KEY ANOMALIES & ISSUES

| # | Issue | Severity | Details |
|---|---|---|---|
| 1 | **`total_signals` mismatch** | **HIGH** | Claimed 245 but only 15 in array |
| 2 | **No editorial categories** | **HIGH** | Categories (geopolitics/markets/wealth/pleasure) don't exist in data — only `sector` |
| 3 | **No INTEL/ALPHA separation** | **MEDIUM** | No stream labels define editorial sections |
| 4 | **211 stories are OSINT drafts** | **MEDIUM** | Most have "correlation regime: tbd" — these are pipeline intermediates, not final content |
| 5 | **No trades.json file** | **MEDIUM** | Trades are embedded in track_record.json but no separate trades endpoint |
| 6 | **No `amount` field on stories** | **LOW** | Capital flow amounts exist in nested `capital_flow.amount_b` |
| 7 | **No entry/stop/target on trades** | **LOW** | Trades are outcome-based, not price-level-based |
| 8 | **Null timestamps on stories** | **LOW** | Individual story timestamps not populated (only file-level `generated_at`) |
| 9 | **8/11 living stories >7 days old** | **LOW** | Some stories haven't been touched since June 3-4 |
| 10 | **ICI flows stale** | **LOW** | ICI data pipeline not configured (status: `stale`, note says "API key not configured") |

---

## 8. QUALITY SCORES

| Dataset | Score | Key Factors |
|---|---|---|
| **Main stories (EN, 245)** | **60/100** | Strong field coverage but all OSINT drafts (no final editorial polish), no categories |
| **Living stories (11)** | **20/100** | Minimal field coverage, no content fields (thesis/body), some stale |
| **Flows (199)** | **85/100** | Excellent structure and consistency; minor issues with 11 null amounts and no flow names |
| **Signals (15)** | **70/100** | Well-structured but count mismatch with claimed total and no flow/trade references |
| **Track Record** | **75/100** | Solid 33-trade record with 76% win rate; no entry/stop/target granularity |

### Overall Platform Quality

| Area | Score |
|---|---|
| Data Structure & Consistency | 75/100 |
| Content Completeness | 55/100 |
| Editorial Organization | 30/100 |
| Pipeline Health | 70/100 |

**Overall: 58/100**

---

## 9. RECOMMENDATIONS

1. **Fix `total_signals` mismatch** — signal.json claims 245 but only shows 15 entries
2. **Add editorial categories** — Implement the 4-category taxonomy (geopolitics/markets/wealth/pleasure)
3. **Add INTEL/ALPHA section labels** — Create clear editorial section differentiation
4. **Define story lifecycle** — Separate pipeline drafts from published editorial content (flag the 211 OSINT drafts)
5. **Populate story timestamps** — Add per-story `published`/`created_at` fields for freshness tracking
6. **Create standalone trades endpoint** — Export a dedicated trades.json for API consumers
7. **Add flow names** — Every flow should have a human-readable `name` field
8. **Add entry/stop/target to trades** — For proper risk management transparency
9. **Configure ICI pipeline** — Install the data pipeline for live ETF/mutual fund flows
10. **Add content body field** — Implement `body`/`body_html` for rich editorial content
