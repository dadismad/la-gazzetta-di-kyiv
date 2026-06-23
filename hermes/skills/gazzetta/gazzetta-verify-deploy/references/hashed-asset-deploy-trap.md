# Hashed-Asset Deployment Trap (v25.10)

## Symptom

You deploy a JS fix to the hashed file (e.g., `app.c05fc65f.js`) but the browser still loads old code. The fix is confirmed on GCS (`curl` shows the new code) but the browser shows old behavior.

## Root Cause

Gazzetta uses content-hashed filenames (`app.031e0adf.js`) with `Cache-Control: max-age=31536000, immutable`. The HTML references a SPECIFIC hash. When you patch `app.js` and run `build_hashed_assets.py`, it generates a NEW hash (`app.c05fc65f.js`) and rewrites local HTML references. But if you only deploy the new hashed JS file WITHOUT deploying the updated HTML, the live HTML still references the OLD hash (`app.031e0adf.js`). The browser loads the old JS from cache (immutable).

## The trap

```bash
# This SEEMS correct but is WRONG:
NEW_HASH=$(grep -o 'app\.[a-f0-9]*\.js' site/stories.html | head -1)
gsutil cp site/app.js gs://BUCKET/$NEW_HASH
# → Browser still loads old hash because HTML was never updated!
```

## The fix

ALWAYS deploy BOTH the new hashed JS AND the rewritten HTML:

```bash
# 1. Copy source to site/
cp app.js site/app.js

# 2. Hash + rewrite HTML references
python scripts/build_hashed_assets.py

# 3. Deploy updated HTML (references new hash)
gsutil -h "Cache-Control:public,max-age=0,must-revalidate" cp site/stories.html gs://BUCKET/stories.html
gsutil -h "Cache-Control:public,max-age=0,must-revalidate" cp site/index.html gs://BUCKET/index.html

# 4. Deploy new hashed JS
NEW_HASH=$(grep -o 'app\.[a-f0-9]*\.js' site/stories.html | head -1)
gsutil -h "Cache-Control:public, max-age=31536000, immutable" cp site/app.js gs://BUCKET/$NEW_HASH
```

## Quick fix (bypass HTML deploy)

If you can't redeploy all HTML, deploy to the LIVE hash that HTML currently references:

```bash
# Find the hash the live site actually loads
LIVE_HASH=$(curl -s https://www.lagazzettadikyiv.com/ | grep -o 'app\.[a-f0-9]*\.js' | head -1)
# Deploy fix to that exact filename
gsutil -h "Cache-Control:public,max-age=0,must-revalidate" cp site/app.js gs://BUCKET/$LIVE_HASH
```

But this is a workaround — next `build_hashed_assets.py` run will change the hash again. The proper fix is deploying HTML + JS together.
