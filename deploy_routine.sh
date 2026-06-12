#!/bin/bash
# deploy_routine.sh — Gazzetta di Kyiv 10-Minute Refresh Pipeline
# 
# Lightweight version of shipit.sh designed for cron execution.
# Skips: nuclear_clean, hashed_assets, git_sync, deploy_report.
# Keeps: data ingestion, build, test gate (BLOCKING), GCS sync.
#
# Usage: bash deploy_routine.sh [--dry-run]
# Cron:  */10 * * * * bash ~/lagazzettadikyiv/deploy_routine.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$SCRIPT_DIR"

BUCKET="gs://www.lagazzettadikyiv.com"
GCLOUD_DIR="${GCLOUD_DIR:-$HOME/lagazzettadikyiv/devvit/google-cloud-sdk}"
GSUTIL="$GCLOUD_DIR/bin/gsutil"
PYTHON="$PROJECT/.venv/bin/python"

DRY_RUN=false
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
    esac
done

# ---- Concurrency Lockfile (Mitigation 2) ----
LOCKFILE="/tmp/gazzetta_deploy.lock"
exec {LOCK_FD}>"$LOCKFILE" || { echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] ABORT: cannot create lockfile $LOCKFILE"; exit 1; }
if ! flock -n "$LOCK_FD"; then
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] ABORT: another deploy_routine.sh instance is running (lockfile $LOCKFILE held)"
    exit 1
fi
# Lock will be released automatically when script exits (fd closed)

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
ERRORS=0

log()  { echo "[$TIMESTAMP] $*"; }
warn() { echo "[$TIMESTAMP] WARNING: $*"; ERRORS=$((ERRORS + 1)); }
abort() {
    echo "[$TIMESTAMP] ABORT: $*"
    echo "[$TIMESTAMP] Pipeline halted. No files deployed to GCS."
    exit 1
}

log "deploy_routine.sh starting"

# ---- Stage 0: Recreate essential directories ----
mkdir -p "$PROJECT/public/data/locales"
mkdir -p "$PROJECT/public/api/v1/home"
cp "$PROJECT/templates/locales/"*.json "$PROJECT/public/data/locales/" 2>/dev/null || true

# ---- Stage 1: Data Ingestion ----
log "Stage 1: db_to_json"
if [ -f "$PROJECT/gazzetta.db" ]; then
    $PYTHON "$PROJECT/scripts/db_to_json.py" || warn "db_to_json.py failed"
else
    warn "No gazzetta.db found — using existing JSON"
fi

log "Stage 1.05: fetch_live_prices"
$PYTHON "$PROJECT/scripts/fetch_live_prices.py" || warn "Live prices skipped"

log "Stage 1.1: build_related_links"
$PYTHON "$PROJECT/scripts/build_related_links.py" || warn "Related links skipped"

log "Stage 1.2: analyze_narratives"
$PYTHON "$PROJECT/ops/analyze_narratives_v2.py" || warn "Narratives skipped"

log "Stage 1.5: enrich + signal + trades + track"
$PYTHON "$PROJECT/scripts/enrich_editorial_stories.py" || warn "enrich_editorial_stories failed"
$PYTHON "$PROJECT/scripts/ensure_generated_at.py" || warn "ensure_generated_at failed"
$PYTHON "$PROJECT/scripts/generate_signal_api.py" || warn "generate_signal_api failed"
$PYTHON "$PROJECT/scripts/generate_trades_api.py" || warn "generate_trades_api failed"
$PYTHON "$PROJECT/scripts/build_track_record.py" || warn "build_track_record failed"

# ---- Stage 2: build_site ----
log "Stage 2: build_site"
$PYTHON "$PROJECT/scripts/build_site.py" || abort "build_site.py FAILED"

# ---- Stage 2.2: generate_broadcasts ----
log "Stage 2.2: generate_broadcasts"
$PYTHON "$PROJECT/scripts/generate_broadcasts.py" || warn "Broadcasts skipped"

# ---- Stage 2.5: TEST GATE (BLOCKING) ----
log "Stage 2.5: test_platform"
if $PYTHON "$PROJECT/scripts/test_platform.py"; then
    log "All tests passed"
else
    abort "test_platform.py FAILED — deploy blocked"
fi

# ---- Clean up stale hashed assets ----
# Remove old hashed CSS/JS files that accumulate from previous runs
find "$PROJECT/public" -maxdepth 1 -name 'styles.*.css' ! -name 'styles.css' -delete 2>/dev/null || true
find "$PROJECT/public" -maxdepth 1 -name 'app.*.js' ! -name 'app.js' -delete 2>/dev/null || true
find "$PROJECT/public" -maxdepth 1 -name 'i18n.*.js' ! -name 'i18n.js' -delete 2>/dev/null || true

# ---- Stage 4: GCS Deploy ----
if [ "$DRY_RUN" = true ]; then
    log "DRY RUN — skipping GCS deploy"
else
    log "Stage 4: GCS deploy"
    
    # Rsync changed files only (no -d flag — preserve existing static files)
    $GSUTIL -m rsync -r "$PROJECT/public/" "$BUCKET/" || abort "gsutil rsync FAILED"
    
    # Cache headers: zero on HTML
    $GSUTIL -m setmeta -h "Cache-Control:public, max-age=0, must-revalidate" \
        "$BUCKET/*.html" 2>/dev/null || true
    
    # Cache headers: no-store on JSON (data must never be stale)
    $GSUTIL -m setmeta -h "Cache-Control:private, no-store" \
        "$BUCKET/data/*.json" \
        "$BUCKET/api/**/*.json" 2>/dev/null || true
    
    # Immutable cache on static CSS/JS
    $GSUTIL -m setmeta -h "Cache-Control:public, max-age=31536000, immutable" \
        "$BUCKET/styles.css" "$BUCKET/app.js" "$BUCKET/i18n.js" 2>/dev/null || true
    
    log "GCS sync complete"
fi

# ---- Stage 5: Quick Verification ----
log "Stage 5: external_verify"
HTTP_CODE=$(curl -sI -o /dev/null -w "%{http_code}" "https://www.lagazzettadikyiv.com/" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" != "200" ]; then
    warn "Homepage returned HTTP $HTTP_CODE (expected 200)"
fi

log "deploy_routine.sh complete — HTTP $HTTP_CODE — warnings: $ERRORS"

# ---- Log Rotation (Mitigation 3) ----
LOG_FILE="$PROJECT/logs/deploy_routine.log"
if [ -f "$LOG_FILE" ]; then
    LOG_LINES=$(wc -l < "$LOG_FILE" 2>/dev/null || echo 0)
    if [ "$LOG_LINES" -gt 10000 ]; then
        tail -n 10000 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
    fi
fi

exit 0
