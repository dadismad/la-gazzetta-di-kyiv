# External Data Pipeline — Integration Architecture (v22.31)

## Sources (priority order)

| Priority | Source | Data | API | Free? | Rate Limit |
|----------|--------|------|-----|-------|------------|
| 1 | Alpha Vantage | Commodities, FX, VIX | REST | Free tier | 25 req/day |
| 2 | FRED | Yields, Fed Funds, CPI, M2 | REST | Free | 120 req/min |
| 3 | World Bank | FDI, GDP, trade balances | REST | Free no-key | Unlimited |
| 4 | GDELT | Geopolitical events 15min | BigQuery | Free | N/A |
| 5 | BIS | Cross-border banking flows | Bulk CSV | Free | N/A |
| 6 | Trading Economics | 300K indicators, MCP | REST | Paid $99-499/mo | Tiered |

## Pipeline

Every 4h: market_data_fetch.sh → fetch_alpha_vantage.py + fetch_fred.py → enrich_market_data.py
Every 60m: capital flows pipeline → enrich → validate → generate_flows → deploy

## Scripts

- scripts/fetch_alpha_vantage.py — commodities, FX, VIX → data/market_data/alpha_vantage.json
- scripts/fetch_fred.py — yields, Fed, CPI, M2 → data/market_data/fred.json
- scripts/enrich_market_data.py — merges into stories.json, generates signals.json
- scripts/market_data_fetch.sh — cron entry point

## API Keys

ALPHA_VANTAGE_KEY — https://www.alphavantage.co/support/#api-key
FRED_API_KEY — https://fred.stlouisfed.org/docs/api/api_key.html
Both free, instant. Set in .env.

## Verification

python3 scripts/enrich_market_data.py
python3 -c "import json; d=json.load(open('data/stories.json')); print(sum(1 for s in d['stories'] if s.get('capital_flow',{}).get('market_data')))"
