# MASTER ARCHITECTURE AUDIT PROMPT
## For Hermes Agent — Gazzetta di Kyiv System Audit

---

## YOUR MISSION

You are conducting a comprehensive architecture audit of La Gazzetta di Kyiv — a contradiction-first capital flow intelligence newspaper running on Google Cloud infrastructure. This is not a casual check. This is a forensic, professional-grade system audit. You will leave no file unread, no script untraced, no data path unmapped.

---

## PHASE 0 — PRE-FLIGHT

Before any investigation, load these skills in order:

1. `gazzetta-newspaper-engine` — pipeline, editorial, deployment
2. `gazzetta-cloud-infrastructure` — VM, systemd services, GCP resources
3. `gazzetta-knowledge-index` — project topology, scripts, reference files

Then read the binding operational rulebook: `HERMES_OPERATIONAL_SOP.md` at the project root. All 8 SOP rules are in effect during this audit.

Project root: `~/lagazzettadikyiv/`

---

## PHASE 1 — INFRASTRUCTURE DISCOVERY

Map EVERYTHING. Do not assume. Verify.

### 1.1 Cloud Resources
- List all GCP resources: VMs, buckets, Cloud Run jobs, Cloud Scheduler triggers, Artifact Registry images, Secret Manager secrets, IAM bindings
- For each resource: status, last activity, cost, whether it's actually used
- Identify dead/orphaned resources consuming quota or causing confusion

### 1.2 VM State
- SSH to `gazzetta-prod` (resolve IP via gcloud, never hardcode)
- Document: OS, CPU, RAM, disk usage, uptime, running processes
- List ALL systemd units (timers and services) with gazzetta prefix
- For each timer: schedule, last fire time, whether it succeeded or failed
- For each service: what script it runs, as which user, with what environment
- Check journalctl for the last 5 runs of each service — capture any errors

### 1.3 File System
- List every file in `/opt/gazzetta-di-kyiv/` — scripts, templates, data, public, config
- Compare VM files against local repo: identify drift, missing files, extra files
- Check ownership (ls -la) on all directories — note any root-owned files that services need to write
- Verify .env file is readable by the service user, contains required keys

### 1.4 Local Environment
- List every script in `scripts/`
- List every file in `public/` and `data/`
- List every template in `templates/`
- Identify any cron jobs (Hermes cron, launchd, crontab)
- Check git status — uncommitted changes, branch state

---

## PHASE 2 — PIPELINE ARCHITECTURE AUDIT

This is the core of the audit. You are tracing data from origin to reader.

### 2.1 Service-to-Script Mapping

For every systemd service on the VM, answer:
- What script does it execute?
- What is the full command line (including arguments)?
- What user does it run as?
- What environment variables does it inherit?
- What files/directories does it need write access to?
- Does it have those permissions?

### 2.2 Script Deep Dive

For EVERY Python script in the pipeline (ingestion_triage.py, market_reality.py, contradiction_synthesizer.py, db_to_json.py, build_site.py, test_platform.py, governor.py, fetch_intel.py, fetch_market_data.py, shipit_cloud.py):

Read the script line by line. Document:
- What it reads (files, DB tables, environment variables)
- What it writes (files, DB tables, stdout)
- What APIs it calls (DeepSeek, yfinance, AlphaVantage, Telegram)
- What order it must run relative to other scripts
- What errors it handles (try/except blocks)
- What errors it does NOT handle (dangerous assumptions)
- What exit codes it produces on failure
- Whether it uses atomic writes or writes directly to live files

### 2.3 Data Lineage

Trace the complete data lineage from ingestion to reader:

**Ingestion layer:**
- What are the source feeds? Are they active?
- ingestion_triage.py: RSS feeds, YouTube channels. Are all URLs working?
- fetch_intel.py: What sources? Is its output connected to anything?
- What deduplication exists? SHA-256? URL-based? Both?
- How many items are in ingestion_hashes? How many unprocessed?

**Market data layer:**
- market_reality.py: 34 tickers + 5 benchmarks. Are all ticker symbols correct for yfinance?
- Does the AlphaVantage fallback work? Is the API key valid?
- What format does the output take? Who reads it?
- fetch_market_data.py: What does it produce? Who consumes it?

**Analysis layer:**
- contradiction_synthesizer.py: What does it read? What LLM does it call?
- What fields does it produce? (contradiction_gap, capital_volume_usd, reality, they_say, etc.)
- Are all required fields present in every story?
- Does it write atomically? (os.replace of .tmp file)
- What happens on API failure? Circuit breaker? Retry?

**Build layer:**
- db_to_json.py: What DB tables does it query? Does it use CONTAINER_META correctly?
- Does db_to_json.py write to the correct directory? (data/ vs public/data/)
- build_site.py: Does it find templates? Does it inject into all HTML files?
- Are there any HTML files missing sentinel markers?
- Does build_site.py use glob or rglob? (subdirectory HTML files)

