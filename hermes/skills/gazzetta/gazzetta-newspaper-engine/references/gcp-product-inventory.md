# GCP Product Inventory — La Gazzetta di Kyiv

Last audited: 2026-06-16. All resources in `europe-west1`, project `project-e5e0244c-b94d-41a1-810`, account `pureciclismo@gmail.com`.

## Cloud Run Jobs (7 active)

| Job | Schedule (Cloud Scheduler) | Purpose | Image |
|-----|---------------------------|---------|-------|
| `gazzetta-pipeline` | `*/10 * * * *` | Core pipeline: download DB, fetch intel, bulk approve, db_to_json, build site, test gate, GCS sync | `gazzetta-pipeline:latest` |
| `cco-distributor` | `*/30 * * * *` | Content distribution: curate top stories, post to Telegram, Reddit drafts, X drafts | `gazzetta-agents:latest` |
| `cdo-auditor` | `0 */2 * * *` | Design compliance audit: Playwright visual checks, token validation, 3 breakpoints | `gazzetta-agents:latest` |
| `memory-synthesizer` | `0 2 * * *` | Agent memory synthesis into persistent context | `gazzetta-agents:latest` |
| `cco-newsletter-daily` | `0 6 * * *` | Daily newsletter draft generation | `gazzetta-agents:latest` |
| `cco-newsletter-weekly` | `0 6 * * 1` | Weekly newsletter draft (Mondays) | `gazzetta-agents:latest` |
| `gazzetta-rd-sweep-weekly` | `15 6 * * 1` | Weekly Reddit content sweep (Mondays) | `gazzetta-rd-agent:latest` |

## Cloud Scheduler (7 cron triggers)

All HTTP-targeted, all `europe-west1`, all ENABLED. One-to-one mapping with Cloud Run jobs above.

## Cloud Storage (1 bucket)

- **Bucket:** `gs://www.lagazzettadikyiv.com`
- **Role:** Full static website hosting (HTML, CSS, JS, data JSON, API endpoints)
- **Lifecycle rule:** Auto-delete objects older than 30 days
- **Cache-Control:** HTML = `no-cache`, JSON = `no-store`, CSS/JS = `immutable`

## Artifact Registry (1 repository)

- **Repository:** `gazzetta-docker` (Docker format, `europe-west1`)
- **Images:**
  - `gazzetta-pipeline` — `:latest` + ~15 back-revisions (~75MB each)
  - `gazzetta-agents` — `:latest` + ~11 back-revisions (~530MB each, includes Playwright + Chromium)
  - `gazzetta-rd-agent` — `:latest` + 0 revisions (~100MB)
  - `chief-architect` — `:latest` + 2 revisions (ORPHANED — Cloud Run service deleted June 2026)

## Secret Manager (2 secrets)

| Secret | Created | Purpose |
|--------|---------|---------|
| `deepseek-api-key` | 2026-06-12 | DeepSeek API key for editorial AI pipeline |
| `telegram-bot-token` | 2026-06-12 | Telegram Bot API token for CCO distribution |

## Authentication

Credentials stored in `~/.config/gcloud/credentials.db`. Authenticated gcloud/gsutil path: `~/lagazzettadikyiv/devvit/google-cloud-sdk/bin/`. The pip-installed gsutil in Hermes venv has no write access (returns 401).

## Quick Health Check

```bash
GCLOUD=~/lagazzettadikyiv/devvit/google-cloud-sdk/bin/gcloud
REGION=europe-west1
PROJECT=project-e5e0244c-b94d-41a1-810

# All Cloud Run jobs
$GCLOUD run jobs list --region=$REGION

# All Cloud Scheduler triggers
$GCLOUD scheduler jobs list --location=$REGION

# Latest pipeline execution
$GCLOUD run jobs executions list --job=gazzetta-pipeline --region=$REGION --limit=1

# All Docker images
$GCLOUD artifacts docker images list europe-west1-docker.pkg.dev/$PROJECT/gazzetta-docker --include-tags
```
