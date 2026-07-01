# CDN Cache Invalidation — Hashed Assets

## The Problem

GCS is the origin. Cloud CDN sits in front. When you deploy a new version of a content-hashed file (e.g., `story-app.7931b318.js`), the CDN edge nodes may continue serving the OLD bytes even though GCS has the new content. This happens when:

1. A previous deploy used the same content hash for different content (rare but possible)
2. CDN edge nodes cache aggressively and ignore `Cache-Control: no-store` headers
3. The file was previously served from that edge node and the cache hasn't expired

## Detection

```bash
# Check what GCS actually has (bypasses CDN)
curl -sk "https://storage.googleapis.com/www.lagazzettadikyiv.com/story-app.7931b318.js" | grep -c 'EXPECTED_FUNCTION'

# Check what CDN serves
curl -sk "https://www.lagazzettadikyiv.com/story-app.7931b318.js" | grep -c 'EXPECTED_FUNCTION'

# If counts differ → CDN is serving stale cache
```

## Browser-side detection

```js
// Fetch the JS from the browser and check its content
fetch(document.querySelector('script[src*="story-app"]').src)
  .then(r => r.text())
  .then(t => JSON.stringify({
    len: t.length,
    hasExpectedFunction: t.includes('renderMultiPersona')
  }))
```

If `hasExpectedFunction` is false but GCS direct URL has it → CDN cache stale.

## Fix: Force New Content Hash

The build_hashed_assets.py script generates hashes from file content. To force a new hash when the CDN is stuck:

1. Add a unique comment to the source file:
```js
// v24.1: ... [fbac8fa8]  // unique marker changes hash
```

2. Rebuild:
```bash
cp story-app.js site/story-app.js
python3 scripts/build_hashed_assets.py
```

3. Deploy the NEW hash (not the old one):
```bash
GSDK=~/lagazzettadikyiv/google-cloud-sdk/bin
$GSDK/gsutil -h "Cache-Control:no-store,max-age=0" cp site/story-app.NEWHASH.js gs://www.lagazzettadikyiv.com/
$GSDK/gsutil -h "Cache-Control:no-store,max-age=0" cp site/story.html gs://www.lagazzettadikyiv.com/
```

4. Verify the new hash is live:
```bash
curl -sk "https://storage.googleapis.com/www.lagazzettadikyiv.com/story-app.NEWHASH.js" | grep -c 'EXPECTED_FUNCTION'
# Must print >0
```

## Prevention

- Always use `Cache-Control:no-store,max-age=0` on deploy
- Verify via `storage.googleapis.com` (bypasses CDN) before checking `www.lagazzettadikyiv.com`
- If the CDN is stale, DON'T wait — force a new hash immediately
- The version comment technique takes 30 seconds and guarantees a fresh edge cache

## Google Cloud CDN Programmatic Invalidation (v32.0+ June 2026)

The delete-reupload pattern (`gsutil rm` + `gsutil cp`) updates the GCS object immediately but the **CDN edge cache continues serving stale bytes** until `max-age` expires. This is NOT a GCS issue — it's the Cloud CDN layer in front of the Load Balancer.

### Detection

```bash
# GCS direct (bypasses CDN) — shows truth
curl -sk "https://storage.googleapis.com/www.lagazzettadikyiv.com/data/stories.json" | python3 -c "import json,sys; print(json.load(sys.stdin).get('total_stories'))"

# CDN (via LB) — may be stale
curl -sk "https://www.lagazzettadikyiv.com/data/stories.json" | python3 -c "import json,sys; print(json.load(sys.stdin).get('total_stories'))"

# If counts differ → CDN is serving stale cache
```

Also check the `age:` header — if it's growing and the `stored-content-length` differs from GCS, the CDN cache is stale.

### Fix: gcloud compute url-maps invalidate-cdn-cache

```bash
GSDK=~/lagazzettadikyiv/devvit/google-cloud-sdk/bin

# Find the URL map name
$GSDK/gcloud compute url-maps list --format='value(name)'
# → gazzetta-url-map

# Invalidate specific paths
$GSDK/gcloud compute url-maps invalidate-cdn-cache gazzetta-url-map --path '/data/stories.json'
$GSDK/gcloud compute url-maps invalidate-cdn-cache gazzetta-url-map --path '/index.html'
$GSDK/gcloud compute url-maps invalidate-cdn-cache gazzetta-url-map --path '/'

# The CDN edge cache is purged immediately. Next request fetches fresh from GCS.
```

**When to use:** EVERY time you deploy a non-hashed file (stories.json, index.html, flows.json) and need it live immediately. The delete-reupload trick does NOT bypass the CDN edge — only invalidation does.

**When NOT needed:** Hashed files (app.HASH.js) — those use content-addressing so a new hash IS a new URL that the CDN has never seen.

### Session Incidents

- **June 22, 2026 v32.0**: `data/stories.json` — Deployed with `Cache-Control:no-cache,no-store` and even deleted + re-uploaded. CDN continued serving `age: 293` with `stored-content-length: 3349968` (old 401-story file) while GCS had `3502760` bytes (411-story file). `gsutil stat` confirmed new file on GCS. Only `gcloud compute url-maps invalidate-cdn-cache` resolved it.

## Session Incidents

- **June 10, 2026 v24.0**: `story-app.503dffb5.js` — CDN served old content under new hash for ~10 minutes. Multiple browser tests showed `gazzettaLoaded: false` despite GCS having correct content. Forced new hash `story-app.0eb534c3.js` with `[fbac8fa8]` marker, then `story-app.cc2e0196.js`.
- **June 10, 2026 v24.0**: `story-app.7931b318.js` — Same pattern. GCS confirmed via `storage.googleapis.com`, CDN served stale. Resolved by hash rotation.
