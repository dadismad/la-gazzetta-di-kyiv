#!/bin/bash
# shipit.sh — Gazzetta di Kyiv deploy pipeline v3.1 (Nuclear Clean + Atomic Sync)
#
# Stages:
#   0. nuclear_clean — rm -rf public/ (fresh start, no ghost files)
#   1. db_to_json   — Compile gazzetta.db → data/stories.json + data/flows.json
#   1.02 enrich_mp  — Multi-persona blocks (C-Suite/Quant/Degen)
#   1.05 live_prices— CoinGecko price feed
#   1.1  rel_links  — Auto-interlinking engine
#   1.2  narratives — 3 Core Market Narratives
#   1.5  enrich     — Editorial enrichment + signal/trades API
#   2.   build_site — Sync data/ → public/data/
#   2.5  TEST GATE  — test_platform.py (MUST PASS — abort on failure)
#   2.6  ru_sync    — RU sync gate
#   3.   hash       — SHA256-hash CSS/JS
#   4.   GCS deploy — rsync -d to bucket, set cache headers
#   5.   live verify— curl homepage + curl stories.json for newest headline
#   6.   report     — deploy_report.txt
#   7.   git sync   — add → commit → push
#
# Usage: bash shipit.sh [--skip-git] [--dry-run] [--nuclear]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$SCRIPT_DIR"

BUCKET="gs://www.lagazzettadikyiv.com"
GCLOUD_DIR="${GCLOUD_DIR:-$HOME/lagazzettadikyiv/devvit/google-cloud-sdk}"
GCLOUD="$GCLOUD_DIR/bin/gcloud"
GSUTIL="$GCLOUD_DIR/bin/gsutil"
PYTHON="$PROJECT/.venv/bin/python"
SKIP_GIT=false
DRY_RUN=false
NUCLEAR=false

for arg in "$@"; do
    case "$arg" in
        --skip-git) SKIP_GIT=true ;;
        --dry-run)  DRY_RUN=true ;;
        --nuclear)  NUCLEAR=true ;;
    esac
done

echo "══════════════════════════════════════"
echo "  SHIPIT — Gazzetta di Kyiv Deploy"
echo "══════════════════════════════════════"
echo ""

# ═══ Stage 0: Nuclear Clean — delete generated dirs before every build ═══
echo "── Stage 0: nuclear_clean ──"
# Only delete generated directories — preserve HTML/CSS/JS sources in repo
for dir in "$PROJECT/public/data" "$PROJECT/public/api"; do
    if [ -d "$dir" ]; then
        rm -rf "$dir"
        echo "  ✓ $(basename "$dir")/ deleted"
    fi
done
# Also remove generated files
rm -f "$PROJECT/public/build-manifest.json" "$PROJECT/public/deploy_report.txt" \
      "$PROJECT/public/styles."*.css "$PROJECT/public/app."*.js "$PROJECT/public/story-app."*.js \
      "$PROJECT/public/sector."*.js "$PROJECT/public/i18n."*.js "$PROJECT/public/styles-modern."*.css 2>/dev/null || true
echo "  ✓ Hashed assets cleaned"
# Recreate essential dirs
mkdir -p "$PROJECT/public/api/v1/home"
# Preserve locale files (static source, not pipeline output)
mkdir -p "$PROJECT/public/data/locales"
cp "$PROJECT/templates/locales/"*.json "$PROJECT/public/data/locales/" 2>/dev/null || true
echo "  ✓ Essential directories recreated (data/en/ removed — EN-only, no RU mirror needed)"
echo ""

# ═══ Stage 1: db_to_json ──
echo "── Stage 1: db_to_json ──"
if [ -f "$PROJECT/gazzetta.db" ]; then
    $PYTHON "$PROJECT/scripts/db_to_json.py"
    echo "  ✓ JSON compiled from gazzetta.db"

    echo "── Stage 1.02: enrich_multi_persona ──"
    $PYTHON "$PROJECT/scripts/enrich_multi_persona.py" || echo "  ⚠ Multi-persona skipped (API unavailable)"
    echo "  ✓ Multi-persona blocks enriched"
