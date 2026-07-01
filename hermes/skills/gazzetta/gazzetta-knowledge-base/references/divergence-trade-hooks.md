# Divergence-Driven Trade Hooks — Specification (v23.22)

## Purpose
Replace meaningless percentage-based trade hooks (`CRYPTO ↓ OUT 50%`) with institutional-grade narrative-price divergence scores that traders can act on.

## Data Sources
- **Flows:** `data/flows.json` → `flows[].asset_class`, `flows[].net_direction`, `flows[].confidence_pct`, `flows[].pace_multiplier`
- **Prices:** `data/market_prices.json` → `prices.{asset_class}.change_pct` (keyed by: crypto, equities, commodities, fixed_income, fx, defense, tech, gold)

## Computation

```
narrativeForce = directionSign × confidence
  directionSign = (direction == 'outflow' || direction == 'bearish') ? -1 : 1
  confidence = clamp(confidence_pct / 100, 0, 1)

priceForce = clamp(priceDeltaPct / 100, -1, 1)

gap = |narrativeForce - priceForce|
```

## Labels & Colors

| gap range | Label | Color | Meaning |
|-----------|-------|-------|---------|
| > 0.5 | DIVERGENT | #DC2626 | High divergence — narrative and price moving opposite directions. Strong trade signal. |
| > 0.25 | LAGGING | #D97706 | Moderate divergence — price hasn't caught up to narrative yet. |
| ≤ 0.25 | ALIGNED | #059669 | Low divergence — narrative and price in sync. Consensus trade. |

## Display Format (Kobeissi/ZeroHedge style)

```
[ASSET] · [DIVERGENT/LAGGING/ALIGNED] · [↑/↓ GAP%]
```

Example: `CRYPTO · DIVERGENT · ↑ 75.0%`
Tooltip: `75.0% narrative-price gap · Narrative 60% BULLISH vs Price +0.4%`

## Implementation

Located in `app.js`:
- `computeDivergence(flowDirection, flowConfidence, priceDeltaPct)` — returns `{gap, narrativeForce, priceForce}`
- `getDivergenceLabel(gap)` — returns DIVERGENT/LAGGING/ALIGNED
- `getDivergenceColor(gap)` — returns hex color
- `updateTradeHooks(flowsData)` — populates sidebar hook elements (`#hook0Symbol`, `#hook0Label`, `#hook0Gap`)
- Price data loaded in `boot()` → `window._lastTickerMap` indexed by asset class name

## SENTIMENT Section

Also updated to show aggregate divergence instead of inflow ratio:
```
<pct>% · Divergence · <N> flows
```
Computed as average gap across all flows.
