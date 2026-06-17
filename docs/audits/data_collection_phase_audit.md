# DATA COLLECTION PHASE AUDIT — La Gazzetta di Kyiv
**Analyst:** Hermes Agent (Pipeline Auditor)
**Date:** 2026-06-16
**Scope:** link_processor.py, CCO pipeline, Cloud Scheduler, story ingestion path, classification

---

## 1. LINK PROCESSOR ANALYSIS

### File: `scripts/link_processor.py`

#### 1A. Full-JSON Format Conflict (CRITICAL)

| Field | Pipeline Stories (28 keys) | link_processor (11 keys) | Impact |
|---|---|---|---|
| `source` | `"osint_reuters_business"` | **MISSING** | db_to_json.py extracts source_name from `source` field. Without it, source_name = `""` |
| `source_name` | MISSING (derived from `source`) | `"investing.com"` | Misaligned field name — no downstream code uses `source_name` from full_json |
| `source_url` | MISSING | `"https://..."` | Useful but not consumed by pipeline |
| `they_say` | `"Source: reuters_business..."` | **MISSING** | CCO Telegram formatting crashes (tries `story.get("they_say","")`) |
| `reality` | full text | **MISSING** | CCO uses `reality` for "Consensus vs Reality" block |
| `multi_persona` | `{"c_suite":..., "quant":..., "degen":...}` | **MISSING** | enrich_editorial_stories.py and multi_persona generators skip these stories |
| `capital_flow` | `{"direction":"inflow", "amount_b":2.1,...}` | **MISSING** | CCO Telegram uses capital_flow for "Capital flow impact" line |
| `confidence` | `"low"` | `"medium"` (hardcoded) | Wrong confidence; cco_curate.py impact_score computed as `cs * (cp/100)` → missing cp |
| `contradiction_score` | 75 (0-100) | 50 (hardcoded) | Always default, never refined |
| `evidence` | list of strings | **MISSING** | No evidence tracking |
| `entity_tags` | dict with assets/geographies/actors | **MISSING** | No entity extraction |
| `time_decay` | dict with half-life/curve | **MISSING** | Decay_stories.py can't decay these |
| `body` | **MISSING** (field name different) | extracted body up to 5000 chars | Not stored in full_json; only used locally |

**BUG:** `fetch_url()` extracts `body` (used for classification) but **does not store it** in the returned dict sent to full_json. The body is only used transiently for keyword matching.

#### 1B. `source_name` Emptiness Bug in db_to_json.py

`db_to_json.py` (lines 112-126) tries to extract `source_name` from stories:

```python
raw_source = story.get("source", "")
if raw_source and raw_source != "osint":
    cleaned = raw_source.replace("osint_", "").replace("_", " ").title()
    story["source_name"] = cleaned
else:
    story["source_name"] = ""
    # Fallback: extract " - SourceName" from headline suffix
```

Since link_processor stories have **no `source` field**, `raw_source = ""`, so `source_name = ""` for every link_processor story. The regex fallback may or may not match.

#### 1C. INSERT OR REPLACE Danger (MEDIUM)

`link_processor.py` line 179-184:
```sql
INSERT OR REPLACE INTO stories (id, headline, sector, pillar, tier, container, 
           generated_at, full_json, confidence, contradiction_score)
```

- Story ID = `sha256(url)[:16]` (16 hex chars, e.g. `"a1b2c3d4e5f67890"`)
- Pipeline IDs = `n21_osint__reuters_business__strateg...` (long slug format)

**Format completely different — no collision risk between link_processor and pipeline stories.**

**However:** Re-processing the same URL via link_processor silently overwrites the previous link_processor version. The `<full_json>` is replaced with a new raw fetch, losing any downstream enrichment (multi_persona, capital_flow, etc.) that a subsequent pipeline run may have added.

**FIX:** Change `INSERT OR REPLACE` to `INSERT OR IGNORE` — or add an existence check before writing.

#### 1D. `classify()` Function Quality (LOW)

```python
def classify(text):
    scores = {}
    for cname, keywords in CONTAINER_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text_lower)
        if score > 0:
            scores[cname] = score
    container = max(scores, key=scores.get) if scores else "flashpoints"
```

**Issues:**
- Pure keyword counting — no NLP, no context, no entity resolution
- Single-word matches on short substrings cause false positives (e.g. "ai" matches inside "bailout", "said", "mail", "captain")
- No sector/pillar signal — link_processor sets `sector = container` and `pillar = "multi_pillar"` (both wrong for downstream)
- Default fallback to `"flashpoints"` catches everything that doesn't match keywords
- Tag threshold is 2+ keyword matches with only 3-5 keywords per tag — biased toward no tags
- Container keywords are a **subset** of the `classify_stories.py` keywords (less comprehensive)

