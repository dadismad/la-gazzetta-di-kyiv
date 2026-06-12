#!/bin/bash
# Pipeline Chain Script — Gazzetta di Kyiv
# Runs: db_to_json.py → generate_flows.py → generate_signal_api.py → generate_trades_api.py → deploy to GCS
set -e

cd /Users/alexstocchi/lagazzettadikyiv

echo "[1/5] db_to_json.py — SQLite → JSON"
python3 scripts/db_to_json.py

echo "[2/5] generate_flows.py — story → flow extraction"
python3 scripts/generate_flows.py

echo "[3/5] generate_signal_api.py — triangulation signals"
python3 scripts/generate_signal_api.py

echo "[4/5] generate_trades_api.py — trade ideas"
python3 scripts/generate_trades_api.py

echo "[5/5] Deploy to GCS"
cp data/stories.json public/data/stories.json
cp data/flows.json public/data/flows.json

~/lagazzettadikyiv/google-cloud-sdk/bin/gsutil cp public/data/stories.json gs://www.lagazzettadikyiv.com/data/stories.json
~/lagazzettadikyiv/google-cloud-sdk/bin/gsutil cp public/data/flows.json gs://www.lagazzettadikyiv.com/data/flows.json
~/lagazzettadikyiv/google-cloud-sdk/bin/gsutil cp public/data/signal.json gs://www.lagazzettadikyiv.com/data/signal.json
~/lagazzettadikyiv/google-cloud-sdk/bin/gsutil cp public/data/trades.json gs://www.lagazzettadikyiv.com/data/trades.json

~/lagazzettadikyiv/google-cloud-sdk/bin/gsutil setmeta -h "Cache-Control:private, no-store" gs://www.lagazzettadikyiv.com/data/*.json

echo "✓ Pipeline chain complete — data deployed to GCS"
