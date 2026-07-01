# Trade Hook Divergence Format & UX Authority Standards (v23.24)

**User directive:** "A professional trader does not care about '75% Prob.' They care about The Gap. Replace all percentages with 'ASKEW TELEMETRY' indicators."
Old format `CRYPTO ↓ OUT 50%` and `CRYPTO [DIVERGENT]` rejected as still percentage-adjacent.

## ASKEW TELEMETRY Format (current)

```
CRYPTO · BULLISH SKEW · 50.0% divergence
```

Δ = |sentiment direction × conviction − actual price delta|

## Skew Tiers

| Gap | Skew Label | Color |
|-----|-----------|-------|
| >0.5 | `BULLISH SKEW` / `BEARISH SKEW` | `#DC2626` red |
| >0.25 | `BULLISH TILT` / `BEARISH TILT` | `#D97706` amber |
| ≤0.25 | `NEUTRAL` | `#059669` green |

Skew = flow direction × gap tier.

## NEVER use in Trade Hooks
- Raw percentages (75%, 50%)
- Confidence scores / "Prob" labels
- Inflow ratio counts (9/12)
- "INF" or "OUT" abbreviations
- Labels without skew direction (DIVERGENT/LAGGING/ALIGNED alone)

## Freshness → Last Big Inflow (v23.24)

Hero indicator replaced with most recent $1B+ flow:
```
$4.8B out LAST INFLOW    (red for outflow)
$12.3B in  LAST INFLOW   (green for inflow)
```

**NEVER use:** timers, "Xm ago", "just now", "FRESHNESS" as metric.

## Container Authority Wording

| Container | EN | RU |
|-----------|-----|-----|
| Stories | **WHAT THE CAPITAL IS SAYING** | **О ЧЁМ ГОВОРИТ КАПИТАЛ** |
| Flows | **WHERE THE CAPITAL IS GOING** | **КУДА ИДЁТ КАПИТАЛ** |
