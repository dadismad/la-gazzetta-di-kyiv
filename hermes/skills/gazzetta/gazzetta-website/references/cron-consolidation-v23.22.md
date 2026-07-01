# Cron Consolidation & Product Factory (v23.22)

## Problem

17 crons running on various schedules, 2 in ERROR state, 4 redundant/duplicate. Split-brain risk: `gazzetta-telegram-monitor` + `gazzetta-continuous-source-monitor` both ingesting sources. `gazzetta-agentic-nlp-guarded-autopost-8h` + `gazzetta-hourly-narrative-review` both generating editorial content. `gazzetta-reddit-ingestion-hourly` + `gazzetta-devvit-only-pipeline` both handling Reddit.

LLM-agent crons fabricate `{"ok": true}` output when scripts don't exist — silent failures.

## Solution: Product Factory

Single `no_agent=true` script cron that runs the full pipeline end-to-end:

```
fetch_intel → intel_to_stories → generate_flows → db_to_json → shipit → health_check
```

Every 60 minutes. Script-only — no LLM hallucination, no phantom script failures.

## v23.22 Cron Inventory

### Removed (6)
| Cron | Reason |
|------|--------|
| `gazzetta-telegram-monitor` | ERROR state — phantom script |
| `gazzetta-osint-collector` | ERROR state — fetch_intel script not found |
| `gazzetta-agentic-nlp-guarded-autopost-8h` | Duplicate of narrative-review editorial |
| `gazzetta-devvit-only-pipeline` | Split-brain with reddit-ingestion |
| `gazzetta-reddit-ingestion-hourly` | Folded into product-factory |
| `gazzetta-continuous-source-monitor` | Duplicate of pipeline ingestion |

### Created (1)
| Cron | Schedule | Type | Job ID |
|------|----------|------|--------|
| `gazzetta-product-factory` | every 60m | no_agent script | `6353a0ebfbd9` |

### Remaining (10)
- `gazzetta-hourly-narrative-review` — Telegram posting
- `gazzetta-phase3-daily-brief` — daily scoring
- `x-health-watchdog-gazzetta` — X account health
- `gazzetta-focus-group-quality-gate` — quality gate
- `gazzetta-living-stories-enrich` — living stories
- `link-intelligence-synthesis` — link learning
- `gazzetta-editorial-style-audit` — style audit
- `daily-session-review` — session review
- `gazzetta-health-check` — health check
- `gazzetta-ceo-overseer` — CEO oversight
- `gazzetta-market-data-pipeline` — market data (6h)

## Detection Pattern

To find error crons, cross-check `last_status=error` against script existence. Phantom LLM crons with `last_status=ok` can hide broken scripts — any cron that runs an LLM agent and claims success should be verified by checking whether its output files actually changed.

## Script Location

`scripts/gazzetta_product_factory.sh` in this skill. Must be copied to `~/.hermes/scripts/` for cron execution.
