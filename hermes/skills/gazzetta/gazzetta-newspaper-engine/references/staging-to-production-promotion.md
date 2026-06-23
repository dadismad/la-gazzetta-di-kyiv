# Staging-to-Production Promotion Workflow

Atomic promotion sequence for deploying Phase changes from staging to production. Used for Phase A (trust foundation) and Phase B (WCAG contrast) — the same pattern applies for all UI/data pipeline promotions.

## When to Use

- A staging feature has passed the 102-test gate and is ready for production
- The change involves `build_frontend_staging.py` (UI) or `contradiction_synthesizer.py` (data pipeline)
- Promotion must be atomic: no partial deploys, no manual GCS edits

## Promotion Sequence

### Phase 1: Local Promotion

```bash
# 1. Copy staging compiler over production
cp scripts/build_frontend_staging.py scripts/build_frontend.py

# 2. Fix output path: index_staging.html → index.html
# Use byte-level replacement (NOT patch tool — escape sequences fail):
python3 -c "
with open('scripts/build_frontend.py', 'rb') as f:
    raw = f.read()
raw = raw.replace(b'index_staging.html', b'index.html')
with open('scripts/build_frontend.py', 'wb') as f:
    f.write(raw)
"

# 3. Rebuild production locally to verify
GAZZETTA_HOME=$(pwd) python3 scripts/build_frontend.py
```

### Phase 2: SCP to VM

```bash
GSDK=devvit/google-cloud-sdk/bin

# SCP to home directory (NOT directly to /opt/ — permission denied)
$GSDK/gcloud compute scp scripts/build_frontend.py gazzetta-prod:~ --zone=us-central1-a
$GSDK/gcloud compute scp scripts/build_frontend_staging.py gazzetta-prod:~ --zone=us-central1-a

# If data pipeline changed too:
$GSDK/gcloud compute scp scripts/contradiction_synthesizer.py gazzetta-prod:~ --zone=us-central1-a
```

### Phase 3: Remote Rebuild + Deploy

```bash
$GSDK/gcloud compute ssh gazzetta-prod --zone=us-central1-a --command="
sudo mv ~/build_frontend.py /opt/gazzetta-di-kyiv/scripts/build_frontend.py &&
sudo mv ~/build_frontend_staging.py /opt/gazzetta-di-kyiv/scripts/build_frontend_staging.py &&
sudo chown gazzetta:gazzetta /opt/gazzetta-di-kyiv/scripts/build_frontend*.py &&
cd /opt/gazzetta-di-kyiv &&
python3 scripts/build_frontend.py &&
python3 scripts/test_platform.py | tail -4 &&
gsutil cp public/index.html gs://www.lagazzettadikyiv.com/index.html
"
```

### Phase 4: CDN Invalidation

```bash
$GSDK/gcloud compute ssh gazzetta-prod --zone=us-central1-a --command="
gcloud compute url-maps invalidate-cdn-cache gazzetta-url-map --path='/*' --async
"
```

### Phase 5: Verify Live

```bash
# Check markers in live domain (not GCS — CDN may be stale)
curl -s https://www.lagazzettadikyiv.com/ | grep -c 'new-marker'

# Cross-check: GCS file vs CDN file must match
curl -sI https://www.lagazzettadikyiv.com/ | grep content-length
# Must equal: gsutil stat gs://www.lagazzettadikyiv.com/index.html | grep Content-Length
```

## Pitfalls

1. **SCP directly to `/opt/gazzetta-di-kyiv/` fails** — files owned by `gazzetta:gazzetta`. SCP to `~` then `sudo mv`.
2. **Forgetting to fix output path** — staging writes `index_staging.html`, production must write `index.html`.
3. **CDN cache hides success** — `gsutil cp` reports success but `curl` returns old content. Always invalidate CDN after deploy.
4. **`patch` tool fails on JS-in-Python strings** — fall back to byte-level replacement via Python `rb`/`wb` mode.
5. **`read_file` with offset/limit returns line-numbered output** — never write this back to disk. Use `execute_code` with Python's `open()` for byte-level reads.
6. **Cloud CDN fronts the bucket** — `gcloud compute backend-buckets list` shows `ENABLE_CDN: True`. CDN caches independently of GCS object Cache-Control headers. Invalidation is mandatory.

## Governor Automation (C3)

The governor's deploy step now handles CDN invalidation automatically every 10-minute cycle:

```python
# In governor.py STEPS list:
("deploy", ["bash", "-c", 
    "gsutil -h 'Cache-Control:public,max-age=300' cp " + str(PUBLIC) + 
    "/index.html gs://www.lagazzettadikyiv.com/index.html && "
    "gsutil -m rsync -r -x index.html -d " + str(PUBLIC) + 
    "/ gs://www.lagazzettadikyiv.com/ && "
    "gcloud compute url-maps invalidate-cdn-cache gazzetta-url-map "
    "--path='/*' --async"
], 120, False),
```

300s TTL allows CDN edge caching for cost savings. The `--async` invalidation fires without blocking the governor cycle.
