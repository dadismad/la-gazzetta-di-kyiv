# Hermes Prompt — Hedge-Fund Grade Data Pipeline & Source Management

## Objective
Acquire and apply modern techniques for building resilient, audit-ready, alpha-oriented data pipelines and source management systems used in hedge-fund-like research operations.

## Learn-and-Implement Scope
1. **Pipeline architecture**
   - event-driven ingestion + scheduled backfill
   - idempotent transforms
   - late-arrival handling
   - deterministic snapshots
2. **Source management**
   - source registry with quality score, reliability score, latency score
   - source drift detection and automatic re-ranking
   - fallback source routing when primary fails
3. **Research representation**
   - narrative extraction + regime classification
   - cross-asset mapping (equities, rates, FX, commodities, crypto)
   - 3-day flow and price projection estimation with confidence bands
4. **Governance and controls**
   - schema contracts, freshness SLAs, anomaly detection
   - reproducibility artifacts and audit logs
   - canary deployment checks before publish

## Standards to Follow
- SRE reliability patterns
- DataOps contract testing
- MLOps monitoring discipline
- Quant PM-style risk framing (base/bull/bear scenario and invalidation)

## Deliverables
- Source registry + ranking outputs
- Freshness and schema reports
- Narrative/projection dataset for publishing
- Incident and remediation reports
- Continuous cron-based autonomous operation with alerting

## Acceptance Criteria
- No empty critical UI container under normal operation.
- Website and data endpoints externally verifiable.
- Every narrative has actionable insight + 3-day flow/projection metadata.
- Failures trigger auto-remediation and explicit blocked status.
