# CSS/JS Cache Poisoning on GCS

The GCS bucket serving `www.lagazzettadikyiv.com` has an edge cache that poisons deployments in 3 patterns.

## Pattern A: CSS 0-Parsed-Rules (Browser Cache)

**Symptom**: `getComputedStyle` returns browser defaults (Times font, black text, 16px). `document.styleSheets[n].cssRules.length === 0` — stylesheet loaded but no rules parsed.

**Root cause**: Browser cached a version of the CSS file that was broken (HTTP 200 but invalid CSS). `Cache-Control: max-age=3600` from GCS keeps this cached for 1 hour.

**Why hash change didn't help**: If the CSS source file didn't change, the hash is the same. Browser serves cached broken version.

**Fix**:
```bash
# 1. Touch CSS to change hash
echo "/* cache bust */" >> site/styles.css

# 2. Regenerate hashed assets
.venv/bin/python3 scripts/build_hashed_assets.py

# 3. Delete old hashed file from disk
rm site/styles.OLDHASH.css

# 4. Force-upload with no-cache headers  
gsutil -m -h "Cache-Control:no-cache,no-store,must-revalidate" \
  cp site/styles.NEWHASH.css site/*.html gs://www.lagazzettadikyiv.com/

# 5. Verify with fresh browser (no cache)
# Navigate to: https://www.lagazzettadikyiv.com/?nocache=$RANDOM
```

## Pattern B: Hashed JS Truncation (GCS Upload Corruption)

**Symptom**: `typeof window.i18n === 'undefined'` but `fetch('/i18n.HASH.js')` returns HTTP 200 with correct `Content-Type: application/javascript`.

**Root cause**: JS file was corrupted during GCS upload — content becomes truncated (e.g., `window.i18n` → `window.i1`). The hash doesn't change because the SOURCE file is correct. `gsutil rsync` skips the file because timestamps match.

**Fix**:
```bash
# Force re-upload the specific file
gsutil cp site/i18n.NEWHASH.js gs://www.lagazzettadikyiv.com/i18n.NEWHASH.js
```

**Detection**:
```js
// In browser_console after deploy:
fetch('/i18n.HASH.js').then(r => r.text()).then(t => t.includes('window.i18n'))
// Must return true. False = file is corrupted.
```

## Pattern C: Stale HTML (Browser Cache)

**Symptom**: GCS serves correct files (verified via `fetch`), but the browser's `document.querySelectorAll('script[src]')` shows OLD hashes. CSS/JS don't apply.

**Root cause**: Browser cached `index.html` from a previous visit. The HTML references old hashed files that no longer exist on GCS.

**Fix**: Navigate with cache-busting query parameter:
```
https://www.lagazzettadikyiv.com/?nocache=1
```

**Prevention**: Set `Cache-Control: no-cache,no-store,must-revalidate` on ALL HTML files during deploy.

## Correct Deploy Workflow

```bash
cd ~/lagazzettadikyiv

# 1. Delete old files from GCS
gsutil rm gs://www.lagazzettadikyiv.com/index.html \
  gs://www.lagazzettadikyiv.com/styles.OLD.css \
  gs://www.lagazzettadikyiv.com/app.OLD.js \
  gs://www.lagazzettadikyiv.com/i18n.OLD.js

# 2. Upload with no-cache headers
gsutil -m -h "Cache-Control:no-cache,no-store,must-revalidate" \
  cp site/*.html site/*.css site/*.js gs://www.lagazzettadikyiv.com/

# 3. Set no-cache on existing objects
gsutil setmeta -h "Cache-Control:no-cache" \
  gs://www.lagazzettadikyiv.com/*.html

# 4. Verify
# Navigate to: https://www.lagazzettadikyiv.com/?v=$RANDOM
# Wait 5s, then in console:
# [typeof window.i18n, document.querySelectorAll('section.container').length]
# Expected: ["object", 6+]
```
