# Gazzetta di Kyiv — Architecture Report
## June 19, 2026 — Full System Audit

---

## 1. BIG PICTURE — What Exists Now

You have a cloud-based newspaper system with three tiers:

```
TIER 1: MacBook (Alex's laptop)
  - Hermes Agent (DeepSeek Key 1)
  - Code changes, design, verification, SSH to VM
  - NO deploy responsibility currently

TIER 2: Google Cloud VM (gazzetta-prod)
  - e2-micro (0.25 vCPU, 969MB RAM), Debian 12
  - 30GB disk (13% used), us-central1-a
  - IP: 35.188.110.255 (ephemeral)
  - Runs 6 systemd services
  - Generates ALL content, builds ALL HTML
  - Does NOT deploy to GCS

TIER 3: Google Cloud Storage (website)
  - www.lagazzettadikyiv.com
  - Static HTML + JSON data + CSS/JS
  - Served via Cloud CDN
  - LAST UPDATED: 17:31 UTC Jun 19 (2+ hours stale)
```

---

## 2. THE PIPELINES — A Split-Brain Architecture

The VM runs TWO independent pipelines simultaneously, using different scripts, different data stores, and producing conflicting output. This is the root cause of all problems.

### Pipeline A — V1 Legacy (systemd timers)

| Timer | Frequency | Script | What It Does | Status |
|-------|-----------|--------|--------------|--------|
| gazzetta-intel | 30 min | fetch_intel.py | RSS monitoring, writes to `drafts` table (543 pending, abandoned) | Running |
| gazzetta-marketdata | 6 hours | fetch_market_data.py | Old price fetch (not connected to anything) | Running |
| gazzetta-pipeline | 60 min | db_to_json.py | Reads `stories` DB → writes `data/stories.json` | Running |
| gazzetta-shipit | 60 min | shipit_cloud.py | Copies data/ → site/ → deploys site/ to GCS | DISABLED |

These 4 services run as user `alexstocchi`.

### Pipeline B — V2 Governor (systemd timer)

