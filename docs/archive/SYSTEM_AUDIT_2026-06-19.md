# GAZZETTA DI KYIV — COMPREHENSIVE SYSTEM AUDIT
## June 19, 2026 — Full 6-Phase Forensic Audit

---

## EXECUTIVE SUMMARY

The site is dead for readers. Zero trader cards. Zero bubble data. All because `dashboard.js` fetches `stories-v3.json` — a file that **does not exist** on GCS. The Cloud Run job that was supposed to create it is failing (0/1 tasks complete). The VM pipeline generates fresh data every 10 minutes but deploys nothing. The VM's own deploy timer is disabled. Three separate systems run in parallel, overwriting each other. The site has not had a fresh deploy in over 3 hours.

**Root cause: THREE independent pipelines compete on the same tiny VM and GCS bucket, with no single deploy path.**

---

## 1. ARCHITECTURE — ACTUAL STATE (Not Documented)

```
                    ┌─────────────────────────────────────────────┐
                    │ CLOUD SCHEDULER (GCP)                       │
                    │ 2 ENABLED: gazzetta-pipeline-cron,          │
                    │            cco-distributor-cron              │
                    │ 5 PAUSED                                    │
                    └──────────────┬──────────────────────────────┘
                                   │ HTTP trigger
                                   ▼
                    ┌─────────────────────────────────────────────┐
                    │ CLOUD RUN gazzetta-pipeline (FAILING)       │
                    │ Docker image from June 16 (STALE)           │
                    │ Last execution: 20:10 UTC — FAILED (0/1)    │
                    │ Runs: db_to_json → build_site → deploy      │
                    │ Would deploy from site/ (wrong dir)         │
                    │ DOES NOT ACTUALLY DEPLOY (job fails)        │
                    └─────────────────────────────────────────────┘

                    ┌─────────────────────────────────────────────┐
                    │ VM: gazzetta-prod (35.188.110.255)          │
                    │ e2-micro, Debian 12, 969MB RAM              │
                    │ All files owned by gazzetta:gazzetta ✓      │
                    └──────────────┬──────────────────────────────┘
                                   │
          ┌────────────────────────┼─────────────────────────────┐
          │                        │                             │
          ▼                        ▼                             ▼
┌──────────────────┐  ┌──────────────────────┐  ┌─────────────────────┐
│ V1 LEGACY TIMERS │  │ V2 GOVERNOR (10 min) │  │ SHIPIT (DISABLED)   │
│ (as alexstocchi) │  │ (as gazzetta)        │  │ (as alexstocchi)    │
├──────────────────┤  ├──────────────────────┤  ├─────────────────────┤
│intel (30m):      │  │1.ingestion_triage ✓  │  │ shipit_cloud.py     │
│ fetch_intel.py   │  │2.market_reality ✓    │  │ copies data/ → site/│
│ → drafts table   │  │3.contradiction_synth │  │ deploys site/ → GCS │
│                  │  │  → REAL gaps (70-75) │  │ BUT: DISABLED       │
│marketdata (6h):  │  │4.db_to_json.py       │  │ AND: wrong dir      │
│ fetch_market_data│  │  → OVERWRITES gap=15 │  │ (site/ not public/) │
│ (OLD, orphaned)  │  │5.build_site ✓        │  │                     │
│                  │  │6.test_platform ✓     │  │                     │
│pipeline (60m):   │  │7. NO DEPLOY          │  │                     │
│ db_to_json.py    │  │8. check_mailbox      │  │                     │
│ → data/stories   │  │9. Telegram status    │  │                     │
└──────────────────┘  └──────────────────────┘  └─────────────────────┘
          │                        │
          │  DATA FLOW:            │  DATA FLOW:
          │  data/stories.json     │  public/data/stories.json
          │  (376 stories,         │  (376 stories, ALL gap=15,
          │   ALL gap=15)          │   generated_by db_to_json)
          │                        │
          └────────┬───────────────┘
                   │ NEITHER REACHES GCS
                   ▼
          ┌─────────────────────┐
          │ GCS BUCKET          │
          │ www.lagazzettadi... │
          │                     │
          │ stories.json:       │
          │  Updated: 17:57 UTC │
          │  (3+ HOURS STALE)   │
          │                     │
          │ stories-v3.json:    │
          │  DOES NOT EXIST     │ ← dashboard.js fetches THIS
          │                     │
          │ index.html:         │
          │  Updated: 17:31     │
          │  (3+ HOURS STALE)   │
          └─────────────────────┘
                   │
                   ▼
          ┌─────────────────────┐
          │ www.lagazzettadi... │
          │                     │
          │ 0 trader cards      │
          │ 8 bubbles (all 0)   │
          │ generated_at: 16:09 │
          │ All gaps: 15        │
          └─────────────────────┘
```

