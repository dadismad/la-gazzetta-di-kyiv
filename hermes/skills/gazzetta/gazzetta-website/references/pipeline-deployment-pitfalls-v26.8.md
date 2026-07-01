# Pipeline and Deployment Pitfalls (v26.8)

Compiled from June 2026 emergency pipeline restoration session.

## site/ Directory Missing After Pipeline Run

**Symptom:** Dropdown buttons, share buttons, or other JS-powered UI elements don't work on the live site. The hashed JS file on GCS (e.g., `app.ad499bee.js`) doesn't contain recent functions like `wireNavDropdowns`. Local `public/app.js` has the function but the deployed hash doesn't.

**Root cause:** The `site/` directory doesn't exist (wiped by nuclear clean or never created). `build_hashed_assets.py` reads from `site/app.js` to create `site/app.<hash>.js`. If `site/app.js` doesn't exist, the build silently creates no hashed JS file. The previous hash (`app.ad499bee.js`) remains on GCS from an old deploy — with old code.

**Detection:**
```bash
# Check if deployed JS has the expected function
curl -sk https://www.lagazzettadikyiv.com/app.*.js 2>&1 | grep -c 'wireNavDropdowns'
# Returns 0 → stale hash on GCS
# Check local hashed JS
grep -c 'wireNavDropdowns' public/app.*.js
# Returns 2 → local hash is correct, just not deployed
```

**Fix:**
```bash
cd ~/lagazzettadikyiv
mkdir -p site
cp public/app.js public/styles.css public/i18n.js site/
.venv/bin/python scripts/build_hashed_assets.py
ls public/app.*.js  # verify new hash exists
gsutil -h "Cache-Control:public, max-age=0, must-revalidate" cp public/index.html gs://www.lagazzettadikyiv.com/index.html
gsutil cp public/app.*.js gs://www.lagazzettadikyiv.com/
gsutil cp public/styles.*.css gs://www.lagazzettadikyiv.com/
curl -sk https://www.lagazzettadikyiv.com/ | grep -o 'app\.[a-f0-9]*\.js'  # verify new hash
```

**Prevention:** Always verify `ls site/app.js` after `build_site.py` and before `build_hashed_assets.py`. If `site/` is empty, the hashed build silently produces nothing.

## Cloud Scheduler Freeze — scheduleTime Stuck in Past

**Symptom:** Cloud Run pipeline stops executing. GCS data goes stale for hours. `gcloud scheduler jobs describe` shows `scheduleTime` in the past and `state: ENABLED`. Cloud Run logs show no new executions.

**Diagnostic:**
```bash
gcloud scheduler jobs describe gazzetta-pipeline-cron --location=europe-west1 --format="yaml(state, scheduleTime, lastAttemptTime)"
# Frozen: scheduleTime is >10min in past, lastAttemptTime matches it
```

**Fix:**
```bash
# Method 1: Pause/resume (resets internal clock)
gcloud scheduler jobs pause gazzetta-pipeline-cron --location=europe-west1
gcloud scheduler jobs resume gazzetta-pipeline-cron --location=europe-west1
gcloud scheduler jobs run gazzetta-pipeline-cron --location=europe-west1  # force-immediate

# Method 2: Schedule toggle (if pause/resume doesn't work)
gcloud scheduler jobs update http gazzetta-pipeline-cron --location=europe-west1 --schedule="*/5 * * * *"
gcloud scheduler jobs update http gazzetta-pipeline-cron --location=europe-west1 --schedule="*/10 * * * *"
```

## macOS bash timeout Compatibility

The `timeout` command from GNU coreutils is not available on macOS by default. Scripts that call `timeout` (like `gazzetta_pipeline_unified.sh`) will fail with "command not found" on every stage.

**Native macOS replacement pattern** (bg + sleep + kill):
```bash
run_stage() {
    local name="$1"
    local script="$2"
    shift 2
    echo "── $name ──"
    python3 "$script" "$@" 2>&1 &
    local cmd_pid=$!
    (
        sleep "$STAGE_TIMEOUT"
        kill -TERM "$cmd_pid" 2>/dev/null || true
    ) &
    local watcher_pid=$!
    wait "$cmd_pid" 2>/dev/null
    local rc=$?
    kill -TERM "$watcher_pid" 2>/dev/null || true
    wait "$watcher_pid" 2>/dev/null || true
    if [ $rc -eq 0 ]; then
        echo "  ✓ $name OK"
    elif [ $rc -ge 128 ]; then  # SIGTERM = 128+15=143
        echo "  ⚠ $name TIMED OUT (${STAGE_TIMEOUT}s) — continuing"
    else
        echo "  ⚠ $name FAILED (exit $rc) — continuing"
    fi
    echo ""
}
```

## Pipeline Order: fetch_live_prices BEFORE db_to_json

fetch_live_prices.py writes to `public/data/market_prices.json` (by default — the path in the script). db_to_json.py reads `data/market_prices.json`, adds asymmetry_scores, writes to BOTH `data/` and `public/data/`. If db_to_json runs first, it reads stale market_prices.json (8 assets, old timestamp), then fetch_live_prices writes fresh data (25 assets). But db_to_json's `public/data/` mirror may have stale data if the order is wrong.

**Fix applied (June 2026):**
- Changed fetch_live_prices.py OUT_PATH from `public/data/market_prices.json` to `data/market_prices.json`
- Reordered gazzetta_pipeline_unified.sh: fetch_live_prices (Stage 0.95) runs BEFORE db_to_json (Stage 1)
- This ensures db_to_json reads the fresh prices and writes them with asymmetry_scores to both locations

**Verification:** test_platform.py P7 checks market_prices.json for >=25 assets, source_stats, and last_updated fields.
