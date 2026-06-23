# Cloud Scheduler Stall — Diagnostic & Recovery

## Symptom

Live website stops updating. GCS bucket shows data files with timestamps hours old. Cloud Run pipeline logs show no executions since the last successful run. The Cloud Scheduler job shows ENABLED but `scheduleTime` is stuck in the past.

## Root Cause

Cloud Scheduler's internal clock can freeze — the job remains ENABLED but stops advancing `scheduleTime`. The scheduler never invokes the HTTP target (Cloud Run job). No error logs are produced because the scheduler never attempts to fire. This is a GCP infrastructure-level stall, not a code failure.

## Detection

```bash
GCLOUD=~/lagazzettadikyiv/devvit/google-cloud-sdk/bin/gcloud
REGION=europe-west1

# 1. Check scheduler job state
$GCLOUD scheduler jobs describe gazzetta-pipeline-cron --location=$REGION

# Look for:
#   state: ENABLED (not PAUSED)
#   scheduleTime: <timestamp in the past>  <- STALL INDICATOR
#   lastAttemptTime: <timestamp hours ago> <- confirmation

# 2. Check Cloud Run job logs — confirm no recent executions
$GCLOUD logging read "resource.type=cloud_run_job AND resource.labels.job_name=gazzetta-pipeline" \
  --freshness=2h --limit=5

# If the last log entry is hours old and exit(0), the scheduler is stalled.

# 3. Confirm by checking GCS object timestamps
$GCLOUD/gsutil ls -l gs://www.lagazzettadikyiv.com/index.html
# Compare timestamp to current wall clock — staleness confirms the halt.
```

## Remediation

Pause and resume resets the scheduler's internal state:

```bash
$GCLOUD scheduler jobs pause gazzetta-pipeline-cron --location=$REGION
$GCLOUD scheduler jobs resume gazzetta-pipeline-cron --location=$REGION
```

If `scheduleTime` does not advance after pause/resume, force recalculation by changing the schedule temporarily:

```bash
$GCLOUD scheduler jobs update http gazzetta-pipeline-cron --location=$REGION --schedule="*/5 * * * *"
$GCLOUD scheduler jobs update http gazzetta-pipeline-cron --location=$REGION --schedule="*/10 * * * *"
```

For immediate execution (does not wait for the next `*/10` tick):

```bash
$GCLOUD scheduler jobs run gazzetta-pipeline-cron --location=$REGION
```

## Verification

After resume, `scheduleTime` should advance past current wall clock. Monitor for the next execution:

```bash
$GCLOUD scheduler jobs describe gazzetta-pipeline-cron --location=$REGION --format="yaml(scheduleTime)"
$GCLOUD logging read "resource.type=cloud_run_job AND resource.labels.job_name=gazzetta-pipeline" \
  --freshness=10m --limit=3
```

The Cloud Run pipeline (`deploy_routine.sh` via `cloud_entrypoint.py`) will execute on the next `*/10` tick and sync public/ to GCS.

## Reference Incidents

2026-06-16: Scheduler stalled at 12:00 UTC after a successful run (exit 0, 57 files synced). Site froze for 3+ hours. Pause/resume initially advanced `scheduleTime` from 12:10 to 12:20 but it remained stuck — the scheduler did not auto-fire until a manual `gcloud scheduler jobs run` was used. The schedule-change workaround (`*/5` then back to `*/10`) forced full recalculation. Manual trigger confirmed the pipeline was healthy. By 12:50, the automated cycle was self-sustaining again.

Key finding: pause/resume alone may not be sufficient if the scheduler's clock has drifted more than one cycle behind. Combine with schedule-change or manual run for guaranteed recovery.

## Pitfalls

- `gcloud scheduler jobs update` requires the job type: `http`, `pubsub`, or `app-engine`. Use `gcloud scheduler jobs update http gazzetta-pipeline-cron` — omitting `http` returns "Invalid choice."
- `gcloud run jobs executions list` is NOT a valid command for Cloud Run Jobs. Use `gcloud logging read` to inspect execution history.
- `gcloud scheduler jobs describe` may show stale `scheduleTime` for up to 60 seconds after pause/resume due to display caching. Check `lastAttemptTime` for confirmation of actual execution.
