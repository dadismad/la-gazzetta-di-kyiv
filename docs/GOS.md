# Gazzetta Operating System (GOS) v1.0

**The single source of truth for how Gazzetta di Kyiv operates.**

---

## ORGANIZATIONAL IDENTITY

| Attribute | Value |
|-----------|-------|
| **Name** | La Gazzetta di Kyiv |
| **Mission** | Contradiction-first narrative intelligence. Track capital flows before they move prices. |
| **Principle** | "It's hard to create simple, but easy to create hard." |
| **Canonical Path** | `/Users/alexstocchi/projects/gazzetta-di-kyiv` |
| **Live Site** | `https://www.lagazzettadikyiv.com` |
| **Version Control** | `pureciclismo/gazzetta-di-kyiv` (GitHub) |
| **Operating Cadence** | Continuous (24/7 autonomous pipeline) |

---

## MANAGEMENT LAYERS

### I. STRATEGY
→ See [`strategy.md`](strategy.md)
> What we track, why we track it, how we measure success.

### II. PROCESSES
→ See [`process-registry.md`](process-registry.md)
> Every process: owner, inputs, outputs, schedule, dependencies, failure modes.

### III. EXECUTION
→ See [`execution-framework.md`](execution-framework.md)
> Pipeline chain, cron orchestration, skill dispatch, handoff patterns.

### IV. MONITORING
→ See [`monitoring.md`](monitoring.md) + `/dashboard/index.html`
> Health checks, alerts, metrics, CEO dashboard.

### V. GOVERNANCE
→ See [`governance.md`](governance.md)
> Decision rights, change management, audit cadence, quality gates.

---

## FILE MANAGEMENT SYSTEM

| Rule | Standard |
|------|----------|
| **Canonical path** | `/Users/alexstocchi/projects/gazzetta-di-kyiv` — single source of truth |
| **Ghost path** | `~/.hermes/hermes-agent/gazzetta-di-kyiv` → symlink to canonical |
| **Naming** | `snake_case.py` for scripts, `kebab-case.md` for docs, `YYYY-MM-DD` for dated data |
| **Directories** | `scripts/` (pipeline), `data/` (source), `site/` (deploy target), `docs/` (governance), `skills/` (agent skills) |
| **Version control** | Git at canonical path. Push to `pureciclismo/gazzetta-di-kyiv` daily. |
| **No credentials** | Never store API keys, tokens, or secrets in project files. Use `~/.hermes/.env`. |

### Directory Structure

```
gazzetta-di-kyiv/
├── docs/                    # Governance & operations documentation
│   ├── GOS.md               # This document
│   ├── strategy.md          # Strategy framework
│   ├── process-registry.md  # All processes catalogued
│   ├── execution-framework.md
│   ├── monitoring.md
│   ├── governance.md
│   └── runbooks/            # SOPs for common tasks
├── scripts/                 # Pipeline Python/Bash scripts
│   ├── pipeline_chain.sh    # Master pipeline orchestrator
│   ├── intel_to_stories.py  # Telegram intel → stories bridge
│   ├── decay_stories.py     # Freshness decay + lead rotation
│   ├── validate_stories.py  # Schema validation + repair
│   ├── generate_flows.py    # Stories → capital flows
│   ├── build_site.py        # data/ → site/data/ sync
│   └── ...                  # Other pipeline scripts
├── data/                    # Source data (pipeline input)
│   ├── stories.json         # Canonical stories
│   ├── flows.json           # Canonical flows
│   ├── telegram_intel/      # Telegram monitor output
│   ├── publish/             # Editorial publishing artifacts
│   ├── quality_gates/       # Quality gate output
│   └── config/              # Source registries, pillar configs
├── site/                    # Deploy target → GCS
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   ├── i18n.js
│   ├── i18n_ru.json
│   ├── data/                # Deployed data (sync from ../data/)
│   ├── api/v1/home/         # API endpoints
│   └── dashboard/           # CEO management dashboard
└── .gitignore
```

---

## PROCESS MANAGEMENT

### Pipeline Chain (Primary)

```
telegram_monitor (30m) → telegram_intel/latest.json
    ↓
pipeline_chain.sh (60m):
  1. intel_to_stories.py    → stories.json (new stories from intel)
  2. decay_stories.py        → freshness tiers + lead rotation + archive
  3. validate_stories.py     → repair malformed capital_flow dicts
  4. generate_flows.py       → flows.json (from stories)
  5. build_site.py           → sync data/ → site/data/
    ↓
deploy (15m)                 → gsutil rsync site/ → GCS
```

### Process Ownership

