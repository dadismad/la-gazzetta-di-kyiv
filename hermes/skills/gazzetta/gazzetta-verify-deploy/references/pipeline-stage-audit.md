# Pipeline Stage Audit (v27.2)

Verifies that all required build stages are present in `deploy_routine.sh`. Run after any pipeline refactor or when hash mismatches appear.

## Required Stages (in order)

| Stage | Script | Required | Notes |
|-------|--------|----------|-------|
| 0 | Recreate directories | Yes | `mkdir -p public/data public/api/v1/home` |
| 1 | `db_to_json.py` | Yes | Source of truth for stories.json, flows.json |
| 1.05 | `fetch_live_prices.py` | No | Market data (skip if unavailable) |
| 1.1 | `build_related_links.py` | No | Editorial cross-linking |
| 1.2 | `analyze_narratives.py` | No | Narrative quality scoring |
| 1.5 | `enrich_*.py` | No | Signal/trades/track generation |
| **2** | **`build_site.py`** | **Yes** | Component injection + data sync |
| **2.1** | **`build_hashed_assets.py`** | **Yes** | Content-hash JS/CSS + rewrite HTML refs |
| 2.2 | `generate_broadcasts.py` | No | Telegram/Reddit broadcast drafts |
| 2.5 | `test_platform.py` | Yes | Blocking gate — must pass |
| Cleanup | Remove stale hashed assets | Yes | `find public/ -name 'styles.*.css' ... -delete` |
| 4 | GCS Deploy | Yes | `gsutil rsync` or `sync_public()` |

## Detection Commands

```bash
# Must return matches for all required stages
grep -n 'build_site\|build_hashed\|test_platform\|db_to_json' deploy_routine.sh

# Verify hashed asset cleanup covers JS too (not just CSS)
grep -n 'find.*public.*delete' deploy_routine.sh
```

## Common Failure Mode

`build_hashed_assets.py` was never in the pipeline. The script only ran locally during development. Result:
1. Developer fixes `public/story-app.js` locally → runs `build_hashed_assets.py` → hashes update
2. Docker build: `COPY public/` includes hashed files + rewritten HTML
3. Pipeline runs: `build_site.py` injects components but NO re-hashing
4. Next developer change to `public/story-app.js` → hash goes stale
5. HTML references old hash → JS 404 → page stuck on "Loading..."

## Fix Applied (2026-06-16)

Added Stage 2.1 to `deploy_routine.sh`:
```bash
# ---- Stage 2.1: build_hashed_assets ----
log "Stage 2.1: build_hashed_assets"
$PYTHON "$PROJECT/scripts/build_hashed_assets.py" || warn "build_hashed_assets.py skipped"
```

And updated cleanup to cover JS hashed files:
```bash
find "$PROJECT/public" -maxdepth 1 \( -name 'styles.*.css' ! -name 'styles.css' \) -delete
find "$PROJECT/public" -maxdepth 1 \( -name '*.????????.js' ! -name 'app.js' ! -name 'i18n.js' ! -name 'sector.js' ! -name 'story-app.js' \) -delete
```
