# Gazzetta Data Pipeline Audit Report
**Date:** 2026-06-11  
**Audit scope:** stories.json, flows.json, confidence/pace/amount distributions, data sync, generate_flows.py

---

## 1. STORIES.JSON (root: `data/stories.json`)

| Metric | Value |
|---|---|
| **generated_at** | 2026-06-11T07:21:27 |
| **Total stories** | 59 (1 lead + 58 in array) |
| **Stories with capital_flow dict** | 59/59 (100%) |
| **Stories with capital_flow_implication** | 56/59 |
| **Stories with portfolio_implication** | 59/59 |
| **Stories with contradiction_score > 0** | 58/59 |
| **Stories with `source` field** | 58/59 |

### Confidence_pct Distribution (stories, nested in capital_flow dicts)

| Value | Count | Note |
|---|---|---|
| **50** | 25 | The `[LIVE-DATA]` tier — baseline low |
| **65** | 1 | Single story: `iran_strikes_kuwait` |
| **75** | 33 | The `[CALC-EST]` tier — baseline medium |
| **Range** | 50–75 | **⚠️ Only 3 unique values** — extremely tight clustering |
| **Mean** | 64.2 | |

**Finding:** Stories confidence only has 3 values (50, 65, 75). No high-confidence (80+) stories exist at the story level. These are set by `source_label`: `[LIVE-DATA]` → 50, `[CALC-EST]` → 75. The single 65 is an anomalous case. **This is a flat confidence problem at the story source level** — confidence is pre-assigned by pipeline tier, not computed dynamically.

### Amount_b Distribution (stories, capital_flow)

| Stat | Value |
|---|---|
| **Count** | 59 stories |
| **Range** | 0.0 – 300.0 |
| **Mean** | 17.36 |
| **Unique values** | 47 out of 59 — good diversity |
| **amount_b == 5.0** | **6 stories** (10%) — possible default/hardcoded |

**Finding:** 6 stories stuck at exactly 5.0 with no evidence of parsing from text. These are the flat-5.0 suspects. Most other stories have varied amounts.

### Pace_multiplier Distribution (stories, capital_flow)

| Stat | Value |
|---|---|
| **Range** | 1.0 – 2.4 |
| **Mean** | 1.58 |
| **pace == 1.0** | **21 stories (36%)** — significant flat default |
| **pace > 1.0** | 38 stories (64%) |

**Finding:** 21 out of 59 stories have pace_multiplier exactly 1.0 — this is the default returned by `extract_pace()` when no `x`-pattern is found. All 21 are `osint_the_cradle` and `osint_reuters_business` stories where pace wasn't explicitly set. **This is a flat pace problem** for OSINT-sourced stories.

### Direction (capital_flow)

| Direction | Count |
|---|---|
| inflow | 35 |
| neutral | 17 |
| outflow | 7 |

### Asset Class (capital_flow)

| Asset Class | Count |
|---|---|
| commodities | 25 |
| crypto | 12 |
| equities | 10 |
| defense | 8 |
| tech | 4 |

### Positioning Field

**No `positioning` key exists in any capital_flow dict.** The field is absent from all 59 stories. In `generate_flows.py`, the code falls through to `derive_positioning(direction, amount_b)` which returns `"accumulating"` / `"distributing"` / `"hedging"`.

---

## 2. FLOWS.JSON (root + site, identical)

| Metric | Value |
|---|---|
| **generated_at** | 2026-06-11T07:21:27 / 11:28 EET (after regenerate) |
| **generated_by** | generate_flows.py |
| **Total flows tracked** | 12 |
| **Summary** | 11 inflows · 1 outflow |
| **Aggregate confidence** | 86% (bullish) |

### Confidence_pct Distribution (flows)

| Value | Count |
|---|---|
| 77 | 1 |
| 82 | 3 |
| 85 | 2 |
| 86 | 1 |
| 90 | 3 |
| 92 | 1 |
| 97 | 1 |
| **Range** | 77–97 |
| **Mean** | 86.4 |

**Finding:** Much better spread than stories (8 unique values vs 3). The `compute_confidence()` function recalculates confidence from amount_b, pace_mult, positioning, contradiction, and source — producing wider distribution.

### Amount_b Distribution (flows)

| Amount | Count |
|---|---|
| 9.7 | 1 |
| 10.1 | 1 |
| 10.3 | 1 |
| 11.5 | 1 |
| 12.0 | 1 |
| 12.5 | 1 |
| 14.6 | 1 |
| 31.5 | 1 |
| 34.0 | 1 |
| 88.0 | 1 |
| 250.0 | 1 |
| 300.0 | 1 |
| **Range** | 9.7 – 300.0 |
| **Mean** | 66.0 |
| **amount_b == 5.0** | **0** ✅ |

**Finding:** **No flat 5.0 problem in flows.** The 6 stories with 5.0 were filtered out because they didn't rank in top 12 by amount, or the diversity gate excluded them.

### Pace_multiplier Distribution (flows)

| Value | Count |
|---|---|
| 1.0 | 3 |
| 1.9 | 1 |
| 2.0 | 2 |
| 2.1 | 1 |
| 2.2 | 2 |
| 2.3 | 2 |
| **Range** | 1.0 – 2.3 |
| **Mean** | 1.82 |
| **pace == 1.0** | 3 flows |

**Finding:** Better than stories (3 out of 12 vs 21 out of 59) but still 3 flows with default 1.0 pace.

### Asset Class Distribution (flows)

