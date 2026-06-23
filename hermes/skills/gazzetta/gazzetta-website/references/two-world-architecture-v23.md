# Two-World Architecture — INTEL / ALPHA Split (v23.0)

**Deployed: 2026-06-10. Design pattern for cognitive load reduction.**

## Concept

Split the Gazzetta portal's cognitive load into two distinct areas:

- **INTEL LAYER** (Reality, black badge #0F172A): Analysis and news supported or contradicted by capital flows. Contains Stories, Flows, Horizon, Flow Nodes. Tagline: "What's happening — and where the money is actually going."

- **ALPHA LAYER** (Execution, gold badge #B8860B): Strategic bets following or fading the intel. Contains The Signal, Track Record, Trade Ideas. Tagline: "Strategic positioning derived from the intel — where to act."

## Implementation

### Navigation (masthead)
```html
<nav class="product-nav">
  <span class="nav-group-label">INTEL</span>
  <a href="./stories.html">Stories</a>
  <a href="./flows.html">Flows</a>
  <a href="./event_horizon.html">Horizon</a>
  <a href="./flow-nodes.html">Nodes</a>
  <span class="nav-group-label">ALPHA</span>
  <a href="./signal.html">Signal</a>
  <a href="./trades.html">Trades</a>
  <a href="./track.html">Track</a>
</nav>
```

### Section Headers (on index.html)
```html
<div class="layer-header intel-header">
  <span class="layer-label">INTEL</span>
  <span class="layer-desc">What's happening — and where the money is actually going.</span>
</div>
<!-- ... Intel containers ... -->
<div class="layer-header alpha-header">
  <span class="layer-label">ALPHA</span>
  <span class="layer-desc">Strategic positioning derived from the intel — where to act.</span>
</div>
<!-- ... Alpha containers ... -->
```

### CSS (styles.css v23.0)
```css
.layer-header { display: flex; align-items: baseline; gap: 12px; padding: 32px 0 8px; border-top: 1px solid var(--divider); }
.intel-header .layer-label { background: #0F172A; color: #FFF; }
.alpha-header .layer-label { background: #B8860B; color: #FFF; }
.layer-desc { font-family: var(--serif); font-size: 13px; font-style: italic; color: var(--ink-muted); }
```

## Anti-Patterns

- ❌ Do NOT put Trade Ideas in INTEL layer — it's execution, not analysis
- ❌ Do NOT put Flows in ALPHA layer — flows are evidence, not action
- ❌ Do NOT use emoji in layer labels or service cards
- ❌ The nav-group-label must use `var(--sans)` font, 8px, 700 weight
