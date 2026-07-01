# CDN Hash Rotation Pitfall (v25.13 — June 2026)

## The Problem

After deploying new HTML files with updated CSS/JS hash references, the CDN may continue serving old HTML (with old hash references) for several minutes — even with `Cache-Control: public, max-age=0, must-revalidate`.

## Symptom

- `gsutil cat` shows the new hash reference on GCS
- `curl` shows the old hash reference from the live URL
- Browser loads old hashed JS, which may be missing critical fixes
- Console errors reference old hash filenames (e.g., `app.561d59c0.js:2345` instead of `app.647011af.js`)

## Why It Happens

The CDN edge cache may:
1. Serve stale bytes even with `must-revalidate` (especially under load)
2. Hold byte-range caches that don't revalidate the full object
3. Have intermediate proxy caches that ignore `max-age=0`

## Fix

**Always do a full hash rotation + deploy cycle:**

```bash
# 1. Build new hashes
python3 scripts/build_hashed_assets.py

# 2. Extract new hash from generated HTML
NEW_CSS=$(grep -oE 'styles\.[a-f0-9]{8}\.css' site/index.html | head -1)
NEW_JS=$(grep -oE 'app\.[a-f0-9]{8}\.js' site/index.html | head -1)

# 3. Deploy new hashed assets FIRST (so they exist when HTML references them)
$GSDK/gsutil -m cp "site/$NEW_CSS" "site/$NEW_JS" gs://www.lagazzettadikyiv.com/
$GSDK/gsutil -m setmeta -h "Cache-Control:public, max-age=31536000, immutable" \
    "gs://www.lagazzettadikyiv.com/$NEW_CSS" \
    "gs://www.lagazzettadikyiv.com/$NEW_JS"

# 4. Deploy rewritten HTML files
for f in site/*.html; do
    $GSDK/gsutil -h "Cache-Control:public, max-age=0, must-revalidate" \
        cp "$f" "gs://www.lagazzettadikyiv.com/$(basename $f)"
done

# 5. Delete old hashes to prevent confusion
OLD_CSS=$(curl -sk https://www.lagazzettadikyiv.com/ | grep -oE 'styles\.[a-f0-9]{8}\.css' | head -1)
OLD_JS=$(curl -sk https://www.lagazzettadikyiv.com/ | grep -oE 'app\.[a-f0-9]{8}\.js' | head -1)
[ "$OLD_CSS" != "$NEW_CSS" ] && $GSDK/gsutil rm "gs://www.lagazzettadikyiv.com/$OLD_CSS" 2>/dev/null
[ "$OLD_JS" != "$NEW_JS" ] && $GSDK/gsutil rm "gs://www.lagazzettadikyiv.com/$OLD_JS" 2>/dev/null

# 6. Verify live
curl -sk https://www.lagazzettadikyiv.com/ | grep -oE '(styles|app)\.[a-f0-9]{8}\.(css|js)'
```

## Verification

After deploy, ALWAYS verify the browser is actually loading the new hashes:

```js
JSON.stringify({
    cssHash: document.querySelector('link[href*="styles."]')?.href?.match(/styles\.([a-f0-9]+)\.css/)?.[1],
    jsHash: document.querySelector('script[src*="app."]')?.src?.match(/app\.([a-f0-9]+)\.js/)?.[1]
})
```

If the browser shows old hashes, the CDN is still serving stale HTML — wait 5 minutes and re-check.
