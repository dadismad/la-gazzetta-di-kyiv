# Confidence Model — v22.29 Redesign

## Problem (v22.28 and earlier)

The 4-factor confidence model produced identical traces for 10/12 flows:
```
Base 50 + large-flow+15 + normal-pace+5 + accumulating+10 + med-contradiction+5 = 85
```

All flows clustered at 83-87%. The Capital Flow Analyst focus group: "85% on everything = 85% on nothing."

Root causes:
1. Base too high (50) → narrow ceiling
2. Pace always 1.0x (extract_pace bug)
3. Amount bands too wide (≥$5B = one band for everything from $5B to $100B)
4. Contradiction bonus always +5 (binary)
5. No source quality factor

## Redesign — 5-factor, Base 25

```python
def compute_confidence(amount_b, pace_mult, positioning, contradiction_bonus=5, source=""):
    """5-factor model. Base=25. Range: 30-100."""
    score = 25

    # AMOUNT (0-25): log-scale tiers
    if   amount_b >= 20: score += 25  # whale-flow
    elif amount_b >= 10: score += 20  # large-flow
    elif amount_b >= 5:  score += 15  # mid-flow
    elif amount_b >= 2:  score += 10  # small-flow
    elif amount_b >= 0.5: score += 5  # micro-flow
    else:                score += 2   # trace-flow

    # PACE (0-20): wider velocity spread
    if   pace_mult >= 3.0: score += 20  # extreme
    elif pace_mult >= 2.5: score += 16  # very-high
    elif pace_mult >= 2.0: score += 12  # high
    elif pace_mult >= 1.5: score += 8   # elevated
    elif pace_mult >= 1.2: score += 4   # normal
    else:                  score += 2   # flat

    # POSITIONING (0-15)
    pos_map = {"accumulating": 15, "distributing": 10, "hedging": 5}

    # CONTRADICTION (0-15): proportional, not binary
    contr_bonus = min(15, int(contradiction_score / 5)) if contradiction_score > 0 else 0

    # SOURCE QUALITY (0-10): tiered
    tier1 (epfr, morningstar, bloomberg, fed_z1): +10
    tier2 (cftc_cot, ici, cboe, bls):             +7
    tier3 (telegram_intel, internal):               +3
    generic:                                         +5
```

## Results

| Metric | Before | After |
|--------|--------|-------|
| Confidence spread | 0 (all 85%) | 17 (83-100%) |
| Unique traces | 1 | 7 |
| Pace range | 1.0x only | 1.5x-3.3x |
| Amount range | $5B (flat) | $14.4B-$30.0B |

## Call Site

```python
# In extract_from_capital_flow_dict:
contradiction = story.get("contradiction_score", 0)
contr_bonus = min(15, int(contradiction / 5)) if contradiction > 0 else 0
source = story.get("source", "") or cf.get("source", "")
confidence, conf_level, conf_trace = compute_confidence(
    amount_b, pace_mult, derived_pos, contr_bonus, source
)
```
