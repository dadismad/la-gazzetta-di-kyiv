#!/usr/bin/env bash
set -euo pipefail
cd /Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv
python3 scripts/collect_multisource.py
python3 scripts/analyze_narratives_v2.py
python3 scripts/prepare_publish_payloads_v2.py
python3 scripts/pipeline_audit.py
