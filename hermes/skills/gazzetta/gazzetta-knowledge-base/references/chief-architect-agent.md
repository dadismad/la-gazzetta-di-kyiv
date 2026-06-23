# Chief Architect Agent — Sprint 4 Deployment

## Service

Cloud Run service (internal-only, `--no-allow-unauthenticated`):
```
URL: https://gazzetta-chief-architect-ot6iczzwga-ew.a.run.app
Region: europe-west1
SA: gazzetta-pipeline@project-e5e0244c-b94d-41a1-810.iam.gserviceaccount.com
Resources: 256MiB, 1 vCPU, port 8080
```

## Auth

User `pureciclismo@gmail.com` has `roles/run.invoker`. Authenticate with:
```bash
TOKEN=$(gcloud auth print-identity-token)
curl -H "Authorization: Bearer $TOKEN" $URL/health
```

## Rules Loaded

3 documents from container filesystem:
- `HERMES_OPERATIONAL_SOP.md` (R1-R9)
- `HERMES_DESIGN_AND_PRODUCT_GUIDELINES.md` (D1-D8, P1-P6, C1-C6)
- `HERMES_CORE_DIRECTIVES.md` (architecture philosophy)

## Endpoints

### GET /health
Returns `{"status": "healthy", "rules_loaded": 3, "timestamp": "..."}`

### POST /review
```json
{
  "self_prompt": "...",
  "directive": "...",
  "context": "..."
}
```
Returns `{"decision": "ARCH_APPROVED" | "ARCH_REJECTED", "violations": [...], "notes": "..."}`

## Deterministic Checks (pre-LLM)

| Check | Rule | Pattern |
|-------|------|---------|
| Blind patching | R1 | `sed -i`, `grep | xargs sed`, `perl -pi` |
| Destructive ops | R3 | `rm -rf`, `DROP TABLE`, crontab modification |
| Credential exposure | R5 | API key patterns (`sk-...`, `AIza...`) |
| Immutable chain | AMEND | modification verb near `db_to_json.py`/`app.js fetch`/`init_db.py`/`import_json_to_db.py` |

## AMEND Tuning (v1.1, June 2026)

The immutable chain check was refactored from unconditional file-name match to context-aware modification-verb detection:

- **Before:** Any mention of `db_to_json.py` triggered AMEND — even "Read db_to_json.py (READ ONLY)"
- **After:** Only triggers when a modification verb (modify, patch, edit, rewrite, delete, sed, change, update, alter, replace, refactor, fix, implement, rebuild, transform, overwrite, rework, revise) appears within 80 characters before the protected file name

Read-only upstream dependency listings pass deterministic checks and proceed to LLM review.

## Secret Mount

DEEPSEEK_API_KEY loaded from `projects/PROJECT/secrets/deepsee...n:latest` via `--set-secrets` flag. LLM review calls DeepSeek API directly from the container.

## Container

Build from `~/lagazzettadikyiv/chief_architect/`:
```bash
gcloud builds submit --tag LOCATION-docker.pkg.dev/PROJECT/gazzetta-docker/chief-architect:latest .
```

## Integration

`hermes-execution-framework` skill Stage 1.5: submit Self-Prompt to Chief Architect before implementation. ARCH_REJECTED → reformulate. ARCH_APPROVED → proceed.

---

## Architect V2 Expansion (June 2026)

Architect V2 added two modules to the pipeline, approved via `/review` endpoint (`ARCH_APPROVED`):

- **Module 4 (Auto-Revert):** `scripts/auto_revert.py` + `cloud_entrypoint.py` hook. On test_platform failure: Telegram alert via Bot API, GCS sync blocked, failure logged to `pipeline-run-log.jsonl`.
- **Module 6 (Memory Synthesis):** `scripts/memory_synthesizer.py` as separate Cloud Run Job (daily 02:00 UTC). Reads `pipeline-run-log.jsonl`, generates `DRAFT_SKILL_UPDATE.md`, uploads to GCS.

Both modules use the same Docker image. Module 6 runs via `--command=python3 --args=/app/scripts/memory_synthesizer.py,--days,7`.

Full implementation details in `references/gcp-cloud-run-migration.md` (Architect V2 section).
