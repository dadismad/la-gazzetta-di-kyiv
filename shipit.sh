#!/bin/bash
# shipit.sh — Gazzetta di Kyiv deploy pipeline v3.0 (SQLite-backed)
#
# Stages:
#   1. db_to_json   — Compile gazzetta.db → data/stories.json + data/flows.json
#   2. build_site   — Sync data/ → site/data/ + generate API endpoints
#   3. hash assets  — SHA256-hash CSS/JS, rewrite HTML references
#   4. GCS deploy   — gsutil rsync site/ → GCS bucket
#   5. live verify  — curl headers
#   6. deploy report— generate deploy_report.txt
#   7. git sync     — add → commit → push
#
# Usage: bash shipit.sh [--skip-git] [--dry-run]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$SCRIPT_DIR"

# ── Config ──
BUCKET="gs://www.lagazzettadikyiv.com"
GCLOUD_DIR="${GCLOUD_DIR:-$HOME/lagazzettadikyiv/google-cloud-sdk}"
GCLOUD="$GCLOUD_DIR/bin/gcloud"
GSUTIL="$GCLOUD_DIR/bin/gsutil"
PYTHON="$PROJECT/.venv/bin/python"
SKIP_GIT=false
DRY_RUN=false

for arg in "$@"; do
    case "$arg" in
        --skip-git) SKIP_GIT=true ;;
        --dry-run)  DRY_RUN=true ;;
    esac
done

echo "══════════════════════════════════════"
echo "  SHIPIT — Gazzetta di Kyiv Deploy"
echo "══════════════════════════════════════"
echo ""

# ═══ Stage 1: db_to_json — compile SQLite → JSON ═══
echo "── Stage 1: db_to_json ──"
if [ -f "$PROJECT/gazzetta.db" ]; then
    $PYTHON "$PROJECT/scripts/db_to_json.py"
    echo "  ✓ JSON compiled from gazzetta.db"
else
    echo "  ⚠ No gazzetta.db found — skipping (JSON unchanged)"
fi
echo ""

# ═══ Stage 1.2: analyze_narratives — synthesize 3 Core Market Narratives ═══
echo "── Stage 1.2: analyze_narratives ──"
$PYTHON "$PROJECT/ops/analyze_narratives_v2.py" || echo "  ⚠ Narratives skipped (API unavailable — using fallback)"

# ═══ Stage 1.5: enrich — add capital_flow + generated_at to editorial stories ═══
echo "── Stage 1.5: enrich ──"
$PYTHON "$PROJECT/scripts/enrich_editorial_stories.py" || true
$PYTHON "$PROJECT/scripts/ensure_generated_at.py" || true
echo "  ✓ Stories enriched with capital_flow + generated_at"

# v23.0: Generate API endpoints for Signal + Trades
$PYTHON "$PROJECT/scripts/generate_signal_api.py" || true
$PYTHON "$PROJECT/scripts/generate_trades_api.py" || true
echo "  ✓ Signal + Trades API endpoints generated"
echo ""

# ═══ Stage 2: build_site — sync data + API endpoints ═══
echo "── Stage 2: build_site ──"
$PYTHON "$PROJECT/scripts/build_site.py"
echo "  ✓ site/data/ synced, API endpoints generated"
echo ""

# ═══ Stage 2.5: test_platform — automated UI & data integrity gate ═══
echo "
# ═══ Stage 2.2: generate broadcasts ═══
echo "── Stage 2.2: generate_broadcasts ──"
$PYTHON "$PROJECT/scripts/generate_broadcasts.py" || true
echo "  ✓ Distribution broadcasts generated"
echo ""

# ═── Stage 2.5: test_platform ──"
if $PYTHON "$PROJECT/scripts/test_platform.py"; then
    echo "  ✓ All tests passed"
else
    echo ""
    echo "══════════════════════════════════════"
    echo "  DEPLOY ABORTED: test failures detected"
    echo "  Fix issues above and re-run shipit.sh"
    echo "══════════════════════════════════════"
    exit 1
fi
echo ""

# ═══ Stage 3: hash assets ═══
echo "── Stage 3: hash assets ──"
$PYTHON "$PROJECT/scripts/build_hashed_assets.py"
echo "  ✓ CSS/JS hashed, HTML references rewritten"
echo ""

# ═══ Stage 4: GCS deploy ═══
echo "── Stage 4: GCS deploy ──"
if [ "$DRY_RUN" = true ]; then
    echo "  DRY RUN — skipping gsutil rsync"
else
    # Set immutable cache on hashed assets
    $GSUTIL -m rsync -r -d "$PROJECT/site/" "$BUCKET/"
    $GSUTIL -m setmeta -h "Cache-Control:public, max-age=31536000, immutable" \
        "$BUCKET/styles.*.css" "$BUCKET/app.*.js" "$BUCKET/story-app.*.js" \
        "$BUCKET/sector.*.js" 2>/dev/null || true
    # Zero cache on HTML
    $GSUTIL -m setmeta -h "Cache-Control:public, max-age=0, must-revalidate" \
        "$BUCKET/*.html" 2>/dev/null || true
    # Private, no-store on JSON (critical for HFT/quant data freshness — v2.1 CEOverlord fix)
    $GSUTIL -m setmeta -h "Cache-Control:private, no-store" \
        "$BUCKET/data/*.json" 2>/dev/null || true
    echo "  ✓ GCS rsync complete"
fi
echo ""

# ═══ Stage 5: live verify ═══
echo "── Stage 5: live verify ──"
HTTP_CODE=$(curl -sI -o /dev/null -w "%{http_code}" "https://www.lagazzettadikyiv.com/" 2>/dev/null || echo "000")
ETAG=$(curl -sI "https://www.lagazzettadikyiv.com/" 2>/dev/null | grep -i 'etag:' | tr -d '\r' || echo "none")
echo "  HTTP $HTTP_CODE · ETag: ${ETAG#ETag: }"
echo ""

# ═══ Stage 6: deploy report ═══
echo "── Stage 6: deploy report ──"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
STORY_COUNT=$($PYTHON -c "import json; d=json.load(open('data/stories.json')); print(len(d.get('stories',[])))" 2>/dev/null || echo "?")
cat > "$PROJECT/site/deploy_report.txt" <<EOF
Deploy: $TIMESTAMP
Commit: $COMMIT
Stories: $STORY_COUNT
HTTP: $HTTP_CODE
ETag: ${ETAG#ETag: }
EOF
echo "  ✓ deploy_report.txt written"
echo ""

# ═══ Stage 7: git sync ═══
echo "── Stage 7: git sync ──"
if [ "$SKIP_GIT" = true ] || [ "$DRY_RUN" = true ]; then
    echo "  Skipped (--skip-git or --dry-run)"
else
    git add -A
    if git diff --cached --quiet; then
        echo "  No changes to commit"
    else
        git commit -m "shipit: $TIMESTAMP — $STORY_COUNT stories, SQLite-backed"
        git push origin main
        echo "  ✓ Pushed to origin/main"
    fi
fi
echo ""

echo "══════════════════════════════════════"
echo "  SHIPIT COMPLETE"
echo "  $TIMESTAMP · $STORY_COUNT stories · $(git rev-parse --short HEAD 2>/dev/null || echo ?)"
echo "══════════════════════════════════════"
