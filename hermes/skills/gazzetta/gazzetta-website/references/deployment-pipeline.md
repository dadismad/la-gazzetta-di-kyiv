# Gazzetta Deployment Pipeline Reference
# v1.0 — Extracted from CSS 404 catastrophe, June 2026

## Critical Failure Mode: Hashed CSS Ghost Files

### What Happened
`build_hashed_assets.py` created `styles.d0b7cbda.css` locally and rewrote all 20 HTML files to reference it. The subsequent `gsutil rsync` failed silently because `shipit.sh` GCLOUD_DIR pointed to a non-existent path, causing fallback to unauthenticated pip gsutil (401 on writes). The hashed CSS file was never uploaded. The live site lost ALL CSS styling — masthead gold border gone, fonts fell back to Times, SVGs exploded to viewport width (1264x2528px for caduceus).

### Root Causes
1. `shipit.sh` GCLOUD_DIR: `~/lagazzettadikyiv/google-cloud-sdk` did not exist
2. Fallback gsutil in Hermes venv had no write credentials (read-only)
3. No pre-deployment check verified the hashed CSS file existed on GCS
4. No post-deployment browser_console verification caught the missing CSS

### Prevention Checklist
Before any deployment that touches CSS or asset references:
1. Verify `index.html` line 13 CSS href matches an actual file on GCS:
   ```
   curl -sI https://www.lagazzettadikyiv.com/styles.css | head -1
   ```
2. Use ONLY the authenticated gsutil:
   ```
   ~/lagazzettadikyiv/devvit/google-cloud-sdk/bin/gsutil
   ```
3. After deploy, verify live: `getComputedStyle(document.body).fontFamily` must include "Source Serif 4"

## Correct gsutil Path

```
~/lagazzettadikyiv/devvit/google-cloud-sdk/bin/gsutil
```

Located inside the devvit SDK directory. The pip-installed gsutil:
```
~/.hermes/hermes-agent/venv/bin/gsutil
```
has READ-ONLY access and returns 401 on all write operations.

## Deployment Commands

### Full deploy (shipit.sh):
```bash
bash ~/lagazzettadikyiv/shipit.sh
```

### 10-minute refresh (deploy_routine.sh):
```bash
bash ~/lagazzettadikyiv/deploy_routine.sh
```

### Manual rsync:
```bash
~/lagazzettadikyiv/devvit/google-cloud-sdk/bin/gsutil -m rsync -r -d \
  ~/lagazzettadikyiv/public/ gs://www.lagazzettadikyiv.com/
```

## Current Pipeline State (June 2026)

- Hashed assets: DISABLED (all HTML references `./styles.css` directly)
- `build_hashed_assets.py`: exists but not in `deploy_routine.sh`
- `deploy_routine.sh`: NOT active in crontab (commented out, awaiting activation after Phase 2 approval)
- 16/21 HTML files use shared header/footer via `build_site.py` sentinel injection
- `shipit.sh` GCLOUD_DIR: fixed to `~/lagazzettadikyiv/devvit/google-cloud-sdk`
- `build_site.py`: fixed encoding declaration for Python 3
