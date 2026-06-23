#!/bin/bash
# Gazzetta Product Factory — Unified Pipeline (v23.24)
# Full ingestion → approval → build → deploy → verify loop.
# 7-stage pipeline replacing 6 fragmented crons.
set -euo pipefail
cd /Users/alexstocchi/projects/gazzetta-di-kyiv
LOG="/tmp/gazzetta-product-factory.log"
echo "[$(date -Iseconds)] Product Factory START" >> "$LOG"

# Stage 1: Ingest fresh intel from 12 RSS sources → drafts table
echo "[$(date -Iseconds)] Stage 1: fetch_intel.py" >> "$LOG"
.venv/bin/python scripts/fetch_intel.py >> "$LOG" 2>&1 || true

# Stage 2: Intel → stories (telegram_intel + structured feeds)
echo "[$(date -Iseconds)] Stage 2: intel_to_stories" >> "$LOG"
.venv/bin/python scripts/intel_to_stories.py >> "$LOG" 2>&1 || true

# Stage 3: Auto-approve top 15 pending drafts (osint sources)
echo "[$(date -Iseconds)] Stage 3: approve_drafts" >> "$LOG"
.venv/bin/python -c "
import sqlite3, subprocess
db = sqlite3.connect('gazzetta.db')
cur = db.execute('SELECT id FROM drafts WHERE status=\"pending\" ORDER BY created_at DESC LIMIT 15')
ids = [str(r[0]) for r in cur.fetchall()]
if ids:
    subprocess.run(['.venv/bin/python', 'scripts/approve_draft.py', '--id', ','.join(ids)],
                   capture_output=True, text=True)
" >> "$LOG" 2>&1 || true

# Stage 4: Generate capital flows
echo "[$(date -Iseconds)] Stage 4: generate_flows" >> "$LOG"
.venv/bin/python scripts/generate_flows.py >> "$LOG" 2>&1 || true

# Stage 5: DB → JSON (all sources, no osint filter)
echo "[$(date -Iseconds)] Stage 5: db_to_json" >> "$LOG"
.venv/bin/python scripts/db_to_json.py >> "$LOG" 2>&1 || true

# Stage 6: Build + Deploy via shipit
echo "[$(date -Iseconds)] Stage 6: shipit" >> "$LOG"
bash shipit.sh >> "$LOG" 2>&1 || true

# Stage 7: Health check
echo "[$(date -Iseconds)] Stage 7: health check" >> "$LOG"
curl -sI https://www.lagazzettadikyiv.com/ | head -1 >> "$LOG" 2>&1 || true
curl -sI https://www.lagazzettadikyiv.com/ru/ | head -1 >> "$LOG" 2>&1 || true

echo "[$(date -Iseconds)] Product Factory DONE" >> "$LOG"