**Deploy layer:**
- shipit_cloud.py: What directory does it deploy? (site/ or public/?)
- Is the timer enabled? When did it last run successfully?
- Governor.py: Does it include a deploy step? If not, what deploys?
- What gsutil command is used? Is it authenticated?
- What Cache-Control headers are set?

### 2.4 Script Execution Order Analysis

For EVERY pair of scripts that write to the same file or table:
- What is the execution order?
- Does script B overwrite script A's output?
- Is this intentional or accidental?
- What data is lost in the overwrite?

Specifically investigate the `public/data/stories.json` write chain:
- Who writes first? Who writes last?
- What is the final state of the file?
- Compare the file on GCS vs the file on the VM — are they the same?

### 2.5 Gap Analysis

Identify every gap where:
- Data is produced but never consumed
- Data is consumed but never produced
- A file is written but never deployed
- A step succeeds but its output is overwritten by a later step
- A step fails but the pipeline continues (no circuit breaker)
- A step fails and the pipeline stops (missing data downstream)

---

## PHASE 3 — BOTTLENECK AND CHOKEPOINT INVESTIGATION

### 3.1 Resource Bottlenecks

- VM: e2-micro (0.25 vCPU, 1GB RAM). Is CPU usage spiking during pipeline runs?
- Memory: Are any scripts loading entire datasets into RAM? (stories.json, gazzetta.db)
- Disk: 30GB, 13% used. Any log rotation? Any temp files accumulating?
- Network: Are API calls sequential or concurrent? Any unnecessary blocking?
- SQLite: WAL mode active? Busy timeout set? Any lock contention between parallel services?

### 3.2 Concurrency Bottlenecks

- How many services can write to gazzetta.db simultaneously?
- Does traffic_cop.py provide a real lock? Is every pipeline step using it?
- What happens if the governor timer fires while the previous run is still executing?
- Are there any race conditions between the governor and the v1 legacy timers?

### 3.3 API Bottlenecks

- DeepSeek API: Rate limits? Cost per call? Retry logic?
- yfinance: Rate limits? Reliability? Fallback to AlphaVantage?
- AlphaVantage: Free tier limit (5 calls/min). Is the 13-second delay respected?
- Telegram API: Rate limits? Message size limits?

### 3.4 Data Volume Bottlenecks

- 376 stories. How large is stories.json? (bytes)
- How long does contradiction_synthesizer.py take per story?
- How long does db_to_json.py take to query and serialize 376 stories?
- Is the pipeline completing within the 300-second systemd timeout?

### 3.5 Reliability Chokepoints

Identify every single point of failure:

- If the DeepSeek API is down, what happens?
- If yfinance is rate-limited, what happens?
- If the VM restarts (IP changes), what breaks?
- If the VM runs out of disk space, what fails first?
- If the .env file is corrupted, what services die?
- If gsutil loses authentication, does anyone notice?
- If the Cloud CDN caches a stale response, how is it detected?
- If a pipeline step fails silently (exit code 0 but wrong output), is it caught?

### 3.6 Observability Chokepoints

- Are pipeline failures reported to Alex? How? How fast?
- Is site staleness detected? How? By whom?
- Is data quality degradation detected? (all gaps=15, all volumes=$100M)
- Are there any health checks? Heartbeats? Dashboards?
- What does journalctl show for the last 24 hours of each service?

---

## PHASE 4 — LIVE SITE VERIFICATION

### 4.1 Data Freshness

- curl the live site's stories.json. What is generated_at?
- Compare to the VM's stories.json generated_at. What is the delta?
- Is the delta acceptable? (<10 min = good, <60 min = acceptable, >60 min = broken)

### 4.2 Data Quality

- How many stories have contradiction_gap = 15? (migration baseline — should be zero)
- How many stories have contradiction_gap > 60? (should be some)
- How many stories have capital_volume_usd = 100,000,000? (migration baseline — should be zero)
- Are there stories with tier=BREAKING? DEVELOPING? ALIGNED?
- Is the lead story set? Is it the highest-gap story?

### 4.3 Rendering Verification

- Browser navigate to the live site
- Check: How many trader cards render?
- Check: What do the bubble labels show? (capital and gap values)
- Check: Are CSS and JS loading? (browser console — any 404s?)
- Check: Does i18n load? (typeof window.i18n)
- Check: Does the masthead render correctly? (browser_vision screenshot)
- Check: Mobile viewport — is the site usable at 375px width?

### 4.4 Console Error Audit

- browser_console: capture all errors, warnings, failed fetches
- Any 404s on JS/CSS/data files?
- Any CORS errors?
- Any JavaScript exceptions?
- Any failed fetch() calls returning HTML instead of JSON?

