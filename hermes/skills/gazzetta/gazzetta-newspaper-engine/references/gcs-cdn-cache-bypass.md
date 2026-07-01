# GCS Cloud CDN Cache Bypass — June 2026

## Symptom

`gsutil cp` and `gsutil rsync` report success (bytes transferred, operation
completed), but `curl` returns the old file with different SHA256 and byte
count. Even `gsutil rm` followed by `gsutil cp` of the new file doesn't help.
`gsutil stat` shows the updated metadata on the bucket object, but public HTTP
requests get the cached version.

## Root Cause

Cloud CDN sits between the GCS bucket and public HTTP. Its edge cache has a
TTL that ignores the object-level `Cache-Control: max-age=0,no-store` header
in some configurations. The CDN serves the stale copy regardless of what
happens to the underlying bucket object.

## Detection

```bash
local_sha=$(shasum -a 256 public/data/stories.json | cut -d' ' -f1)
remote_sha=$(curl -s https://www.lagazzettadikyiv.com/data/stories.json | shasum -a 256 | cut -d' ' -f1)
# If they differ, CDN is serving a stale cached copy.
```

Also check: `gsutil ls -L gs://BUCKET/path` shows correct generation/metadata,
but `curl -sI https://site/path` shows different `x-goog-stored-content-length`.

## Fix

Upload to a FRESH versioned path that has no CDN cache entry:

```bash
gsutil -h "Cache-Control:max-age=0,no-store" cp \
  public/data/stories.json \
  gs://www.lagazzettadikyiv.com/data/stories-v2.json
```

Then update the JavaScript fetch URL to point at the versioned path:

```javascript
// dashboard.js
const resp = await fetch("./data/stories-v2.json");
```

The versioned file serves instantly with no cache interference because the CDN
has never seen that path before.

## Prevention

For critical data files that change schema or format, use versioned filenames
(`stories-v3.json`) or append `?v=N` query parameters in JS fetch calls to
force CDN cache invalidation on each deploy.

When migrating between major schema versions (6-container → 8-narrative),
ALWAYS use a versioned path. The CDN will hold the old format for an unknown
duration even after bucket operations succeed.

## Pitfalls

### P1: CDN caches 404 responses too

A file that previously returned 404 will CONTINUE returning 404 via CDN even
after `gsutil cp` succeeds. The `Cache-Control: no-store` header on upload does
NOT purge the CDN's cached 404 response. The CDN's 404 TTL is independent of
the object's cache headers. Detection: `curl -sI` returns 404 but `gsutil stat`
shows the object exists with correct metadata. Fix: upload to a completely new
path (e.g., `stories-v3.json` instead of `stories-v2.json`).

### P2: CDN also caches JavaScript and CSS files

The CDN edge cache applies to ALL static assets, not just JSON data. A
re-uploaded `dashboard.js` with `Cache-Control: no-store` will still be served
stale from the CDN. Fix: add a `?v=N` query parameter to the `<script>` tag
in the HTML to force a fresh fetch path (e.g., `<script src="./dashboard.js?v=3">`).

### P3: `gsutil rsync -d` deletes versioned files

When a versioned file (e.g., `stories-v3.json`) is uploaded directly to GCS
via `gsutil cp`, it exists on GCS but NOT in the local `public/data/` directory.
A subsequent `gsutil rsync -d -r public/ gs://BUCKET/` will DELETE the versioned
file because `-d` removes destination objects that have no source counterpart.
**Fix**: After `rsync -d`, re-upload the versioned file manually:
```bash
gsutil -h "Cache-Control:max-age=0,no-store" cp \
  public/data/stories.json \
  gs://www.lagazzettadikyiv.com/data/stories-v3.json
```
Or keep a local copy at `public/data/stories-v3.json` so `rsync` preserves it.
