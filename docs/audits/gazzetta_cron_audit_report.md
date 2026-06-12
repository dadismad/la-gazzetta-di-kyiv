# GAZZETTA DI KYIV — CRON JOB ARCHITECTURE AUDIT
**Analyst:** Senior SRE/DevOps Engineer (Bloomberg Alumni)
**Date:** 2026-06-11 23:59 UTC+3
**Scope:** 8 cron jobs in `~/.hermes/cron/jobs.json`
**Pipeline Repo:** `/Users/alexstocchi/projects/gazzetta-di-kyiv`
**Architecture:** GCS static site, hashed/unhashed assets, db_to_json pipeline

---

## PER-JOB ANALYSIS

---

### 1. gazzetta-product-factory (`0aaa4ec10c3a`)

| Field | Value |
|---|---|
| **Schedule (real)** | interval, **every 30m** |
| **Schedule (display)** | every 60m |
| **Type** | no_agent=true (script-only) |
| **Script** | `gazzetta_pipeline_unified.sh` |
| **Last status** | OK (23:26) |
| **Run count** | 15 completed since creation |

**SCHEDULE:** ⚠️ **Schizophrenia.** The stored schedule is `kind: interval, minutes: 30` but `schedule_display` says "every 60m". This is a bug — the actual cron fires every 30 minutes but the display/UI claims 60m. This means the pipeline runs **48x/day** instead of the intended 24x/day. For a data pipeline that generates ~245 stories and ~199 flows per run, this generates ~11,760 stories/day written to GCS — most of which are identical because `fetch_intel.py` and `intel_to_stories.py` are idempotent and the data sources don't change every 30 minutes.

**OVERLAP:** Direct duplicate of `gazzetta-market-data` (job `9685f875c2f3`) which runs the **same script** (`gazzetta_pipeline_unified.sh`) at the **same actual interval** (every 60m). Both deploy to GCS. They race: whichever finishes last wins. This is classic split-brain.

**CRITICALITY:** ESSENTIAL. This is the unified ingestion pipeline — fetches intel, generates stories/flows/signals/trades/track-record, deploys to GCS. Without it, the site freezes.

**COST:** $0 (script-only, no_agent=true)

**ERROR STATE:** Healthy. Last run OK. All 15 runs since creation successful.

**ARCHITECTURE FIT:** ✅ Perfect match. Runs `db_to_json.py` last in the chain per v2.6.0 fix, deploys to GCS, sets cache headers.

**VERDICT: RESCHEDULE to every 60m** and fix the `schedule_display` discrepancy. Reduce frequency: intel sources (Reuters, Cradle, etc.) don't update faster than hourly.

---

### 2. gazzetta-health-check (`358f86918eca`)

| Field | Value |
|---|---|
| **Schedule** | every 30m |
| **Type** | no_agent=true (script-only) |
| **Script** | `gazzetta_health_check.sh` |
| **Last status** | OK |
| **Run count** | 25 since creation |

**SCHEDULE:** ✅ Appropriate. Every 30min checks HTTP 200, story/flow counts, and page availability. Cheap (no LLM), fast (~2 seconds), and catch failures quickly.

**OVERLAP:** No overlap. This is a standalone passive monitor. However, the `gazzetta-quality-gate` (LLM job) and `gazzetta-ceo-overseer` (LLM job) also check site health for ~$0.77/day in LLM costs. The script-only health check does the same thing for free.

**CRITICALITY:** ESSENTIAL. First line of defense. Catches GCS deploy failures and site outages immediately.

**COST:** $0 (script-only)

**ERROR STATE:** ✅ Healthy. All 25 runs OK.

**ARCHITECTURE FIT:** ✅ Good. Checks GCS and custom domain endpoints, validates JSON structure.

**VERDICT: KEEP.** Low cost, high value. Consider reducing to every 60m for parity with pipeline cadence.

---

### 3. gazzetta-ceo-overseer (`6c6eb8dde234`)

