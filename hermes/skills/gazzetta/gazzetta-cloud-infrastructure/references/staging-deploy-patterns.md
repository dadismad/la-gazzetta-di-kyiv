# Staging Deployment Patterns (June 2026)

Deploying isolated design variants to GCS subpaths (`/staging/`) for parallel review.

## GCS gsutil Quirks

### CRITICAL: `gsutil -m cp -r` Creates Nested Directories

When the local directory name matches the GCS path prefix:

```bash
# WRONG — creates gs://bucket/staging/staging/stitch-mobile/
gsutil -m cp -r staging/ gs://bucket/staging/

# RIGHT — use individual file uploads
gsutil -o 'GSUtil:parallel_process_count=1' cp staging/stitch-mobile/feed.html gs://bucket/staging/stitch-mobile/feed.html
```

`gsutil cp -r local_dir/ gs://bucket/local_dir/` copies the directory INSIDE the target path, creating a nested `local_dir/local_dir/` structure. Always use explicit per-file uploads when the source directory name matches the destination prefix.

### `gsutil mv` Timeout on MacOS

GCS-to-GCS `gsutil mv` commands (moving objects within a bucket) frequently time out on MacOS even on small files (~200KB). Use individual `gsutil cp` with `parallel_process_count=1` instead:

```bash
# WORKS:
GSU=devvit/google-cloud-sdk/bin/gsutil
$GSU -o 'GSUtil:parallel_process_count=1' cp local_file gs://bucket/path/

# TIMES OUT (30s+):
$GSU -m mv gs://bucket/staging/staging/ gs://bucket/staging/
```

### GCS Website `notFoundPage: index.html` — Staging 404 Fallback

When the GCS bucket has `notFoundPage: "index.html"` (SPA fallback pattern), newly-created staging paths return 404 that redirects to `index.html`. The CDN caches this 404 redirect. Use cache-busting query parameters until CDN expires:

```bash
# May return 404/HTML fallback initially:
curl https://www.lagazzettadikyiv.com/staging/stitch-mobile/feed.html

# Returns 200 immediately:
curl "https://www.lagazzettadikyiv.com/staging/stitch-mobile/feed.html?v=1"
```

After CDN cache expiry (~1 hour for GCS), bare URLs resolve correctly.

## Stitch Design Variant Discovery

Stitch exports arrive as numbered ZIPs in `~/Downloads/`:

```
stitch_la_gazzetta_di_kyiv_mobile.zip       # May contain only screen.png + DESIGN.md
stitch_la_gazzetta_di_kyiv_mobile (1).zip   # May contain screen.png only per page
stitch_la_gazzetta_di_kyiv_mobile (2).zip   # LATEST — contains code.html + screen.png per page
```

The highest-numbered ZIP contains the actual deployable `code.html` files. Earlier ZIPs are partial exports (screenshots only). Always check all numbered variants before concluding files are missing.

Each variant directory in the ZIP contains:
- `code.html` — self-contained Tailwind CDN HTML page
- `screen.png` — reference screenshot for pixel verification

HTMLs are standalone (Tailwind CDN + Google Fonts + Material Symbols CDN). No build step required — deploy as-is.
