# Cloud CDN Cache-404 Bypass Pattern

## The Problem

Cloud CDN caches 404 responses for paths that never existed. After uploading the actual file, the CDN continues serving the cached HTML (the 404 redirect page, which is `index.html`). The JS consumer gets HTML instead of JSON.

**Symptoms:**
- `gsutil ls -L` shows correct object with correct hash and size
- `curl` without query param returns HTML (`<!doctype html>...`)
- `curl` WITH query param (`?t=123`) returns correct JSON (bypasses CDN)
- Browser console: `Dashboard: failed to load stories-v2.json ... not valid JSON`

## The Nuclear Fix: Fresh Path

When a path is hopelessly poisoned by CDN cached-404, upload to a COMPLETELY new path that has never been requested before:

```bash
gsutil -h "Cache-Control:no-store,max-age=0" cp stories.json \
  gs://BUCKET/data/stories-v4.json
```

Then update the JS consumer to fetch from the new path. The CDN has no cached entry for `stories-v4.json` — it serves the fresh file immediately.

## The Multiple-Version Deploy Pattern (Prevention)

Since version numbers drift between dashboard.js deployments (v2 vs v3 vs v4), the deploy step copies the data file to ALL known version paths:

```python
("deploy", ["bash", "-c", f"""
gsutil -m rsync -r -d {PUBLIC}/ gs://BUCKET/ && \
gsutil -h 'Cache-Control:no-store,max-age=0' cp {PUBLIC}/data/stories.json gs://BUCKET/data/stories-v2.json && \
gsutil -h 'Cache-Control:no-store,max-age=0' cp {PUBLIC}/data/stories.json gs://BUCKET/data/stories-v3.json && \
gsutil -h 'Cache-Control:no-store,max-age=0' cp {PUBLIC}/data/stories.json gs://BUCKET/data/stories-v4.json
"""], 120, False),
```

Whichever version the frontend fetches, the data is there. Cost: 3 extra `gsutil cp` calls per cycle (fraction of a cent).

## The Dashboard.js Version Drift Problem

The dashboard.js file and the HTML `<script>` tag may reference different version numbers:
- HTML: `<script src="./dashboard.js?v=4"></script>`
- dashboard.js internal fetch: `fetch("./data/stories-v2.json")`

The HTML's `?v=4` forces the CDN to serve fresh dashboard.js. But the dashboard.js INTERNALLY fetches `stories-v2.json` which may be cache-poisoned. BOTH need to be aligned.

**Fix chain (June 2026):**
1. Upload data to stories-v4.json (fresh path, no CDN cache)
2. Update dashboard.js fetch to `stories-v4.json`
3. Update HTML script tag to `dashboard.js?v=4` (forces CDN to serve new JS)
4. Deploy all three files

## Cache-Control for Data Files

Data files change every 10 minutes. Caching provides no benefit and creates staleness risk. Always upload with:
```
Cache-Control: no-store, max-age=0
```

For static assets (CSS, JS, images) that change rarely, use standard caching:
```
Cache-Control: public, max-age=3600
```

## Detection Script

```bash
# Check if CDN is serving HTML instead of JSON
FILE="stories-v4.json"
CONTENT=$(curl -s "https://www.lagazzettadikyiv.com/data/$FILE?_=$(date +%s)" | head -c 20)
if echo "$CONTENT" | grep -q '<!doctype'; then
  echo "CDN CACHE POISON: $FILE is serving HTML"
else
  echo "OK: $FILE is serving JSON"
fi
```

## Pitfall: gsutil rsync -d Deletes Versioned Files

`gsutil rsync -d public/ gs://...` deletes ANY file on GCS not present in `public/`. This includes versioned data files (`stories-v2.json`, `stories-v3.json`, `stories-v4.json`) that were uploaded via `gsutil cp`. The rsync deletes them, then the `cp` commands re-upload them. There is a fraction-of-a-second window where the files don't exist.

**Mitigation:** The `cp` commands run AFTER rsync in the deploy bash one-liner. The window is sub-second. If a request lands in that window, the CDN would serve a 404. The next request (seconds later) would succeed. Acceptable risk at current traffic levels.
