# Organizational Management Framework (June 2026)

## What was built

After the user requested "research how to manage such organizations and implement findings into workflows":

### Gazzetta Operating System (GOS)
Single source of truth document at `docs/GOS.md` covering 5 management layers:
- Strategy → Process → Execution → Monitoring → Governance
- File management system (canonical paths, naming, version control)
- Directory structure with documented conventions
- Decision rights matrix
- Incident severity levels (P0-P3)
- Review cadence (weekly/monthly/quarterly)

### Process Registry
`docs/process-registry.md` — all 17 cron jobs catalogued:
- Process map showing data flow between layers
- Each process: inputs, outputs, schedule, dependencies, failure modes
- Dependency graph with conflict detection
- Failure mode inventory (10/17 processes have no alerting)

### Strategy Framework
`docs/strategy.md`:
- 6 paradigm pillars with KPI targets
- 4-phase growth strategy (Stabilize→Scale→Grow→Monetize)
- Competitive positioning matrix
- Target audience personas

### Operations Runbook
`docs/runbooks/operations.md`:
- Incident response for P0-P3
- Daily health check script
- Common task procedures (add source, add pillar, deploy, create skill)
- File recovery procedures

### CEO Dashboard
`site/dashboard/index.html` — live HTML dashboard:
- Pipeline health (stories, flows, confidence, data age)
- Site & deploy status with latency
- Data freshness gauges by tier
- Alert feed with severity levels
- Auto-refresh every 60s

## When to use
- User asks "manage this organization" or "implement management frameworks"
- User wants process documentation
- User asks for strategy/roadmap
- Building operational resilience

## Key lesson
Organizational management for AI-driven operations requires BOTH:
1. Automation layer (crons, scripts, agents)
2. Documentation layer (GOS, process registry, runbooks, dashboard)

Many AI operations over-invest in #1 and under-invest in #2. The user explicitly asked for both.
