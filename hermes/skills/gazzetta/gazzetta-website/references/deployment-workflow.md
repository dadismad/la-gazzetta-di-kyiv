# Gazzetta Deployment Workflow — Block B Reference

Session date: 2026-06-16. Block B: Docker build, Cloud Run update, deploy.

## Pre-Flight Checklist

1. **All 7 schedulers PAUSED** (europe-west1, -cron suffix):
   ```
   gcloud scheduler jobs pause <name>-cron --location=europe-west1
   ```
   Jobs: cco-distributor-cron, cco-newsletter-daily-cron, cco-newsletter-weekly-cron, 
   memory-synthesizer-cron, gazzetta-rd-sweep-weekly-cron, cdo-auditor-cron, gazzetta-pipeline-cron

2. **gcloud SDK path**: `~/lagazzettadikyiv/devvit/google-cloud-sdk/bin/gcloud`
   - Account: pureciclismo@gmail.com
   - Project: `project-e5e0244c-b94d-41a1-810` (NOT the number 397576418262)
   - Region: europe-west1

## Docker Build

Artifact Registry path (NOT gcr.io):
```
europe-west1-docker.pkg.dev/project-e5e0244c-b94d-41a1-810/gazzetta-docker/gazzetta-pipeline
```

**Build command:**
```bash
gcloud builds submit \
  --tag europe-west1-docker.pkg.dev/project-e5e0244c-b94d-41a1-810/gazzetta-docker/gazzetta-pipeline:latest \
  --project=project-e5e0244c-b94d-41a1-810
```

**Discovery**: If you don't know the registry, check:
```bash
gcloud artifacts repositories list --project=project-e5e0244c-b94d-41a1-810
gcloud run jobs describe gazzetta-pipeline --region=europe-west1 --project=project-e5e0244c-b94d-41a1-810 --format=json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['spec']['template']['spec']['template']['spec']['containers'][0]['image'])"
```

## CRITICAL: DB Migration → GCS Upload BEFORE Pipeline

**Pitfall**: After any `gazzetta.db` schema change (new tables, new columns, ALTER TABLE), the Cloud Run pipeline downloads DB FROM GCS. If GCS has the old schema, `db_to_json.py` fails with `sqlite3.OperationalError: no such table: X`.

**Fix sequence**:
```bash
# 1. Run migration on local DB
python3 scripts/migrate_db.py

# 2. Upload migrated DB to GCS BEFORE executing pipeline
gsutil cp gazzetta.db gs://www.lagazzettadikyiv.com/gazzetta.db

# 3. Now execute pipeline
gcloud run jobs execute gazzetta-pipeline --region=europe-west1 --project=project-e5e0244c-b94d-41a1-810 --wait
```

**Symptom of stale DB**: Pipeline log shows `sqlite3.OperationalError: no such table: <table_name>` at db_to_json stage, then `ABORT: db_to_json.py FAILED`, then `Skipping GCS upload — pipeline failed`.

## Cloud Run Job Update + Execute

```bash
# Update with sha256 digest (forces new image pull):
gcloud run jobs update gazzetta-pipeline --region=europe-west1 --project=project-e5e0244c-b94d-41a1-810 --image=europe-west1-docker.pkg.dev/project-e5e0244c-b94d-41a1-810/gazzetta-docker/gazzetta-pipeline@sha256:<digest>

# Execute with --wait (blocks until done):
gcloud run jobs execute gazzetta-pipeline --region=europe-west1 --project=project-e5e0244c-b94d-41a1-810 --wait
```

## Pipeline Log Retrieval

```bash
EXEC_NAME="gazzetta-pipeline-<suffix>"
gcloud logging read \
  "resource.type=cloud_run_job AND resource.labels.job_name=gazzetta-pipeline AND labels.\"run.googleapis.com/execution_name\"=$EXEC_NAME" \
  --project=project-e5e0244c-b94d-41a1-810 \
  --limit=50 --format="value(textPayload)"
```

Key log lines to look for: `Container called exit(0)` = success, `Container called exit(1)` = failure. Stage markers: `Stage 1: db_to_json`, `Stage 2: build_site`, `Stage 2.1: hashing`, `Stage 2.5: test_platform`, `Synced N files`.

## Post-Deploy Verification

After pipeline success:
1. Browser: load `https://www.lagazzettadikyiv.com` — verify 6 containers render
2. Log: verify `All tests passed — PASS: 88 FAIL: 0`
3. Log: verify `Synced N files from public/ to GCS`
4. Re-enable `gazzetta-pipeline-cron` scheduler if desired
