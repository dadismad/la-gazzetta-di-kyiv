# Math Sanity Check — Asymmetry Score Formula v2.0 (v23.12)

## Formula

```
Score = |(NarrativeSentiment [-1 to 1] - PriceActionVelocity [-1 to 1]) × 50|
```

## Component Derivations

### NarrativeSentiment
- `inflow`/`bullish` → `+confidence/100` (range: +0.5 to +1.0)
- `outflow`/`bearish` → `-confidence/100` (range: -0.5 to -1.0)
- `neutral` → `0.0`

### PriceActionVelocity
```
velocity = tanh(change_pct / 5.0)
```
| % Change | tanh value | Interpretation |
|----------|-----------|----------------|
| 1% | ±0.20 | Slight move |
| 2% | ±0.38 | Moderate move |
| 5% | ±0.76 | Significant move |
| 10% | ±0.96 | Extreme move |

## Score Tiers

| Score | Tier | Edge |
|-------|------|------|
| ≥ 80 | MAX ASYMMETRY | Massive contradiction — institutional edge |
| ≥ 60 | HIGH ASYMMETRY | Significant divergence — trade opportunity |
| ≥ 40 | MODERATE | Some misalignment |
| < 40 | LOW ASYMMETRY | Market and narrative aligned |

## Test Vectors (from test_platform.py Round 8)

| Direction | Confidence | Price Δ% | Expected Signal | Score | Formula |
|-----------|-----------|----------|-----------------|-------|---------|
| inflow | 100 | -5.0% | MAX ASYMMETRY | 88 | (1.00 - -0.76) × 50 |
| outflow | 100 | +5.0% | MAX ASYMMETRY | 88 | (-1.00 - 0.76) × 50 |
| inflow | 80 | +5.0% | LOW ASYMMETRY | 2 | (0.80 - 0.76) × 50 |
| outflow | 80 | -5.0% | LOW ASYMMETRY | 2 | (-0.80 - -0.76) × 50 |
| inflow | 90 | -2.0% | HIGH ASYMMETRY | 64 | (0.90 - -0.38) × 50 |

## User's Specification Verification

"If the news is +0.9 (Bullish) but the price is -0.5 (Bearish), the score is 70 (Extreme Contradiction)."

- ns = +0.9, pv = -0.5 → Score = (0.9 - (-0.5)) × 50 = 70 ✓

Note: -0.5 velocity corresponds to approximately -2.5% price change via tanh⁻¹(0.5) × 5 ≈ 2.75%.

## Diagnostic Trace Format

Every asymmetry score in `market_prices.json` carries:

```json
{
  "diagnostic_trace": {
    "narrative_sentiment": -0.80,
    "price_velocity": 0.40,
    "raw_delta": -60.0,
    "formula": "(-0.80 - 0.40) * 50 = |-60.0| = 60"
  }
}
```

## Verification Commands

```bash
# Check all asymmetry scores have diagnostic traces
python3 -c "import json; d=json.load(open('data/market_prices.json')); traces=sum(1 for v in d.get('asymmetry_scores',{}).values() if v.get('diagnostic_trace')); total=len(d.get('asymmetry_scores',{})); print(f'{traces}/{total} traces')"

# Run the math sanity test vectors
python3 -c "
import math, json
tests = [
    ('inflow', 100, -5.0, 'MAX ASYMMETRY'),
    ('outflow', 100, 5.0, 'MAX ASYMMETRY'),
    ('inflow', 80, 5.0, 'LOW ASYMMETRY'),
    ('outflow', 80, -5.0, 'LOW ASYMMETRY'),
    ('inflow', 90, -2.0, 'HIGH ASYMMETRY'),
]
for dir, conf, pct, exp in tests:
    ns = conf/100 if dir=='inflow' else (-conf/100 if dir=='outflow' else 0)
    pv = math.tanh(pct/5.0)
    raw = (ns-pv)*50
    score = abs(raw)
    score = min(100, max(0, round(score)))
    signal = 'MAX ASYMMETRY' if score>=80 else 'HIGH ASYMMETRY' if score>=60 else 'MODERATE' if score>=40 else 'LOW ASYMMETRY'
    ok = '✓' if signal == exp else '✗'
    print(f'{ok} ns={ns:+.2f} pv={pv:+.2f} score={score:3d} [{signal}] expected=[{exp}]')
"
```

## Formula Migration (v23.9 → v23.12)

**Old formula (deprecated):**
```python
if narrative_bullish == price_up:
    base = max(0, 30 - abs(price_change_pct) * 3)
else:
    base = 50 + abs(price_change_pct) * 5 + (100 - narrative_confidence) * 0.3
return min(100, max(0, round(base)))
```

**Issues with old formula:**
- No mathematical traceability (two branches, magic constants)
- No diagnostic trace
- Low discriminating power at extreme divergences
- Could not be audited by quants

**New formula benefits:**
- Single continuous mathematical function
- Diagnostic trace on every score
- tanh normalization creates natural [-1,1] bounds
- 5 test vectors provide mathematical proof
- Auditable by institutional quants