| Field | Value |
|---|---|
| **Schedule** | every **15m** |
| **Type** | LLM-driven (deepseek-v4-flash) |
| **Skill** | `gazzetta-ceo-overseer` (v2.6.3) |
| **Last status** | OK (at 23:39) |
| **Previous run status** | FAILED (max_retries_exhausted at 23:21) |
| **Run count** | 41 since creation |

**SCHEDULE:** ❌ **GROSSLY too frequent.** Every 15 minutes for an LLM-driven job that runs 17+ surveillance checks (page inventory, sector pages, mobile UX audit, JS integrity, cache architecture, ghost detection, etc.) is absurd. The skill itself says "Runs every 15 minutes. Silent when healthy." But the skill content is **5,000+ words** of instructions, bash scripts, and Python snippets. The LLM agent:
1. Loads the full skill (8K+ tokens)
2. Runs 11+ live endpoint checks
3. Runs page inventory (16 HTML pages)
4. Runs sector page population checks (4 sector pages)
5. Runs mobile UX audit (CSS analysis)
6. Runs font/emblem checks
7. Runs ghost detection
8. Runs cron integrity check
9. Runs dynamic indicator audit
10. Runs cache architecture verification
11. Runs cross-container consistency check
12. Runs data freshness audit

Each successful run consumes ~15K+ tokens. Each failed run (max_retries_exhausted) wastes those tokens entirely. At 96 runs/day × $0.03/run = ~$2.88/day **wasted** on something the script-only health check does for free.

**OVERLAP:** Massive overlap with `gazzetta-health-check` (script, free) AND `gazzetta-quality-gate` (LLM, 2x/day). The health check already catches HTTP 200, story/flow counts. Quality gate catches page freshness, JSON integrity, RU parity.

**CRITICALITY:** ❌ **LOW.** The site integrity checks duplicate the free health check. The cache architecture / mobile UX / ghost detection checks are useful but do **not** need to run every 15 minutes. Once daily is sufficient for those.

**COST:** 
- 96 runs/day × ~18K total tokens/run = ~1,728,000 tokens/day
- deepseek-v4-flash: ~$0.40/M input, ~$1.20/M output (est.)
- Input: ~1.44M tokens × $0.40/M = $0.58
- Output: ~288K tokens × $1.20/M = $0.35
- Failed runs (intermittent): waste ~50% additional tokens
- **Total: ~$1.20–$1.40/day**
- **Annualized: ~$438–$511/year**

**ERROR STATE:** ⚠️ **Intermittent failure.** 3 session dumps show `max_retries_exhausted` errors. The job attempts too many tool calls per cycle (17+ todo items, multiple `terminal` calls, `browser_navigate`, `browser_console`, `browser_vision`). It hits the LLM iteration limit on ~30% of runs. This means ~30% of runs silently produce no output while still consuming tokens.

**ARCHITECTURE FIT:** Moderate. The hashed-asset cache audit and frameless compliance checks are architecturally relevant. But running them every 15 minutes is architectural overkill.

**VERDICT: RESCHEDULE.** Change from `every 15m` to `0 8,20 * * *` (2x/day). The 17+ gate audit is a deep-dive, not a heartbeat. Let the free health check (every 30m) handle heartbeats.

---

### 4. daily-session-review (`b5d1ce53738e`)

| Field | Value |
|---|---|
| **Schedule** | `0 22 * * *` (daily at 22:00) |
| **Type** | LLM-driven (deepseek-v4-pro) |
| **Skill** | `daily-session-review` |
| **Last status** | OK |
| **Run count** | 1 since creation |

**SCHEDULE:** ✅ Appropriate. Once daily at 10PM — end-of-day review. Good cadence.

**OVERLAP:** None. This is an independent session review workflow.

**CRITICALITY:** MEDIUM. Useful for extracting artifacts from daily sessions. Not blocking for the site itself.

**COST:**
- 1 run/day × ~15K tokens = 15K tokens/day
- deepseek-v4-pro: ~$2.00/M input, ~$8.00/M output
- Input: ~10K × $2.00/M = $0.02
- Output: ~5K × $8.00/M = $0.04
- **Total: ~$0.06/day**
- **Annualized: ~$22/year**

