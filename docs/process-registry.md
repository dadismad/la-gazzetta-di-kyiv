# Process Registry

**Every process in the Gazzetta di Kyiv operation, catalogued with inputs, outputs, schedule, dependencies, and failure modes.**

---

## PROCESS MAP

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA COLLECTION LAYER                         │
│                                                                      │
│  P1: Telegram Monitor (30m)                                          │
│  P2: Source Monitor (60m)      P3: Devvit Ingest (480m)             │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        PROCESSING LAYER                              │
│                                                                      │
│  P4: Pipeline Chain (60m)                                            │
│    ┌─ P4a: intel_to_stories ──┐                                     │
│    ├─ P4b: decay_stories      ─┤                                    │
│    ├─ P4c: validate_stories   ─┤                                    │
│    ├─ P4d: generate_flows     ─┤                                    │
│    └─ P4e: build_site         ─┘                                    │
│                                                                      │
│  P5: Living Stories Enrich (2h)                                      │
│  P6: Phase3 Daily Brief (24h)                                        │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        PUBLISHING LAYER                              │
│                                                                      │
│  P7: Deploy to GCS (15m)                                             │
│  P8: Editorial Autopost (12h)                                        │
│  P9: Narrative Review (12h)                                          │
│  P10: Quality Gate (12h)                                             │
│  P11: Devvit Reddit Post (480m)                                      │
└─────────────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        GOVERNANCE LAYER                              │
│                                                                      │
│  P12: CEO Overseer (15m)                                             │
│  P13: Health Check (30m)     P14: Style Audit (24h)                 │
│  P15: Dynamic Indicator Audit (included in P12)                      │
│  P16: X Health Watchdog (8h)                                         │
│  P17: Session Review (24h)                                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## PROCESS CATALOGUE

### P1: Telegram Monitor
| Field | Value |
|-------|-------|
| **Cron ID** | `4e973ff20bf3` |
| **Type** | LLM Agent |
| **Schedule** | Every 30 minutes |
| **Inputs** | Telegram channels (monitoring feeds) |
| **Outputs** | `data/telegram_intel/latest.json`, `data/telegram_intel/raw_fetch.json` |
| **Dependencies** | Telegram API access |
| **Failure Mode** | Silent. LLM may produce output without real data. |
| **Last Status** | ok |

### P2: Continuous Source Monitor
| Field | Value |
|-------|-------|
| **Cron ID** | `9e2da8f71d73` |
| **Type** | LLM Agent |
| **Schedule** | Every 60 minutes |
| **Inputs** | `data/config/data_sources_v2.json`, `site/data/stories.json`, web_search |
| **Outputs** | Claims to append stories to `site/data/stories.json` (LLM writes) |
| **Dependencies** | DeepSeek API, web_search capability |
| **Failure Mode** | Claims "added story" without actually writing. Fabricates output. ⚠️ Known issue. |
| **Last Status** | ok |

### P3: Devvit Reddit Ingest
| Field | Value |
|-------|-------|
| **Cron ID** | `67609e89de17` |
| **Type** | LLM Agent |
| **Schedule** | Every 60 minutes |
| **Inputs** | Devvit API (Reddit), 7 target subreddits |
| **Outputs** | `data/reddit_ingest/latest.json` |
| **Dependencies** | Devvit API URL (currently unreachable — DNS failure) |
| **Failure Mode** | Devvit API DNS failure → 0 posts ingested. Agent still reports ok. |
| **Last Status** | ok |

---

### P4: Pipeline Chain (CAPITAL FLOWS)
| Field | Value |
|-------|-------|
| **Cron ID** | `51c1bb776729` |
| **Type** | `no_agent` Script (Bash) |
| **Schedule** | Every 60 minutes |
| **Script** | `gazzetta_pipeline_chain.sh` |
| **Workdir** | `/Users/alexstocchi/projects/gazzetta-di-kyiv` |
| **Steps** | P4a→P4b→P4c→P4d→P4e (sequential, `set -e`) |
| **Deliver** | local only |
| **Failure Mode** | `set -e` stops chain on first failure. No retry. No notification. |

#### P4a: intel_to_stories
| Field | Value |
|-------|-------|
| **Script** | `scripts/intel_to_stories.py` |
| **Inputs** | `data/telegram_intel/latest.json` |
| **Outputs** | `data/stories.json`, `site/data/stories.json` (appends new stories) |
| **Key Logic** | Reads `intel["stories"]` (corrected from `actionable_stories`), converts to story format, deduplicates on story_id |

#### P4b: decay_stories
| Field | Value |
|-------|-------|
| **Script** | `scripts/decay_stories.py` |
| **Inputs** | `data/stories.json` |
| **Outputs** | `data/stories.json`, `site/data/stories.json`, `data/stories_archive.json` |
| **Key Logic** | Downgrades freshness tiers by age (breaking→new→active→developing→background), rotates lead story, archives >7 days |

#### P4c: validate_stories
| Field | Value |
|-------|-------|
| **Script** | `scripts/validate_stories.py` |
| **Inputs** | `data/stories.json` |
| **Outputs** | `data/stories.json`, `site/data/stories.json` (repaired) |
| **Key Logic** | Ensures every story has complete `capital_flow` dict with `projected`, `confidence_pct`, `pace_multiplier`, `direction`, `amount_b` |

#### P4d: generate_flows
| Field | Value |
|-------|-------|
| **Script** | `scripts/generate_flows.py` |
| **Inputs** | `data/stories.json` |
| **Outputs** | `data/flows.json`, `site/data/flows.json` |
| **Key Logic** | 3-tier extraction: capital_flow dict → capital_flow_implication → portfolio_implication. Computes confidence, pace, positioning |

