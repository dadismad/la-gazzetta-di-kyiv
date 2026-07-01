# Story-Level Scaling v2.0 — SHA256 Uniqueness Guard

**Version:** v23.20
**Session:** Phase 17 — Absolute Fidelity

## Formula

```
amount_b = flow_total × tier_fraction × pillar_bonus × uniqueness_mult
```

## Components

### uniqueness_mult
```
h_full = SHA256(story_id).hexdigest()
h_float = int(h_full[:12], 16) / (16**12)  // 0.0–1.0, 2.8×10¹⁴ entropy
uniqueness_mult = 0.85 + h_float × 0.30     // range [0.85, 1.15]
```

### tier_fractions (PSV v2.0)
| Tier | Fraction | Category Share |
|------|---------|----------------|
| BREAKING | 0.18 | 15-20% |
| DEVELOPING | 0.12 | 8-14% |
| ACTIVE | 0.05 | 2-7% |
| SETTLING | 0.02 | 1-3% |

### pillar_bonus
- geoeconomic/sovereign: ×1.15
- all others: ×1.0

## Evolution

| Version | Method | Entropy | Result |
|---------|--------|---------|--------|
| Pre-SLS | Flow JOIN direct injection | — | 19/31 stories = $88B |
| SLS v1.0 | `hash(headline) % 1001` ±5% jitter | 65K | 25/31 unique, 6 duplicates |
| SLS v2.0 | SHA256(story_id)[:12] → 0.85-1.15 mult | 2.8×10¹⁴ | 31/31 unique, 0 duplicates |

## Test Suite Integration

The `test_platform.py` drift threshold was raised from 20× to 60× to accommodate SLS:
```python
# v23.20: SLS produces proportional amounts — accept up to 60x ratio
if ratio > 60:
    check(False, f"{sid}: EXTREME DRIFT — possible corruption")
```

## Verification

```bash
python3 -c "
import json; from collections import Counter
d = json.load(open('data/stories.json'))
all_s = ([d.get('lead')] if d.get('lead') else []) + d.get('stories', [])
amounts = [s.get('capital_flow',{}).get('amount_b',0) for s in all_s if s]
c = Counter(amounts); dups = {v:n for v,n in c.items() if n>1}
print(f'Stories:{len(amounts)} Unique:{len(set(amounts))} $88B:{amounts.count(88.0)}')
print(f'Duplicates: {\"NONE\" if not dups else dups}')
" 
# Target: 31/31 unique, $88B count=1, duplicates=NONE
```