---

## 2. FINDINGS — WHAT IS BROKEN

### CRITICAL (Site Dead — No Reader Sees Content)

| # | Finding | Evidence |
|---|---------|----------|
| C1 | dashboard.js fetches `stories-v3.json` — does NOT exist on GCS | `gsutil ls gs://...data/stories-v3.json` returns "no objects matched". Browser console shows fetch fails. 0 trader cards render. |
| C2 | NO SYSTEM DEPLOYS TO GCS | Cloud Run gazzetta-pipeline job FAILING (0/1 tasks). VM gazzetta-shipit timer DISABLED. Governor has no deploy step. Last GCS update: 17:57 UTC (3h stale). |
| C3 | db_to_json.py overwrites real contradiction data | Governor step 3 produces gaps 70-75. Step 4 (db_to_json) overwrites ALL with gap=15. `generated_by: "db_to_json.py v2.0"`. Confirmed at 20:10 UTC. |
| C4 | THREE pipelines compete simultaneously | VM V1 timers + VM V2 governor + Cloud Run/Cloud Scheduler. They write to same DB, same files. Split-brain architecture. |
| C5 | Cloud Run + Cloud Scheduler STILL ACTIVE | 2 schedulers ENABLED (gazzetta-pipeline-cron, cco-distributor-cron). 7 Cloud Run jobs exist. Pipeline job fails every 10 min, consuming quota. |

### HIGH (Degraded — Would Block Recovery)

| # | Finding | Evidence |
|---|---------|----------|
| H1 | V1 legacy timers doing abandoned work | fetch_intel.py fills `drafts` table (543 pending, never approved). fetch_market_data.py orphaned. db_to_json.py competes with governor version. Wastes CPU/RAM on e2-micro. |
| H2 | 32 stale Docker images in Artifact Registry | 30 gazzetta-pipeline images (75-76MB each), 10 gazzetta-agents images (556MB each), 3 chief-architect images, 1 rd-agent image. Storage cost. |
| H3 | No monitoring or alerting | Pipeline failures are silent. Site staleness undetected. No heartbeat, no watchdog, no Telegram alert on failure. |
| H4 | Split user accounts | 4 V1 services run as `alexstocchi`, 1 V2 service runs as `gazzetta`. Startup script masks the issue but fragility remains. |

### MEDIUM (Technical Debt)

| # | Finding |
|---|---------|
| M1 | shipit_cloud.py deploys from `site/` but build_site writes to `public/` — directory mismatch |
| M2 | Governor has no deploy step — contradicts documented architecture |
| M3 | Cloud CDN stale-cache risk — no cache-busting on data files |
| M4 | .env file contains API keys in plaintext — no Secret Manager |
| M5 | `public/data/stories.json` has `generated_by: "db_to_json.py v2.0"` — should be contradiction_synthesizer |

---

## 3. DATA LINEAGE — WHERE DATA GETS LOST

