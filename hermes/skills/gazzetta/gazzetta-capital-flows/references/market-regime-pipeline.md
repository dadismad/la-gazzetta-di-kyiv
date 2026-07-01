# Market Regime Pipeline — Implementation Notes (v22.35)

## Overview
Autonomous 6h pipeline that fetches external market data and generates Mike Green's top 3 retail indicators on flows.html.

## Data Sources (all free)
- **CFTC COT**: Weekly futures positioning — Lev_Money (CTA proxy), Asset_Mgr, Dealer. 11 markets. Script: `scripts/fetch_cot.py`
- **ICI Flows**: Weekly ETF/mutual fund flows. Combined flows − MF flows = ETF estimates. Script: `scripts/fetch_ici.py`
- **Alpha Vantage**: Commodities (WTI, BRENT, Gold, NG), FX, VIX. Script: `scripts/fetch_alpha_vantage.py`
- **FRED**: Yields (DGS10, DGS2), Fed Funds, CPI, M2. Script: `scripts/fetch_fred.py`

## Output Files
- `data/market_data/cot.json` — 11 markets with categories, net positioning, week-over-week changes
- `data/market_data/ici_flows.json` — 58 data points, monthly+weekly, ETF vs MF breakdown
- `site/data/market_regime.json` — 3 Mike Green indicators consumed by flows.html

## Mike Green Top 3 Retail Indicators
1. **Money Flow**: ETF flows ($B) × COT bullish bias → BULLISH/BEARISH/NEUTRAL + strength 0-100
2. **Top Heavy**: SPX Asset_Mgr net % OI → concentration risk. EXTREME >40%, HIGH >25%, MODERATE >15%
3. **Bond Fear**: Treasury futures positioning divergence between Lev_Money and Asset_Mgr + yield curve spread → score 0-100

## Pipeline Chain
```
fetch_cot.py + fetch_ici.py + fetch_alpha_vantage.py + fetch_fred.py
  → generate_market_regime.py (reads all 4 → writes market_regime.json)
  → enrich_market_data.py (enriches stories.json with market context)
  → deploy_to_gcs.sh (pushes site/ → GCS)
```
Entry point: `scripts/fetch_all_market_data.sh` (cron: ed4a4d4de85f, every 6h)

## Track Record — Server-Side Paper Trade Backfill (v22.35)
Problem: Track record was localStorage-only → empty for all new visitors, 0 settled trades → zero credibility.
Solution: `site/data/track_record.json` with paper trades backfilled from stories' predictions.
- `renderTrackRecord()` fetches `track_record.json` and merges with localStorage
- Shows: settled count, win rate, total P&L, expectancy, last 5 trades with per-trade P&L
- 12 trades (6 settled: 3W/3L, 50% win rate, +3.5% avg win, -2.8% avg loss)
- Fallback: `renderTrackRecordLocal()` uses localStorage only if server data unavailable

## Flow Decomposition Spec
`docs/architecture/data-schemas/flows-decomposition-spec.md` — 1,607 lines, 5 layers:
- L1: Secular/Regime (passive dominance, AI capex, deglobalization, energy transition, demographic inversion)
- L2: Cyclical/Liquidity (credit cycle, Fed BS, global M2, SLOOS, swap lines)
- L3: Asset Class Rotation (equities→bonds, active→passive, public→private)
- L4: Sector Flows (11 S&P sectors, ETF proxies, COT overlay)
- L5: Product/Security Flows (BCI, semiconductors, rocket engines, quantum, biotech, defense tech)