| Asset Class | Count |
|---|---|
| commodities | 3 |
| crypto | 4 |
| defense | 3 |
| tech | 2 |

### Direction Ratios (flows)

| Direction | Count |
|---|---|
| inflow | 11 |
| outflow | 1 |

### Positioning Diversity (flows)

| Positioning | Count |
|---|---|
| accumulating | 11 |
| distributing | 1 |

---

## 3. FLAT CONFIDENCE / PACE / AMOUNT ANALYSIS

### Flat 1.0 Pace Problem
- **Status: ⚠️ PRESENT**
- 21/59 stories (36%) have pace_multiplier = 1.0 (all OSINT-sourced)
- In flows: 3/12 flows still show pace = 1.0
- Root cause: `extract_pace()` defaults to 1.0 when no `Nx` pattern found in text. OSINT stories lack explicit pacing descriptions.

### Flat 5.0 Amount Problem
- **Status: ⚠️ PRESENT in stories, NOT in flows**
- 6/59 stories have amount_b = 5.0 exactly
- 0/12 flows have amount_b = 5.0 (filtered by top-12 + diversity gate)
- Root cause: Hardcoded default in story ingestion, survived by insufficient text parsing

### Flat Confidence Problem
- **Status: ⚠️ PRESENT in stories, MITIGATED in flows**
- Stories: Only 3 confidence values (50, 65, 75) — set by pipeline tier tag
- Flows: 8 distinct values (77–97) — recalculated by `compute_confidence()` with 5 factors
- The `compute_confidence()` function in `generate_flows.py` works correctly but the source data feeding it has limited granularity

---

## 4. DATA SYNC: `data/` vs `site/data/`

| Check | Result |
|---|---|
| **stories.json** — MD5 match | ✅ **IDENTICAL** |
| **flows.json** — MD5 match | ✅ **IDENTICAL** |
| **Story count** | 59 both sides |
| **Story IDs** | Identical sets |
| **Lead story** | Same on both sides |
| **generated_at** | Same timestamps |
| **generated_by** | Both report `db_to_json.py` |

**Finding: Root and site are perfectly in sync** for both stories.json and flows.json. No drift detected.

Note: `generate_flows.py` writes to both `site/data/flows.json` and `data/flows.json` (line 631-633), maintaining dual sync.

---

## 5. GENERATE_FLOWS.PY — `compute_confidence()` ANALYSIS

**Function:** `compute_confidence(amount_b, pace_mult, positioning, contradiction_bonus=5, source="")`

### 5-Factor Model (v22.29)

| Factor | Weight | Details |
|---|---|---|
| Base | 25 | Always applied |
| Amount | 0–25 | Log-scale: 2 (trace) → 25 (whale ≥20B) |
| Pace | 2–20 | Linear: 2 (flat) → 20 (extreme ≥3.0x) |
| Positioning | 5–15 | accumulating=15, distributing=10, hedging=5 |
| Contradiction | 0–15 | Proportional to contradiction_score/5, capped at 15 |
| Source | 0–10 | tier1=10, tier2=7, tier3=3, generic=5 |
| **Total** | **25–100** | Clamped at both ends |

### Simulated Output on All 59 Stories

| Confidence | Count |
|---|---|
| 54 | 8 |
| 63 | 1 |
| 64 | 1 |
| 67 | 5 |
| 71 | 2 |
| 72 | 5 |
| 75 | 4 |
| 76 | 16 |
| 77 | 2 |
| 80 | 3 |
| 81 | 1 |
| 82 | 2 |
| 85 | 3 |
| 86 | 1 |
| 90 | 3 |
| 92 | 1 |
| 97 | 1 |
| **Range** | 54–97 |
| **Mean** | 73.7 |

Simulated flow output (top-12 after diversity gate):

| Confidence | Count |
|---|---|
| 67 | 1 |
| 72 | 1 |
| 77 | 1 |
| 82 | 2 |
| 85 | 2 |
| 86 | 1 |
| 90 | 3 |
| 92 | 1 |
| 97 | 1 |
| **Range** | 67–97 |
| **Mean** | 84.8 |

### Key Observations

1. **The function works correctly** — produces 17 unique confidence values from 59 inputs
2. **Biggest discriminator is amount_b** (+25 max, vs +2 for trace flows)
3. **Pace contributes little** — max pace in data is 2.4x, which gets +12 (high-pace) but never reaches extreme (+20) or very-high (+16)
4. **Source factor is limited** — most stories have `telegram_intel` (+3) or generic/empty (+5)
5. **Contradiction bonus is consistent** — most stories have contradiction_score ≥ 60, giving contr_bonus of 12-15, so most get +10 or +15

---

## SUMMARY OF ISSUES

| Issue | Severity | Scope | Root Cause |
|---|---|---|---|
| Flat 1.0 pace in stories | **MEDIUM** | 21/59 stories | `extract_pace()` default; OSINT stories lack pacing text |
| Flat 5.0 amount | **LOW** | 6/59 stories | Hardcoded default in ingestion pipeline |
| Flat confidence in stories | **MEDIUM** | 59/59 stories (3 values only) | Confidence set by `source_label` tag, not computed |
| No positioning field in stories | **LOW** | 59/59 | Field not generated by story pipeline; derived by generate_flows.py |
| Data sync root↔site | **NONE** | ✅ | Perfect match |
| Flows confidence diversity | **GOOD** | 86.4 mean, range 77–97 | `compute_confidence()` spreads well |
| Flows amount diversity | **GOOD** | No flat 5.0; 12 unique amounts | Amount gate filters well |
