# Cloud Brain Provisioning — Gazzetta di Kyiv

## VM Creation

```bash
GSDK=~/lagazzettadikyiv/google-cloud-sdk/bin

$GSDK/gcloud compute instances create gazzetta-prod \
  --zone=us-central1-a \
  --machine-type=e2-micro \
  --boot-disk-size=30GB \
  --boot-disk-type=pd-standard \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --tags=http-server,https-server \
  --metadata=startup-script='#!/bin/bash
    apt-get update -qq && apt-get install -y -qq python3.11 python3.11-venv git curl sqlite3
    python3.11 -m venv /opt/gazzetta-di-kyiv/.venv
    /opt/gazzetta-di-kyiv/.venv/bin/pip install -q yfinance pyyaml requests
    git clone https://github.com/pureciclismo/gazzetta-di-kyiv.git /opt/gazzetta-di-kyiv
    chown -R root:root /opt/gazzetta-di-kyiv
  '
```

## Upload Database & Config

```bash
$GSDK/gcloud compute ssh gazzetta-prod --zone=us-central1-a --command="sudo chown -R \$USER:\$USER /opt/gazzetta-di-kyiv"
$GSDK/gcloud compute scp gazzetta.db gazzetta-prod:/opt/gazzetta-di-kyiv/ --zone=us-central1-a
$GSDK/gcloud compute scp config.yaml gazzetta-prod:/opt/gazzetta-di-kyiv/ --zone=us-central1-a
$GSDK/gcloud compute scp -r scripts/ gazzetta-prod:/opt/gazzetta-di-kyiv/ --zone=us-central1-a
```

## Systemd Timer Setup

Four timer files in `/etc/systemd/system/`:

1. **gazzetta-intel.service + .timer** — `ExecStart=/opt/gazzetta-di-kyiv/.venv/bin/python scripts/fetch_intel.py`
   Timer: `OnUnitActiveSec=30m, OnBootSec=2m`

2. **gazzetta-pipeline.service + .timer** — `ExecStart=/opt/gazzetta-di-kyiv/.venv/bin/python scripts/db_to_json.py`
   Timer: `OnUnitActiveSec=60m, OnBootSec=5m`

3. **gazzetta-marketdata.service + .timer** — `ExecStart=/opt/gazzetta-di-kyiv/.venv/bin/python scripts/fetch_market_data.py`
   Timer: `OnUnitActiveSec=6h, OnBootSec=10m`

4. **gazzetta-shipit.service + .timer** — `ExecStart=/opt/gazzetta-di-kyiv/.venv/bin/python scripts/shipit_cloud.py`
   Timer: `OnUnitActiveSec=60m, OnBootSec=15m`

All services: `Type=oneshot, WorkingDirectory=/opt/gazzetta-di-kyiv, User=alexstocchi`

Activate: `systemctl daemon-reload && systemctl enable gazzetta-*.timer && systemctl start gazzetta-*.timer`

## shipit_cloud.py

```python
#!/usr/bin/env python3
import subprocess, shutil, os
os.chdir('/opt/gazzetta-di-kyiv')
for f in ['stories.json', 'flows.json']:
    src = f'data/{f}'; dst = f'site/data/{f}'
    if os.path.exists(src): shutil.copy(src, dst)
subprocess.run(['gsutil', '-m', 'rsync', '-d', '-r', 'site/', 'gs://www.lagazzettadikyiv.com/'], check=False)
```

## Post-Provisioning Verification (MANDATORY)

Run this checklist after EVERY provision or reprovision. The VM status can be `RUNNING` while all four timers fail silently.

### 1. Script presence

```bash
$GSDK/gcloud compute ssh gazzetta-prod --zone=us-central1-a --command="ls -la /opt/gazzetta-di-kyiv/scripts/"
```

Expected: `db_to_json.py`, `fetch_intel.py`, `fetch_market_data.py`, `shipit_cloud.py` all present.
If missing: `$GSDK/gcloud compute scp -r scripts/ gazzetta-prod:/opt/gazzetta-di-kyiv/ --zone=us-central1-a`

### 2. Database presence and row count

```bash
$GSDK/gcloud compute ssh gazzetta-prod --zone=us-central1-a --command="cd /opt/gazzetta-di-kyiv && sqlite3 -readonly gazzetta.db 'SELECT COUNT(*) FROM stories; SELECT COUNT(*) FROM flows'"
```

Use `-readonly` flag — the VM user may not have write permission on the db file.

### 3. Pipeline execution (dry run)

```bash
$GSDK/gcloud compute ssh gazzetta-prod --zone=us-central1-a --command="cd /opt/gazzetta-di-kyiv && .venv/bin/python scripts/db_to_json.py --data-only"
```

Must print container counts (>0). Exit code must be 0.

### 4. Pipeline journal — last 3 runs

```bash
$GSDK/gcloud compute ssh gazzetta-prod --zone=us-central1-a --command="sudo journalctl -u gazzetta-pipeline --no-pager -n 15"
```

Look for `can't open file` (missing script), `OperationalError` (db issue), or any non-zero exit.
If every run shows `can't open file 'scripts/db_to_json.py'` → step 1 was missed.

### 5. Shipit journal — GCS auth

```bash
$GSDK/gcloud compute ssh gazzetta-prod --zone=us-central1-a --command="sudo journalctl -u gazzetta-shipit --no-pager -n 20 | grep -c 'AccessDeniedException'"
```

If >0: gsutil auth scope mismatch. The VM service account needs `storage.objects.delete` and `storage.objects.create` on the GCS bucket. Check GCP Console → IAM → VM service account → roles.

### 6. Live site data freshness

```bash
curl -s https://www.lagazzettadikyiv.com/data/stories.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'generated_at: {d.get(\"generated_at\")}'); print(f'stories: {len(d.get(\"stories\",d.get(\"all_stories\",[])))}')"
curl -s https://www.lagazzettadikyiv.com/data/flows.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'generated_at: {d.get(\"generated_at\")}'); print(f'flows: {len(d.get(\"flows\",[]))}')"
```

`generated_at` must be <2h old. Story count must be >0.

## Health Check

```bash
$GSDK/gcloud compute instances describe gazzetta-prod --zone=us-central1-a --format='value(status)'
$GSDK/gcloud compute ssh gazzetta-prod --zone=us-central1-a --command="systemctl list-timers --no-pager | grep gazzetta"
```

## Monthly Cost: $0.00 (Always Free Tier)
