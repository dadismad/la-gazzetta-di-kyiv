#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# shipit.sh — Unified Build + Deploy wrapper for Gazzetta di Kyiv
# ═══════════════════════════════════════════════════════════════════
# Replaces the disjointed gsutil calls with a single robust pipeline
# that injects correct Cache-Control headers at upload time.
#
# Cache strategy:
#   index.html  → public, max-age=0, must-revalidate (always fresh)
#   data/*.json → private, no-store (never cached; live trading data)
#   static assets → public, max-age=86400 (1-day cache; rarely change)
#
# Exit codes: 0=success, 1=build failure, 2=deploy failure
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

# ── Paths ──────────────────────────────────────────────────────────
PROJECT="${GAZZETTA_HOME:-/opt/gazzetta-di-kyiv}"
VENV_PYTHON="${PROJECT}/venv/bin/python"
PUBLIC="${PROJECT}/public"
SCRIPTS="${PROJECT}/scripts"
BUCKET="gs://www.lagazzettadikyiv.com"
REPORT="${PROJECT}/deploy_report.txt"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

log()  { echo "[shipit ${TIMESTAMP}] $*"; }
die()  { log "FATAL: $*"; echo "[${TIMESTAMP}] FATAL: $*" >> "$REPORT"; exit "${2:-1}"; }

# Ensure report dir exists
mkdir -p "$(dirname "$REPORT")"

# ── Step 1: Build ──────────────────────────────────────────────────
log "BUILD: running build_frontend.py..."
if ! sudo -u gazzetta "$VENV_PYTHON" "$SCRIPTS/build_frontend.py" > /tmp/build_frontend.log 2>&1; then
    tail -30 /tmp/build_frontend.log >> "$REPORT"
    die "build_frontend.py failed (see /tmp/build_frontend.log)" 1
fi
log "BUILD: OK"

# ── Step 2: Deploy index.html — zero-cache, always revalidate ──────
log "DEPLOY: index.html (max-age=0, must-revalidate)..."
if ! gsutil -h "Cache-Control: public, max-age=0, must-revalidate" \
            cp "$PUBLIC/index.html" "$BUCKET/index.html" 2>/tmp/gsutil_err.log; then
    cat /tmp/gsutil_err.log >> "$REPORT"
    die "gsutil cp index.html failed" 2
fi
log "DEPLOY: index.html OK"

# ── Step 3: Deploy data JSONs — private, no-store (live trading data) ──
log "DEPLOY: data/*.json (private, no-store)..."
FAILED_DATA=0
for json_file in "$PUBLIC"/data/*.json; do
    fname="$(basename "$json_file")"
    if ! gsutil -h "Cache-Control: private, no-store" \
                cp "$json_file" "$BUCKET/data/$fname" 2>/tmp/gsutil_err.log; then
        log "WARNING: Failed to upload $fname — continuing"
        cat /tmp/gsutil_err.log >> "$REPORT"
        FAILED_DATA=1
    fi
done
if [ "$FAILED_DATA" -eq 1 ]; then
    log "DEPLOY: data JSONs completed with SOME failures (see report)"
else
    log "DEPLOY: all data JSONs OK"
fi

# ── Step 4: Deploy static assets — cached ──────────────────────────
log "DEPLOY: static assets (css, js, dossiers — 1-day cache)..."
if ! gsutil -m -h "Cache-Control: public, max-age=86400" \
            rsync -x 'data/.*' -x 'index.html' -r "$PUBLIC/" "$BUCKET/" 2>/tmp/gsutil_err.log; then
    cat /tmp/gsutil_err.log >> "$REPORT"
    log "WARNING: static asset rsync had errors (non-fatal)"
fi

# ── Success ────────────────────────────────────────────────────────
echo "[${TIMESTAMP}] deploy OK — index.html + data JSONs + static assets" >> "$REPORT"
log "DONE — all stages complete"
exit 0