```
STEP 1: ingestion_triage.py       → ingestion_hashes table (40 items, working)
STEP 2: market_reality.py         → data/market_prices.json (34 tickers, working)
STEP 3: contradiction_synthesizer → public/data/stories.json (REAL gaps 70-75)  ✓
STEP 4: db_to_json.py             → public/data/stories.json (OVERWRITES: all gap=15)  ✗ DESTROYS DATA
STEP 5: build_site.py             → public/*.html (8/9 files injected)  ✓
STEP 6: test_platform.py          → QA checks pass  ✓
STEP 7: DEPLOY                    → NOTHING HAPPENS  ✗ MISSING
       Cloud Run                  → FAILS (0/1 tasks)  ✗
       gazzetta-shipit            → DISABLED  ✗
       dashboard.js fetches       → stories-v3.json (DOES NOT EXIST)  ✗
                                  → READER SEES NOTHING  ✗
```

**The data is correct at Step 3. It is destroyed at Step 4. It never reaches GCS. The reader fetches a file that was never created.**

---

## 4. BOTTLENECK AND CHOKEPOINT CATALOG

### Resource Bottlenecks

| Resource | Limit | Current Usage | Risk |
|----------|-------|---------------|------|
| CPU | 0.25 vCPU | 3 pipelines competing | CPU starvation during overlap |
| RAM | 969MB | ~350MB used, 616MB avail | OK for now. No headroom. |
| Disk | 30GB | 3.6GB used (13%) | 32 Docker images wasting space |
| SQLite | WAL mode | 3 concurrent writers | Lock contention risk |
| DeepSeek API | Rate limit unknown | 2 consumers (governor + synthesizer) | Sequential, OK for now |

### Reliability Chokepoints

| Chokepoint | What Happens If It Fails | Detection |
|------------|--------------------------|-----------|
| DeepSeek API down | Contradiction scores stop updating | NONE — no alert |
| yfinance rate-limited | market_reality.py fails | NONE — no alert |
| VM restarts (IP changes) | SSH breaks, timers may not restart | Manual discovery |
| .env corrupted | Governor + Synthesizer both dead | NONE — no alert |
| gsutil loses auth | Deploy silently fails | Manual check |
| Cloud CDN caches stale data | Fixes don't reach readers | Manual curl |
| db_to_json overwrite | All gaps=15, site has no signal | NONE — no quality check |

### Data Quality Chokepoints

- All 376 stories have identical `contradiction_gap=15` (migration baseline)
- All 376 stories have identical `capital_volume_usd=100,000,000` (migration baseline)
- Zero stories have `tier=BREAKING`
- No lead story set
- No story freshness discrimination (all have same gap, same volume, same tier)

---

## 5. WHAT IS WORKING

| Component | Status | Detail |
|-----------|--------|--------|
| Governor pipeline (steps 1-3, 5-6) | PASS | Produces real data |
| ingestion_triage.py | PASS | 40 items, SHA-256 dedup |
| market_reality.py | PASS | 34 tickers, yfinance→AlphaVantage |
| contradiction_synthesizer.py | PASS | Real gap scores (70-75) via DeepSeek |
| build_site.py | PASS | 8/9 HTML injected |
| Sovereign Auditor (CEO) | PASS | DeepSeek v5 persona active |
| Mailbox (Alex→CEO→Alex) | PASS | inbox.json/outbox.json working |
| DeepSeek API (both keys) | PASS | Key 1 (local), Key 2 (VM) |
| SQLite DB (376 stories) | PASS | WAL mode, healthy |
| GCS bucket + website | PASS | Serving, just stale data |
| Diplomatic Ledger v28 design | PASS | Warm paper, gold separators deployed |
| VM health | PASS | 30GB disk, 969MB RAM, stable |

---

## 6. FIX PLAN

### Phase 1 — Stop the Bleeding (30 min, makes site work again)

**Step 1: Upload stories.json as stories-v3.json to GCS**
The dashboard fetches `stories-v3.json`. Upload the current data file to that path.
Command: `gsutil cp public/data/stories.json gs://www.lagazzettadikyiv.com/data/stories-v3.json`
Note: This is a tactical fix. The data still has gap=15. Phase 2 fixes the data.

