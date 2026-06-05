# Homepage v1 Execution Checklist (Gazzetta di Kyiv)

## Phase 1 — Data/API readiness
- [ ] Define canonical `IntelligenceObject` schema in code
- [ ] Expose homepage endpoints:
  - [ ] `/api/v1/home/regime`
  - [ ] `/api/v1/home/setups`
  - [ ] `/api/v1/home/divergences`
  - [ ] `/api/v1/home/contradictions`
  - [ ] `/api/v1/home/aftershocks`
- [ ] Add response metadata: `generated_at`, `data_freshness_seconds`, `source_count`

## Phase 2 — Homepage modules
- [ ] Regime strip
- [ ] High-conviction setup cards
- [ ] Belief vs Reality panel
- [ ] Contradiction + invalidation rail
- [ ] Second-order effects queue
- [ ] Expand/collapse narrative drawer

## Phase 3 — Quality gates
- [ ] Block publish if invalidation missing
- [ ] Block publish if confidence missing
- [ ] Block publish if scenario probabilities != 100
- [ ] Block publish if citation count missing

## Phase 4 — Reliability/observability
- [ ] Pipeline lag metric
- [ ] Module staleness metric
- [ ] Endpoint error-rate metric
- [ ] Alerts for stale or failed module updates
- [ ] Replay failed batches capability

## Phase 5 — Visual doctrine checks
- [ ] Compact typography readability check
- [ ] Light metallic-blue palette consistency
- [ ] Non-repetitive left/right content check
- [ ] Accessibility contrast check

## Pass/Fail Criteria (Production-ready)
- [ ] Ingestion lag < 60s (high-priority)
- [ ] Read endpoint p95 < 800ms
- [ ] Homepage p95 load < 1.5s
- [ ] No hard-gate violations in last 7 days