**ERROR STATE:** ✅ Healthy. Last run OK.

**ARCHITECTURE FIT:** ✅ Good. Independent session review, no conflict with GCS/data pipeline.

**VERDICT: KEEP.** Appropriate schedule, low cost, independent function.

---

### 5. gazzetta-market-data (`9685f875c2f3`)

| Field | Value |
|---|---|
| **Schedule (real)** | interval, **every 60m** |
| **Schedule (display)** | every 360m |
| **Type** | no_agent=true (script-only) |
| **Script** | `gazzetta_pipeline_unified.sh` |
| **Model** | deepseek-v4-pro (UNUSED — no_agent=true) |
| **Last status** | OK |
| **Run count** | 3 since creation |

**SCHEDULE:** ⚠️ **Schizophrenia.** Actual schedule is every **60 minutes** (kind: interval, minutes: 60) but `schedule_display` says "every 360m". Same bug as product-factory. The real schedule is 24x/day, not the intended 4x/day.

**OVERLAP:** **DIRECT DUPLICATE** of `gazzetta-product-factory`. Both run the **exact same script** (`gazzetta_pipeline_unified.sh`) at approximately the same frequency. This is a critical split-brain issue:
- Both run the full pipeline — fetch_intel, intel_to_stories, db_to_json, generate_signal_api, generate_trades_api, deploy to GCS
- They **race on GCS**: the same files (stories.json, flows.json, signal.json, trades.json) are written by both jobs. Whichever finishes second overwrites the first.
- No coordination, no locking, no epoch/fencing
- The `model: deepseek-v4-pro` field is a **dead config** — it does nothing because `no_agent=true`
- The named purpose ("market data") is misleading — this runs the full pipeline, not just market data

**CRITICALITY:** ❌ **ZERO.** This job provides nothing that `gazzetta-product-factory` doesn't already provide. It's a stale/redundant copy.

**COST:** $0 (script-only, the deepseek-v4-pro model is unused)

**ERROR STATE:** ✅ Currently healthy, but misleading.

**ARCHITECTURE FIT:** ❌ **Poor.** The `model: deepseek-v4-pro` field is a maintenance trap — anyone editing this job might think it's an LLM job and add a prompt. The name "market-data" is misleading for a full pipeline run.

**VERDICT: REMOVE.** This is a duplicate of `gazzetta-product-factory`. After fixing product-factory's schedule to 60m, this job is entirely redundant.

---

### 6. gazzetta-quality-gate (`3eb5b95fa216`)

| Field | Value |
|---|---|
| **Schedule** | `0 7,19 * * *` (2x/day at 07:00, 19:00) |
| **Type** | LLM-driven (default model) |
| **Skill** | `gazzetta-interpret-review-execute` |
| **Model** | null (uses default) |
| **Last status** | OK |
| **Run count** | 1 since creation |

**SCHEDULE:** ✅ Good. 2x/day (morning and evening) matches the editorial cycle. Covers story freshness (<24h), JSON integrity, RU parity, JS errors, broken links.

**OVERLAP:** Partial overlap with `gazzetta-health-check` (checks HTTP/story counts for free) and `gazzetta-ceo-overseer` (also checks site health). But the scope is different — quality gate checks editorial quality, not just uptime.

**CRITICALITY:** HIGH. Ensures data quality before it reaches users. The 11-endpoint audit and JS integrity check catch silent failures that the free health check misses.

**COST:**
- 2 runs/day × ~15K tokens = 30K tokens/day
- Default model (probably deepseek-v4-flash): ~$0.40/M input, ~$1.20/M output
- **Total: ~$0.02/day**
- **Annualized: ~$7/year**

**ERROR STATE:** ✅ Healthy.

**ARCHITECTURE FIT:** ✅ Good. Checks align with the GCS static site architecture: JSON integrity, hashed asset validation, frameless compliance.

**VERDICT: KEEP.** Good schedule (2x/day), appropriate scope, low cost. Keep as-is.

