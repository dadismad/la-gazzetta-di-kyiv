# System Audit Master Prompt

This is a reusable 6-phase forensic audit framework for the Gazzetta di Kyiv system.
When the user says "audit the system," follow this methodology exactly.

## Phase 0 — Pre-Flight
- Load skills: gazzetta-newspaper-engine, gazzetta-cloud-infrastructure, gazzetta-knowledge-index
- Read HERMES_OPERATIONAL_SOP.md at project root

## Phase 1 — Infrastructure Discovery
- Map every GCP resource: VMs, buckets, Cloud Run jobs, Cloud Scheduler triggers, Artifact Registry images
- Document VM state: CPU, RAM, disk, running processes, all systemd units
- Check file ownership on all VM directories
- Compare VM scripts against local repo

## Phase 2 — Pipeline Architecture Audit
- Map service-to-script: every systemd timer, what it runs, as which user
- Read every pipeline script line by line: what it reads, what it writes, exit codes
- Trace complete data lineage: source to screen
- Identify overwrite patterns: does script B destroy script A's output?

## Phase 3 — Bottleneck Investigation
- Resource bottlenecks: CPU, RAM, disk, network on e2-micro
- Concurrency: how many writers to gazzetta.db? Lock contention?
- API bottlenecks: DeepSeek rate limits, yfinance reliability, AlphaVantage fallback
- Reliability chokepoints: what fails silently? What has no alert?

## Phase 4 — Live Site Verification
- Data freshness: compare VM generated_at vs GCS generated_at
- Data quality: how many stories have gap=15 (baseline)? How many have gap>60?
- Rendering: browser_console check trader-card count, bubble data, console errors
- Verify: dashboard.js fetch target file EXISTS on GCS

## Phase 5 — Cross-Validation
- Spawn 3 subagents: SRE Auditor, Pipeline Engineer, Systems Architect
- Each receives same forensic data, different lens
- Findings confirmed by 2+ agents are verified

## Phase 6 — Report
- Executive summary
- Architecture diagram (ASCII)
- Numbered findings table with severity, evidence, fix
- Data flow map
- Bottleneck catalog
- Fix plan (phased: stop bleeding -> make reliable -> future-proof)
- Target architecture
- Verification checklist
