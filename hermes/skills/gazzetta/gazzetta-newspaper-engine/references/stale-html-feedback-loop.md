# Stale HTML Feedback Loop — Complete Diagnostic (June 2026)

## The Bug

The live site at `lagazzettadikyiv.com` loads old JavaScript/CSS despite correct files existing locally. Manual GCS fixes get overwritten within 10 minutes. The core mechanism is a feedback loop between three components.

## The Feedback Loop

```
1. Docker image built with COPY public/ /app/public/
   → OLD public/*.html frozen in container with old hashes

2. Every 10 min, Cloud Run starts:
   a. deploy_routine.sh runs build_site.py
      → injects templates/footer.html (OLD hash: app.ad499bee.js)
      → overwrites public/*.html with old script references
   b. Old deploy_routine.sh THEN deleted hashed assets from public/:
      find "$PROJECT/public" -name 'app.*.js' ! -name 'app.js' -delete
      → Current hashed JS files destroyed
   c. cloud_entrypoint.py sync_public() uploads everything
      → GCS gets: HTML with old hashes, NO current hashed JS files
      → Browser loads old app.ad499bee.js (if it exists on GCS from prior build)
        OR loads nothing (if file was deleted from GCS too)

3. Manual fix: upload app.64037977.js to GCS, update index.html
   → Works for <10 minutes
   → Next Cloud Run cycle: overwrites HTML back to old hash
   → Manual fix undone
```

## Detection Pattern

```js
// In browser_console on live site:
document.querySelector('script[src*="app."]')?.src
// Returns: "https://www.lagazzettadikyiv.com/app.ad499bee.js"
// But local templates/footer.html and build-manifest.json say app.64037977.js

// Check GCS:
gsutil cat gs://www.lagazzettadikyiv.com/index.html | grep 'app\.'
// Returns: app.ad499bee.js

// Check local:
grep 'app\.' public/index.html
// Returns: app.64037977.js

// MISMATCH = stale HTML feedback loop
```

## Root Cause Identification

Step through each component:

1. **Check templates/footer.html** — the hash written here is what gets injected into ALL 22 HTML pages every 10 minutes
2. **Check deploy_routine.sh** — if it deletes hashed assets (lines with `find ... -delete`) without regenerating them via `build_hashed_assets.py`, the HTML references broken files
3. **Check Docker image age** — `COPY public/` at build time freezes the state. If the image is older than the fix, the fix gets overwritten.

## Fix (3 components — all required)

### 1. Update templates/footer.html
```html
<!-- Old (STALE): -->
<script src="./app.ad499bee.js"></script>
<!-- New (CURRENT): -->
<script src="./app.64037977.js"></script>
```

### 2. Update deploy_routine.sh
```bash
# REMOVE these lines (they destroy hashed assets):
# find "$PROJECT/public" -maxdepth 1 -name 'app.*.js' ! -name 'app.js' -delete

# ADD this stage (AFTER build_site, BEFORE sync):
log "Stage 3: build_hashed_assets"
$PYTHON "$PROJECT/scripts/build_hashed_assets.py" || warn "build_hashed_assets.py failed"
```

### 3. Rebuild Docker image
```bash
# Must rebuild and update Cloud Run or the next cycle will re-inject old footer
gcloud builds submit --tag europe-west1-docker.pkg.dev/PROJECT/gazzetta-docker/gazzetta-pipeline:latest
gcloud run jobs update gazzetta-pipeline --region=europe-west1 --image=...gazzetta-pipeline:latest
```

## Immediate GCS Fix (bypasses the loop until next cycle)
```bash
# Deploy correct files directly to GCS
gsutil -m rsync -r public/ gs://www.lagazzettadikyiv.com/
gsutil -m setmeta -h "Cache-Control:public, max-age=0, must-revalidate" gs://www.lagazzettadikyiv.com/*.html
```

## Prevention
- After any change to `templates/footer.html` or `public/app.js`, always:
  1. Run `build_hashed_assets.py`
  2. Rebuild the Docker image
  3. Deploy immediately to GCS (don't wait for the next pipeline cycle to overwrite)
- The `deploy_routine.sh` pipeline now calls `build_hashed_assets.py` after `build_site.py`, breaking the loop at the source