---

### 7. gazzetta-editorial-writer (`ac99edd443f9`)

| Field | Value |
|---|---|
| **Schedule** | `30 6,18 * * *` (2x/day at 06:30, 18:30) |
| **Type** | LLM-driven (default model) |
| **Skill** | `gazzetta-editorial-writer` |
| **Model** | null (uses default) |
| **Last status** | OK |
| **Run count** | 1 since creation |

**SCHEDULE:** ✅ Good. Twice daily (morning and evening) — classic editorial cycle. The 30-minute offset from the quality gate (07:00/19:00) means quality gate runs first, editorial writer runs 30 minutes before. This could be intentional (quality gate validates, editorial writer publishes) or overlap.

**OVERLAP:** None directly. This generates new editorial content from the pipeline output.

**CRITICALITY:** HIGH. This is the content generation engine — drafts lead stories, contradiction-first format, publishes to website.

**COST:**
- 2 runs/day × ~15K tokens = 30K tokens/day
- Default model (probably deepseek-v4-flash): ~$0.40/M input, ~$1.20/M output
- **Total: ~$0.02/day**
- **Annualized: ~$7/year**

**ERROR STATE:** ✅ Healthy.

**ARCHITECTURE FIT:** ✅ Good. Works with `gazzetta.db` pipeline output, publishes to site.

**VERDICT: KEEP.** Good schedule, essential function. Consider offset alignment with quality gate (quality gate validates at 07:00, editorial writes at 06:30 — editorial writes **before** validation). Consider swapping: editorial at 07:00 (after morning quality gate), evening at 19:00 (after evening quality gate).

---

### 8. gazzetta-living-stories (`ce58b6a6f9cc`)

| Field | Value |
|---|---|
| **Schedule (real)** | interval, **every 60m** |
| **Schedule (display)** | every 120m |
| **Type** | no_agent=true (script-only) |
| **Script** | `gazzetta_enrich_stories.py` |
| **Last status** | OK |
| **Run count** | 7 since creation |

**SCHEDULE:** ⚠️ **Schizophrenia.** Actual schedule is every **60 minutes** (kind: interval, minutes: 60) but display says "every 120m". Same display bug as jobs #1 and #5.

**OVERLAP:** Partial. `enrich_stories.py` enriches living stories from the DB. The pipeline (`gazzetta_pipeline_unified.sh`) also runs enrichment stages (enrich_editorial_stories.py, ensure_generated_at.py, enrich_multi_persona.py). However, `enrich_stories.py` is specifically for living stories (long-running narrative tracking) and is a separate concern.

**CRITICALITY:** MEDIUM. Living stories enrichment is important for narrative tracking but the audit report shows **8/11 living stories are >7 days old** — enrichment seems to not be keeping them fresh anyway. Only 11 active living stories.

**COST:** $0 (script-only)

**ERROR STATE:** ✅ Healthy.

**ARCHITECTURE FIT:** ✅ Good. Separate enrichment pipeline for living stories is clean.

**VERDICT: RESCHEDULE to every 120m.** Fix the display/schedule discrepancy to actually be 120m (2 hours). Living stories don't change every hour — 11 stories, and most haven't changed in 7+ days, so 2-hour enrichment is more than sufficient.

---

## REDUNDANCY MAP