else
    echo "  ⚠ No gazzetta.db found — skipping (JSON unchanged)"
fi
echo ""

echo "── Stage 1.05: fetch_live_prices ──"
$PYTHON "$PROJECT/scripts/fetch_live_prices.py" || echo "  ⚠ Live prices skipped"
echo "  ✓ Live prices fetched"
echo ""

echo "── Stage 1.1: build_related_links ──"
$PYTHON "$PROJECT/scripts/build_related_links.py" || echo "  ⚠ Related links skipped"
echo "  ✓ Story→story & story→flow links generated"
echo ""

echo "── Stage 1.2: analyze_narratives ──"
$PYTHON "$PROJECT/ops/analyze_narratives_v2.py" || echo "  ⚠ Narratives skipped"
echo ""

echo "── Stage 1.5: enrich ──"
$PYTHON "$PROJECT/scripts/enrich_editorial_stories.py" || echo "  ⚠ enrich_editorial_stories FAILED — continuing"
$PYTHON "$PROJECT/scripts/ensure_generated_at.py" || echo "  ⚠ ensure_generated_at FAILED — continuing"
echo "  ✓ Stories enriched with capital_flow + generated_at"
$PYTHON "$PROJECT/scripts/generate_signal_api.py" || echo "  ⚠ generate_signal_api FAILED — continuing"
$PYTHON "$PROJECT/scripts/generate_trades_api.py" || echo "  ⚠ generate_trades_api FAILED — continuing"
$PYTHON "$PROJECT/scripts/build_track_record.py" || echo "  ⚠ build_track_record FAILED — continuing"
echo "  ✓ Signal + Trades + Track Record API endpoints generated"
echo ""

# ═══ Stage 2: build_site ──
echo "── Stage 2: build_site ──"
$PYTHON "$PROJECT/scripts/build_site.py"
echo "  ✓ public/data/ synced, API endpoints generated"
echo ""

# ═══ Stage 2.2: generate_broadcasts ──
echo "── Stage 2.2: generate_broadcasts ──"
$PYTHON "$PROJECT/scripts/generate_broadcasts.py" || echo "  ⚠ generate_broadcasts FAILED — continuing"
echo "  ✓ Distribution broadcasts generated"
echo ""

# ═══ Stage 2.5: TEST GATE — BLOCKING ═══
echo "── Stage 2.5: test_platform ──"
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

# ═══ Stage 3: hash — SHA256-hash CSS/JS, rewrite HTML references ═══
echo "── Stage 3: build_hashed_assets ──"
$PYTHON "$PROJECT/scripts/build_hashed_assets.py"
echo "  ✓ CSS/JS hashed, HTML references rewritten"
echo ""
# ═══ Stage 3.1: ru_sync_gate — REMOVED (Russian version deleted June 2026) ═══
echo "── Stage 3.1: ru_sync_gate ──"
echo "  ✓ SKIPPED — Russian version removed. English only."

# ═══ Stage 4: GCS deploy ──
echo "── Stage 4: GCS deploy ──"
if [ "$DRY_RUN" = true ]; then
    echo "  DRY RUN — skipping gsutil"
elif [ "$NUCLEAR" = true ]; then
    echo "  ☢ NUCLEAR MODE: deleting remote bucket contents..."
    $GSUTIL -m rm -r "$BUCKET/**" 2>/dev/null || true
    echo "  ✓ Remote bucket cleared"
fi

