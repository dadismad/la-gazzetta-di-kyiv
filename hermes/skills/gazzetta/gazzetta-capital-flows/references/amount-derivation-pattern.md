# Amount Derivation Pattern — v22.29

When `stories.json` has all stories with identical hardcoded `amount_b: 5.0` and `pace_multiplier: 1.0`, the flows pipeline produces garbage — identical trace strings, flat distribution, zero information content.

## Derivation Algorithm

Three-tier amount extraction from narrative content:

### Tier 1: Explicit dollar amounts in text
```python
import re
# Search headline, thesis, portfolio_implication, they_say for $XB patterns
amount_matches = re.findall(r'\$(\d+\.?\d*)\s*(B|billion|million|M)', full_text)
```

### Tier 2: Market cap / value indicators
```python
mc_match = re.search(r'(\d+\.?\d*)\s*(trillion|billion)', full_text)
# Use 10% of market cap as flow estimate
```

### Tier 3: Event-magnitude derivation from headline keywords
```python
magnitude_keywords = {
    'war': 18, 'strike': 12, 'missile': 12, 'invasion': 18, 'occupation': 14,
    'deal': 20, 'acquisition': 25, 'merger': 25, 'ipo': 30, 'launch': 8,
    'sanctions': 10, 'blockade': 12, 'crash': 15, 'crisis': 12, 'default': 20,
    'rate hike': 18, 'rate cut': 18, 'election': 8, 'coup': 15, 'ceasefire': 6,
    'drone': 6, 'audit': 4, 'ban': 5, 'approve': 8, 'sign': 10, 'agree': 5,
    'nuclear': 15, 'mobilization': 12, 'offensive': 14, 'counter': 10,
    'surrender': 20, 'cyberattack': 8, 'hack': 7, 'breach': 10,
}
# Multiply by sector multiplier: tech×1.5, crypto×1.3, commodities×1.2, defense×1.1
# Adjust by confidence: high×1.2, low×0.7
```

## Pace Derivation

```python
def derive_pace(story):
    horizon = story.get('horizon', '').lower()
    freshness = story.get('freshness', '').lower()
    
    if '24h' in horizon or 'hours' in horizon:     base = 3.0
    elif '48h' in horizon or '72h' in horizon:      base = 2.0
    elif 'week' in horizon or '7d' in horizon:      base = 1.5
    else:                                            base = 1.0
    
    if freshness == 'breaking':    base += 0.5
    elif freshness == 'developing': base += 0.3
    
    return round(base, 1)
```

## Projected Amount Extraction

```python
# Try range patterns: "gap +$10-15/bbl", "move $5-8B"
proj_match = re.search(r'(?:gap|move|rise|fall)\s*\+?\$?(\d+)[-–]\$?(\d+)', text)
# Try single projections: "rally of $15", "surge $12B"  
pct_match = re.search(r'(?:gain|rise|rally|surge|spike|jump)\s*(?:of\s*)?\+?\$?(\d+)', text)
# Fallback: amount × 0.15 for high-pace, amount × 0.08 for normal
```

## Expected Results

Before: 23 stories all `$5.0B`, 1.0x pace → flows all 85% with identical traces
After:  15 unique amounts ($3.3B-$30.0B), 7 unique paces (1.3x-3.3x) → 7 unique confidence traces, spread 83-100%

## Caps and Guards

- Cap at 50B for any derived amount (prevents headline values like "$900B chip stock" treated as flow)
- Cap at 100 for confidence
- Floor at 25 for confidence
- Remove the `validate_stories.py` default of `amount_b: 5.0` in REQUIRED_FLOW_FIELDS