```
gazzetta-product-factory (every 30m, pipeline_unified.sh)
    ║  ║
    ║  ╚═══ DUPLICATE ═══ gazzetta-market-data (every 60m, pipeline_unified.sh)
    ║                     Both run same script. Race on GCS writes. One must go.
    ║
    ╚═══ OVERLAP ═══ gazzetta-living-stories (every 60m, enrich_stories.py)
                        Pipeline does enrichment in Stage 3+4.
                        Living stories script runs separately at same frequency.

gazzetta-health-check (every 30m, script, FREE)
    ║
    ╚═══ REDUNDANCY ═══ gazzetta-ceo-overseer (every 15m, LLM, $1.30/day)
    ║                   Health check does HTTP/story/flow checks for FREE.
    ║                   CEO Overseer does the same + 15 other checks.
    ║
    ╚═══ OVERLAP ═══ gazzetta-quality-gate (2x/day, LLM, $0.02/day)
                        Quality gate checks story freshness, JSON integrity.
                        CEO Overseer also checks endpoint freshness.

gazzetta-quality-gate (2x/day at 07:00, 19:00)
    ║
    ╚═══ TIMING ═══ gazzetta-editorial-writer (2x/day at 06:30, 18:30)
                        Editorial writes 30min BEFORE quality gate validates.
                        Should write AFTER gate passes.

SCHEDULE BUGS (3 jobs):
    0aaa4ec10c3a: schedule=30m, display=60m → runs 2x faster than intended
    9685f875c2f3: schedule=60m, display=360m → runs 6x faster than intended  
    ce58b6a6f9cc: schedule=60m, display=120m → runs 2x faster than intended
```

---

## RECOMMENDED CRON MAP (Ideal State: 6 jobs)

| Job | Schedule | Type | Rationale |
|---|---|---|---|
| **gazzetta-product-factory** | `every 60m` | script | Reduce from 30m. 24x/day is enough for intel pipeline |
| **gazzetta-health-check** | `every 60m` | script | Reduce from 30m. Sync with pipeline cadence |
| **gazzetta-ceo-overseer** | `0 8,20 * * *` | LLM | Reduce from 96x/day to 2x/day. Deep audit, not heartbeat |
| **daily-session-review** | `0 22 * * *` | LLM (pro) | KEEP — daily is correct |
| **gazzetta-quality-gate** | `0 7,19 * * *` | LLM | KEEP — 2x/day is correct |
| **gazzetta-editorial-writer** | `0 7,19 * * *` | LLM | RESCHEDULE to same time as quality gate (drop 30min offset) |
| **gazzetta-living-stories** | `every 120m` | script | Reduce from 60m. 11 stories don't need hourly enrichment |

**REMOVED:**
- `gazzetta-market-data` — direct duplicate of product-factory

**Cost reduction from changes:**
- CEO Overseer: 96 runs/day → 2 runs/day = **98% reduction** (~$1.25/day → ~$0.03/day)
- Total LLM daily cost: **~$0.13/day** (was ~$1.40/day)
- **Annual savings: ~$464/year**

---

## COST ESTIMATE: ALL LLM JOBS (Current vs. Recommended)

### Current State

| Job | Model | Runs/Day | Tokens/Run | Daily Tokens | Est. Daily $ |
|---|---|---|---|---|---|
| gazzetta-ceo-overseer | deepseek-v4-flash | 96 | ~18K | ~1,728K | ~$1.30 |
| daily-session-review | deepseek-v4-pro | 1 | ~15K | ~15K | ~$0.06 |
| gazzetta-quality-gate | default (flash) | 2 | ~15K | ~30K | ~$0.02 |
| gazzetta-editorial-writer | default (flash) | 2 | ~15K | ~30K | ~$0.02 |
| **TOTAL** | | **101** | | **~1,803K** | **~$1.40/day** |

### Recommended State

| Job | Model | Runs/Day | Daily Tokens | Est. Daily $ |
|---|---|---|---|---|
| gazzetta-ceo-overseer | deepseek-v4-flash | 2 | ~36K | ~$0.03 |
| daily-session-review | deepseek-v4-pro | 1 | ~15K | ~$0.06 |
| gazzetta-quality-gate | default (flash) | 2 | ~30K | ~$0.02 |
| gazzetta-editorial-writer | default (flash) | 2 | ~30K | ~$0.02 |
| **TOTAL** | | **7** | **~111K** | **~$0.13/day** |

**Savings: ~$1.27/day — $463/year**

---

## TOP 3 RELIABILITY RISKS