---

## PHASE 5 — CROSS-VALIDATION

Spawn 3 independent subagents with the same forensic data. Each has a different lens:

### Agent 1: SRE Auditor
- Focus: operational integrity, data flow gaps, silent failures
- Question: "Is this system reliable? What breaks silently? What needs monitoring?"

### Agent 2: Pipeline Engineer
- Focus: data lineage, script interactions, overwrite patterns
- Question: "Does the data that's produced reach the reader? Where does it get lost or corrupted?"

### Agent 3: Systems Architect
- Focus: architecture coherence, simplification, removing dead weight
- Question: "What is the minimum viable architecture? What can be removed?"

Each agent receives:
- Full systemd service listing with status
- Script-to-service mapping
- Data lineage diagram
- Live site vs VM data comparison
- Known error patterns

Collect findings. Cross-reference. Any finding confirmed by 2+ agents is a verified issue.

---

## PHASE 6 — REPORT

Produce a single comprehensive report. Structure:

### Section 1: Executive Summary
- One paragraph. What state is the system in? What is the single biggest problem?

### Section 2: Architecture Diagram
- ASCII diagram showing: data sources → VM services → pipeline scripts → data files → deploy → GCS → reader
- Mark broken connections with ---X--- and label why

### Section 3: Audit Findings Table
- Numbered list. Each finding has: severity (CRITICAL/HIGH/MEDIUM/LOW), description, file:line evidence, impact

### Section 4: Data Flow Map
- Complete data lineage from source to screen
- Every transform, every write, every read
- Highlight where data is lost or corrupted

### Section 5: Bottleneck Catalog
- Resource bottlenecks (CPU, memory, disk, network)
- Concurrency bottlenecks (locks, races, overlaps)
- API bottlenecks (rate limits, timeouts, costs)
- Reliability chokepoints (single points of failure)

### Section 6: Fix Plan
- Phased approach: Stop the bleeding → Make it reliable → Future-proof
- Each phase: numbered steps with exact commands
- Estimated time per step
- Dependencies between steps
- Rollback procedure for each step

### Section 7: Target Architecture
- What the system should look like after all fixes
- Single pipeline diagram
- Monitoring and alerting design
- Agent roles and communication paths

### Section 8: Verification Checklist
- After each fix phase, what to verify
- Specific curl commands, browser checks, console expressions
- Pass/fail criteria for each check

---

## RULES OF ENGAGEMENT

1. **Verify, don't assume.** Every claim must be backed by a tool call result — a file read, an SSH command output, a curl response, a browser console value.

2. **Read scripts line by line.** Do not trust documentation or comments. Read the actual code. Documentation is often stale.

3. **Trace data, not intentions.** Follow the bytes. Where does file A get written? Who reads it? Who overwrites it? What bytes are on GCS right now?

4. **Cross-validate.** Single-agent conclusions are opinions. Multi-agent consensus is evidence.

5. **No opinions without evidence.** "The pipeline is broken" is an opinion. "The pipeline produces stories with contradiction_gap=15 for all 376 stories because db_to_json.py at line 163 writes to public/data/stories.json after contradiction_synthesizer.py already wrote real gaps" is evidence.

6. **Separate what's broken from what's design.** A gap=15 is broken. A gold border color choice is design. Don't report design choices as bugs.

7. **Prioritize by reader impact.** A bug that makes the site show no signal is CRITICAL. A bug that wastes CPU is HIGH. A dead file that nobody reads is LOW.

8. **Produce actionable output.** Every bug must have a fix. Every fix must have exact commands. No hand-waving.

9. **The report goes to a newspaper publisher, not an engineer.** Plain language. Bottom line first. No unnecessary detail. Diagrams where helpful.

10. **SOP rules are binding.** R1 (no sed on HTML/CSS/JS), R2 (one change one verify), R3 (no deploy without approval), R4 (file boundaries), R5 (gsutil path), R6 (SVG failsafes), R7 (verification pyramid), R8 (zero-symbol communication). All in effect.

---

## DELIVERABLES

1. **ARCHITECTURE_REPORT_YYYY-MM-DD.md** — The full report (Sections 1-8 above)
2. **ARCHITECTURE_DIAGRAM.md** — Standalone ASCII diagram for quick reference
3. **FIX_PLAN.md** — Phase-by-phase execution plan with exact commands
4. **Telegram message to Alex** — One-paragraph summary of findings and recommended action

---

## ESCALATION

If at any point you discover:
- Data loss that cannot be recovered
- Security vulnerability (exposed credentials, open permissions)
- Cost anomaly (unexpected GCP charges)
- Systemic corruption (DB schema mismatch, all data affected)

Stop the audit immediately and report to Alex with the specific finding, evidence, and severity.
