# Flow Nodes Visualization — Pitfalls & Quick Fixes (v22.35)

From Macro PM + Data Viz Designer focus group audit, June 2026.

## Critical Visual Fixes

### Arrowheads Invisible
```css
/* WAS (all arrows invisible): */
.cn-edge-arrow { fill: none; }

/* FIX: */
.cn-edge-arrow.inflow { fill: var(--cn-green); }
.cn-edge-arrow.outflow { fill: var(--cn-red); }
.cn-edge-arrow.low-conf { opacity: 0.5; }
```

### Mobile Breakage
```css
/* WAS (forces horizontal scroll at 390px): */
#cn-graph-container svg { min-width: 900px; }

/* FIX: */
#cn-graph-container svg { width: 100%; max-width: 1100px; }
```

## Data Pipeline Fixes

### Pace Always 1.0x
```python
# WAS (reads wrong field — stories use pace_multiplier, not pacing/pace):
p = cf.get("pacing", "") or cf.get("pace", "")

# FIX:
pm = cf.get("pace_multiplier", 0)
if pm and pm > 0: return float(pm)
p = cf.get("pacing", "") or cf.get("pace", "")
```

## Remaining Gaps (not yet fixed)

- Detail panel shows "No source data tracked" — edge-level inflow/outflow decomposition not implemented
- Zero Retail nodes despite category existing
- Comma-delimited node labels bundle multiple flows ("equities,crypto,fx" = 3 flows in 1 label)
- No edge labels (23 edges, zero text)
- Page has no site navigation bar — visual disconnect from rest of site
- Dead `<marker>` defs in SVG — defined but never referenced
- No meta theme-color for mobile browser chrome
