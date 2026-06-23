# Gazzetta Pipeline Operations and Recovery

Last updated: June 16, 2026

## Cloud Scheduler Freeze Recovery

**Symptom:** Live site stops updating. Cloud Run job logs show no executions for hours despite ENABLED scheduler. `gcloud scheduler jobs describe` shows `scheduleTime` stuck in the past while `state: ENABLED`.

**Root cause:** GCP Cloud Scheduler's internal clock can freeze on a specific `scheduleTime`, stopping all future invocations. Not a quota issue, not a pipeline failure — a scheduler infrastructure glitch.

**Recovery (proven June 2026):**
```bash
gcloud scheduler jobs pause gazzetta-pipeline-cron --location=europe-west1
gcloud scheduler jobs resume gazzetta-pipeline-cron --location=europe-west1
```

If pause/resume alone doesn't advance `scheduleTime`, force a schedule recalculation:
```bash
gcloud scheduler jobs update http gazzetta-pipeline-cron --location=europe-west1 --schedule="*/5 * * * *"
gcloud scheduler jobs update http gazzetta-pipeline-cron --location=europe-west1 --schedule="*/10 * * * *"
```

Trigger an immediate manual run to confirm pipeline health:
```bash
gcloud scheduler jobs run gazzetta-pipeline-cron --location=europe-west1
```

**Verification:** After recovery, `gcloud scheduler jobs describe` should show `scheduleTime` advancing past the current wall-clock time. Monitor for one full 10-minute cycle.

**Diagnostic commands:**
```bash
# Check scheduler state
gcloud scheduler jobs describe gazzetta-pipeline-cron --location=europe-west1 --format="yaml(state, scheduleTime, lastAttemptTime)"

# Check scheduler execution log
gcloud logging read "resource.type=cloud_scheduler_job AND resource.labels.job_id=gazzetta-pipeline-cron" --freshness=4h --limit=20

# Check Cloud Run pipeline logs
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=gazzetta-pipeline" --freshness=4h --limit=10
```

---

## Pipeline Stage Ordering: fetch_live_prices MUST Run Before db_to_json

**Pitfall:** `db_to_json.py` reads `data/market_prices.json` during asymmetry score computation and writes back with scores merged. If `fetch_live_prices.py` runs AFTER `db_to_json.py`, it overwrites the merged file with fresh prices but drops asymmetry scores. If `fetch_live_prices.py` runs FIRST, `db_to_json.py` preserves the fresh prices AND adds scores.

**Correct order in ALL pipeline scripts:**
```
Stage 0.95: fetch_live_prices.py  →  data/market_prices.json (25 assets, fresh prices)
Stage 1:    db_to_json.py         →  data/market_prices.json (25 assets + asymmetry_scores)
```

**Wrong order (causes stale data):**
```
Stage 1:    db_to_json.py         →  reads OLD data/market_prices.json (8 assets, June 11 timestamp)
Stage 1.05: fetch_live_prices.py  →  overwrites with fresh prices, drops asymmetry_scores
```

**Output path note:** `fetch_live_prices.py` writes to `data/market_prices.json` (not `public/data/`). The `build_site.py` step then syncs `data/` → `public/data/`. DO NOT set `OUT_PATH` to `public/data/` — this causes `db_to_json.py` to read stale data.

---

## Dual Pipeline Script Synchronization

The Gazzetta pipeline has TWO scripts that MUST stay in sync:

| Script | Runner | Key difference |
|--------|--------|----------------|
| `deploy_routine.sh` | Cloud Run (GCP) | Skips nuclear clean, no hashed assets, CLOUD_RUN=1 skips gsutil |
| `gazzetta_pipeline_unified.sh` | Local cron | Nuclear clean, per-stage timeouts, gsutil deploy |