| Process | Owner | Runs |
|---------|-------|------|
| Telegram monitoring | `gazzetta-telegram-monitor` (LLM agent) | 30m |
| Pipeline chain | `gazzetta_pipeline_chain.sh` (no_agent script) | 60m |
| Deploy to GCS | `gazzetta_deploy_to_gcs.sh` (no_agent script) | 15m |
| CEO oversight | `gazzetta-ceo-overseer` (LLM agent) | 15m |
| Health check | `gazzetta-health-check` (LLM agent) | 30m |
| Living stories | `gazzetta_enrich_stories.py` (no_agent script) | 2h |
| Source monitoring | `gazzetta-continuous-source-monitor` (LLM agent) | 60m |
| Editorial publishing | `gazzetta-agentic-nlp-guarded-autopost` (LLM agent) | 2x daily |

---

## STRATEGIC FRAMEWORK

### Six Paradigm Pillars

| Pillar | Definition | Sources |
|--------|-----------|---------|
| `china_ascendancy` | China tech/industrial execution, semiconductor autonomy | Telegram, web_search |
| `dollar_decline` | De-dollarization, BRICS, IMF COFER | Telegram, web_search |
| `eu_fragmentation` | EU structural stress, defense divergence | Telegram, web_search |
| `abundance_tech` | Fusion, space economy, AI compute, longevity | Telegram, web_search |
| `blockchain_agentic` | RWA tokenization, DeFi institutional, agentic economy | Telegram, web_search |
| `multi_pillar` | Geopolitical, macro regime shifts, commodity shocks | Telegram (primary) |

### Success Metrics

| Metric | Target | Measured |
|--------|--------|----------|
| Stories/day | ≥ 5 new | stories.json count delta |
| Flow confidence | ≥ 70% | flows.json aggregate_confidence |
| Data freshness | < 2h | File mtime vs now |
| Pipeline success rate | ≥ 95% | cron last_status |
| Deploy cadence | 15m | Last deploy timestamp |
| Site uptime | 99%+ | HTTP 200 checks |
| Story quality | Contradiction score > 40 | validate_stories output |
| Skills utilization | > 50% | Skills loaded by active crons |

### Review Cadence

| Review | Frequency | Owner |
|--------|-----------|-------|
| Pipeline health | Every 60m (automated) | pipeline_chain.sh |
| Data freshness | Every 30m (automated) | health-check |
| Site availability | Every 15m (automated) | deploy script |
| Strategic alignment | Weekly | CEO overseer |
| Skill audit | Bi-weekly | Manual review |
| Full system audit | Monthly | 3-persona focus group |

---

## TACTICAL PLAYBOOKS

### Standard Operating Procedures

1. **Adding a new cron job**: See `docs/runbooks/add-cron.md`
2. **Responding to pipeline failure**: See `docs/runbooks/incident-response.md`
3. **Adding a new paradigm pillar**: See `docs/runbooks/add-pillar.md`
4. **Deploying a site update**: See `docs/runbooks/deploy.md`
5. **Creating a new skill**: See `docs/runbooks/add-skill.md`
6. **Running a focus group review**: See `docs/runbooks/focus-group.md`

### Incident Severity Levels

| Level | Criteria | Response |
|-------|----------|----------|
| **P0 — Critical** | Site down, deploy failing, stories frozen > 4h | Immediate manual intervention |
| **P1 — High** | Pipeline chain failing, data > 6h stale | Auto-retry 3x, then alert |
| **P2 — Medium** | Individual cron failure, schema drift | Logged, auto-healed if possible |
| **P3 — Low** | Cosmetic issues, unused skills, stale docs | Scheduled for next maintenance window |

---

## GOVERNANCE

### Decision Rights

| Decision | Authority |
|----------|-----------|
| Add/remove cron job | Operator (requires Telegram confirmation) |
| Change pipeline logic | Operator (requires test run) |
| Modify site HTML/CSS | Operator (auto-deploy after change) |
| Change strategic pillars | Operator (requires weekly review) |
| Add new data source | Operator (requires pillar alignment) |
| Archive skill | Operator (after 2 weeks unused) |

### Change Management

1. All pipeline changes → test locally first → verify output → deploy
2. All site changes → validate in browser → deploy → verify live
3. All cron changes → pause old → create new → test run → enable
4. All data schema changes → add backward compat → migrate → validate

### Audit Cadence

| Audit | Schedule | Method |
|-------|----------|--------|
| Data schema | Every pipeline run | `validate_stories.py` |
| Dynamic indicators | Every 15m | `gazzetta-dynamic-indicator-audit` |
| Skill inventory | Bi-weekly | Manual: check usage, update, archive |
| Cron health | Continuous | `last_status` field per job |
| Full system | Monthly | 3-persona focus group audit |

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-06-06 | Initial GOS. Unified management framework. Process registry. Strategy pillars. Governance model. |