**Contrast with `classify_stories.py`:**
- Uses sector/pillar matching (score +5 for sector match, +3 for pillar match)
- Has more comprehensive keyword lists per container
- Has fallback logic by sector type (crypto→monetary_order, commodities→energy_resources)
- Same basic approach (keyword counting) but more thorough

**VERDICT:** `classify()` produces container assignments but they may be wrong for 20-30% of stories vs the more thorough `classify_stories.py`.

---

## 2. CCO PIPELINE STATUS (Cloud Scheduler)

```
$ gcloud scheduler jobs list --location=europe-west1

ID                             STATE        SCHEDULE
────────────────────────────────────────────────────────────
gazzetta-pipeline-cron         ENABLED     */10 * * * *  (every 10 min!)
cco-distributor-cron           PAUSED      */30 * * * *
cco-newsletter-weekly-cron     PAUSED      0 6 * * 1
cco-newsletter-daily-cron      PAUSED      0 6 * * *
cdo-auditor-cron               PAUSED      0 */2 * * *
gazzetta-rd-sweep-weekly-cron  PAUSED      15 6 * * 1
memory-synthesizer-cron        PAUSED      0 2 * * *
```

**Status: 6 of 7 jobs PAUSED.** Only `gazzetta-pipeline-cron` is ENABLED.

### Choke Points:

| Job | Status | Impact |
|---|---|---|
| **cco-distributor-cron** | **PAUSED** 🔴 | Telegram, Reddit, X.com distribution DEAD. No stories posted to any platform. |
| **cco-newsletter-daily-cron** | **PAUSED** 🔴 | Daily newsletter DEAD. No email distribution. |
| **cco-newsletter-weekly-cron** | **PAUSED** 🔴 | Weekly newsletter DEAD. No weekly digest. |
| **cdo-auditor-cron** | **PAUSED** 🟡 | CDO auditor DEAD. No contradiction score tuning. |
| **gazzetta-rd-sweep-weekly-cron** | **PAUSED** 🟡 | Weekly sweep DEAD. Research desk cleanup not running. |
| **memory-synthesizer-cron** | **PAUSED** 🟡 | Memory synthesis DEAD. Cross-session learning disabled. |
| **gazzetta-pipeline-cron** | **ENABLED** ✅ | Runs every 10 minutes (excessive — was 10x/hour, 240x/day) |

### gazzetta-pipeline-cron Details:
- **URI:** Cloud Run Job trigger (POST)
- **Schedule:** `*/10 * * * *` (every 10 minutes)
- **Frequency:** 144 runs/day
- **Last run:** 2026-06-16T20:20 UTC
- **SA:** `gazzetta-pipeline@project-e5e0244c...`
- **Retry:** Exponential backoff, max 1h, max 5 doublings

**The pipeline fires every 10 minutes** — the most aggressive schedule in the system. For a data pipeline that fetches intel, generates stories, compiles JSON, and deploys to GCS, this means ~144 full pipeline cycles/day. Even if sources haven't updated, it re-runs idempotent scripts and re-deploys identical data.

---

## 3. STORY INGESTION PATH MAPPING

### Primary Path (Pipeline):
```
URL → intel_to_stories.py → gazzetta.db → db_to_json.py → stories.json → GCS
                                ↓
                          enrich_editorial_stories.py   (adds capital_flow)
                          enrich_multi_persona.py        (adds persona blocks)
                          decay_stories.py               (time decay)
                          classify_stories.py             (container tagging)
                          validate_stories.py             (integrity check)
```

### Secondary Path (link_processor):
```
URL → link_processor.py → gazzetta.db
                                ↓
                          db_to_json.py → stories.json → GCS
                          (but story has only 11 fields — no source, they_say, etc.)
```

### Visibility:
```
gazzetta-pipeline-cron (Cloud Scheduler) → Cloud Run Job
   → [presumably runs gazzetta_pipeline_chain.sh or equivalent]
   → intel_to_stories → db_to_json → generate_flows → deploy to GCS
```

**The link_processor path is a dead end for CCO distribution.** Stories written by link_processor will appear on the site (db_to_json picks them up) but will:
- Show empty source_name (no `source` field)
- Have no "They Say" / "Reality" blocks
- Have no capital_flow data
- Have no multi_persona blocks
- Have a hardcoded contradiction_score of 50

---

## 4. CLASSIFICATION CONFLICT

| Aspect | link_processor.classify() | classify_stories.py | Conflict |
|---|---|---|---|
| Method | Keyword count only | Keyword + sector/pillar | Different classifiers, different results |
| Keyword depth | ~6-10 keywords/container | ~15-25 keywords/container | classify_stories.py is more thorough |
| Sector signal | **None** (always "multi_pillar") | +5 score for sector match | **Massive divergence** — link_processor ignores sector |
| Pillar signal | **None** | +3 score for pillar match | Same divergence |
| Fallback | `flashpoints` | Sector heuristic + flashpoints | Different fallback behavior |
| Tag threshold | 2+ keyword matches, ~5 keywords/tag | 2+ keyword matches, ~10-20 keywords/tag | classify_stories.py assigns more tags |