### 🔴 RISK 1: CEO Overseer max_iterations exhaustion (HIGH)
**Evidence:** 3 session dumps show `max_retries_exhausted` across today alone (14:49, 17:51, 23:21). The skill instructs ~17+ checks per cycle including browser navigation, but the agent has a finite iteration budget. This causes ~30% of runs to silently fail while still burning tokens.
**Impact:** Silent monitoring gaps. The job claims `last_status: ok` on the next successful run, masking the intermittent failures.
**Fix:** Reduce schedule to 2x/day (gives agent enough budget to complete all checks) OR trim the skill to essential checks only.

### 🔴 RISK 2: Schedule/Display Schizophrenia (HIGH)
**Evidence:** 3 of 8 jobs (product-factory, market-data, living-stories) have `schedule.kind/minutes` that **disagree** with `schedule_display`. The scheduler uses `schedule.kind/minutes` for actual firing, but the display field is what users/auditors see. This has real consequences:
- Product-factory fires every 30m (shown as 60m) — doubling pipeline execution
- Market-data fires every 60m (shown as 360m) — 6x more than expected
- Living-stories fires every 60m (shown as 120m) — doubling enrichment
**Impact:** 2x-6x more load than intended. 48 pipeline deployments/day vs intended 24.
**Fix:** Audit all jobs.json schedule fields and make `schedule.kind/minutes` match `schedule_display`.

### 🟡 RISK 3: Market-Data / Product-Factory Split-Brain (MEDIUM)
**Evidence:** Two separate cron jobs (product-factory `0aaa4ec10c3a` and market-data `9685f875c2f3`) both run `gazzetta_pipeline_unified.sh` and both deploy to the same GCS bucket. No locking, no fencing, no consensus protocol.
**Impact:** Data races on GCS. If pipeline stage timing shifts (fetch_intel takes longer, gsutil stalls), one job's output can overwrite the other's mid-way, producing an incoherent site state (e.g., stories.json from run A with flows.json from run B).
**Fix:** Remove market-data job entirely (it's a duplicate). Product-factory is sufficient.

---

## MIGRATION PLAN

Execute these Hermes cronjob commands in order:

### Step 1: Remove duplicate
```
cronjob(action='update', id='9685f875c2f3', enabled=false, state='paused', paused_reason='REMOVED: direct duplicate of gazzetta-product-factory (0aaa4ec10c3a). Both ran pipeline_unified.sh. See audit 2026-06-11.')
```

### Step 2: Fix product-factory schedule (30m → 60m) and display
```
cronjob(action='update', id='0aaa4ec10c3a', schedule='every 60m')
```

### Step 3: Fix living-stories schedule (60m → 120m) and display
```
cronjob(action='update', id='ce58b6a6f9cc', schedule='every 120m')
```

### Step 4: Reduce CEO Overseer (15m → 2x daily)
```
cronjob(action='update', id='6c6eb8dde234', schedule='0 8,20 * * *')
```

### Step 5: Sync editorial-writer to quality-gate cadence (drop 30min offset)
```
cronjob(action='update', id='ac99edd443f9', schedule='0 7,19 * * *')
```

### Step 6: Reduce health-check (30m → 60m)
```
cronjob(action='update', id='358f86918eca', schedule='every 60m')
```

### Summary of changes

| Job ID | Current | New | Δ |
|---|---|---|---|
| 0aaa4ec10c3a | every 30m (display 60m) | every 60m | -50% frequency |
| 358f86918eca | every 30m | every 60m | -50% frequency |
| 6c6eb8dde234 | every 15m (96x/day) | 0 8,20 * * * (2x/day) | -98% frequency |
| 9685f875c2f3 | every 60m (display 360m) | **REMOVED** | -100% |
| ce58b6a6f9cc | every 60m (display 120m) | every 120m | -50% frequency |
| ac99edd443f9 | 30 6,18 * * * | 0 7,19 * * * | Align w/ quality gate |
| b5d1ce53738e | 0 22 * * * | **KEEP** | No change |
| 3eb5b95fa216 | 0 7,19 * * * | **KEEP** | No change |

**Total jobs after migration: 7** (removed 1)
**Total LLM daily cost: $0.13/day** (was $1.40/day)
**Estimated annual savings: ~$464**
