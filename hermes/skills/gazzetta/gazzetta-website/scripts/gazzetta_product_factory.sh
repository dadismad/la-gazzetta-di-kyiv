#!/bin/bash
# Gazzetta Product Factory — Unified Pipeline (v23.22)
# Replaces fragmented crons with 1 atomic product-sync loop.
# Runs: fetch_intel → intel_to_stories → generate_flows → db_to_json → shipit → health_check
set -euo pipefail
cd /Users/alexstocchi/projects/gazzetta-di-kyiv
LOG="/tmp/gazzetta-product-factory.log"
echo "[$(date -Iseconds)] Product Factory START" >> "$LOG"

# Stage 1: Ingest fresh intel
echo "[$(date -Iseconds)] Stage 1: fetch_intel.py" >> "$LOG"
.venv/bin/python scripts/fetch_intel.py >> "$LOG" 2>&1 || true

# Stage 2: Intel → stories
echo "[$(date -Iseconds)] Stage 2: intel_to_stories" >> "$LOG"
.venv/bin/python scripts/intel_to_stories.py >> "$LOG" 2>&1 || true

# Stage 3: Generate capital flows
echo "[$(date -Iseconds)] Stage 3: generate_flows" >> "$LOG"
.venv/bin/python scripts/generate_flows.py >> "$LOG" 2>&1 || true

# Stage 4: DB → JSON
echo "[$(date -Iseconds)] Stage 4: db_to_json" >> "$LOG"
.venv/bin/python scripts/db_to_json.py >> "$LOG" 2>&1 || true

# Stage 5: Build + Deploy via shipit
echo "[$(date -Iseconds)] Stage 5: shipit" >> "$LOG"
bash shipit.sh >> "$LOG" 2>&1 || true

# Stage 6: Health check
echo "[$(date -Iseconds)] Stage 6: health check" >> "$LOG"
curl -sI https://www.lagazzettadikyiv.com/ | head -1 >> "$LOG" 2>&1 || true
curl -sI https://www.lagazzettadikyiv.com/ru/ | head -1 >> "$LOG" 2>&1 || true

echo "[$(date -Iseconds)] Product Factory DONE" >> "$LOG"
