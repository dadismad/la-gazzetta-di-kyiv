# Gazzetta di Kyiv — Cloud Migration Manifest
## Google Cloud Compute Engine (Always Free Tier)

### Current State
- **Host**: macOS laptop (Alex's machine)
- **Data**: SQLite (gazzetta.db), JSON files
- **Deploy**: GCS static website + Cloud CDN
- **Cron**: Hermes Agent scheduler (laptop must be online)

### Target State
- **Host**: GCP Compute Engine e2-micro VM (Always Free: 1 vCPU, 1GB RAM, 30GB disk)
- **Data**: SQLite (gazzetta.db) + Cloud Storage sync
- **Deploy**: Same GCS pipeline
- **Cron**: systemd timers on the VM (no laptop dependency)

---

## Migration Steps

### Step 1: Create VM Instance

```bash
gcloud compute instances create gazzetta-prod \
  --zone=us-central1-a \
  --machine-type=e2-micro \
  --boot-disk-size=30GB \
  --boot-disk-type=pd-standard \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --tags=http-server,https-server
```

### Step 2: SSH into VM and Install Dependencies

```bash
gcloud compute ssh gazzetta-prod --zone=us-central1-a

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python + deps
sudo apt install -y python3 python3-pip python3-venv git

# Clone repo
git clone https://github.com/pureciclismo/gazzetta-di-kyiv.git ~/gazzetta-di-kyiv
cd ~/gazzetta-di-kyiv

# Setup venv
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Install gcloud SDK (for GCS deploy)
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-xxx-linux-x86_64.tar.gz
tar -xf google-cloud-sdk-*.tar.gz
./google-cloud-sdk/install.sh
```

### Step 3: Migrate Database

```bash
# On laptop:
gcloud compute scp ~/projects/gazzetta-di-kyiv/gazzetta.db gazzetta-prod:~/gazzetta-di-kyiv/

# On VM: verify
sqlite3 ~/gazzetta-di-kyiv/gazzetta.db "SELECT COUNT(*) FROM stories;"
```

### Step 4: Setup systemd Timers (Replace Hermes Cron)

Create `/etc/systemd/system/gazzetta-pipeline.service`:
```ini
[Unit]
Description=Gazzetta di Kyiv Pipeline
After=network.target

[Service]
Type=oneshot
User=YOUR_USER
WorkingDirectory=/home/YOUR_USER/gazzetta-di-kyiv
ExecStart=/home/YOUR_USER/gazzetta-di-kyiv/.venv/bin/python scripts/db_to_json.py
ExecStart=/home/YOUR_USER/gazzetta-di-kyiv/.venv/bin/python scripts/generate_flows.py
ExecStart=/home/YOUR_USER/gazzetta-di-kyiv/.venv/bin/python scripts/fetch_market_data.py
ExecStart=/bin/bash /home/YOUR_USER/gazzetta-di-kyiv/shipit.sh
```

Create `/etc/systemd/system/gazzetta-pipeline.timer`:
```ini
[Unit]
Description=Gazzetta Pipeline Timer (every 60 min)
Requires=gazzetta-pipeline.service

[Timer]
OnCalendar=*:0/60
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
sudo systemctl enable gazzetta-pipeline.timer
sudo systemctl start gazzetta-pipeline.timer
```

### Step 5: Firewall & Monitoring

```bash
# Allow HTTP/HTTPS
gcloud compute firewall-rules create allow-http --allow tcp:80
gcloud compute firewall-rules create allow-https --allow tcp:443

# Setup Cloud Monitoring
gcloud compute instances add-tags gazzetta-prod --tags=monitoring
```

### Step 6: Backup Strategy

```bash
# Daily backup to GCS
cat > ~/gazzetta-di-kyiv/scripts/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
gsutil cp gazzetta.db gs://www.lagazzettadikyiv.com/backups/gazzetta-$DATE.db
gsutil cp data/stories.json gs://www.lagazzettadikyiv.com/backups/stories-$DATE.json
EOF
chmod +x ~/gazzetta-di-kyiv/scripts/backup.sh
```

---

## Always Free Tier Limits (Staying Within)

| Resource | Limit | Gazzetta Usage | Status |
|----------|-------|---------------|--------|
| Compute Engine e2-micro | 1 instance | 1 | ✓ |
| Disk | 30 GB | ~5 GB | ✓ |
| Cloud Storage | 5 GB | ~5.2 MB | ✓ |
| Network egress | 1 GB/month | ~50 MB | ✓ |
| Cloud Functions | 2M invocations | 0 (systemd instead) | ✓ |

**Estimated monthly cost: $0.00** (fully within Always Free tier)

---

## Migration Checklist

- [ ] Create e2-micro VM in us-central1-a
- [ ] Install Python 3.11+, git, gcloud SDK
- [ ] Clone repo + setup venv
- [ ] Copy gazzetta.db to VM
- [ ] Setup systemd timers for pipeline + deploy
- [ ] Configure GCS auth (service account or gcloud auth)
- [ ] Test manual pipeline run
- [ ] Verify site deploys from VM
- [ ] Setup backup cron
- [ ] Decommission laptop crons after 48h parallel run
