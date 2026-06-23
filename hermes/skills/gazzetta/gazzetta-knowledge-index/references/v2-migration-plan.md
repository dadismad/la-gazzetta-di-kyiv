# v2.0 Migration Plan — Consequence-Traced

## Architecture Change Summary

**Before (v1):** INTEL/ALPHA two-world split. 43 pipeline scripts. 14-stage pipeline. 23 HTML pages. 377 stories with capital flow annotations. 199 flows. Hero stats. Product pages (Signal, Trades, Track, Stories, Flows, etc.). 7 active Cloud Run jobs.

**After (v2.0):** 6 domain-based geopolitical containers. 9 pipeline scripts. 5-stage pipeline. 9 HTML pages. 377 stories reclassified into containers with power-vector tags. No flows table in output JSON. Collapsible container UI. 2 active Cloud Run jobs.

## Dependency Map (Critical for Migration Safety)

```
gazzetta.db ──► db_to_json.py ──► data/stories.json ──► public/data/stories.json (synced)
            │                                              │
            │                                              ├──► app.js (browser fetch)
            │                                              ├──► archive.html (browser fetch)
            │                                              └──► test_platform.py (reads DATA/stories.json)
            │
            └──► cloud_entrypoint.py ──► download_db() ← GCS
                                     ──► sync_public() → GCS
                                     ──► upload_db() → REMOVED (Agent = sole writer)
```

## Migration Order (Why This Sequence)

The order matters because intermediate states break the running pipeline:

1. **DB migration first** — Add columns (safe, pipeline reads full_json, ignores new columns)
2. **Classification second** — Backfill container + tags (new data in new columns, old columns intact)
3. **Script rewrites third** — db_to_json, build_site, test_platform, deploy_routine, cloud_entrypoint
4. **Frontend fourth** — index.html, app.js, styles.css (depend on new JSON format)
5. **Deletion fifth** — Remove old HTML/JS files (only after new frontend is ready)
6. **Docker build last** — Atomic switchover: all changes deploy together

## What Each Consumer Required

| Consumer | Old Input | New Input | Change |
|----------|-----------|-----------|--------|
| app.js | `data/stories.json` (flat array) + `data/flows.json` | `data/stories.json` (6 containers object) | Complete rewrite |
| build_site.py sync_data() | `data/stories.json` (smart merge) | Removed — db_to_json v2 syncs directly | Function deleted |
| build_site.py generate_apis() | `data/flows.json` → API endpoints | Removed — no APIs needed | Function deleted |
| test_platform.py | `data/stories.json` + `data/flows.json` (flow integrity) | `data/stories.json` (container integrity) | 478→140 lines |
| cloud_entrypoint.py | upload_db() + sync_public() | sync_public() only | upload_db() removed |
| deploy_routine.sh | 14 stages (db_to_json through GCS deploy) | 5 stages (db_to_json through test) | 8 stages removed |

## Rollback Procedure

```bash
# Instant rollback to v1:
cp gazzetta_v1_backup.db gazzetta.db
git checkout public/ scripts/ templates/ deploy_routine.sh cloud_entrypoint.py
gcloud run jobs update gazzetta-pipeline --image <previous-image-hash> --region europe-west1
gcloud scheduler jobs resume cco-distributor-cron --location europe-west1
# (repeat for all 5 paused schedulers)
gcloud run jobs execute gazzetta-pipeline --region europe-west1 --wait
```

## SQLite WAL Fix (Critical)

**Problem:** GCS round-trip loses `gazzetta.db-wal` and `gazzetta.db-shm`. Cloud Run downloads incomplete checkpoint. Multiple concurrent writers = corruption.

**Fix implemented:**
1. Hermes Agent = SOLE WRITER to gazzetta.db
2. Cloud Run = READ-ONLY (downloads DB, generates JSON, does NOT upload DB)
3. Agent runs `PRAGMA wal_checkpoint(TRUNCATE)` before every GCS upload
4. Agent uploads all three files: `gazzetta.db`, `gazzetta.db-wal`, `gazzetta.db-shm`
5. `upload_db()` removed from `cloud_entrypoint.py` (line 130)

## Pipeline Simplification (43 → 9 active scripts)

**Removed from pipeline (8 stages):**
- fetch_live_prices.py (no market data)
- build_related_links.py (no story linking)
- analyze_narratives_v2.py (Agent classifies)
- enrich_editorial_stories.py (no capital flow enrichment)
- ensure_generated_at.py (DB has timestamps)
- generate_signal_api.py (no Signal product)
- generate_trades_api.py (no Trades product)
- build_track_record.py (no Track Record)
- generate_broadcasts.py (no auto-distribution)
- generate_flows.py (no flows table in output)
- generate_flow_nodes.py (no flow visualization)

**Kept in pipeline (5 stages):**
- db_to_json.py (Stage 1 — 6-container JSON)
- build_site.py (Stage 2 — component injection)
- build_hashed_assets.py (Stage 2.1 — hash JS/CSS)
- test_platform.py (Stage 2.5 — BLOCKING gate, 88 assertions)
- gsutil rsync (Stage 4 — GCS deploy via cloud_entrypoint)
