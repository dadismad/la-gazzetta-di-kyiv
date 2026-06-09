#!/bin/bash
# market_data_fetch.sh — Fetch external market data for Gazzetta pipeline
# Cron: every 4h via cronjob ce99ba57723d
# Requires: ALPHA_VANTAGE_KEY and FRED_API_KEY environment variables

set -e
cd /Users/alexstocchi/projects/gazzetta-di-kyiv

echo "=== Market Data Fetch — $(date) ==="

# Step 1: Alpha Vantage
if [ -n "$ALPHA_VANTAGE_KEY" ]; then
    echo "→ Fetching Alpha Vantage data..."
    python3 scripts/fetch_alpha_vantage.py || echo "⚠ Alpha Vantage fetch failed (non-fatal)"
else
    echo "⚠ ALPHA_VANTAGE_KEY not set — skipping Alpha Vantage"
    echo "  Get free key: https://www.alphavantage.co/support/#api-key"
fi

# Step 2: FRED
if [ -n "$FRED_API_KEY" ]; then
    echo "→ Fetching FRED data..."
    python3 scripts/fetch_fred.py || echo "⚠ FRED fetch failed (non-fatal)"
else
    echo "⚠ FRED_API_KEY not set — skipping FRED"
    echo "  Get free key: https://fred.stlouisfed.org/docs/api/api_key.html"
fi

# Step 3: Enrich stories with market data
echo "→ Enriching stories..."
python3 scripts/enrich_market_data.py || echo "⚠ Enrichment failed (non-fatal)"

echo "=== Done — $(date) ==="
