# Deployment Pitfalls — Reproduction Recipes

## CDN Cache: Upload Succeeds, Site Shows Old Data

**Symptom:** `gsutil cp` reports "Operation completed over 1 objects." SHA-256 of remote file differs from local. `gsutil ls -L` shows correct metadata but `curl` returns old content. After deleting the object from GCS and re-uploading, CDN continues serving stale data for minutes.

**Reproduction (2026-06-18):**
1. Run `db_to_json.py` locally → produces `data/stories.json` with 377 stories, 8 containers
2. `gsutil -h "Cache-Control:max-age=0,no-store" cp data/stories.json gs://www.lagazzettadikyiv.com/data/stories.json`
3. Output: "Operation completed over 1 objects/2.9 MiB"
4. `curl -s https://www.lagazzettadikyiv.com/data/stories.json | python3 -c "..."` → still shows 5 old stories with 6 containers
5. `gsutil rm gs://www.lagazzettadikyiv.com/data/stories.json` → file deleted
6. Re-upload with same command → same result: old data served
7. Upload to NEW path: `gsutil cp data/stories.json gs://.../data/stories-v2.json` → WORKS. Fresh path returns correct data immediately.

**Root cause:** Google Cloud CDN caches content at the edge. Per-object Cache-Control headers are ignored by the CDN's internal TTL. Only a new URL path reliably bypasses CDN.

**Fix:** Upload data files to versioned paths (`stories-v2.json`) and update the JS consumer fetch URL. When CDN cache expires on the old path, both converge.

## Double Script Loading: Silent IIFE Failure

**Symptom:** Dashboard renders 0 bubbles, 0 cards. No console errors. Scripts appear to load. `document.querySelectorAll('script[src]')` shows each JS file loaded exactly twice.

**Reproduction (2026-06-18):**
1. `templates/footer.html` contains:
   ```html
   <script src="./i18n.js"></script>
   <script src="./dashboard.js"></script>
   <script src="./app.17099070.js"></script>
   ```
2. `public/index.html` contains after `COMPONENT:FOOTER:END`:
   ```html
   <script src="./i18n.js"></script>
   <script src="./dashboard.js"></script>
   <script src="./app.17099070.js"></script>
   ```
3. `build_site.py` injects footer template content BETWEEN `FOOTER:START` and `FOOTER:END` markers
4. The HTML page's scripts AFTER `FOOTER:END` are preserved
5. Result: 6 script tags (3 from template + 3 from page), each JS file executes twice
6. `dashboard.js` is an IIFE — second execution finds `window.Gazzetta` already defined, aborts all rendering silently
7. Zero console errors, zero visual output

**Fix:** Remove ALL `<script>` tags from `templates/footer.html`. Scripts belong only in the HTML page, outside `COMPONENT:FOOTER:END`. The footer template should contain ONLY the footer HTML (`<footer>...</footer>`).

## Hashed CSS Self-Nuke: Full Layout Collapse

**Symptom:** Masthead symbols black instead of gold, fonts fall back to Times, layout collapses. CSS file not found (404 or empty response).

**Reproduction:**
1. `build_site.py` generates HTML with `<link rel="stylesheet" href="./styles.ab6de8dd.css"/>`
2. `gsutil rsync -d public/ gs://...` syncs `styles.css` AND deletes old `styles.ab6de8dd.css` (not in local `public/`)
3. Browser loads HTML, requests `styles.ab6de8dd.css` → 404
4. All CSS fails silently, page renders with default browser styles

**Fix:** Reference `styles.css` (non-hashed) in `templates/header.html` CSS link. Delete all hashed CSS files from GCS. Update `build_site.py` to use non-hashed references.