#### P4e: build_site
| Field | Value |
|-------|-------|
| **Script** | `scripts/build_site.py` |
| **Inputs** | `data/*.json` (13 files) |
| **Outputs** | `site/data/*.json`, `site/api/v1/home/*.json` |
| **Key Logic** | Copies 13 data files from `data/` → `site/data/`, generates API endpoints |

---

### P5: Living Stories Enrich
| Field | Value |
|-------|-------|
| **Cron ID** | `0f4f65873bd9` |
| **Type** | `no_agent` Script (Python) |
| **Schedule** | Every 2 hours |
| **Script** | `gazzetta_enrich_stories.py` |
| **Inputs** | `data/stories.json`, `data/living_stories.json` |
| **Outputs** | `data/living_stories.json` (enriched with sub-threads) |
| **Last Status** | ok (2 stories updated, 5 tagged stale last run) |

### P6: Phase3 Daily Brief
| Field | Value |
|-------|-------|
| **Cron ID** | `feef56da90cb` |
| **Type** | LLM Agent |
| **Schedule** | Daily at 09:00 |
| **Inputs** | `data/phase2_scores.json` (or fallback) |
| **Outputs** | `data/phase3_daily_brief.md` |
| **Dependencies** | `phase2_scoring.py` → `generate_candidates_fallback.py` |
| **Failure Mode** | Both scripts may fail. Fallback produces empty brief. |

---

### P7: Deploy to GCS
| Field | Value |
|-------|-------|
| **Cron ID** | `f9a24ed64aa5` |
| **Type** | `no_agent` Script (Bash) |
| **Schedule** | Every 15 minutes |
| **Script** | `gazzetta_deploy_to_gcs.sh` |
| **Inputs** | `site/` directory |
| **Outputs** | `gs://www.lagazzettadikyiv.com` (42 objects synced) |
| **Dependencies** | gcloud SDK, gcloud auth (`pureciclismo@gmail.com`) |
| **Failure Mode** | Auth expiry, bucket inaccessible, disk full. No retry. No alert. |

---

### P8-P11: Editorial Publishing Layer

| ID | Process | Cron ID | Schedule | Type | Output |
|----|---------|---------|----------|------|--------|
| P8 | Editorial Autopost | `011c8be0b17c` | 6:45/18:45 | LLM Agent | `data/publish/telegram_latest.md` |
| P9 | Narrative Review | `a8c20991c60a` | 6:30/18:30 | LLM Agent | Telegram channel post |
| P10 | Quality Gate | `07c3f044ecd5` | 7:00/19:00 | LLM Agent | `data/quality_gates/latest.json` |
| P11 | Devvit Reddit Post | `12051ebe2746` | Every 480m | LLM Agent | Reddit post on r/LaGazzettadiKyiv |

---

### P12-P17: Governance Layer

| ID | Process | Cron ID | Schedule | Type | Function |
|----|---------|---------|----------|------|----------|
| P12 | CEO Overseer | `2066f604df18` | Every 15m | LLM Agent | Surveillance + auto-fix |
| P13 | Health Check | `8e74f70215d5` | Every 30m | LLM Agent | Site verification |
| P14 | Style Audit | `1d427378d0fa` | Daily 10:00 | LLM Agent | Content quality review |
| P15 | Dynamic Indicator Audit | *(in P12)* | *(in P12)* | Skill | Hardcoded digit scan |
| P16 | X Health Watchdog | `89392959` | 8h (0,8,16) | `no_agent` Script | ⚠️ Last run: June 1 (5 days dead) |
| P17 | Session Review | `9f74801e` | Daily 22:00 | LLM Agent | Hermes meta-review |

---

## PROCESS DEPENDENCY GRAPH

```
P1 (telegram_monitor)
    └──→ P4a (intel_to_stories) ──→ P4b ──→ P4c ──→ P4d ──→ P4e
                                        │
P2 (source_monitor)                     │
    └──→ (writes stories.json directly) │ ⚠️ CONFLICT
                                        │
P5 (living_stories_enrich) ────────────→│
                                        ▼
                                  P7 (deploy) ──→ LIVE SITE
                                        │
                                  P9 (narrative) ──→ Telegram
                                  P11 (devvit) ──→ Reddit
                                  
P8 (autopost) ──→ P10 (quality_gate) ──→ feedback loop ⚠️ BROKEN
```

---

## FAILURE MODE INVENTORY

| Process | Silent Failure? | Auto-Recovery? | Alert? |
|---------|----------------|----------------|--------|
| P1 Telegram Monitor | ✅ Silent (may produce empty output) | ❌ | ❌ |
| P2 Source Monitor | ⚠️ Fabricates success | ❌ | ❌ |
| P3 Devvit Ingest | ✅ DNS failure → 0 posts, reports ok | ❌ | ❌ |
| P4 Pipeline Chain | ⚠️ `set -e` kills on first error | ❌ | ❌ (local only) |
| P5 Living Stories | ❌ Reports errors | ❌ | ❌ |
| P6 Phase3 | ✅ Fallback produces empty brief | ❌ | ❌ |
| P7 Deploy | ⚠️ Auth expiry → silent fail | ❌ | ❌ (local only) |
| P8 Autopost | ✅ Directory didn't exist (was missing) | ❌ | ❌ |
| P10 Quality Gate | ✅ Directory didn't exist (was missing) | ❌ | ❌ |
| P16 X Watchdog | ⚠️ Dead 5 days, no alert | ❌ | ❌ |

**Summary:** 10 of 17 processes have no failure alerting. 6 fail silently.
