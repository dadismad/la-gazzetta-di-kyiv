# Pace Derivation — v22.45 Algorithm

Replaces the hardcoded `pace_multiplier: 1.0` with content-derived velocity scores.

## Formula

```
pace = clamp((horizon_base + urgency_bonus) × contra_mult × asset_velocity, 0.5, 5.0)
```

## Dimensions

### 1. Horizon Base
| Horizon | Base Pace |
|---------|-----------|
| 1-6h | 3.0x |
| 6-24h | 2.2x |
| 24-72h | 1.5x |
| 1w+ | 1.1x |
| structural | 0.8x |
| default | 1.3x |

### 2. Urgency Bonus
Keywords in headline + bet text: "breaking", "urgent", "flash", "alert", "crash", "spike", "plunge", "surge", "rout", "panic", "soar", "tumble", "crisis", "emergency", "imminent", "warning", "red alert".

Each hit adds 0.3x. Multiple keywords can compound.

### 3. Contradiction Multiplier
```
contra_mult = 1.0 + (contradiction_score - 50) × 0.01  if score > 50
contra_mult = 1.0                                           otherwise
```
Higher contradiction = capital moves faster. At score=80, multiplier is 1.3x.

### 4. Asset-Class Velocity
| Asset Class | Multiplier |
|-------------|-----------|
| crypto | 1.3x |
| defense | 1.2x |
| commodities | 1.1x |
| tech | 1.1x |
| equities | 0.95x |
| fx | 0.9x |
| fixed_income | 0.8x |
| default | 1.0x |

## Expected Distribution
- 0.8–1.2x: structural/long-horizon bond stories
- 1.3–1.8x: standard market narratives
- 1.9–2.5x: breaking/contradictory stories with urgency
- 2.6–5.0x: crypto crashes, defense escalations, flash events

## Implementation
- **intel_to_stories.py** (v22.45): derives pace at story creation time
- **backfill_pace.py**: one-time migration for existing stories with hardcoded 1.0
- **enrich_editorial_stories.py**: applies default 1.5x to editorial stories lacking derived pace

## Verification
```bash
python3 -c "import json; from collections import Counter; d=json.load(open('data/stories.json')); p=[s.get('capital_flow',{}).get('pace_multiplier',0) for s in d['stories']]; print(dict(Counter(p)))"
# Must show > 3 unique values, no value accounting for > 50% of stories
```
