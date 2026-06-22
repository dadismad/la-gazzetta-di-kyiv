# La Gazzetta di Kyiv — Cloud Architecture & Infrastructure

## What This Is
A fully autonomous geopolitical intelligence newspaper. Every 30 minutes, software scrapes financial and news data, an LLM analyzes it for contradictions between official narratives and market reality, and a website is automatically built and deployed. There is no human editorial staff — the entire operation runs on code and AI.

---

## 1. WHERE IT RUNS

### Google Cloud Platform (GCP)
- **Project ID:** project-e5e0244c-b94d-41a1-810
- **Account:** pureciclismo@gmail.com
- **Credits:** $300 free credits available (Vertex AI can consume these, but Terms of Service not yet accepted)

### Virtual Machine (the "Governor")
- **Name:** gazzetta-prod
- **IP:** 34.132.179.205
- **Type:** e2-micro (smallest GCP VM, ~$7/month)
- **OS:** Debian 12
- **Location:** us-central1-a (Iowa, USA)
- **Code location:** /opt/gazzetta-di-kyiv/
- **Service account:** Has cloud-platform scope and IAM roles for storage

### Storage
- **Bucket:** gs://www.lagazzettadikyiv.com
- **CDN:** Google Cloud CDN (caches for 3600 seconds / 1 hour)
- **Live URL:** https://www.lagazzettadikyiv.com

### Local Machine (Hermes)
- **Location:** Alex's MacBook in Kyiv
- **Role:** Code editor, deploy pipeline, manual intervention
- **Code:** /Users/alexstocchi/lagazzettadikyiv/

---

## 2. THE TWO AI AGENTS

### Hermes (me)
- **Where:** Alex's MacBook
- **Model:** DeepSeek (deepseek-v4-pro)
- **Role:** Strategic assistant — code changes, architecture decisions, design work, manual interventions, troubleshooting
- **Communication:** Telegram (group "Stocchi Labs")
- **Has access to:** Terminal (SSH to VM), GCS (gsutil), browser, code editor, memory across sessions

### CEO / Governor
- **Where:** VM (gazzetta-prod)
- **Model:** DeepSeek (same provider, separate API key)
- **Role:** 24/7 editorial director — reviews every pipeline cycle, applies editorial judgment using Lefevre techniques (tape-reading, curiosity gaps, "why now" test), has 8 execution commands
- **Runs:** Via systemd timer every 30 minutes
- **Execution commands:**
  1. trigger_pipeline — force a full pipeline run
  2. rebuild_site — rebuild and redeploy the website
  3. set_gap_threshold — change contradiction sensitivity
  4. promote — promote a story to front page
  5. spike — kill/spike a story
  6. add_source — add a new RSS/data source
  7. run_step — run a single pipeline step
  8. config_set — change any configuration parameter
- **Mailbox system:** /opt/gazzetta-di-kyiv/mailbox/ (inbox.json / outbox.json)
- **Hermes can send directives** to the CEO by writing to the inbox; CEO responds in outbox

### Communication Between Hermes and CEO
- **Current method:** File-based mailbox on the VM (JSON files)
- **Problem:** No real-time connection, no persistent conversation, no shared context
- **Goal:** Establish proper agent-to-agent communication (API-based, bidirectional, with shared memory)

---

## 3. THE DATA PIPELINE (runs every 30 minutes)

### Step 1: Ingestion Triage
- **Script:** ingestion_triage.py
- **What it does:** Pulls from RSS feeds and YouTube, deduplicates articles using SHA-256 hashing
- **Database:** SQLite with WAL mode (Write-Ahead Logging for concurrent access)
- **Concurrency lock:** traffic_cop.py ensures only one pipeline runs at a time

### Step 2: Market Reality
- **Script:** market_reality.py
- **What it does:** Fetches financial data for 34 tickers mapped to 8 narratives
- **Data source:** yfinance (primary), AlphaVantage (fallback)
- **Example tickers:** UUP (dollar), USO/XLE (energy), EWG/EWZ (deglobalization), FXI (China), etc.

### Step 3: Contradiction Synthesis
- **Script:** contradiction_synthesizer.py
- **What it does:** DeepSeek-powered async analysis — compares ingested news against market data, finds contradictions between official narratives and market reality
- **Output:** stories.json with fields: reality, contradiction_gap (0-100), capital_volume_usd
- **What makes it unique:** It measures the GAP between what officials say and what markets bet

### Step 4: Database to JSON
- **Script:** db_to_json.py
- **Converts:** SQLite database → stories.json (site data file)
- **Also copies:** data files to public/data/ for the frontend

### Step 5: Build Site
- **Script:** build_site.py
- **What it does:** Injects header/footer from templates into HTML files
- **Template:** templates/header.html (contains the masthead design with Fox & Lion + crossed bulavas)
- **Test suite:** 94 automated checks run on every build (test_platform.py)
- **CSS:** styles.css — Diplomatic Ledger v28.0 design

### Step 6: Deploy (via local Hermes cron)
- **Problem:** VM's gsutil authentication is broken (can't write to GCS from VM)
- **Workaround:** Local MacBook cron runs `gsutil rsync -d public/ gs://www.lagazzettadikyiv.com/` every 10 minutes
- **This is a known fragility** — if the MacBook is offline, the site doesn't update