**The two classifiers are separately maintained and produce different results for the same input.** They share similar keyword lists but with different keyword sets, different scoring, and link_processor entirely missing sector/pillar awareness.

---

## 5. STORY_TAGS SPARSITY

Current tag distribution across 377 stories:

| Tag | Stories |
|---|---|
| american-decline | 44 |
| eu-strategy | 3 |
| china-ascendancy | 1 |
| russia | 1 |
| **No tags** | **328 (87%)** |

**87% of stories have zero tags.** This means:
- `tags_index` in stories.json is nearly empty
- Site's tag-filtering UX is non-functional
- `classify_stories.py` should assign tags but either wasn't run or tag threshold is too high

Container distribution is healthier (all 377 assigned), but tags need work.

---

## BUG SUMMARY & FIXES NEEDED

### 🔴 CRITICAL (blocks core functionality)

| # | Bug | File | Fix |
|---|---|---|---|
| C1 | `full_json` missing `source` field | link_processor.py:165-177 | Add `"source": content["source_name"]` to full_json dict, or better: add `"source": f"web_{domain}"` |
| C2 | `full_json` missing `they_say`, `reality` | link_processor.py:165-177 | Add these fields with extracted title/body content |
| C3 | `full_json` missing `multi_persona` | link_processor.py:165-177 | Add stub: `"multi_persona": {"c_suite":{}, "quant":{}, "degen":{}}` |
| C4 | `full_json` missing `capital_flow` | link_processor.py:165-177 | Add stub: `"capital_flow": {"direction":"neutral", "amount_b":0, "asset_class":"equities", "confidence_pct":50}` |
| C5 | CCO distribution cron jobs all PAUSED | Cloud Scheduler | Enable `cco-distributor-cron` (and newsletter crons) |
| C6 | `body` extracted but not stored in full_json | link_processor.py:119-129 | Add `"body": body` to the returned dict |

### 🟡 HIGH (causes data quality issues)

| # | Bug | File | Fix |
|---|---|---|---|
| H1 | `INSERT OR REPLACE` overwrites enriched data | link_processor.py:179 | Change to `INSERT OR IGNORE`, or check existence first with UPDATE-or-INSERT |
| H2 | Container classification uses different rules from classify_stories.py | link_processor.py:133-154 | Align keyword lists and add sector/pillar awareness, or remove classify() and use classify_stories.py's logic |
| H3 | No sector/pillar awareness in classify() | link_processor.py:133-154 | Add sector/pillar matching (copy from classify_stories.py) |
| H4 | 87% of stories have no tags | classify_stories.py (or didn't run) | Re-run classify_stories.py with lower tag threshold (1 match instead of 2?) |
| H5 | Pipeline runs every 10 minutes (144x/day) | Cloud Scheduler | Reduce to `*/30 * * * *` or `0 * * * *` (see prior audit) |

### 🟢 MEDIUM (housekeeping)

| # | Bug | File | Fix |
|---|---|---|---|
| M1 | `classify()` tags use threshold ≥2 with only 3-5 keywords per tag | link_processor.py:148-153 | Lower threshold to ≥1 or expand keyword lists |
| M2 | Story source_name is empty for link_processor stories in generated JSON | db_to_json.py:112-126 | Add fallback: check `source_url` from full_json and extract domain |
| M3 | Hardcoded `contradiction_score: 50` never refined | link_processor.py:173 | Add basic contradiction detection or leave as None |
| M4 | Hardcoded `confidence: "medium"` | link_processor.py:184 | Derive from source reliability or leave as "low" for unvetted URLs |
| M5 | gazzetta-pipeline-cron re-deploys identical data 144x/day | Cloud Scheduler | Reduce to 24x/day (every 60m) or add change detection |

---

## RECOMMENDATION: Integration Plan

1. **Fix link_processor.py full_json** to include `source`, `they_say`, `reality`, `multi_persona` (stub), `capital_flow` (stub), `evidence`, and `body`.

2. **Enrich link_processor stories post-insert** by having the enrich pipeline (enrich_editorial_stories.py, enrich_multi_persona.py) process all stories with missing fields, not just editorial ones.

3. **Unpause CCO distribution cron jobs** — cco-distributor-cron is the critical one for Telegram/Reddit/X distribution.

4. **Reduce pipeline frequency** from every 10 min to every 30 or 60 min.

5. **Re-run classify_stories.py** with lower tag threshold (≥1 keyword instead of ≥2) to tag more stories.

6. **Add a `source_url` column to db_to_json.py's source_name fallback** so link_processor stories get a readable source name from their URL.
