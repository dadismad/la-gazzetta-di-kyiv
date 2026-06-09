# Deployment — Gazzetta di Kyiv

> Infrastructure, CI/CD, GCS sync, and repo structure.

## Production Host

- **Provider**: Google Cloud Storage
- **Bucket**: gs://www.lagazzettadikyiv.com
- **Live URL**: https://www.lagazzettadikyiv.com
- **Auth**: gcloud SDK, pureciclismo@gmail.com
- **Deploy Command**: gsutil rsync site/ gs://www.lagazzettadikyiv.com

## Deploy Schedule

- **Cron**: gazzetta-deploy-to-gcs (every 15 minutes)
- **Type**: no_agent Script (~/.hermes/scripts/gazzetta_deploy_to_gcs.sh)
- **Objects**: 42 objects synced per deploy
- **Failure Mode**: Auth expiry, bucket inaccessible, disk full. No retry. No alert.

## CI/CD (GitHub Actions)

- **File**: .github/workflows/deploy.yml
- **Trigger**: Push to main branch (manual dispatch also)
- **Path**: site/ directory
- **Platform**: GitHub Pages
- **Permissions**: contents: read, pages: write, id-token: write

## Local Development

- **Canonical Path**: /Users/alexstocchi/projects/gazzetta-di-kyiv
- **Ghost Path**: ~/.hermes/hermes-agent/gazzetta-di-kyiv (symlink to canonical)
- **Version Control**: Git at canonical path. Push to pureciclismo/gazzetta-di-kyiv daily.

## Directory Structure

gazzetta-di-kyiv/
+-- docs/        Governance and operations documentation
+-- scripts/     Pipeline Python and Bash scripts
+-- data/        Source data (pipeline input)
+-- site/        Deploy target (synced to GCS)
+-- api/         JSON schemas
+-- ops/         Operational tools (watchdogs, auditors)
+-- .github/     CI/CD workflows
