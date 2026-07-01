# Flows Page Redesign — v22.31 Insight-Driven Representation

## Problem

The flows page was a flat list of 12 items sorted by dollar amount. Every flow showed "high" confidence (83-100%). 11/12 were inflows — the page looked like a green wall with no story. A Portfolio Manager PM focus group rated it 4/10 for insightfulness.

## Research Findings (3-Persona Focus Group, June 2026)

### Portfolio Manager ($5B AUM macro fund)
- "All high confidence → nothing is high. The model isn't calibrated."
- "Organize by DIVERGENCE from consensus, not magnitude. That's where alpha lives."
- Missing: timestamps, Δ vs 4wk avg, geography, historical percentile, investor type
- ONE change: "Add Δ vs 4wk avg column — velocity acceleration is the edge, not raw amount."

### Bloomberg Financial Data Journalist
- "The $18B SPX outflow is the real story — buried at position 7 in a flat list."
- "11:1 inflow ratio is noise. The 1 outflow is the signal."
- "Lead with the contrarian insight, then sector aggregation, then full table as appendix."
- "One contrarian chartable insight + actionable takeaway = viral."

### Competitive Research (Bloomberg, EPFR, Morningstar, ZeroHedge)
- Bloomberg: sector rotation grid, flow velocity gauge, flow vs price divergence chart
- EPFR: macro-to-micro drilldown, conviction scoring, flow attribution
- Pattern: NEVER show raw flows without narrative wrapper
- Actionability = Data + Normalization + Context + Signal + Portfolio Implication

## Redesign Implementation (v22.31)

### Backend (generate_flows.py)

```python
# Sector aggregation
sector_agg = {}  # {asset_class: {total_b, inflows, outflows, avg_pace, avg_confidence, count}}

# Divergence scoring
for f in flows:
    is_contrarian = (agg_direction == "bullish" and f["direction"] == "outflow") or \
                    (agg_direction == "bearish" and f["direction"] == "inflow")
    f["divergence"] = "contrarian" if is_contrarian else "aligned"
    f["divergence_score"] = min(100, int(f["amount_b"] * f["pace_multiplier"] * 2))

# Lead insight: auto-detected from most contrarian flow
lead_insight = {
    "type": "contrarian",  # or "velocity"
    "headline": "$18.0B outflow equities — the only outflow in a bullish market",
    "detail": "SPX is being sold while 10 other flows pile in. Institutional distribution signal.",
    "flow_id": lead["id"],
    "amount_b": lead["amount_b"],
    "asset_class": lead["asset_class"],
    "direction": lead["direction"],
}
```

### Frontend (flows.html + app.js)

Layout hierarchy:
1. **Lead Insight** — red/green gradient card with contrarian/velocity signal
2. **Sector Summary Grid** — 4-column auto-fit grid: sector name, total $B, flow count, avg pace, avg confidence
3. **Full Flow Table** — existing flat list (now context-rich with divergence tags)

```html
<!-- Lead insight card -->
<div class="flow-lead-insight" id="flowLeadInsight">
  <span>⚠ Divergence Signal</span>
  <div class="flow-lead-headline">...</div>
  <div class="flow-lead-detail">...</div>
</div>

<!-- Sector summary grid -->
<div class="flow-sector-grid" id="flowSectorGrid">
  <!-- JS-populated: $$total_b ↑, N flows, Xx pace, Y% conf -->
</div>
```

```javascript
function renderFlowInsight(flowsData) {
  // Renders lead_insight card with color coding (red for contrarian, green for velocity)
  // Renders sector_summary grid from sector_agg data
}
```

### Key Design Principles

1. **Divergence-first**: The most contrarian flow ALWAYS goes at top
2. **Sector before items**: Group flows by asset class — PMs think in sectors, not individual flows
3. **Narrative wrapper**: Every data point has a "so what" — why it matters, what to do
4. **Color coding**: Red for contrarian/outflow, green for inflow/aligned
5. **Progressive disclosure**: Hero insight → sector grid → full table (scan in 10 seconds)

## Pitfalls

- **Flat list sorted by magnitude**: Makes the page wallpaper. The biggest flow is rarely the most interesting.
- **All same confidence**: Destroys credibility. PMs expect a distribution (high/medium/low).
- **No contrarian highlight**: The outflow buried in a sea of green = missed signal.
- **No sector context**: Individual flows without sector totals lose the rotation narrative.
