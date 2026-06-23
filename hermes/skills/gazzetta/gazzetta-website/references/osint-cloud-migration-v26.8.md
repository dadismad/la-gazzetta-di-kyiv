# OSINT Cloud Migration Architecture (v26.8 — June 2026)

## Architecture Decision

fetch_intel.py migrated from local macOS cron to Cloud Run pipeline as Stage 0. This eliminates the "Laptop Vulnerability" — if the local machine sleeps, OSINT collection stops and the site goes stale.

## Final Architecture

```
Cloud Scheduler (every 10 min)
  → Cloud Run job gazzetta-pipeline
    1. Download gazzetta.db from GCS
    2. Seed DB from stories.json (fallback when GCS DB empty)
    3. Stage 0: fetch_intel.py (RSS feeds → drafts table, non-blocking)
    4. Stage 0.2: bulk_approve (drafts → stories, inline Python in deploy_routine.sh)
    5. Stage 1: db_to_json.py (stories → JSON)
    6. Stage 1.5f: compute_flow_dimensions.py (duration/counterparty/scale)
    7. Stage 2: build_site.py (data/ → public/data/)
    8. Stage 2.5: test_platform.py (BLOCKING gate, 568 tests)
    9. Upload DB + public/ to GCS
```

## Key Decisions

- **Single writer to gazzetta.db on GCS:** Only the Cloud Run pipeline writes. No race condition risk.
- **fetch_intel is non-blocking:** If RSS feeds fail, the pipeline continues with existing DB data.
- **Local cron paused:** `gazzetta-product-factory` (420d5f0f0c88) is cold standby.
- **Dependencies added to Dockerfile:** feedparser, pyyaml (required by fetch_intel.py).

## File Changes

- `cloud_entrypoint.py`: Added Stage 3.5 (fetch_intel) with 90s timeout, diagnostic logging
- `deploy_routine.sh`: Added Stage 0.1 (fetch_intel) + Stage 0.2 (bulk_approve inline Python)
- `Dockerfile`: Added `feedparser pyyaml` to pip install
- `gazzetta_pipeline_unified.sh`: macOS timeout compat fix (native bg+sleep+kill)
- `scripts/fetch_live_prices.py`: OUT_PATH changed from `public/data/` to `data/`

## Local Standby

The local cron script (`gazzetta_pipeline_unified.sh`) is maintained as cold standby with:
- macOS-native timeout pattern (no GNU coreutils dependency)
- Full pipeline chain including fetch_intel, compute_flow_dimensions, test_platform
- Can be re-enabled if Cloud Run fails: `cronjob action=resume job_id=420d5f0f0c88`
