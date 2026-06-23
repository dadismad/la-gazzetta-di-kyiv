# Build Pipeline Pitfalls (June 2026)

## CSS Hashing: build_site.py ≠ build_hashed_assets.py

**Pitfall**: Editing `site/styles.css` or `site/app.js` and running `build_site.py` does NOT update the hashed filenames or HTML references. `build_site.py` only syncs data JSON files. CSS/JS changes require `build_hashed_assets.py` separately.

**Correct sequence after editing CSS/JS/HTML:**
```bash
python3 scripts/build_site.py          # sync data files
python3 scripts/build_hashed_assets.py # hash CSS/JS, rewrite HTML refs
gsutil -m rsync -d -r site/ gs://www.lagazzettadikyiv.com/
```

**Symptom when skipped**: Browser loads old cached CSS even though `styles.css` was synced to GCS. HTML still references old hash like `styles.d60c0958.css` while new file is `styles.435bac57.css`.

**Verification**: Always check `grep "stylesheet" site/index.html` after hashing to confirm the new hash appears.

## Sidebar CSS Override Trap

**Pitfall**: Adding `.col-alpha { display: none; }` early in `styles.css` gets overridden by a later `.col-alpha { display: flex; }` block. CSS specificity is equal (both class selectors), so last rule wins.

**Fix**: Either remove the old rule block entirely, or add `display: none !important`. Prefer removal — dead code should not remain.

## Focus Group CDN Cache Pitfall

**Pitfall**: After deploying, CDN may serve stale cached CSS/HTML for up to 1 hour. Focus groups evaluating the site see the OLD version.

**Fix**: Always use a fresh cache-bust parameter like `?_v=2606xxx` when verifying or spawning focus groups. Wait 60-120s after gsutil rsync before verifying.
