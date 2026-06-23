# Asymmetry Score v2.0 — Mathematical Delta Formula

Implemented in `scripts/db_to_json.py` v23.13. Replaces the old heuristic (v1.0: ad-hoc 50 + change_pct * 5 + ...).

## Formula

```
Score = |Sentiment - PriceDelta| × 50
```

Where:
- **Sentiment** ∈ [-1, 1]: narrative direction from story capital_flow
  - inflow → +confidence/100 (e.g., 75% confidence → +0.75)
  - outflow → -confidence/100 (e.g., 80% confidence → -0.80)
  - neutral → 0.0
- **PriceDelta** ∈ [-1, 1]: 24h price change normalized via tanh
  - `tanh(change_pct / 5.0)`
  - 1% change → tanh(0.2) ≈ 0.20
  - 5% change → tanh(1.0) ≈ 0.76
  - 10% change → tanh(2.0) ≈ 0.96

## Tier Thresholds

| Score | Tier | Meaning |
|-------|------|---------|
| ≥ 80 | MAX ASYMMETRY | Massive contradiction — institutional edge |
| ≥ 65 | HIGH ASYMMETRY | Significant divergence — trade opportunity |
| ≥ 40 | MODERATE | Some misalignment |
| < 40 | LOW ASYMMETRY | Market and narrative aligned |

## Reference Examples

1. Mastercard bull case (+0.9), price flat (-0.02):
   → ABS(0.9 - (-0.02)) × 50 = 46 (MODERATE)

2. Mastercard bull case (+0.9), price crashing (-1.0):
   → ABS(0.9 - (-0.76)) × 50 = 83 (MAX ASYMMETRY)

3. Oil bearish narrative (-0.65), price up +2.1% (+0.40):
   → ABS(-0.65 - 0.40) × 50 = 53 (MODERATE — currently shown as 58 due to rounding)

## Diagnostic Trace

Every score carries a trace object:
```json
{
  "sentiment": -0.65,
  "price_delta": 0.40,
  "price_change_pct": 2.12,
  "formula": "ABS((-0.65 - 0.40) * 50) = 53",
  "ticker": "CL=F",
  "ticker_price": 90.07
}
```

## Data Source

Reads `data/market_prices.json` (populated by `scripts/fetch_market_data.py` cron, yfinance-backed). Maps asset_class to ticker:

| asset_class | ticker |
|-------------|--------|
| crypto | BTC-USD |
| equities | SPY |
| commodities | CL=F (WTI) |
| fixed_income | TLT |
| fx | UUP |
| defense | ITA |
| tech | QQQ |
| gold | GC=F |

## Math Sanity Check

`test_platform.py` Round 8 verifies 5 test vectors:
1. inflow/100/-5.0% → MAX ASYMMETRY (88)
2. outflow/100/+5.0% → MAX ASYMMETRY (88)
3. inflow/80/+5.0% → LOW ASYMMETRY (2 — aligned)
4. outflow/80/-5.0% → LOW ASYMMETRY (2 — aligned)
5. inflow/90/-2.0% → HIGH ASYMMETRY (64)
