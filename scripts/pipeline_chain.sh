#!/bin/bash
# gazzetta_pipeline_chain.sh — Full data pipeline: intel → decay → flows → build
# Runs every 60m via gazzetta-continuous-capital-flows cron
# Deploy picks up automatically every 15m
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT"

echo "=== PIPELINE CHAIN $(date '+%Y-%m-%d %H:%M:%S') ==="

echo "[1/4] intel_to_stories..."
python3 scripts/intel_to_stories.py

echo "[2/4] decay_stories..."
python3 scripts/decay_stories.py

echo "[2.5/4] validate_stories..."
python3 scripts/validate_stories.py

echo "[3/4] generate_flows..."
python3 scripts/generate_flows.py

echo "[3.5/4] translate_content..."
python3 scripts/translate_content.py

echo "[4/4] build_site..."
python3 scripts/build_site.py

echo "=== PIPELINE COMPLETE ==="
