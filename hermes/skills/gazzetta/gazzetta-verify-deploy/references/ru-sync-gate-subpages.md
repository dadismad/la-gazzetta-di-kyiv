# RU Sync Gate Sub-Page File List Fix

## The Bug

`shipit.sh` §3.1 (ru_sync_gate) originally copied only 10 files to `site/ru/`:

```bash
for f in about.html capital.html data.html index.html methodology.html sources.html terms.html robots.txt sitemap.xml; do
```

**Missing:** `stories.html`, `flows.html`, `event_horizon.html`, `flow-nodes.html`, `signal.html`, `trades.html`, `track.html`, `privacy.html`

## The Consequence

GCS returns 404 for `/ru/stories.html`, `/ru/flows.html`, etc. GCS bucket falls back to serving `ru/index.html` (the homepage template). Every RU sub-page appears to render the homepage with hero indicators showing `—`. User sees same content on every page.

## The Fix

### 1. Expand the file list in shipit.sh ru_sync_gate:

```bash
for f in about.html capital.html data.html index.html methodology.html sources.html terms.html robots.txt sitemap.xml stories.html flows.html event_horizon.html flow-nodes.html signal.html trades.html track.html privacy.html; do
  if [ ! -f "$PROJECT/site/ru/$f" ]; then
    cp "$PROJECT/site/$f" "$PROJECT/site/ru/$f" 2>/dev/null || true
    case "$f" in *.html) sed -i '' 's/<html lang="en"/<html lang="ru"/g' "$PROJECT/site/ru/$f" ;; esac
    RU_MISSING=$((RU_MISSING + 1))
  fi
done
```

### 2. Fix RU HTML files for subdirectory serving:

After copying, ALL RU HTML files need three fixes:
- `lang="ru"` on `<html>` tag
- `<base href="/">` after `<meta charset>` (so `./data/stories.json` resolves from root)
- `src="./` → `src="../` and `href="./` → `href="../` for all script/stylesheet references

```bash
for f in site/ru/*.html; do
  # Add base href if missing
  if ! grep -q '<base href="/">' "$f"; then
    sed -i '' 's|<meta charset="utf-8"/>|<meta charset="utf-8"/>\n  <base href="/">|' "$f"
  fi
  # Fix script/stylesheet paths
  sed -i '' 's|src="./|src="../|g; s|href="./|href="../|g' "$f"
done
```

### 3. When test gate blocks deploy:

If `shipit.sh` aborts at Stage 2.5 (test failures), run stages 3-4 manually:

```bash
# Stage 3: Hash assets
.venv/bin/python scripts/build_hashed_assets.py

# Stage 3.1: RU sync (run the expanded loop above)
# ... copy + fix all RU HTML files ...

# Stage 4: GCS deploy
GSDK=~/lagazzettadikyiv/google-cloud-sdk/bin
$GSDK/gsutil -m rsync -r -d site/ gs://www.lagazzettadikyiv.com/
$GSDK/gsutil -m setmeta -h "Cache-Control:public, max-age=0, must-revalidate" \
    gs://www.lagazzettadikyiv.com/*.html gs://www.lagazzettadikyiv.com/ru/*.html
```

### Verification

After deploy, verify each RU sub-page loads unique content (not the homepage template):

```bash
# RU stories page MUST return different content than RU homepage
STORY_LEN=$(curl -sk "https://www.lagazzettadikyiv.com/ru/stories.html" | wc -c)
INDEX_LEN=$(curl -sk "https://www.lagazzettadikyiv.com/ru/" | wc -c)
echo "RU stories: $STORY_LEN bytes, RU index: $INDEX_LEN bytes"
# MUST differ significantly — if identical, sub-pages are serving homepage fallback
```

```js
// Browser console: verify stories loaded
JSON.stringify({
  stories: window.STORIES_DATA?.length,
  firstHeadline: document.querySelector('article h3')?.textContent?.substring(0, 80)
})
// PASS: stories > 0, firstHeadline contains Cyrillic characters
```
