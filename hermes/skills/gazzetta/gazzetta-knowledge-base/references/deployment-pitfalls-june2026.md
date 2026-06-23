# Deployment Pitfalls Discovered June 2026

## GCS Edge Cache Blindness
- GCS HTTP frontend caches with `max-age=3600` (1 hour)
- `gsutil cat` shows fresh content; public `curl` returns stale
- Fix: `gsutil -m setmeta -h "Cache-Control:no-cache, max-age=0" gs://BUCKET/*`
- Verify: `curl -sI URL | grep cache-control`
- **Note**: `setmeta` does NOT always propagate to the CDN edge immediately. Upload with `gsutil cp -h "Cache-Control:no-store,max-age=0"` from the start for instant verification.

## Hashed Filename Cache-Bust (Sprint 1 pattern)
- When GCS edge cache refuses to serve fresh content despite cache-control headers
- Upload versioned files: `app.SHA256.js` with `Cache-Control:immutable`
- Update HTML references to the hashed filename
- Pros: cache works for you instead of against you. Cons: must update HTML every deploy.
- Command: `gsutil -h "Cache-Control:public, max-age=31536000, immutable" cp file gs://BUCKET/file.$HASH.ext`

## Deleting Old CSS Breaks Cached Sub-Pages
- Edge cache serves old HTML referencing deleted CSS files
- Sub-pages load with ZERO styles → user sees broken layout
- Fix: update ALL HTML on GCS before deleting any CSS, or overwrite old hashed CSS with latest content

## CSS Duplicate Rules Outside @media
- Later rules in cascade win silently
- `read_file` pagination truncates large CSS files, hiding duplicates
- Fix: `grep -n "selector" styles.css` to find ALL occurrences before editing

## browser_vision Hallucinates Colors
- Both browser_vision and vision_analyze reported "dark bar" when computed styles proved white
- Primary verification: `browser_console` with `getComputedStyle()`
- Vision is backup only, never primary for color/layout

## Project Reorganization (June 2026)
- 25 HTML files existed in BOTH root and site/ — root copies were stale
- 5 CSS/JS files duplicated — root copies stale
- FIX: deleted all root HTML/CSS/JS duplicates
- site/ is now the SOLE source of truth
- archive/ holds 5 unique old HTML files
- docs/audits/ holds 8 old reports
