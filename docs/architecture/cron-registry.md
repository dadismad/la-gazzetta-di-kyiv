# Cron Registry — Gazzetta di Kyiv

> All 17 Hermes cron jobs. Auto-generated from ~/.hermes/cron/jobs.json.
> See docs/process-registry.md for detailed failure mode analysis.

## Summary

17 jobs total. 12 LLM Agent, 3 Script (no_agent), 2 Script.

## Data Collection Layer

| Job | Type | Schedule | Last Status |
|-----|------|----------|-------------|
| gazzetta-telegram-monitor | LLM Agent | every 30m | ok |
| gazzetta-continuous-source-monitor | LLM Agent | every 60m | ok |
| gazzetta-reddit-ingestion-hourly | LLM Agent | every 60m | ok |

## Processing Layer

| Job | Type | Schedule | Last Status |
|-----|------|----------|-------------|
| gazzetta-continuous-capital-flows | LLM Agent | every 60m | ok |
| gazzetta-living-stories-enrich | Script | 15 */2 * * * | ok |
| gazzetta-phase3-daily-brief | LLM Agent | 0 9 * * * | ok |

## Publishing Layer

| Job | Type | Schedule | Last Status |
|-----|------|----------|-------------|
| gazzetta-deploy-to-gcs | Script | every 15m | ok |
| gazzetta-agentic-nlp-guarded-autopost-8h | LLM Agent | 45 6,18 * * * | ok |
| gazzetta-hourly-narrative-review | LLM Agent | 30 6,18 * * * | ok |
| gazzetta-focus-group-quality-gate | LLM Agent | 0 7,19 * * * | ok |
| gazzetta-devvit-only-pipeline | LLM Agent | every 480m | ok |

## Governance Layer

| Job | Type | Schedule | Last Status |
|-----|------|----------|-------------|
| gazzetta-ceo-overseer | LLM Agent | every 15m | ok |
| gazzetta-health-check | Script | every 30m | ok |
| gazzetta-editorial-style-audit | LLM Agent | 0 10 * * * | ok |
| x-health-watchdog-gazzetta | Script | 0 0,8,16 * * * | ok |
| link-intelligence-synthesis | LLM Agent | 0 3 * * * | ok |
| daily-session-review | LLM Agent | 0 22 * * * | ok |

## Skills Used by Cron Jobs

- gazzetta-editorial-writer (used by autopost)
- gazzetta-capital-flows (references, not wired to cron prompt)
- gazzetta-ceo-overseer (loaded by CEO overseer)
- Various gazzetta-* skills in ~/.hermes/skills/gazzetta/

## Key Enables/Disables

All 17 jobs currently enabled. No paused jobs.