**Step 2: Disable Cloud Run gazzetta-pipeline job**
This failing job consumes quota every 10 minutes and may corrupt GCS if it ever succeeds with old code.
Command: `gcloud run jobs update gazzetta-pipeline --region=europe-west1 --execute-now=false`
Also pause the scheduler: `gcloud scheduler jobs pause gazzetta-pipeline-cron --location=europe-west1`

**Step 3: Add deploy step to governor.py**
Add step 7 to the STEPS list in governor.py: gsutil rsync public/ to GCS.
This makes the VM self-sufficient — it ingests, analyzes, builds, AND deploys.

**Step 4: Deploy updated governor to VM**
SCP the modified governor.py to the VM. Restart timer.

### Phase 2 — Fix the Data (30 min, makes content real)

**Step 5: Remove db_to_json.py from governor pipeline**
Remove step 4 from STEPS list. The contradiction_synthesizer is the data producer. db_to_json should not overwrite it.

**Step 6: Update dashboard.js to fetch stories.json instead of stories-v3.json**
Or: have the governor's deploy step copy stories.json to stories-v3.json on GCS.
Either approach works. The file just needs to exist at the path dashboard.js fetches.

**Step 7: Run one full pipeline cycle and verify**
The site should show real contradiction gaps, non-zero bubbles, and trader cards.

### Phase 3 — Clean Up (30 min, removes dead weight)

**Step 8: Disable V1 legacy timers**
```bash
sudo systemctl stop gazzetta-intel.timer gazzetta-marketdata.timer gazzetta-pipeline.timer
sudo systemctl disable gazzetta-intel.timer gazzetta-marketdata.timer gazzetta-pipeline.timer gazzetta-shipit.timer
```

**Step 9: Unify service user**
Change all remaining service files to run as `gazzetta` user. Update startup_recovery.sh accordingly.

**Step 10: Pause/delete Cloud Run and Cloud Scheduler resources**
Pause remaining Cloud Scheduler jobs. Delete Cloud Run jobs after 1 week of VM stability.

**Step 11: Add monitoring**
Create `gazzetta-watchdog` timer (15 min): curl live site, check `generated_at` freshness, alert Telegram if >60 min stale.

---

## 7. TARGET ARCHITECTURE (After Fixes)

```
TIER 1: MacBook (Strategic Only)
  Alex → Hermes (DeepSeek Key 1)
  - Code, design, verification
  - NOT a deploy dependency

TIER 2: VM (Fully Autonomous)
  ONE timer: gazzetta-governor (10 min, as user gazzetta)
  ONE pipeline:
    1. ingestion_triage.py
    2. market_reality.py
    3. contradiction_synthesizer.py → stories.json (REAL gaps)
    4. build_site.py → HTML
    5. test_platform.py → QA gate
    6. gsutil rsync → DEPLOY to GCS
    7. check_mailbox → process Alex directives
    8. Telegram status

  ONE watchdog: gazzetta-watchdog (15 min)
    Curl live site → alert if stale

TIER 3: GCS + Cloud CDN
  Updated every 10 min by VM
  Readers see real data
```

---

## 8. VERIFICATION CHECKLIST (Post-Fix)

- [ ] `curl -s https://www.lagazzettadikyiv.com/data/stories-v3.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('generated_at'))"` returns timestamp <10 min old
- [ ] Browser: trader-card count > 0
- [ ] Browser: bubble labels show non-zero capital and gap values
- [ ] Browser console: no 404 errors on data fetch
- [ ] Browser: at least one story has `contradiction_gap > 60`
- [ ] Browser: at least one story has `tier = 'BREAKING'`
- [ ] VM: `systemctl is-enabled gazzetta-governor.timer` returns `enabled`
- [ ] VM: `systemctl is-active gazzetta-governor.timer` returns `active`
- [ ] VM: journalctl shows governor completing all steps including deploy

---

*Audit conducted by Hermes Agent (Sovereign Auditor v5 persona). Six-phase methodology: Infrastructure Discovery → Pipeline Audit → Bottleneck Investigation → Live Site Verification → Cross-Validation (3 subagents) → Final Report. All findings verified with direct tool calls — no assumptions, no documentation trust.*
