# Gazzetta di Kyiv — Systems Architecture Audit

## 1. What the Architecture SHOULD Be (Single Coherent Pipeline)

```
┌─────────────────────────────────────────────────────────┐
│                    GOVERNOR (v2)                         │
│  Timer: every 10 min                                    │
│                                                         │
│  1. ingestion_triage.py     → ingestion_hashes table    │
│  2. market_reality.py --all → data/market_prices.json   │
│  3. contradiction_synthesizer.py → stories table        │
│  4. db_to_json.py           → public/data/stories.json  │
│  5. build_site.py           → inject HTML components    │
│  6. test_platform.py        → validate output           │
│  7. DEPLOY TO GCS           → gsutil rsync to bucket    │
│                                                         │
│  └── deploy_routine.sh or inlined deploy step           │
│                                                         │
│  Monitoring: health_check.py (runs after deploy)        │
│  Secrets: .env file via EnvironmentFile= in systemd     │
│  Lock: traffic_cop.py (PipelineLock via SQLite)         │
│  Concurrency: systemd oneshot (no concurrent runs)      │
└─────────────────────────────────────────────────────────┘
```

This is a **single, linear, oneshot pipeline** triggered by a systemd timer. One process runs to completion, then exits. No overlap, no races, no parallel systems.

**Key properties of the ideal state:**
- **One authoritative ingestion path**: `ingestion_hashes` table with SHA-256 dedup
- **One authoritative market data path**: `market_reality.py` (yfinance → AlphaVantage fallback)
- **One db_to_json.py call** per cycle
- **Deploy is the terminal step** — the pipeline is not complete until GCS is updated
- **Lock ensures idempotency** — `traffic_cop.PipelineLock` prevents concurrent runs
- **Systemd oneshot** — timer guarantees at most one running instance
- **Single user account** — gazzetta:gazzetta owns /opt/gazzetta-di-kyiv

---

## 2. What It Currently IS (Fragmented with 2 Parallel Systems)

```
┌─────────────────── VM: gazzetta-prod ───────────────────┐
│                                                         │
│  SYSTEM 1: OLD v1 (possibly still running via systemd)  │
│  ─────────────────────────────────────────────────────   │
│                                                         │
│  gazzetta-intel.timer (every 30min)                     │
│   └── fetch_intel.py  → writes to   `drafts` table      │
│                                                         │
│  gazzetta-marketdata.timer (every 10min)                │
│   └── fetch_market_data.py → data/market_prices.json    │
│                                                         │
│  gazzetta-pipeline.timer (every 10min)                  │
│   └── intel_to_stories.py                               │
│   └── db_to_json.py         → public/data/stories.json  │
│   └── build_site.py                                     │
│   └── test_platform.py                                  │
│                                                         │
│  gazzetta-shipit.timer [DISABLED]                       │
│   └── shipit_cloud.py → deploys from WRONG directory    │
│                                                         │
│  SYSTEM 2: NEW v2 (service defined but NOT installed)    │
│  ─────────────────────────────────────────────────────   │
│                                                         │
│  gazzetta-governor.timer (every 10min) [NOT INSTALLED]  │
│   └── governor.py orchestrates:                         │
│        1. ingestion_triage.py   → ingestion_hashes tbl  │
│        2. market_reality.py     → data/market_prices.json│
│        3. contradiction_synthesizer.py → stories table  │
│        4. db_to_json.py         → public/data/stories.j.│
│        5. build_site.py                                 │
│        6. test_platform.py                              │
│        ⚠ NO DEPLOY STEP at end!                         │
│                                                         │
│  CONFLICT ZONE:                                          │
│  ───────────────                                         │
│  Both pipelines call db_to_json.py on the same DB       │
│  → They race writing public/data/stories.json            │
│  → diff ingestion tables (drafts vs ingestion_hashes)   │
│  → diff market data providers                           │
│  → diff user accounts (alexstocchi vs gazzetta)         │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────── LEGACY CLOUD ARTIFACTS ─────────────────┐
│                                                         │
│  Dockerfile       — Cloud Run container (never used)    │
│  cloud_entrypoint.py — Cloud Run entrypoint (never used)│
│  cloudbuild.yaml  — CI/CD pipeline (never triggered)    │
│  Cloud Scheduler  — would trigger Cloud Run (not set up)│
│  Secret Manager   — referenced but never created        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Specific Problems (mapped to numbered items):

| # | Problem | Evidence |
|---|---------|----------|
| 1 | **Parallel pipelines overlap on db_to_json.py** | Both v1 systemd services and v2 governor.py call db_to_json.py. They race on `public/data/stories.json` |
| 2 | **Different ingestion paths** | v1: fetch_intel.py → `drafts` table. v2: ingestion_triage.py → `ingestion_hashes` table (SHA-256 dedup). Different tables, different hashing, different columns |
| 3 | **Different market data paths** | v1: fetch_market_data.py (8 tickers, simple). v2: market_reality.py (34 tickers across 8 narratives with AlphaVantage fallback) |
| 4 | **Governor never deploys** | governor.py's `cycle()` runs all 6 STEPS (lines 441-448) but has zero GCS sync. The `rebuild_site` EXEC command only runs db_to_json+build_site+test_platform — no `gsutil rsync` |
| 5 | **Shipit disabled + wrong dir** | shipit_cloud.sh is bash that references `$PROJECT/public/` but the old shipit_cloud.py references wrong paths. Service is disabled. |
| 6 | **No deploy step in governor cycle** | governor.py STEPS list (line 441) ends at test_platform. No `DEPLOY` step exists. |
| 7 | **Split user accounts** | Service file says `User=gazzetta`. All local dev under `alexstocchi`. Permissions issues on lock files |
| 8 | **No monitoring/alerting** | health_check.py exists in OLD repo (~/gazzetta-di-kyiv/scripts/) but NOT in the active repo. References services that may not exist. |
| 9 | **No Secret Manager** | .env file exposed. cloud_entrypoint.py references Secret Manager but entirely unimplemented |
| 10 | **Legacy Cloud Run/Scheduler** | Dockerfile + cloud_entrypoint.py + cloudbuild.yaml from commit 6dec520. Never deployed. Adds maintenance debt. |

---

## 3. Minimum Changes to Make It Work Reliably

### CRITICAL (P0 — must do for a working system)

**1. Kill v1 entirely on the VM**
- Disable and stop: `gazzetta-intel`, `gazzetta-marketdata`, `gazzetta-pipeline`, `gazzetta-shipit`
- Delete their service and timer files from `/etc/systemd/system/`
- Delete old scripts: `fetch_intel.py`, `fetch_market_data.py` (or leave as dead code, disable execution)
- Result: one pipeline path, zero races

**2. Add deploy step to governor.py**
- Insert a `DEPLOY` step as STEP 7 in the STEPS list after test_platform
- Should: `gsutil -m rsync -r public/ gs://www.lagazzettadikyiv.com/`
- Set cache headers (HTML: max-age=0, JSON: no-store, CSS/JS: immutable)
- Verify with HTTP 200 check via curl after sync