**Pitfall:** `deploy_routine.sh` had `compute_flow_dimensions.py` (Stage 1.5 — line 77) but `gazzetta_pipeline_unified.sh` was missing it. This caused test_platform.py to fail with "199 flows missing duration/counterparty/scale" on the LOCAL pipeline but pass on Cloud Run (Cloud Run container had an older test_platform.py that didn't check Sprint 4 fields).

**Rule:** When adding a new pipeline stage, add it to BOTH scripts. Verify with grep:
```bash
grep 'compute_flow_dimensions' deploy_routine.sh gazzetta_pipeline_unified.sh
```

**Current stage order (both scripts, as of June 2026):**
```
0.    nuclear_clean (local only)
0.5   fetch_intel.py
0.6   bulk_approve (drafts → stories)
0.95  fetch_live_prices.py
1.    db_to_json.py
1.02  enrich_multi_persona.py
1.1   build_related_links.py
1.2   analyze_narratives_v2.py
1.5   enrich_editorial_stories.py
1.5b  ensure_generated_at.py
1.5c  generate_signal_api.py
1.5d  generate_trades_api.py
1.5e  build_track_record.py
1.5f  compute_flow_dimensions.py
2.    build_site.py
2.2   generate_broadcasts.py
2.5   test_platform.py (BLOCKING — exit 1 aborts deploy)
3.    build_hashed_assets.py (local only)
4.    GCS deploy (gsutil rsync)
```

---

## test_platform.py Gate: Known Failure Categories

The test gate at Stage 2.5 is BLOCKING. These are the known failure categories and their fixes:

| Failure | Fix |
|---------|-----|
| `199 flows missing duration/counterparty/scale` | Add `compute_flow_dimensions.py` to the pipeline script |
| `flow_dimensions metadata present` | Same — compute_flow_dimensions.py adds this |
| `Duplicate headlines` | Delete duplicate story from gazzetta.db: `DELETE FROM stories WHERE id = <duplicate_id>` |
| `public/data/stories.json not found` | Nuclear clean wiped it — db_to_json.py must complete before test |
| `market_prices.json has 8 assets (target 25+)` | fetch_live_prices.py must run BEFORE db_to_json.py |
| `8 assets missing last_updated timestamp` | Same — fetch_live_prices.py adds timestamps |
| `market_prices.json has source_stats` | Same — fetch_live_prices.py adds source_stats block |

**Diagnosis command:**
```bash
cd ~/lagazzettadikyiv && .venv/bin/python scripts/test_platform.py 2>&1 | grep -E 'FAIL|RESULTS|VERDICT'
```

**When shipit.sh test gate blocks on pre-existing data issues:** Deploy directly via gsutil (bypass shipit.sh):
```bash
GSUTIL=/Users/alexstocchi/lagazzettadikyiv/devvit/google-cloud-sdk/bin/gsutil
$GSUTIL -m rsync -r public/ gs://www.lagazzettadikyiv.com/
$GSUTIL -m setmeta -h "Cache-Control:public, max-age=0, must-revalidate" gs://www.lagazzettadikyiv.com/*.html
$GSUTIL -m setmeta -h "Cache-Control:private, no-store" gs://www.lagazzettadikyiv.com/data/*.json
```

---

## macOS `timeout` Command Dependency

**Pitfall:** `gazzetta_pipeline_unified.sh` uses `timeout` in its `run_stage()` function. macOS does not ship with GNU `timeout`. All stages wrapped in `run_stage` will fail with exit 127 ("command not found").

**Fix:** Install GNU coreutils:
```bash
brew install coreutils
# Then replace 'timeout' with 'gtimeout' in the script, OR symlink:
# sudo ln -s /usr/local/bin/gtimeout /usr/local/bin/timeout
```

**Workaround (no brew):** Run the pipeline stages individually without the wrapper script:
```bash
cd ~/lagazzettadikyiv
.venv/bin/python scripts/fetch_live_prices.py
.venv/bin/python scripts/db_to_json.py
.venv/bin/python scripts/compute_flow_dimensions.py
.venv/bin/python scripts/build_site.py
.venv/bin/python scripts/test_platform.py
# If all pass, deploy:
bash deploy_routine.sh  # (skips GCS in CLOUD_RUN mode) OR use gsutil directly
```

---

## OSINT Pipeline Starvation Pattern

**Symptom:** Site content frozen (no new stories for days). `gazzetta.db` `generated_at` timestamp is days old. No pipeline errors visible.

**Root cause chain:**
1. Local pipeline (`gazzetta_pipeline_unified.sh`) blocked at test_platform.py gate
2. `fetch_intel.py` runs but output (drafts in local gazzetta.db) never flows through to stories
3. Local gazzetta.db never gets uploaded to GCS (pipeline abort before gsutil stage)
4. Cloud Run pipeline downloads stale gazzetta.db from GCS, re-compiles same data
5. Site appears "updating" (Cloud Run exits 0) but content is frozen

**Detection:**
```bash
# Check DB freshness
.venv/bin/python -c "import sqlite3; c=sqlite3.connect('gazzetta.db'); print(c.execute('SELECT MAX(generated_at) FROM stories').fetchone()[0])"
# Check drafts queue
.venv/bin/python -c "import sqlite3; c=sqlite3.connect('gazzetta.db'); print(c.execute(\"SELECT status, COUNT(*) FROM drafts GROUP BY status\").fetchall())"
```

**Recovery:**
```bash
# 1. Pull fresh OSINT
.venv/bin/python scripts/fetch_intel.py

# 2. Approve drafts → stories
.venv/bin/python -c "..."  # bulk_approve logic

# 3. Full pipeline chain (correct order)
.venv/bin/python scripts/fetch_live_prices.py
.venv/bin/python scripts/db_to_json.py
.venv/bin/python scripts/compute_flow_dimensions.py
.venv/bin/python scripts/build_site.py
.venv/bin/python scripts/test_platform.py

# 4. Upload DB and deploy
gsutil cp gazzetta.db gs://www.lagazzettadikyiv.com/gazzetta.db
gsutil -m rsync -r public/ gs://www.lagazzettadikyiv.com/
```

---

## GCS Direct Deploy (Emergency)

When the full pipeline chain is blocked and you need to deploy NOW:
```bash
cd ~/lagazzettadikyiv
GSUTIL=~/lagazzettadikyiv/devvit/google-cloud-sdk/bin/gsutil

# Sync public/ to GCS (changed files only, no delete)
$GSUTIL -m rsync -r public/ gs://www.lagazzettadikyiv.com/

# Set cache headers
$GSUTIL -m setmeta -h "Cache-Control:public, max-age=0, must-revalidate" gs://www.lagazzettadikyiv.com/*.html
$GSUTIL -m setmeta -h "Cache-Control:private, no-store" gs://www.lagazzettadikyiv.com/data/*.json

# Upload DB
$GSUTIL cp gazzetta.db gs://www.lagazzettadikyiv.com/gazzetta.db

# Verify
curl -skI https://www.lagazzettadikyiv.com/ | head -3
curl -sk https://www.lagazzettadikyiv.com/data/stories.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Stories: {len(d.get(\"stories\",[]))}  Generated: {d.get(\"generated_at\",\"?\")[:19]}')"
```
