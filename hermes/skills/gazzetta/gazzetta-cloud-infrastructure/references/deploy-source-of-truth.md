# Deploy Source of Truth — VM-First Architecture

## The Rule

The VM's `/opt/gazzetta-di-kyiv/public/` directory is the sole source of truth for all production assets. Every file that reaches GCS must pass through the VM first. Direct `gsutil cp` from local to GCS is temporary at best — the governor's `rsync -r -d` will destroy it within 10 minutes.

## Why Direct GCS Deploys Fail

The governor deploy step uses:
```bash
gsutil -m rsync -r -d /opt/gazzetta-di-kyiv/public/ gs://www.lagazzettadikyiv.com/
```

The `-d` flag means DELETE mode: any file on GCS that does not exist in the VM's `public/` directory is removed. This includes:
- Files you uploaded directly with `gsutil cp file gs://BUCKET/path`
- Versioned files like `flows.json` and `living_stories.json` deployed outside the rsync flow
- Any staging content not present in `public/`

## The Hallucination Trap

The failure mode is insidious:
1. You `gsutil cp file.html gs://BUCKET/index.html` — it succeeds, returns "Operation completed"
2. You `curl -sI https://www.lagazzettadikyiv.com/index.html` — returns 200
3. You tell the user "deployed successfully"
4. 10 minutes later, the governor rsync cycle runs and overwrites your file with the VM's copy
5. User checks the site — it's broken/stale
6. You've hallucinated success and lost credibility

## The Correct Deploy Sequence

```
LOCAL                    VM                          GCS
  │                       │                           │
  │  scp file to /tmp/    │                           │
  ├──────────────────────>│                           │
  │                       │ sudo cp to public/        │
  │                       │ sudo chown gazzetta:       │
  │                       │                           │
  │                       │ governor rsync (next tick) │
  │                       ├──────────────────────────>│
  │                       │                           │
  │  verify via browser   │                           │
  │  getComputedStyle()   │                           │
```

## Verification Sequence (Mandatory)

After any deploy, verify ALL three levels:

1. **VM**: `ssh ... "head -3 /opt/gazzetta-di-kyiv/public/index.html"` — must show expected content
2. **GCS**: `curl -sI "https://www.lagazzettadikyiv.com/index.html"` — must return 200
3. **Browser**: `browser_console` with `getComputedStyle()` — must match expected values

Never claim success from gsutil output alone.

## SCP Permission Workaround

VM files are owned by `gazzetta:gazzetta`. The `alexstocchi` SSH user cannot write directly to `/opt/gazzetta-di-kyiv/public/`.

```bash
# DON'T:
scp file gazzetta-prod:/opt/gazzetta-di-kyiv/public/index.html  # Permission denied

# DO:
scp file gazzetta-prod:/tmp/file
ssh gazzetta-prod "sudo cp /tmp/file /opt/gazzetta-di-kyiv/public/ && sudo chown gazzetta:gazzetta /opt/gazzetta-di-kyiv/public/file"
```

## The Governor Environment

The governor service runs as `gazzetta` user (from systemd service file `User=gazzetta`). It reads `.env` via `EnvironmentFile=/opt/gazzetta-di-kyiv/.env`. Key variables: `DEEPSEEK_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `ALPHAVANTAGE_API_KEY`.

## CDN Staleness + Deploy Step Harden (June 2026)

The CDN load balancer has `enableCdn: true` and caches responses with `max-age=3600`. Even when CDN is disabled on the backend bucket, the load balancer may cache. The old deploy step used plain `gsutil rsync -r -d` which inherited default cache headers from GCS objects.

**Fixed deploy step (in governor.py):**
```python
("deploy", ["bash", "-c",
    f"gsutil -h 'Cache-Control:no-cache,no-store,max-age=0' cp {PUBLIC}/index.html gs://BUCKET/index.html && "
    f"gsutil -m rsync -r -x 'index.html' -d {PUBLIC}/ gs://BUCKET/"],
    120, False),
```

Key changes:
1. `index.html` uploaded separately with `Cache-Control: no-cache,no-store,max-age=0`
2. Rsync uses `-x "index.html"` to exclude it — avoids overwriting the cache headers
3. All other assets (data/, robots.txt) still use default headers via rsync

**CDN invalidation (when cache is stuck):**
```bash
GSDK=~/lagazzettadikyiv/devvit/google-cloud-sdk/bin
$GSDK/gcloud compute url-maps invalidate-cdn-cache gazzetta-url-map --path "/*" --project=PROJECT
```

Invalidation can take 1-10 minutes to propagate.

## File Permission Gotcha (June 2026)

When files are compiled MANUALLY (via `ssh ... python3 build_frontend.py`), they're owned by `alexstocchi`. The systemd service runs as `gazzetta` user and CANNOT overwrite files owned by `alexstocchi`. This causes `PermissionError` on the next governor cycle.

**Fix after any manual compilation:**
```bash
sudo chown -R gazzetta:gazzetta /opt/gazzetta-di-kyiv/public/
sudo chmod -R 775 /opt/gazzetta-di-kyiv/public/
```

**Detection:** Governor logs show `PermissionError` at `build_frontend.py line 269` (the `open(out, "w")` call).

## Staging Isolation Pattern (June 2026)

For safe pre-production testing without disrupting the live site:

1. Create `build_frontend_staging.py` (copy of production compiler with changes)
2. It compiles to `public/index_staging.html` (NOT `index.html`)
3. Upload to GCS staging path for browser review
4. After verification, `cp build_frontend_staging.py build_frontend.py`
5. Fix output path from `index_staging.html` back to `index.html`
6. Next governor cycle picks it up

```bash
# On VM:
python3 scripts/build_frontend_staging.py  # writes index_staging.html
gsutil cp public/index_staging.html gs://BUCKET/staging/index_staging.html
# Review at: https://www.lagazzettadikyiv.com/staging/index_staging.html
# After approval:
cp scripts/build_frontend_staging.py scripts/build_frontend.py
# CRITICAL: fix output path in build_frontend.py (index_staging.html → index.html)
sudo chown gazzetta:gazzetta scripts/build_frontend.py
```
