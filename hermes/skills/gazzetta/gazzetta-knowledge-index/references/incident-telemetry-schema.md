# Incident Telemetry Schema

## File

`/opt/gazzetta-di-kyiv/mailbox/incidents.json` — flat JSON array, append-only.

## Schema

```json
[
  {
    "ticket_id": "INC-20260622-205145",
    "type": "pipeline_failure",
    "severity": "CRITICAL",
    "step": "synthesis",
    "context": {
      "exit_code": 1,
      "error_summary": "DEEPSEEK_API_KEY not set",
      "detected_at": "2026-06-22T20:51:45+00:00"
    },
    "remediation_attempts": 0,
    "status": "unresolved"
  }
]
```

## Severity Classification

CRITICAL steps (pipeline backbone — failure stops data flow):
- ingestion, synthesis, classify, calc_capital, build_frontend

WARNING steps (degraded mode — pipeline continues without them):
- market_data, cftc_data, fred_data, derivatives, gen_flows, test_platform, telegram_post, deploy

## Processing Path (Phase 2b — 1-minute CEO timer)

1. Read incidents.json
2. Filter for `status: "unresolved"`
3. Sort by severity (CRITICAL first) then by detected_at
4. For each incident:
   - Tier 1 failures (data-only): auto-fix and mark resolved
   - Tier 2 failures (infrastructure): push remediation plan to outbox.json with `status: "pending_approval"`
5. Increment `remediation_attempts` on each attempt
6. After 3 failed attempts: escalate to Telegram alert and stop retrying

## Separation of Concerns

- `inbox.json` — human-to-CEO directives (editorial commands, pipeline audits)
- `outbox.json` — CEO responses + editorial judgments
- `incidents.json` — machine-generated pipeline failure telemetry

DO NOT mix incident schema with directive schema. They have different processing paths and different `status` enumerations (`unresolved/resolved` vs `pending/answered`).
