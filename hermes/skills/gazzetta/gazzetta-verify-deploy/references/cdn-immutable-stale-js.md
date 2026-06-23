# CDN Immutable Cache Serving Stale JS — Sprint 4 Reproduction

## Symptom

After deploying updated `app.js` to GCS, `curl -sI` shows correct `stored-content-length` (127,720 bytes matches local) but `curl -s` returns old code. New JS functions (e.g., `durationLabel`) return 0 matches in `grep -c`.

## Root Cause

`cloud_entrypoint.py` `sync_public()` sets `Cache-Control: public, max-age=31536000, immutable` on all `.js` and `.css` files:

```python
elif rel.endswith((".css", ".js")):
    cache = "public, max-age=31536000, immutable"
```

The `immutable` directive tells browsers and CDN edge nodes to cache for one year AND never revalidate — even when GCS object content changes. GCS shows the new bytes (`stored-content-length` matches), but the HTTP response is the cached stale copy.

## Reproduction

```bash
# 1. Deploy updated app.js
gsutil cp public/app.js gs://BUCKET/app.js

# 2. Verify GCS stored content (CORRECT — shows new bytes)
curl -sI https://www.lagazzettadikyiv.com/app.js | grep stored-content-length
# → x-goog-stored-content-length: 127720

# 3. Verify served content (STALE — old code)
curl -s https://www.lagazzettadikyiv.com/app.js | grep -c "durationLabel"
# → 0 (should be 1+)

# 4. Compare local vs GCS
wc -c public/app.js
# → 127720
# Bytes match but content differs — CDN is withholding the update
```

## Fix Options

### Option A: Versioned filename (recommended)
Upload as `app.v4.js` and update all 20 HTML file references. CDN treats it as a new file.

### Option B: Flush cache headers temporarily
```bash
gsutil setmeta -h "Cache-Control:no-cache, max-age=0" gs://BUCKET/app.js
gsutil cp -h "Cache-Control:no-cache, max-age=0" public/app.js gs://BUCKET/app.js
# Wait 60s for CDN propagation
curl -s https://www.lagazzettadikyiv.com/app.js | grep -c "durationLabel"
# → 1 (fresh!)
# Then restore sensible cache
gsutil setmeta -h "Cache-Control:public, max-age=3600" gs://BUCKET/app.js
```

### Option C: CDN invalidation (if CDN is GCP-managed)
```bash
gcloud compute url-maps invalidate-cdn-cache URL_MAP_NAME \
  --path "/app.js" --project=PROJECT
```

## Prevention

- After any JS/CSS deploy, verify with `grep -c UNIQUE_NEW_CODE` on the live URL with `Cache-Control: no-cache` request header.
- Consider reducing the immutable period from 31536000 (1 year) to 86400 (24 hours) for rapidly-evolving files.
- For sprint-level changes, always verify browser_console reflects the new code after deploy.
