# CDN Timestamp Cache Bust — build_site.py

v28, June 2026. Standard cache-busting strategies (`?v=27.1`, hashed filenames) fail
when CDN edge caches retain stale CSS/JS despite new query params. This pattern
guarantees cache eviction on every single build.

## Mechanism

`build_site.py` runs `cache_bust_assets()` after component injection and before API
generation. It appends `?t=<unix_timestamp>` to every `<link rel="stylesheet" href="*.css">`
and `<script src="*.js">` in all 22 HTML files.

```python
def cache_bust_assets():
    import time
    ts = str(int(time.time()))  # e.g. "1781622458"
    
    for fname in html_files:
        html = open(fpath).read()
        
        # <link rel="stylesheet" href="./styles.css"> → <link ... href="./styles.css?t=1781622458">
        html = re.sub(
            r'(<link\s+[^>]*href=")([^"]+\.css)(")',
            rf'\1\2?t={ts}\3',
            html
        )
        
        # <script src="./app.js"> → <script src="./app.js?t=1781622458">
        html = re.sub(
            r'(<script\s+[^>]*src=")([^"]+\.js)(")',
            rf'\1\2?t={ts}\3',
            html
        )
        
        if html != original:
            write_back(html)
```

## Pipeline Position

```
build_site.py main():
  1. sync_data()           — data/ → public/data/
  2. inject_components()   — templates/ → public/*.html
  3. cache_bust_assets()   — append ?t=TS to all CSS/JS imports  ← NEW (v28)
  4. generate_apis()       — API endpoints
```

Cache bust MUST run AFTER component injection (step 3 after step 2) because injection
creates fresh HTML with un-busted asset refs. It MUST run BEFORE deploy so the timestamps
are baked into the deployed HTML.

## What It Replaces

**Before v28:** `build_hashed_assets.py` generated content-hashed filenames (`styles.bd2f4368.css`)
and `build_site.py` injected them. This had two failure modes:
- Hashed file missing from GCS → CSS 404 (entire site unstyled) — see `references/css-404-outage-2026-06-12.md`
- Hashed file corrupted on GCS upload → silent JS failure — see bug class "Hashed File Corruption on GCS"

**After v28:** Timestamp-based cache busting on every build. No hash dependency. No separate
`build_hashed_assets.py` step needed. The timestamp changes on every build, so every deploy
is a guaranteed cache miss.

## Pitfall: `__pycache__` Staleness

When a new function like `cache_bust_assets()` is added to `build_site.py`, the old `.pyc`
bytecode in `scripts/__pycache__/build_site.cpython-311.pyc` silently runs the OLD version
without the new function. The build succeeds with zero errors but zero cache busting.

**Detection:** Check output for `Cache bust (?t=...) applied to N HTML files`. If absent,
stale bytecode is running.

**Fix:**
```bash
rm -rf scripts/__pycache__
python3 -m py_compile scripts/build_site.py  # regenerate fresh .pyc
```

In deploy scripts (`deploy_routine.sh`, `shipit.sh`), add `rm -rf $PROJECT/scripts/__pycache__`
before running `build_site.py`. The `.pyc` files are gitignored anyway — they regenerate on
first import.

## Pitfall: Regex Silently Skips URLs With Existing Query Params

The regex `([^"]+\.css)(")` matches `styles.css"` but NOT `styles.css?v=1"` because the
`?v=1` sits between `.css` and `"`. Assets with existing `?v=` query params are silently
skipped — no cache bust applied, no error logged.

**Current state (v28):** No `?v=` params exist in any HTML file. This is preemptive only.
If you later add `?v=` params to specific assets, update the regex:

```python
# Handle both bare and query-string-tagged URLs:
re.sub(
    r'(<link\s+[^>]*href=")([^"]+\.css)(\?[^"]*)?(")',
    lambda m: f'{m.group(1)}{m.group(2)}{m.group(3) or ""}?t={ts}{m.group(4)}',
    html
)
```

## Verification

After build, verify every HTML file has the timestamp:
```bash
grep -c '?t=' public/*.html
# Expected: 22 (one per HTML file)
# If < 22: some files missed — check regex or __pycache__
```

## Pitfall: build_hashed_assets.py Overwrites Timestamp Cache Busts

deploy_routine.sh runs build_site.py (which now includes cache_bust_assets()) FIRST,
then runs build_hashed_assets.py SECOND. build_hashed_assets.py replaces raw filenames
with hashed versions via regex — and the regex does NOT preserve ?t= query parameters.
The result: hashed CSS/JS references retain an OLD ?t= from a previous deploy while
raw JS references get the new timestamp.

Symptom: styles.6d32f5c7.css?t=1781622344 (old timestamp) but app.js?t=1781622898 (new).

Fix: either remove build_hashed_assets.py from the pipeline (timestamp bust makes it
redundant), or run cache_bust_assets() AFTER build_hashed_assets.py.

## Stale Hashed CSS Force-Upload Pattern

When HTML references a hashed CSS filename (e.g. styles.6d32f5c7.css) from a previous
build_hashed_assets.py run, but that file exists only on GCS — not locally. The local
styles.css was changed (e.g. added .nav-dropdown:hover rule) but the hashed copy was
never regenerated. gsutil rsync skips the file because local public/ has different
hashed files (styles.bd2f4368.css etc.).

Symptom: after deploy, getComputedStyle(body).fontFamily is "Times" and masthead
border is "0px none" — CSS file loads (HTTP 200) but contains old rules.

Fix:
```bash
cp public/styles.css public/styles.HASH.css
gsutil cp public/styles.HASH.css gs://BUCKET/styles.HASH.css
gsutil setmeta -h "Cache-Control:no-cache" gs://BUCKET/styles.HASH.css
```

Prevention: after any styles.css change, regenerate ALL hashed CSS files:
```bash
cp public/styles.css public/styles.*.css
```
Or remove hashed CSS entirely — the ?t= timestamp bust covers cache eviction.