**3. Install governor service + timer on VM**
```
sudo cp ops/gazzetta-governor.service /etc/systemd/system/
sudo cp ops/gazzetta-governor.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gazzetta-governor.timer
```
- Verify: `systemctl list-timers | grep gazzetta`
- Monitor: `journalctl -u gazzetta-governor -f -n 50`

**4. Fix the WorkingDirectory in governor service file**
- Current: `WorkingDirectory=/opt/gazzetta-di-kyiv`
- If VM uses different path, correct it. Ensure `gazzetta` user owns the tree.
- Ensure `gazzetta` user is in the group that can write to the GCS bucket via gcloud auth

### HIGH (P1 — reliability, observability)

**5. Add health_check.py to the active repo**
- Move from `~/gazzetta-di-kyiv/scripts/` → `~/lagazzettadikyiv/scripts/`
- Update to check only `gazzetta-governor` service (single source of truth)
- Add as final step after deploy in governor, or run as periodic cron

**6. Add pipeline_state monitoring**
- Already have `traffic_cop.py` PipelineLock — extend to record last cycle timestamp + status
- Have governor.py write a `data/cycle_health.json` with: ok/fail, step timings, story count
- This enables external monitoring to detect stuck pipelines

**7. Fix user/permissions on VM**
- Ensure one user (`gazzetta` or `alexstocchi`) owns the entire `/opt/gazzetta-di-kyiv/` tree
- Match the `User=` line in governor service file
- Test: `sudo -u gazzetta python3 scripts/governor.py`

### MEDIUM (P2 — polish, cleanup)

**8. Clean up legacy artifacts in repo**
- Delete: `Dockerfile`, `cloud_entrypoint.py`, `agents_build/`, `.dockerignore`, `.gcloudignore`
- Delete: `devvit/google-cloud-sdk/` (1GB+ of dead SDK)
- These are from Sprint 3 Cloud Run experiment — never used, never will be

**9. Consolidate config**
- `config.yaml` (v1 pipeline chain) is stale — references old scripts like `fetch_intel.py`, `intel_to_stories.py`, `decay_stories.py`, `validate_stories.py`, `generate_flows.py`
- Either update it to reflect the v2 pipeline or remove it entirely (govvernor.py uses hardcoded STEPS)

