#!/bin/bash
# shipit.sh — Full build → hash → deploy → verify → git
# Run from project root. Uses .venv/bin/python for all Python execution.
set -euo pipefail

cd /Users/alexstocchi/projects/gazzetta-di-kyiv
PYTHON=".venv/bin/python"
NOW=$(date '+%Y-%m-%d %H:%M:%S')
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "═════════════════════════════════════════════"
echo "  SHIPIT  $NOW"
echo "═════════════════════════════════════════════"

# ── §1: DATA UPDATE ──────────────────────────────────
echo ""
echo "[1/6] intel_to_stories — ingest latest intel..."
$PYTHON scripts/intel_to_stories.py
echo "  ✓ stories updated"

# ── §2: LOCAL SYNC — canonical sources → site/ ──────
echo ""
echo "[2/6] Local sync — copy canonical sources → site/..."
SYNC_FILES=(
  index.html about.html capital.html contacts.html cooperation.html
  data.html event_horizon.html flows.html geopolitics.html markets.html
  ops.html pleasure.html privacy.html research.html signal.html
  stories.html story.html track.html trades.html
  variant-modern.html wealth.html
  styles.css
  app.js story-app.js
  robots.txt sitemap.xml
)
for f in "${SYNC_FILES[@]}"; do
  [ -f "$f" ] && cp "$f" site/
done
echo "  ✓ HTML/CSS/JS synced to site/"

# ── §3: DATA SYNC — data/ → site/data/ + API ────────
echo ""
echo "[3/6] build_site — data → site/data/ + API endpoints..."
$PYTHON scripts/build_site.py
echo "  ✓ data synced + API generated"

# ── §4: BUILD & HASH — content-hashed assets ─────────
echo ""
echo "[4/6] build_hashed_assets — hash CSS/JS, rewrite HTML..."
$PYTHON scripts/build_hashed_assets.py
echo "  ✓ assets hashed + HTML rewritten"

# ── §5: GCS DEPLOY ───────────────────────────────────
echo ""
echo "[5/6] Deploy to GCS..."
export CLOUDSDK_CONFIG="/Users/alexstocchi/.config/gcloud"
GCLOUD_DIR="/Users/alexstocchi/lagazzettadikyiv/google-cloud-sdk"
export PATH="$GCLOUD_DIR/bin:$PATH"

gsutil -m rsync -d -r site/ gs://www.lagazzettadikyiv.com/ 2>&1 | grep -v "Copying mtime" || true

# Hashed assets → immutable cache
gsutil -m setmeta -h "Cache-Control:public, max-age=31536000, immutable" \
  "gs://www.lagazzettadikyiv.com/styles.[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f].css" \
  "gs://www.lagazzettadikyiv.com/styles-modern.[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f].css" \
  "gs://www.lagazzettadikyiv.com/app.[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f].js" \
  "gs://www.lagazzettadikyiv.com/i18n.[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f].js" \
  "gs://www.lagazzettadikyiv.com/sector.[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f].js" \
  "gs://www.lagazzettadikyiv.com/story-app.[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f].js" 2>&1 | tail -3 || true

# HTML → short revalidation
gsutil -m setmeta -h "Cache-Control:public, max-age=0, must-revalidate" \
  "gs://www.lagazzettadikyiv.com/*.html" 2>&1 | tail -3 || true

# JSON data → no cache
gsutil -m setmeta -h "Cache-Control:private, no-store" \
  "gs://www.lagazzettadikyiv.com/data/stories.json" \
  "gs://www.lagazzettadikyiv.com/data/flows.json" \
  "gs://www.lagazzettadikyiv.com/data/living_stories.json" \
  "gs://www.lagazzettadikyiv.com/data/flow_nodes.json" \
  "gs://www.lagazzettadikyiv.com/data/event_horizon.json" \
  "gs://www.lagazzettadikyiv.com/data/stories_ru.json" \
  "gs://www.lagazzettadikyiv.com/data/flows_ru.json" \
  "gs://www.lagazzettadikyiv.com/data/i18n_ru.json" \
  "gs://www.lagazzettadikyiv.com/data/story_registry.json" \
  "gs://www.lagazzettadikyiv.com/data/representation_techniques.json" \
  "gs://www.lagazzettadikyiv.com/api/v1/home/regime.json" \
  "gs://www.lagazzettadikyiv.com/api/v1/home/setups.json" \
  "gs://www.lagazzettadikyiv.com/api/v1/home/contradictions.json" \
  "gs://www.lagazzettadikyiv.com/api/v1/home/divergences.json" \
  "gs://www.lagazzettadikyiv.com/api/v1/home/aftershocks.json" 2>&1 | tail -3 || true

echo "  ✓ deployed to GCS"

# ── §6: LIVE VERIFICATION ────────────────────────────
echo ""
echo "[6/6] Live verification..."
echo "─────────────────────────────────────────────"
curl -s -D - https://www.lagazzettadikyiv.com/ -o /dev/null 2>&1
echo "─────────────────────────────────────────────"

if curl -skI "https://www.lagazzettadikyiv.com/" 2>&1 | grep -q "200"; then
    echo -e "  ${GREEN}✓ DEPLOY OK${NC} — $(date '+%Y-%m-%d %H:%M:%S')"
else
    echo -e "  ${RED}⚠ DEPLOY WARN${NC} — check site"
fi

# ── §7: GIT SYNC ────────────────────────────────────
echo ""
echo "  git add . && git commit && git push..."
git add .
git commit -m "deploy: automatic site update via shipit" || echo "  (nothing to commit)"
git push origin main 2>&1 || echo "  (push skipped — check remote)"

echo ""
echo "═══════════════════════════"
echo "  SHIPIT COMPLETE"
echo "═══════════════════════════"
