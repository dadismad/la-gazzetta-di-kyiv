# Three-Column Golden Ratio Grid (v23.5)

Deployed June 10, 2026. Replaces the single-column hints-lobby with a desktop layout based on φ = 1.618.

## Layout

```
┌──────────────┬────────────────────────────────────┬──────────────┐
│  COLUMN A    │  COLUMN B                          │  COLUMN C    │
│  ALPHA (21%) │  INTEL (61%)                       │  CONTEXT (18%)│
├──────────────┼────────────────────────────────────┼──────────────┤
│ TRADE HOOKS  │ ── INTEL ──                        │ FRESHNESS    │
│ [3 items]    │ What's happening — and where       │ • Stories    │
│              │ the money is actually going.       │ • Flows      │
│ TOP VELOCITY │                                     │ • Trades     │
│ [2.4×]      │ ▸ Stories (expanded)               │ • Signal     │
│              │ ▸ Capital Flows (collapsed)        │              │
│ SENTIMENT    │ ▸ Trade Ideas (collapsed)          │ NAVIGATE     │
│ [75%]        │                                     │ → Horizon    │
│              │ ── ALPHA ──                        │ → Flow Nodes │
│              │ Strategic positioning derived      │ → All Stories│
│              │ from the intel — where to act.     │ → All Trades │
│              │                                     │              │
│              │ ▸ The Signal (collapsed)           │ GAZZETTA     │
│              │ ▸ Track Record (collapsed)         │ • About      │
│              │                                     │ • Methodology│
│              │ HOW WE SERVE YOU                   │ • Data       │
│              │ C-SUITE | QUANT | EXECUTION        │ • Privacy    │
│              │                                     │ • Terms      │
└──────────────┴────────────────────────────────────┴──────────────┘
```

## CSS Grid

```css
.hints-lobby {
  display: grid;
  grid-template-columns: 21fr 61fr 18fr;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px 24px;
  align-items: start;
}
```

Columns A and C use `position: sticky; top: 20px` so they remain visible while the user scrolls through the main intel column.

## Responsive Breakpoints

### ≤1100px — Tablet
- Grid collapses to single column (`grid-template-columns: 1fr`)
- Side columns become horizontal grids (`grid-template-columns: repeat(auto-fit, minmax(160px, 1fr))`)

### ≤600px — Mobile
- Side columns become 2-column grids
- Font sizes reduce: velocity 20px, sentiment 22px

## Side-Column Populator

The side columns are populated by an inline `<script>` at the bottom of `index.html` that polls for `window.CAPITAL_FLOWS_DATA` (set by `app.js` after `fetchFlows()`). Polling loop: 500ms intervals, 15s max wait.

```javascript
(function(){
  var MAX_WAIT = 15000, waited = 0;
  function populateSides() {
    var fd = window.CAPITAL_FLOWS_DATA;
    if (!fd || !fd.flows || !fd.flows.length) {
      if (waited < MAX_WAIT) { waited += 500; setTimeout(populateSides, 500); }
      return;
    }
    // Populate trade hooks, velocity, sentiment, freshness
  }
  setTimeout(populateSides, 1000);
})();
```

## Column A — ALPHA Sidebar

| Section | Source | Content |
|---------|--------|---------|
| TRADE HOOKS | `CAPITAL_FLOWS_DATA.flows` (sorted by pace) | Top 3 flows: asset class, direction, confidence % |
| TOP VELOCITY | `CAPITAL_FLOWS_DATA.flows[0]` (by pace) | `N.N×` value + `$XB direction asset_class` description |
| SENTIMENT | `CAPITAL_FLOWS_DATA.flows` (inflow ratio) | `XX%` — bullish (≥70%), bearish (≤30%), neutral |

## Column C — CONTEXT/META Sidebar

| Section | Content |
|---------|---------|
| FRESHNESS | Colored dots + age for Stories, Flows, Trades, Signal |
| NAVIGATE | Breadcrumb links: Horizon, Flow Nodes, All Stories, All Trades |
| GAZZETTA | Meta links: About, Methodology, Data Sources, Privacy, Terms |

## Pitfalls

- **Side columns show "—" placeholders**: The populator runs 1s after page load. If `CAPITAL_FLOWS_DATA` isn't available within 15s, all values remain `—`. This is normal for first-visit cold loads — the polling interval (5 min in `app.js`) eventually refreshes.
- **col-context not in deployed HTML**: If `build_hashed_assets.py` doesn't scan index.html during the hash step, the column C markup may be missing. Verify with `curl -s URL | grep -c 'col-context'`.
- **RU pages need base href**: The `/ru/` pages use `<base href="/">` so that relative URLs (`./app.js`, `./styles.css`) resolve from the bucket root, not `/ru/`.