**10. Add deploy_routine.sh integration or retire it**
- Currently, `deploy_routine.sh` does the same thing as governor.py would after adding deploy — it's a shell alternative
- Either: (a) have governor.py call deploy_routine.sh as its final step, or (b) inline GCS sync in governor.py
- If (a), keep deploy_routine.sh. If (b), mark deploy_routine.sh as deprecated.

---

## 4. What Can Be REMOVED to Simplify

### REMOVE IMMEDIATELY (dead code, no impact)

| Artifact | Reason |
|----------|--------|
| `fetch_intel.py` | v1 ingestion, replaced by ingestion_triage.py |
| `fetch_market_data.py` | v1 market data, replaced by market_reality.py |
| `intel_to_stories.py` | v1 pipeline stage, replaced by contradiction_synthesizer.py |
| `decay_stories.py` | v1 pipeline stage, feature flag `decay_stories: false` |
| `validate_stories.py` | v1 pipeline stage |
| `generate_flows.py` | v1 pipeline stage |
| `enrich_multi_persona.py` | Only called from shipit.sh (disabled) |
| `enrich_editorial_stories.py` | Only called from shipit.sh |
| `ensure_generated_at.py` | Only called from shipit.sh |
| `generate_signal_api.py` | Only called from shipit.sh |
| `generate_trades_api.py` | Only called from shipit.sh |
| `build_track_record.py` | Only called from shipit.sh |
| `fetch_live_prices.py` | Only called from shipit.sh |
| `build_related_links.py` | Only called from shipit.sh |
| `build_hashed_assets.py` | Creates hashed CSS — root cause of hash rot |
| `shipit_cloud.sh` | Disabled, wrong paths |
| `shipit.sh` | Heavy deploy script, not used in production |
| `gcf_governor_bridge.py` | Cloud Function bridge — never deployed |
| `cloud_entrypoint.py` | Cloud Run entrypoint — never deployed |
| `Dockerfile` | Cloud Run — never deployed |
| `agents_build/` (entire directory) | CCO/CDO agent code — unrelated to core pipeline |

### REMOVE AFTER CONSOLIDATION (clean up in phase 2)

| Artifact | Reason |
|----------|--------|
| `config.yaml` | Pipeline chain definition is stale (references v1 scripts). Keep if used by something else |
| `devvit/google-cloud-sdk/` | 1GB+ of SDK — use system install or gcloud CLI instead |
| `deploy_routine.sh` | Only if deploy is inlined in governor.py |
| Old service files on VM | `gazzetta-intel`, `gazzetta-marketdata`, `gazzetta-pipeline`, `gazzetta-shipit` |
| `gazzetta-di-kyiv/` (parallel repo at ~/) | Contains only health_check.py — relocate that file and delete the directory |

### KEEP (core architecture)

| Artifact | Role |
|----------|------|
| `governor.py` | Pipeline orchestrator — KEEP and add deploy step |
| `traffic_cop.py` | Concurrency lock — KEEP |
| `circuit_breaker.py` | API retry logic — KEEP |
| `ingestion_triage.py` | SHA-256 dedup ingestion — KEEP |
| `market_reality.py` | yfinance+AlphaVantage market data — KEEP |
| `contradiction_synthesizer.py` | DeepSeek enrichment — KEEP |
| `db_to_json.py` | DB→JSON compilation — KEEP |
| `build_site.py` | HTML component injection — KEEP |
| `test_platform.py` | Output validation gate — KEEP |
| `ops/gazzetta-governor.service` | systemd unit — KEEP (install on VM) |
| `ops/gazzetta-governor.timer` | systemd timer — KEEP (install on VM) |
| `shipit.sh` / `deploy_routine.sh` | KEEP ONE as deploy reference (integrate into governor.py) |

---

## Min Viable Architecture Summary

```
gazzetta-governor.timer (every 10 min, ~10s randomized delay)
│
└── gazzetta-governor.service (oneshot, User=gazzetta)
    │
    ├── 1. ingestion_triage.py          (RSS+YouTube → ingestion_hashes)
    ├── 2. market_reality.py --all      (34 tickers → market_prices.json)
    ├── 3. contradiction_synthesizer.py (DeepSeek → stories table)
    ├── 4. db_to_json.py                (stories → public/data/stories.json)
    ├── 5. build_site.py                (inject masthead/footer into HTML)
    ├── 6. test_platform.py             (validate 8-narrative integrity)
    ├── 7. DEPLOY: gsutil rsync         (public/ → GCS bucket)
    └── 8. health_check.py              (verify HTTP 200, story count)
```

**Total: 3 files to install on VM** (service, timer, .env)
**Total: 8 Python scripts** (6 pipeline + traffic_cop + circuit_breaker)
**Total: 10+ files to delete** (dead v1 scripts, Cloud Run artifacts, stale config)

**One pipeline. One timer. One deploy target. No races.**