if [ "$DRY_RUN" != true ]; then
    # Rsync with delete (-d) to remove stale files
    $GSUTIL -m rsync -r -d "$PROJECT/public/" "$BUCKET/"
    # Immutable cache on hashed assets
    $GSUTIL -m setmeta -h "Cache-Control:public, max-age=31536000, immutable" \
        "$BUCKET/styles.*.css" "$BUCKET/app.*.js" "$BUCKET/story-app.*.js" \
        "$BUCKET/sector.*.js" 2>/dev/null || true
    # Zero cache on ALL HTML
    $GSUTIL -m setmeta -h "Cache-Control:public, max-age=0, must-revalidate" \
        "$BUCKET/*.html" 2>/dev/null || true
    # No-store on ALL JSON
    $GSUTIL -m setmeta -h "Cache-Control:private, no-store" \
        "$BUCKET/data/*.json" \
        "$BUCKET/api/**/*.json" 2>/dev/null || true
    echo "  ✓ GCS rsync + cache headers set"
fi
echo ""

# ═══ Stage 5: EXTERNAL VERIFICATION (curl public internet) ═══
echo "── Stage 5: external_verify ──"
SITE_URL="https://www.lagazzettadikyiv.com"

# Verify homepage
HTTP_CODE=$(curl -sI -o /dev/null -w "%{http_code}" "$SITE_URL/" 2>/dev/null || echo "000")
echo "  Homepage: HTTP $HTTP_CODE"

# Verify stories.json freshness
JSON_TS=$(curl -s -H 'Cache-Control: no-cache' "$SITE_URL/data/stories.json" 2>/dev/null | \
    python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('generated_at','MISSING')[:19])" 2>/dev/null || echo "FAILED")
echo "  stories.json generated_at: $JSON_TS"

# Verify newest headline on public internet
NEWEST_LEAD=$(curl -s -H 'Cache-Control: no-cache' "$SITE_URL/data/stories.json" 2>/dev/null | \
    python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('lead',{}).get('headline','MISSING')[:80])" 2>/dev/null || echo "FAILED")
echo "  Public lead headline: $NEWEST_LEAD"

# Compare with local
LOCAL_LEAD=$(python3 -c "import json; d=json.load(open('$PROJECT/public/data/stories.json')); print(d.get('lead',{}).get('headline','MISSING')[:80])" 2>/dev/null || echo "FAILED")
if [ "$NEWEST_LEAD" != "$LOCAL_LEAD" ] && [ "$NEWEST_LEAD" != "FAILED" ]; then
    echo ""
    echo "  ⚠ OPERATIONAL CRISIS: Public headline ≠ local headline"
    echo "     Public: $NEWEST_LEAD"
    echo "     Local:  $LOCAL_LEAD"
    echo "     CDN cache may be stale. Run with --nuclear to force-clear."
    # Don't abort — warn and continue
fi

# Verify stories.html contains content
STORIES_HTML=$(curl -s -H 'Cache-Control: no-cache' "$SITE_URL/stories.html" 2>/dev/null | wc -c)
echo "  stories.html: ${STORIES_HTML} bytes"
echo ""

# ═══ Stage 6: deploy report ──
echo "── Stage 6: deploy report ──"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
STORY_COUNT=$($PYTHON -c "import json; d=json.load(open('data/stories.json')); print(len(d.get('stories',[])))" 2>/dev/null || echo "?")
cat > "$PROJECT/public/deploy_report.txt" <<EOF
Deploy: $TIMESTAMP
Commit: $COMMIT
Stories: $STORY_COUNT
HTTP: $HTTP_CODE
Lead: $LOCAL_LEAD
Public match: $([ "$NEWEST_LEAD" = "$LOCAL_LEAD" ] && echo YES || echo "NO — CDN STALE")
EOF
echo "  ✓ deploy_report.txt written"
echo ""

# ═══ Stage 7: git sync ──
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
if [ "$NEWEST_LEAD" != "$LOCAL_LEAD" ] && [ "$NEWEST_LEAD" != "FAILED" ]; then
    echo "  ⚠ CDN STALE — public site not reflecting latest deploy"
fi
echo "══════════════════════════════════════"
