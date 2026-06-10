# Gazzetta di Kyiv — Cloud Migration Manifest
## Moving from laptop to Google Cloud Always Free ($0.00/mo)

---

### Target Architecture

```
┌─────────────────────────────────────────────┐
│  Google Cloud VM: e2-micro (Always Free)    │
│  Region: us-central1 (Iowa)                 │
│  OS: Debian 12 (Bookworm)                   │
│  Disk: 30GB persistent (Always Free)        │
│                                              │
│  ┌─────────────────────────────────────┐    │
│  │  /opt/gazzetta-di-kyiv/              │    │
│  │  ├── .venv/         (Python 3.11)    │    │
│  │  ├── gazzetta.db    (SQLite)         │    │
│  │  ├── scripts/       (pipeline)       │    │
│  │  ├── data/          (source truth)   │    │
│  │  ├── site/          (built output)   │    │
│  │  └── config.yaml                     │    │
│  └─────────────────────────────────────┘    │
│                                              │
│  ┌─────────────────────────────────────┐    │
│  │  systemd timers (replaces Hermes cron)│   │
│  │  ├── gazzetta-intel.timer   (30m)    │    │
│  │  ├── gazzetta-pipeline.timer (60m)  │    │
│  │  ├── gazzetta-marketdata.timer (6h) │    │
│  │  ├── gazzetta-translate.timer (3h)  │    │
│  │  └── gazzetta-shipit.timer (60m)    │    │
│  └─────────────────────────────────────┘    │
│                                              │
│  ┌─────────────────────────────────────┐    │
│  │  GCS bucket (same as current)        │    │
│  │  gs://www.lagazzettadikyiv.com       │    │
│  │  ←--- shipit.sh syncs here           │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### Monthly Cost: $0.00

| Resource | Always Free quota | Usage | Status |
|----------|-------------------|-------|--------|
| e2-micro VM | 1 instance | 1 instance | ✓ Free |
| Compute Engine | 30GB-month storage | 30GB boot disk | ✓ Free |
| Network egress | 1GB/month | ~500MB (site to GCS) | ✓ Free |
| GCS storage | 5GB-month | ~2MB | ✓ Free |
| GCS operations | 5000 Class A/month | ~2000 | ✓ Free |
| Cloud CDN | Not in Always Free | Disabled (GCS direct) | ✓ Free |

### Step-by-Step Migration

#### Step 1: Create the VM
```bash
gcloud compute instances create gazzetta-prod \
  --zone=us-central1-a \
  --machine-type=e2-micro \
  --boot-disk-size=30GB \
  --boot-disk-type=pd-standard \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --tags=http-server,https-server \
  --metadata=startup-script='#!/bin/bash
    apt-get update && apt-get install -y python3.11 python3.11-venv git curl sqlite3
    python3.11 -m venv /opt/gazzetta-di-kyiv/.venv
    /opt/gazzetta-di-kyiv/.venv/bin/pip install yfinance pyyaml requests beautifulsoup4 deepseek-sdk
    git clone https://github.com/pureciclismo/gazzetta-di-kyiv.git /opt/gazzetta-di-kyiv
  '
```

#### Step 2: Migrate the Database
```bash
# From laptop:
gcloud compute scp ~/projects/gazzetta-di-kyiv/gazzetta.db \
  gazzetta-prod:/opt/gazzetta-di-kyiv/

# Also migrate config and env
gcloud compute scp ~/projects/gazzetta-di-kyiv/config.yaml \
  gazzetta-prod:/opt/gazzetta-di-kyiv/
gcloud compute scp ~/projects/gazzetta-di-kyiv/.env \
  gazzetta-prod:/opt/gazzetta-di-kyiv/
```

#### Step 3: Create systemd Service Units

**`/etc/systemd/system/gazzetta-intel.service`:**
```ini
[Unit]
Description=Gazzetta di Kyiv — Intel Collection
After=network-online.target

[Service]
Type=oneshot
User=gazzetta
WorkingDirectory=/opt/gazzetta-di-kyiv
Environment=PATH=/opt/gazzetta-di-kyiv/.venv/bin:/usr/local/bin:/usr/bin:/bin
EnvironmentFile=/opt/gazzetta-di-kyiv/.env
ExecStart=/opt/gazzetta-di-kyiv/.venv/bin/python scripts/fetch_intel.py
```

**`/etc/systemd/system/gazzetta-intel.timer`:**
```ini
[Unit]
Description=Gazzetta di Kyiv — Intel Collection Timer

[Timer]
OnCalendar=*:0/30
Persistent=true
RandomizedDelaySec=60

[Install]
WantedBy=timers.target
```

Repeat the pattern for: `gazzetta-pipeline` (60m), `gazzetta-marketdata` (6h), `gazzetta-translate` (3h), `gazzetta-shipit` (60m but staggered 15m after pipeline).

#### Step 4: Enable and Start
```bash
gcloud compute ssh gazzetta-prod -- "
  sudo systemctl daemon-reload
  sudo systemctl enable gazzetta-intel.timer gazzetta-pipeline.timer \
    gazzetta-marketdata.timer gazzetta-translate.timer gazzetta-shipit.timer
  sudo systemctl start gazzetta-intel.timer gazzetta-pipeline.timer \
    gazzetta-marketdata.timer gazzetta-translate.timer gazzetta-shipit.timer
"
```

#### Step 5: Daily GCS Backup
```bash
# Cron on VM (systemd timer):
# 0 3 * * * gsutil cp /opt/gazzetta-di-kyiv/gazzetta.db \
#   gs://www.lagazzettadikyiv.com/backups/gazzetta-$(date +%Y%m%d).db
```

#### Step 6: Cutover
1. Pause laptop cron jobs: `hermes cronjob pause <job_id>` for all 18 jobs
2. Verify VM is producing data: `gcloud compute ssh gazzetta-prod -- "ls -la /opt/gazzetta-di-kyiv/data/"`
3. Verify GCS sync: `gsutil ls -l gs://www.lagazzettadikyiv.com/index.html`
4. Verify HTTPS: `curl -sI https://www.lagazzettadikyiv.com | head -3`
5. Remove laptop cron jobs entirely

### Monitoring

```bash
# Check service health
gcloud compute ssh gazzetta-prod -- "systemctl status gazzetta-*.timer"

# Check disk usage (Always Free: 30GB limit)
gcloud compute ssh gazzetta-prod -- "df -h /"

# Check CPU/memory
gcloud compute ssh gazzetta-prod -- "top -bn1 | head -5"
```

### Disaster Recovery

1. GCS bucket has full site backup (every shipit uploads everything)
2. Database backup daily to GCS
3. Git history on GitHub (repo is public)
4. Rebuild VM from scratch in 15 minutes using startup script

### Migration Decision Matrix

| Factor | Laptop | Cloud VM |
|--------|--------|----------|
| Uptime | Sleep/wake, wifi | 24/7 |
| Cron reliability | Depends on Hermes | systemd (Linux native) |
| Cost | $0 | $0 |
| Storage | Unlimited | 30GB (sufficient) |
| Latency | Local | +30ms to GCS |
| Maintenance | Manual updates | apt auto-updates |
| Backup risk | Single laptop failure | GCS + GitHub |

**Verdict: MIGRATE.** Zero cost increase, significant reliability gain, removes single-laptop point of failure.
