# Gazzetta Visual Audit Methodology

Systematic frontend audit procedure developed June 2026 after user directive: audit content synchronization BEFORE fixing infrastructure.

## When to Run

- User reports site is "a complete mess" or "content is broken"
- After any deploy that touches HTML, JS, or data files
- When EN/RU versions are suspected of divergence
- Weekly health check

## Phase 1: Parallel Data + Frontend Audit

Spawn two delegate_task subagents simultaneously:

**Subagent A — Data Pipeline Audit** (`toolsets: [terminal, file]`)
```
Check: stories.json (count, confidence_pct distribution, amount_b distribution, pace_multiplier distribution, capital_flow presence)
Check: flows.json (count, confidence_pct distribution, pace_multiplier distribution, asset_class distribution, positioning diversity)
Check: data/stories.json vs site/data/stories.json sync
Check: generate_flows.py compute_confidence() output
```

**Subagent B — Frontend Audit** (`toolsets: [browser, terminal]`)
```
Visit every page: homepage EN, homepage RU, stories.html, flows.html, trades.html, signal.html, track.html, flow-nodes.html, event_horizon.html
For each: browser_navigate → browser_console (errors) → browser_console(expression) for card counts, data availability, hero values
Compare EN vs RU: hero indicators, nav labels, container content, sidebar data
```

## Phase 2: Cross-Page Comparison

After subagents return, verify:

| Comparison | What to Check |
|------------|---------------|
| Homepage vs stories.html | Story count (teasers vs full cards), lead headline match |
| EN vs RU | Hero velocity, last inflow, nav labels, container titles |
| Flows vs Trades | Flow→trade cross-linking consistency |
| Signal vs Flows+Trades | Triangulation data sources present |

## Phase 3: DOM Verification (browser_console expressions)

```javascript
// Card counts
document.querySelectorAll('.card, .teaser-item').length

// Hero indicator values
Array.from(document.querySelectorAll('.hero-ind-value')).map(e => e.textContent)

// i18n state
window.i18n ? window.i18n.lang : 'no i18n'

// Data availability
typeof window.CAPITAL_FLOWS_DATA !== 'undefined'

// SVG rendering (flow-nodes)
document.querySelector('#cn-nodes-layer > *').length

// Market regime values
document.getElementById('regimeMFValue')?.textContent
```

## Common Pitfalls

1. **Browser snapshots lie**: JS-rendered content shows 11 elements in snapshot but 59 cards in console. Always verify with console expressions.
2. **CDN caching**: Deploy changes may not be visible for 5-15 minutes. Cache-bust with `?t=<timestamp>`.
3. **RU data paths**: `/ru/` pages resolve `./data/` to `/ru/data/` — files must exist in both locations.
4. **Pre-render empty state**: Hero indicators show "—" until JS executes. Verify with browser_console, not snapshot.

## Verification Checklist

- [ ] All 9 pages return HTTP 200
- [ ] Zero JS errors on homepage (EN)
- [ ] Hero indicators populated (not "—")
- [ ] EN and RU hero values match
- [ ] Homepage teaser count ≤ stories.html card count
- [ ] RU i18n active (nav labels in Russian)
- [ ] Flow Nodes SVG renders (13+ elements in nodesLayer)
- [ ] Market Regime panel populated (not dashes)
- [ ] Trade hooks show directional data
- [ ] Sidebar tickers with live prices