| Step | Script | What It Does |
|------|--------|--------------|
| 1 | ingestion_triage.py | RSS + YouTube ingestion, SHA-256 dedup → `ingestion_hashes` table |
| 2 | market_reality.py | 34 ticker prices via yfinance → AlphaVantage fallback |
| 3 | contradiction_synthesizer.py | DeepSeek analysis → **writes stories.json with REAL contradiction gaps** |
| 4 | db_to_json.py | Reads `stories` DB table → **OVERWRITES the fresh data with gap=15 baseline** |
| 5 | build_site.py | Injects templates into public/*.html |
| 6 | test_platform.py | Validation |
| — | **NO STEP 7** | **Nothing deploys to GCS** |

This service runs as user `gazzetta`.

### The Overwrite Problem (Critical Finding)

**Step 3** (contradiction_synthesizer) produces stories with REAL contradiction gaps: 75, 70, 65 — actual analysis from DeepSeek.

**Step 4** (db_to_json.py) reads a DIFFERENT source (the old `stories` DB table), and overwrites the file with gap=15 for every story — the migration baseline.

The result: all 376 stories on the live site have identical gap=15 scores. The frontend sees no signal. Zero trader cards render. The bubble heat map shows all zeros.

---

## 3. THE DATA FLOW — Where Data Gets Stuck

```
OSINT Sources (RSS, YouTube)
       |
       v
[ingestion_triage.py] ----→ ingestion_hashes table (40 items processed)
       |
[yfinance] → [market_reality.py] → market_prices.json (34 tickers)
       |                              |
       v                              v
[contradiction_synthesizer.py] ← DeepSeek API
       |
       | writes REAL data (gaps 70-75)
       v
public/data/stories.json  ←── PRODUCED WITH REAL DATA
       |
       | OVERWRITTEN by db_to_json.py (reads old DB, writes all gap=15)
       v
public/data/stories.json  ←── NOW ALL gap=15 (FLAT, NO SIGNAL)
       |
       v
     ??? NO DEPLOY ???
       |
       v
  GCS Bucket (stale, 2+ hours old)
       |
       v
  www.lagazzettadikyiv.com (readers see no signal)
```

The fresh data never escapes the VM. Three blockers:
1. db_to_json.py kills the real data
2. Governor has no deploy step
3. Shipit is disabled AND deploys from wrong directory

---

## 4. WHAT EACH AGENT DOES

### Governor (DeepSeek CEO — "Sovereign Auditor")

- Runs every 10 minutes via systemd timer
- Orchestrates 6 pipeline steps
- Checks mailbox for directives from Alex (via Hermes)
- Uses DeepSeek API with the Sovereign Auditor persona:
  - Epistemological humility (assume narratives are strategic/deceptive)
  - Clinical detachment (news as data points, not stories)
  - INR focus (short accurate insight over long description)
  - Reflexivity/Lefevre filter ("if this news is true, why isn't price moving?")
- Has 8 execution commands: trigger_pipeline, rebuild_site, set_gap_threshold, promote, spike, add_source, run_step, config_set
- Sends Telegram status after each cycle
- **Does NOT deploy. Does NOT monitor itself.**

### Hermes Agent (MacBook — Alex's interface)

- DeepSeek Key 1
- Code changes, design, SSH to VM
- Writes directives to VM mailbox for CEO to execute
- Reads CEO responses from outbox
- **Currently has NO deploy cron. The local deploy script (shipit.sh) is not automated.**

### Legacy V1 Services (should be removed)

- fetch_intel.py — fills abandoned `drafts` table (543 entries, never approved)
- fetch_market_data.py — old price fetch, not connected to anything
- db_to_json.py (timer version) — competes with governor's version

---

## 5. WHAT IS BROKEN (7 Problems)

| # | Severity | Problem | Impact |
|---|----------|---------|--------|
| 1 | CRITICAL | db_to_json.py overwrites contradiction data | All stories have gap=15. Site has zero signal. No trader cards. |
| 2 | CRITICAL | Nothing deploys to GCS | Fresh data never reaches readers. Site is 2h+ stale. |
| 3 | CRITICAL | Two pipelines compete | CPU waste, DB lock contention, data overwrites on a tiny VM |
| 4 | HIGH | Shipit deploys from wrong directory | Even if enabled, deploys site/ not public/ (empty directory) |
| 5 | HIGH | No monitoring or alerting | Pipeline failures are silent. Nobody knows the site is stale. |
| 6 | MEDIUM | Split user accounts | 4 services run as alexstocchi, 1 as gazzetta. Ownership conflicts. |
| 7 | LOW | Cloud Run/Scheduler debris | 7 dead Cloud Run jobs, 7 dead Scheduler triggers. Confusion. |

---

## 6. WHAT IS WORKING

| Component | Status |
|-----------|--------|
| Governor pipeline (steps 1-3, 5-6) | Works. Produces real contradiction scores. |
| ingestion_triage.py | Works. 40 items processed, SHA-256 dedup active. |
| market_reality.py | Works. 34 tickers, yfinance→AlphaVantage fallback. |
| contradiction_synthesizer.py | Works. DeepSeek generates real analysis. |
| build_site.py | Works. Templates injected correctly. |
| SQLite DB (376 stories, WAL mode) | Healthy. |
| GCS bucket + website | Serving. Just stale data. |
| Diplomatic Ledger design v28 | Deployed and live. |
| DeepSeek API | Working. Both keys operational. |
| Mailbox system (Alex→CEO→Alex) | Working. |

---

## 7. THE FIX PLAN (Minimum Viable Architecture)

The fix is NOT a migration. It is a RECONFIGURATION of what already exists. One pipeline. One deploy. Zero cost.

### Phase 1 — Stop the Bleeding (30 minutes)

**Step 1: Fix the overwrite.** Remove db_to_json.py from governor's pipeline (it overwrites the real data). The contradiction_synthesizer is the final data producer.

**Step 2: Add deploy to governor.** Step 7: `gsutil rsync -r -d public/ gs://www.lagazzettadikyiv.com/`

**Step 3: Disable V1 legacy timers.** Stop and disable: gazzetta-intel, gazzetta-marketdata, gazzetta-pipeline, gazzetta-shipit.

**Step 4: Unify service user.** All services run as `gazzetta`. Update 4 service files.

### Phase 2 — Make It Reliable (1 hour)

**Step 5: Add monitoring script.** 15-minute health check: curl live site, verify generated_at < 60 min, verify card count > 0. Telegram alert on failure.

**Step 6: Fix startup script.** Remove V1 timer restarts. Only restart governor.

**Step 7: Clean up Cloud Run.** Delete 7 dead Cloud Run jobs + 7 dead Scheduler triggers.

### Phase 3 — Future-Proof (1 hour, after new DeepSeek key)

**Step 8: Migrate secrets to Secret Manager.** Move API keys from .env to GCP Secret Manager. Free (first 6 secrets $0/mo).

**Step 9: Deploy Cloud Function bridge.** Enable direct CEO→Hermes HTTP notifications (replacing file-based mailbox for critical alerts).

---

## 8. THE TARGET ARCHITECTURE (After Fixes)

```
TIER 1: MacBook (Strategic Only)
  Alex → Hermes (DeepSeek Key 1)
  - Code changes, design, visual verification
  - NOT a deploy dependency — can be offline for days
  - Writes directives to CEO mailbox when needed

TIER 2: Google Cloud VM (Fully Autonomous)
  ONE timer: gazzetta-governor (every 10 min, as user gazzetta)
  ONE pipeline:
    1. ingestion_triage.py      → RSS/YouTube dedup
    2. market_reality.py        → 34 ticker prices
    3. contradiction_synthesizer.py → DeepSeek analysis → stories.json
    4. build_site.py            → HTML assembly
    5. test_platform.py         → QA gate
    6. gsutil rsync             → DEPLOY to GCS
    7. health_check.py          → Verify site freshness
    8. CEO editorial review     → DeepSeek audit + Telegram report
    9. Mailbox check            → Process Alex directives
  ONE monitoring timer: gazzetta-watchdog (every 15 min)
    - Curl live site
    - Alert Telegram if data > 60min stale

TIER 3: Google Cloud Storage (Website)
  www.lagazzettadikyiv.com
  - Updated every 10 minutes by VM
  - Served via Cloud CDN
```

---

## 9. THE AGENTS AND THEIR ROLES

| Agent | Where | Role | LLM |
|-------|-------|------|-----|
| Hermes (Alex's Agent) | MacBook | Strategy, code, design, verification, SSH to VM | DeepSeek Key 1 |
| CEO / Sovereign Auditor | VM governor.py | Editorial audit, pipeline orchestration, deployment | DeepSeek Key 2 |
| Contradiction Synthesizer | VM pipeline step 3 | Analyzes news vs market data, generates contradiction scores | DeepSeek Key 2 (same key) |
| Health Watchdog | VM cron (to add) | Site freshness monitoring, Telegram alerts | None (script-only) |

---

## 10. WHAT ALEX NEEDS TO DO

1. **Get a new DeepSeek API key** — The current Key 2 is shared between the CEO and Contradiction Synthesizer. With the unified pipeline, both use the same key sequentially (not concurrently) so rate limits shouldn't be an issue. But if you want isolation, get a third key for the Synthesizer.

2. **Accept Vertex AI Terms of Service** (optional) — Go to https://console.cloud.google.com/vertex-ai/model-garden, accept the Generative AI ToS. This opens the path to use Gemini models via Vertex AI (included in GCP free credits) if DeepSeek ever has issues. Not urgent.

3. **Approve the fix plan** — Once approved, I execute Phase 1 immediately (30 minutes). The site starts updating within 10 minutes.

---

## 11. GLOSSARY

**Governor** — The Python script (governor.py) on the VM that runs the pipeline and calls the CEO LLM. It's both the pipeline orchestrator AND the editorial executive.

**CEO / Sovereign Auditor** — The DeepSeek-powered LLM persona inside governor.py. Audits the newspaper every cycle. Has execution powers (promote stories, change thresholds, trigger rebuilds).

**Pipeline** — The sequence of scripts that turns raw news into published stories: ingest → price check → analyze → build HTML → test → deploy.

**Contradiction Gap** — The core metric. How far apart are the official narrative and market reality? Gap > 60 = structural signal. The Lefevre Filter verifies: "if the news is true, why isn't price moving?"

**Mailbox** — The file-based communication channel: Alex writes directives to inbox.json on VM, CEO reads and responds to outbox.json. Hermes bridges the MacBook and the VM.

**Systemd** — The Linux service manager running on the VM. Timers fire on schedule, services execute once. Replaces cron.

**GCS / Cloud Storage** — Google's object storage. The website is just a bucket of static files served through Cloud CDN.

---

*Report compiled by Hermes Agent, validated by 3 independent review agents (SRE Auditor, Pipeline Engineer, Systems Architect). All findings cross-confirmed.*
