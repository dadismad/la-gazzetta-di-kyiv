#!/bin/bash
# fetch_all_market_data.sh — Fetch ALL external market data in sequence
# Called by cron every 4h to feed the Mike Green market regime monitor
set -e
cd "$(dirname "$0")/.."

echo "=== Market Data Fetch Pipeline ==="
echo "Started: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# 1. Alpha Vantage (commodities, FX, VIX) + FRED (yields, CPI, M2)
python3 scripts/fetch_alpha_vantage.py 2>&1 || echo "⚠ Alpha Vantage fetch failed"
python3 scripts/fetch_fred.py 2>&1 || echo "⚠ FRED fetch failed"

# 2. CFTC COT (weekly — skip if same week already fetched)
python3 scripts/fetch_cot.py 2>&1 || echo "⚠ COT fetch failed"

# 3. ICI flows (weekly)
python3 scripts/fetch_ici.py 2>&1 || echo "⚠ ICI fetch failed"

# 4. Generate market regime indicators
python3 scripts/generate_market_regime.py 2>&1 || echo "⚠ Market regime generation failed"

# 5. Enrich stories with market context
python3 scripts/enrich_market_data.py 2>&1 || echo "⚠ Enrichment failed"

# 6. Deploy to GCS
bash "$HOME/.hermes/scripts/gazzetta_deploy_to_gcs.sh" 2>&1 | tail -3

echo "=== Pipeline complete: $(date -u +"%Y-%m-%dT%H:%M:%SZ") ==="
