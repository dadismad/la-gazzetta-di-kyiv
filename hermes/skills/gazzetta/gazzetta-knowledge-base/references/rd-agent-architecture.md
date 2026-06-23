# R&D Agent Architecture — Sprint 11 (June 2026)

Autonomous Research & Development Agent (Chief Research Officer) deployed as a
Cloud Run Job with weekly cadence. Self-upgrading mechanism via GitHub Issues
→ Draft PRs → C-Suite approval.

## Architecture

```
Cloud Scheduler (Mon 06:15 UTC)
  oauth SA: gazzetta-pipeline@PROJECT.iam
  |
  v
Cloud Run Job (gazzetta-rd-sweep-weekly)
  region: europe-west1
  memory: 512MiB, cpu: 1, timeout: 600s
  SA: gazzetta-pipeline@PROJECT.iam
  Image: europe-west1-docker.pkg.dev/PROJECT/gazzetta-docker/gazzetta-rd-agent
  Phase: 1 (GitHub Issues only)
```

## Research Tracks

| Track | Prompt | Output |
|-------|--------|--------|
| navigation-ui | Analyze Bloomberg/FT/Reuters multi-category nav patterns vs Gazzetta INTEL/ALPHA | UX recommendations |
| capital-flow-apis | Compare EPFR/Morningstar/Lipper API availability, cost, granularity | Integration proposals |
| distribution-roi | Reddit vs X vs Telegram engagement metrics, cost-per-acquisition | Optimal mix report |

Outputs saved to `gs://BUCKET/rd_research/<track>/<YYYY-MM-DD>.json`

## Phase 1: GitHub Issues (Weeks 1-2, ACTIVE)

- Agent researches → creates GitHub Issue per track
- Issues labeled `rd-sweep`, `auto-generated`
- Template: Hypothesis, Key Findings, Recommendations, Awaiting C-Suite
- Token scope: `Issues: write` only
- Read-only: no branch creation, no code push

## Phase 2: Draft PRs (Weeks 3-4+, PENDING UNLOCK)

Unlocked when ≥50% of Phase 1 Issues receive C-Suite attention within 48 hours.

### PR Creation Flow

1. Fetch `github-pat-rd-agent` from Secret Manager
2. `git clone` repo with token auth
3. Research track → create branch `rd-agent/<track>/<YYYY-MM-DD>`
4. Apply code changes (CSS, HTML, Python)
5. Run `test_platform.py` locally in container
6. `git add` + `git commit` + `git push origin <branch>`
7. Create **Draft PR** with hypothesis/change/risk template
8. Clear PAT from memory and environment

### PR Template

```markdown
## R&D Sweep: {track_name}
**Date:** {YYYY-MM-DD}
**Agent Cycle:** Weekly (Mon 06:00 UTC)

### Hypothesis
{2-3 sentences: what the agent believes the change achieves}

### Research Sources
- {link to web research results}
- {link to browser screenshots saved in GCS}

### Code Changed
| File | Change | Risk |
|------|--------|------|
| `path/to/file.css` | {description} | Low/Med/High |

### Test Gate Result
{pass/fail output from test_platform.py}

### ⚠️ AWAITING C-SUITE APPROVAL
Review and merge — or close with rationale. Stale PRs auto-close after 14 days.
```

### Branch Naming Convention

```
rd-agent/<track-name>/<YYYY-MM-DD>
```

Examples:
- `rd-agent/navigation-ui/2026-06-15`
- `rd-agent/capital-flow-apis/2026-06-15`
- `rd-agent/distribution-roi/2026-06-15`

## GitHub Token Requirements

| Field | Value |
|-------|-------|
| Token type | Fine-grained Personal Access Token |
| Repository | Single repo: `lagazzettadikyiv` |
| Phase 1 scope | `Issues: write` |
| Phase 2 scope | `Contents: write` + `Pull requests: write` |
| Secret Manager | `github-pat-rd-agent` |
| IAM binding | `roles/secretmanager.secretAccessor` on Cloud Run SA |
| Rotation | Every 90 days |

**C-Suite provisioning URL:** https://github.com/settings/tokens?type=beta

## Docker Image

### Dockerfile.rd-agent

```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir google-cloud-storage==2.14.0 google-cloud-secret-manager==2.18.0 httpx==0.27.0 beautifulsoup4==4.12.3
COPY rd_entrypoint.py /app/rd_entrypoint.py
RUN git config --global user.email "rd-agent@gazzetta-di-kyiv.local" && git config --global user.name "Gazzetta R&D Agent"
WORKDIR /app
ENTRYPOINT ["python3", "/app/rd_entrypoint.py"]
```

### Build Pattern

```bash
mkdir agents_build_rd
cp Dockerfile.rd-agent agents_build_rd/Dockerfile
cp scripts/rd_entrypoint.py agents_build_rd/
gcloud builds submit --tag IMAGE agents_build_rd/
```

Same pattern as CCO/CDO agents — separate build directory, standard Dockerfile name.

## Cloud Scheduler

```bash
gcloud scheduler jobs create http gazzetta-rd-sweep-weekly-cron \
  --schedule="15 6 * * 1" \
  --uri="https://REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/PROJECT/jobs/gazzetta-rd-sweep-weekly:run" \
  --http-method=POST \
  --oauth-service-account-email=gazzetta-pipeline@PROJECT.iam.gserviceaccount.com \
  --location=europe-west1 \
  --time-zone=UTC
```

Schedule offset: 06:15 UTC avoids overlap with pipeline (:00) and newsletter-daily (06:00).

## Guardrails (Multi-Lens Synthesis Risk Assessment)

| Priority | Risk | Mitigation |
|----------|------|-----------|
| P0 | PAT exfiltration | Single-repo scope, cleared from memory, Secret Manager audit logging |
| P0 | Force-push damaging main | Branch protection on `main`, `force=False` hard-coded |
| P1 | Merge conflict with pipeline | Offset schedule, agent touches source files only |
| P1 | Stale unreviewed PRs | Phase 1 Issues-first proves review loop, auto-close after 14 days |
| P2 | Supply-chain attack | Pinned deps, pip-audit in Docker build |
| P3 | Broken code passes local test | Draft PR + human review + post-merge pipeline deploys within 10 min |

## Verification

### Test execution (manual)

```bash
gcloud run jobs execute gazzetta-rd-sweep-weekly --region=europe-west1 --wait
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=gazzetta-rd-sweep-weekly" --limit=50
```

### Research output check

```bash
gsutil ls gs://www.lagazzettadikyiv.com/rd_research/navigation-ui/
gsutil ls gs://www.lagazzettadikyiv.com/rd_research/capital-flow-apis/
gsutil ls gs://www.lagazzettadikyiv.com/rd_research/distribution-roi/
```

### GitHub Issue check

Look for issues labeled `rd-sweep` in the lagazzettadikyiv repo.
