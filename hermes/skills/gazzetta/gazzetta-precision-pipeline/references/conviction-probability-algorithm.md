# Conviction Probability Algorithm (v23.18)

Multi-factor model computing a 0-100% conviction score for every story.
Implemented in both `scripts/intel_to_stories.py` (new stories) and
`scripts/db_to_json.py` (existing DB stories — fallback computation).

## Formula

```
conviction_prob = min(95, max(50,
  contra_base
  + source_bonus
  + freshness_bonus
  + confidence_bonus
))
```

## Components

### 1. Contradiction Base (50-85)

```
contra_base = 50 + min((contradiction_score - 45) × 0.8, 35)
```

| Contradiction Score | Base Output |
|---------------------|-------------|
| 45 | 50 |
| 55 | 58 |
| 65 | 66 |
| 75 | 74 |
| 85 | 82 |
| 90+ | 85 (capped) |

### 2. Source Corroboration Bonus (0-15%)

```
source_bonus = min((source_count - 1) × 5, 15)
```

+5% per corroborating source beyond the first, capped at +15%.

### 3. Freshness Bonus (0-10%)

| Condition | Bonus |
|-----------|-------|
| `freshness == "breaking"` | +10% |
| `horizon in ("1-6h", "6-24h")` | +5% |
| Otherwise | 0% |

### 4. Confidence Tier Bonus (0-10%)

| Tier | Bonus |
|------|-------|
| `HIGH` | +10% |
| `MEDIUM` | +5% |
| `LOW` | 0% |

## Tiers

| Conviction % | Tier | Color |
|--------------|------|-------|
| ≥ 85% | ALPHA | Gold (#B8860B) |
| 75-84% | HIGH | Blue (#2563EB) |
| 60-74% | MODERATE | Grey (#6B7280) |
| < 60% | BASELINE | No badge |

## Example

Story: "BREAKING: Iran Shoots Down US Apache"
- Contradiction score: 76 → base = 50 + (76-45)×0.8 = 74.8 → capped at 74
- Sources: 2 → bonus = (2-1)×5 = 5
- Freshness: "breaking" → bonus = 10
- Confidence: "high" → bonus = 10
- **Total: 50 + 5 + 10 + 10 = 75 → HIGH tier**

## Frontend

```javascript
function probBadge(story) {
  const prob = story.conviction_probability;
  if (!prob) return '';
  const tier = prob >= 85 ? 'alpha' : prob >= 75 ? 'high' : 'moderate';
  return `<span class="prob-badge ${tier}">${prob}%</span>`;
}
```

Badge is injected BEFORE the headline in story teasers:
```html
<a href="./story.html?id=...">
  <span class="prob-badge high">76%</span>
  <span class="teaser-amount">$16.9B</span>
  BREAKING: Iran Shoots Down US Apache...
</a>
```

Gold for ALPHA (`prob-badge.alpha`): signals high-conviction alpha to C-suite readers.
