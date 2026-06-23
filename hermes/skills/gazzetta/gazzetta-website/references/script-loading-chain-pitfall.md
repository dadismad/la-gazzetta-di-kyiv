# Script Loading Chain — The Footer Comment Pitfall (v27.3)

## Problem

`templates/footer.html` contains the HTML comment `<!-- app.js loaded by build_site.py -->` on line 16. This is **just a comment**, not a script injection mechanism. If a page's HTML source lacks an actual `<script src="./app.js"></script>` tag, the page will NEVER get app.js loaded — through any number of pipeline runs.

## The Chain

```
templates/footer.html  →  <!-- app.js loaded by build_site.py -->   [COMMENT ONLY]
                              ↓
build_site.py          →  injects footer into public/*.html         [does NOT add script tags]
                              ↓
build_hashed_assets.py →  rewrites ./app.js → ./app.HASH.js         [REWRITES existing, never adds]
                              ↓
Result: page without <script src="./app.js"> stays broken forever
```

## How It Happened

After the v2.0 container restructure, `archive.html` was created fresh. The footer template's comment looked like it would pull in app.js, but the actual `<script src="./app.js">` tag was missing from the HTML source. Every pipeline run built, hashed, and deployed — but archive.html never got app.js. The GCS file was a pre-v2.0 version that only had `i18n.js` + inline JS.

**Detection (local):**
```bash
grep -c 'script src.*app\.' public/archive.html
# Must return ≥ 1. If 0, the script tag is missing.
```

**Detection (deployed):**
```bash
curl -s https://www.lagazzettadikyiv.com/archive.html | grep -c 'script src.*app\.'
# Must return ≥ 1.
```

**Fix:** Add `<script src="./app.js"></script>` to the page's HTML source, before any inline `<script>` block. `build_hashed_assets.py` will handle versioning on the next run.

## Prevention

When creating ANY new HTML page for the site:
1. Include `<script src="./i18n.js"></script>` (unhashed reference — hasher handles it)
2. Include `<script src="./app.js"></script>` (unhashed reference — hasher handles it)
3. NEVER rely on the footer comment — it is documentation, not mechanism
4. After first pipeline run, verify: `curl -s $SITE/PAGE.html | grep -c 'app\.[a-f0-9]\{8\}\.js'` must be ≥ 1
