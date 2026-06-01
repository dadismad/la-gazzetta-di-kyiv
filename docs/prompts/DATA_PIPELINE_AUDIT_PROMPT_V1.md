# DATA PIPELINE AUDIT PROMPT — GAZZETTA DI KYIV (V1)

Audit the complete data pipeline from collection to publishing.

## Scope
- Sources and retrieval methods
- Raw storage and normalization
- Scoring and interpretation
- Content preparation
- Distribution outputs (site/reddit/telegram/x)
- Scheduling and reliability
- Data contracts and schema adherence

## Audit checklist
1. **Inventory**: enumerate scripts, data files, cron jobs, and endpoint dependencies.
2. **Source health**: verify each source has retrieval method, auth mode, rate-limit strategy, and fallback.
3. **Freshness**: measure age of critical artifacts (`regime.json`, `setups.json`, publish payloads).
4. **Contract checks**: validate article contract and required narrative fields.
5. **Continuity checks**: verify invalidation and confidence exist in publish artifacts.
6. **Operational risk**: identify single points of failure and external hidden dependencies.
7. **Distribution integrity**: ensure website and channel payloads stem from same canonical dataset.

## Deliverables
- Machine report: `data/audit/pipeline_audit_latest.json`
- Executive report: `data/audit/pipeline_audit_latest.md`
- Severity-tagged findings: blocker/high/medium/low
- Prioritized remediation backlog with exact file paths

## Acceptance criteria
- Every finding references concrete evidence (file path, key, timestamp, status).
- At least one remediation action is implemented in same cycle.