---

## 4. THE 8 NARRATIVES (Editorial Structure)

Each narrative tracks a specific domain of global capital flow:

1. **Strategic Energy Sovereignty** — Oil, gas, renewables, nuclear geopolitics
2. **Monetary Order Collapse** — Dollar hegemony, BRICS, CBDCs, gold flows
3. **Supply Chain Fragmentation** — Deglobalization, reshoring, trade wars
4. **China's Hegemonic Path** — Belt & Road, military expansion, tech competition
5. **Space & Orbital Infrastructure** — Satellites, space mining, orbital weapons
6. **Biotechnology & Longevity** — Gene editing, mRNA platforms, biosecurity
7. **Artificial Intelligence Convergence** — AI race, chips, autonomous weapons
8. **Sovereign Wealth & Soft Power Sports** — Sports washing, sovereign funds, cultural influence

---

## 5. DESIGN SYSTEM — Diplomatic Ledger v28.0

- **Concept:** Archival paper ledger where capital movements are recorded, not a news website
- **Colors:** Warm paper (#FAF9F6), gold separators (#D4AF37), deep charcoal text (#1A1C1A)
- **Typography:** Playfair Display (headlines), Inter (body)
- **Style:** Sharp corners (0px radius), 16px margins, gold rules between stories
- **Files:** styles.css (no hashing — hashed filenames caused deploy breakage)

---

## 6. KNOWN PROBLEMS & FRAGILITIES

### Critical
1. **No real agent-to-agent protocol** — Hermes and CEO communicate via file-based mailbox, not API. Can't share context, can't collaborate in real-time
2. **Deploy depends on Alex's MacBook** — If the MacBook is asleep or offline, site updates stop (VM can build but can't deploy to GCS)
3. **CDN cache delay** — 1-hour cache means design changes take up to an hour to appear
4. **Single VM** — No redundancy, no scaling, single point of failure

### Medium
5. **DeepSeek dependency** — Both Hermes and CEO use DeepSeek. If the API is down, the entire operation stops
6. **No Vertex AI integration** — $300 GCP credits are unused because Terms of Service not accepted
7. **CSS hashing legacy** — Old hashed CSS filenames (styles.15cf53ec.css) still exist and cause confusion
8. **No monitoring/alerting** — If the pipeline fails silently, nobody knows

### Low
9. **No distribution automation** — Reddit/Telegram posting not yet wired
10. **SQLite scales poorly** — 376 stories and growing; no migration path to PostgreSQL

---

## 7. WHAT NEEDS TO HAPPEN NEXT

### Immediate
1. **Fix GCS deploy from VM** — So the site updates even when Alex's MacBook is offline
2. **Establish proper agent-to-agent API** — Hermes ↔ CEO real-time communication
3. **Accept Vertex AI Terms of Service** — Unlock GCP credits for the CEO

### Short-term
4. **Add monitoring** — Health checks, failure alerts to Telegram
5. **Fix CDN caching strategy** — Shorter cache times for HTML, or cache invalidation on deploy
6. **Automate distribution** — Post new stories to Reddit (r/LaGazzettadiKyiv) and Telegram channel

### Long-term
7. **Multi-model resilience** — Fallback to alternative LLMs if DeepSeek is down
8. **Upgrade VM** — e2-micro is sufficient but constrained; migrate to e2-small or add a second VM
9. **Database migration** — SQLite to PostgreSQL for scale

---

## 8. KEY TECHNICAL DETAILS FOR INTEGRATION

- **Hermes is on Alex's MacBook** — Filesystem access, SSH to VM, gsutil to GCS
- **CEO is on VM 34.132.179.205** — Python scripts, systemd timers, mailbox JSON
- **Deploy:** `/Users/alexstocchi/lagazzettadikyiv/devvit/google-cloud-sdk/bin/gsutil -m rsync -d -r public/ gs://www.lagazzettadikyiv.com/`
- **SSH:** `ssh -i ~/.ssh/google_compute_engine gazzetta@34.132.179.205`
- **Database:** `/opt/gazzetta-di-kyiv/data/gazzetta.db` (SQLite, WAL mode, 5.4MB)
- **Stories:** `/opt/gazzetta-di-kyiv/public/data/stories.json`
- **CSS:** `/opt/gazzetta-di-kyiv/public/styles.css`
- **Config/Env:** `/opt/gazzetta-di-kyiv/.env` (DeepSeek API keys, Telegram bot token)
- **DeepSeek API Key 1:** Used by Hermes (local)
- **DeepSeek API Key 2:** Used by CEO (on VM)

---

## 9. THE VISION

La Gazzetta di Kyiv is not a traditional newspaper. It does not report events. It measures the gap between what power says and what capital does. Every 30 minutes, it scans the world, runs the numbers, and publishes the contradiction.

The goal is to make this fully autonomous — two AI agents (Hermes for strategy, CEO for execution) running a cloud-native intelligence operation that needs zero human intervention except for Alex's editorial vision and decision-making.
