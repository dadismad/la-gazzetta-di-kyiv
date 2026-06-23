# Market Data & Asymmetry Score (v23.9)

## Architecture

```
cron (60min)
  └→ fetch_market_data.py (yfinance)
       ├── Fetches 24h price change for 9 tickers
       ├── Computes Asymmetry Scores (Narrative vs Price)
       ├── Writes data/market_prices.json
       └── Syncs to site/data/market_prices.json

shipit.sh Stage 1.5
  └→ generate_signal_api.py
       ├── Reads market_prices.json
       ├── Injects "asymmetry" block into signal.json
       └── Deploys to api/v1/signal.json
```

## Asset→Ticker Map

| Asset Class | Ticker | Description |
|------------|--------|-------------|
| crypto | BTC-USD | Bitcoin |
| equities | SPY | S&P 500 ETF |
| commodities | CL=F | WTI Crude Oil |
| fixed_income | TLT | 20+ Year Treasury |
| fx | UUP | USD Index |
| defense | ITA | Aerospace & Defense |
| tech | QQQ | Nasdaq 100 |
| gold | GC=F | Gold Futures |
| oil | CL=F | WTI Crude (dup) |

## Asymmetry Algorithm

```python
def compute_asymmetry(narrative_dir, price_dir, confidence, price_change_pct):
    price_up = price_dir == "up"
    narrative_bullish = narrative_dir in ("inflow", "bullish")
    
    if narrative_bullish == price_up:
        # Agreement: low asymmetry
        base = max(0, 30 - abs(price_change_pct) * 3)
    else:
        # Contradiction: high asymmetry
        base = 50 + abs(price_change_pct) * 5 + (100 - confidence) * 0.3
    
    return min(100, max(0, round(base)))
```

## Signal Tiers

| Score | Label |
|-------|-------|
| 80+ | MAX ASYMMETRY |
| 60-79 | HIGH ASYMMETRY |
| 40-59 | MODERATE |
| <40 | LOW ASYMMETRY |

## Verification

```bash
# Check asymmetry in signal.json
curl -s https://www.lagazzettadikyiv.com/api/v1/signal.json | python3 -c "
import json,sys; d=json.load(sys.stdin); a=d.get('asymmetry',{})
print(f'High: {a.get(\"high_count\",0)}, Avg: {a.get(\"aggregate_asymmetry\",0)}')"

# Check live prices
curl -s https://www.lagazzettadikyiv.com/data/market_prices.json | python3 -c "
import json,sys; d=json.load(sys.stdin)
for ac,data in sorted(d['prices'].items()):
    print(f'{data[\"ticker\"]:8s} \${data.get(\"price\",0):>10.2f} {data.get(\"change_pct\",0):+.1f}%')"
```

## Dependencies

- yfinance (`pip install yfinance`)
- No API key required (uses Yahoo Finance public data)
- Falls back gracefully if Yahoo rate-limits (returns neutral data)
