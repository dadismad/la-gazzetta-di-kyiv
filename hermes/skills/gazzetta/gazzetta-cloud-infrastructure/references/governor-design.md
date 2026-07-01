# Cloud Governor Design — Gazzetta di Kyiv

## What It Is

`governor.py` is a single Python script (~150 lines) that runs as a systemd timer on the Cloud Brain VM. It orchestrates the newspaper pipeline, self-heals on errors, deploys to GCS when tests pass, and reports to Alex via Telegram.

## What It Is NOT

- NOT a chat interface (no Telegram bot on VM)
- NOT an AI that edits code
- NOT an asyncio daemon (sequential, not concurrent)
- NOT a replacement for Local Hermes

## Operational Loop

```
Every 30 minutes (systemd timer):
  │
  ├─ 1. Lock check ── is another instance running? If yes, skip.
  │
  ├─ 2. fetch_intel.py ── ingest news → SQLite
  │     If fail: log, retry once after 60s delay
  │     If retry fails: alert Alex, skip remaining stages, exit
  │
  ├─ 3. intel_to_stories.py ── raw intel → structured stories
  │     Same retry pattern
  │
  ├─ 4. Enrichment chain ── enrich_editorial → enrich_market → enrich_multi_persona
  │     Each script: retry once, skip on persistent failure
  │
  ├─ 5. decay_stories.py ── archive old, promote fresh
  │
  ├─ 6. validate_stories.py ── check required fields, repair missing
  │
  ├─ 7. generate_flows.py ── stories → capital flow extraction
  │
  ├─ 8. db_to_json.py ── compile SQLite → 6-container stories.json
  │     If fail: alert Alex (critical), skip deploy, exit
  │
  ├─ 9. test_platform.py ── QA gate (BLOCKING)
  │     If fail: alert Alex with failure summary, skip deploy, exit
  │
  ├─ 10. Deploy ── shipit_cloud.py → GCS rsync
  │     If fail: alert Alex
  │
  └─ 11. Report ── Telegram summary to Alex
        "Governor tick 14:00 UTC. 377 stories, 6 containers. GCS synced. No errors."
```

## Error Handling Matrix

| Error Type | Governor Response |
|-----------|-------------------|
| Script not found (exit 2) | Alert Alex immediately — VM needs code deploy |
| DB locked (exit 1) | Wait 30s, retry once |
| yfinance timeout | Log, skip that ticker, continue |
| DeepSeek timeout | Retry once with backoff, skip enrichment if persists |
| test_platform failure | Alert Alex, skip deploy, preserve last good site |
| gsutil 403 | Alert Alex — auth needs fix |
| All stages pass | Deploy + success report |

## Telegram Report Format

**Success:**
```
Governor | 14:00 UTC
Stories: 377 (Monetary 82, Energy 40, Tech 102, Info 5, Bio 8, Flash 140)
Flows: 199 | Market data: fresh (10:46 UTC)
GCS: synced ✓ | Tests: all passed
Next tick: 14:30 UTC
```

**Failure:**
```
Governor | 14:00 UTC — ATTENTION
Stage 8 (db_to_json.py) FAILED
Error: sqlite3.OperationalError: database is locked
Retry: FAILED after 60s wait
GCS: NOT DEPLOYED — site preserved at last good state
Action needed: Check VM DB locks. Manual gcloud ssh required.
```

## Systemd Service Definition

```ini
[Unit]
Description=Gazzetta di Kyiv — Cloud Governor (30m pipeline)
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/opt/gazzetta-di-kyiv
ExecStart=/opt/gazzetta-di-kyiv/.venv/bin/python governor.py
User=alexstocchi
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```ini
[Unit]
Description=Gazzetta Governor Timer (every 30 min)

[Timer]
OnCalendar=*:0/30
Persistent=true

[Install]
WantedBy=timers.target
```

## Startup Sequence

```bash
# On VM after SCP:
sudo cp governor.service governor.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable governor.timer
sudo systemctl start governor.timer

# Verify:
sudo systemctl status governor.timer
sudo journalctl -u governor.service -f
```

## Interaction with Local Hermes

- Governor reports TO Telegram, never reads FROM Telegram
- Local Hermes reads Governor reports and can SSH in to fix issues
- Governor never initiates conversation — it's a reporter, not a chat partner
- If Alex wants to pause the Governor: `sudo systemctl stop governor.timer`
- If Alex wants to trigger immediately: `sudo systemctl start governor.service`
