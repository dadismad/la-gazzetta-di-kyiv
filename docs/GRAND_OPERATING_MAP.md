# Grand Operating Map

Generated: 2026-05-23T12:46:39.644805+00:00

## Data Plane
- social-umbrella-collector | 15m | DataOps | ingestion
- phase2-publish | 8h | PublishingOps | site refresh/deploy prep
- sources-daily-update | daily 06:00 | DataOps | source quality/ranking
- pipeline-audit | daily 06:30 | Governance | audit + integrity

## Control Plane
- ceo-upgrade-control-loop | 2h | CEO | external availability + canary + blockers
- brandbook-representation-ops | daily 09:00 | Brand/Data | brand/content gates
- morning-evening-newsroom-cycle | 06:30 & 18:30 | Editorial | newspaper cadence + newsletter bundles

## KPI Contracts
- availability_target: >=99%
- non_empty_claims: required
- narrative_actionability: required fields present
- publish_cadence: morning+evening fulfilled