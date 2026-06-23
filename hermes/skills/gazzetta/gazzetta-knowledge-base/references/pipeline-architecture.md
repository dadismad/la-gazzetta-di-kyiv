# Pipeline Architecture — Gazzetta di Kyiv (v3.0 SQLite-backed)

## Current Architecture (June 2026)

```
                    ┌──────────────────────────────┐
                    │   OSINT Collector (cron)      │
                    │   fetch_intel.py              │
                    │   RSS feeds → drafts table    │
                    └──────────┬───────────────────┘
                               │ pending_review
                               ▼
                    ┌──────────────────────────────┐
                    │   Draft Approval Queue        │
                    │   approve_draft.py --id N     │
                    │   → stories + flows + links   │
                    └──────────┬───────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
     ┌────────────┐   ┌────────────┐   ┌────────────┐
     │ Telegram   │   │ RSS Feeds  │   │ Manual     │
     │ Monitor    │   │ (ECB,etc)  │   │ Drafts     │
     │ (30m)      │   │ (120m cron)│   │            │
     └─────┬──────┘   └─────┬──────┘   └─────┬──────┘
           │                │                │
           └────────┬───────┴────────┬───────┘
                    │                │
                    ▼                ▼
           ┌──────────────────────────────┐
           │   gazzetta.db (SQLite)       │
           │   · stories (30)             │
           │   · flows (12)               │
           │   · drafts (70)              │
           │   · story_flow_links (12)    │
           └──────────────┬───────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │   db_to_json.py              │
           │   SQL JOIN → stories.json    │
           │   SQL JOIN → flows.json      │
           └──────────────┬───────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │   build_site.py              │
           │   data/ → site/data/ + API   │
           └──────────────┬───────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │   test_platform.py           │
           │   138 assertions (5 rounds)  │
           │   FAIL → abort deploy        │
           └──────────────┬───────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │   shipit.sh (8 stages)       │
           │   hash → GCS → verify → git  │
           └──────────────────────────────┘
```

## Key Database Tables

| Table | Rows | Key Columns |
|---|---|---|
| `stories` | 30 | id (PK), full_json, capital_flow_raw, multi_persona_raw |
| `flows` | 12 | id (PK), story_id (FK→stories), amount_b, velocity |
| `drafts` | 70 | id (PK AUTOINCREMENT), source, status, suggested_flows |
| `story_flow_links` | 12 | story_id + flow_id (PK), FK→both parents |

## Key Scripts (v3.0)

| Script | Function | Run Mode |
|---|---|---|
| `init_db.py --migrate` | Safe schema migration (add new tables) | Manual |
| `import_json_to_db.py` | Seed DB from existing JSON | One-time |
| `db_to_json.py` | SQL → JSON with JOIN (injects real flow metrics) | shipit.sh Stage 1 |
| `intel_to_stories.py` | Telegram intel → INSERT into DB + auto-compile | pipeline_chain.sh |
| `fetch_intel.py` | RSS feeds → drafts table | Cron (120m, no_agent) |
| `approve_draft.py` | Draft → story + flow + links + rebuild | Manual |
| `test_platform.py` | 5-round BS4 test suite (138 assertions) | shipit.sh Stage 2.5 |
| `build_site.py` | Sync data/ → site/data/ + API endpoints | shipit.sh Stage 2 |
| `shipit.sh` | 8-stage deploy pipeline with test gate | Manual / cron |

## Cron Architecture (Key Jobs)

| Job ID | Name | Schedule | Mode |
|---|---|---|---|
| `83bbdb3d275a` | gazzetta-osint-collector | 120m | no_agent (fetch_intel.py) |
| `51c1bb776729` | gazzetta-continuous-capital-flows | 60m | no_agent (pipeline_chain.sh) |
| `f9a24ed64aa5` | gazzetta-deploy-to-gcs | 60m | no_agent (gazzetta_deploy_to_gcs.sh) |
| `4e973ff20bf3` | gazzetta-telegram-monitor | 30m | LLM agent |

## Critical Design Rules

1. **gazzetta.db is local only** — `.gitignore`'d, never committed to git
2. **SQL JOIN for flow metrics** — `db_to_json.py` overwrites story `capital_flow` with real DB values from linked flows (zero mismatch tolerance enforced by tests)
3. **Frameless UX** — all product pages: `border-radius: 0`, `box-shadow: none`, `background: #FFFFFF`
4. **Light theme only** — no dark theme as default on any page
5. **Timestamps on every data container** — `<time>` elements + `flow-freshness` spans
6. **Test gate blocks deploy** — shipit.sh Stage 2.5 exits 1 on any failure
