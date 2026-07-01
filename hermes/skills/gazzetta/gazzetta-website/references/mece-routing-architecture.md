# MECE Routing Architecture — Gazzetta di Kyiv (v25.5)

## Principle

Every sub-page is a **dynamic derivative** of the central data feed — `stories.json` + `flows.json`, both fetched by `app.js`. No page carries its own static data. No page duplicates the data pipeline. Mutually Exclusive, Collectively Exhaustive.

## Architecture Map

```
                  ┌─────────────────────────┐
                  │    index.html (Home)      │
                  │    app.js → stories.json  │
                  │    app.js → flows.json    │
                  │    (central data hub)     │
                  └──────┬──────┬─────────────┘
                         │      │
         ┌───────────────┤      ├───────────────┐
         ▼               ▼      ▼               ▼
   ┌──────────┐   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ stories  │   │  flows   │  │  trades  │  │  signal  │
   │ ALL 190  │   │ sectors  │  │ anchors  │  │ triang   │
   │ cards    │   │ regime   │  │ ATR stop │  │ diverg   │
   └──────────┘   └──────────┘  └──────────┘  └──────────┘
         │               │          │              │
         ▼               ▼          ▼              ▼
   ┌──────────┐   ┌──────────┐  ┌──────────┐
   │ horizon  │   │  flow    │  │  track   │
   │ FILTERED │   │  nodes   │  │ record   │
   │ C-SUITE  │   │ QUANT    │  │ settled  │
   └──────────┘   └──────────┘  └──────────┘
```

**All 7 pages** load the same `app.js` → same `stories.json` + `flows.json`. Each page **filters/renders differently**:

| Page | Data Source | Rendering |
|------|-------------|-----------|
| `stories.html` | stories.json | All 190 story cards, full descriptions |
| `flows.html` | flows.json | Sector grid, market regime indicators, flows list |
| `trades.html` | ANCHOR_ASSETS (app.js) | Trade hooks with ATR stops, PDR gauge |
| `signal.html` | stories.json × flows.json | Triangulation (stories × flows × trades) |
| `track.html` | track_record.json | Settled bets, win rate, realized P&L |
| `event_horizon.html` | stories.json (filtered) | Horizon-relevant stories (macro, geopolitics, sovereign, commodities, energy) |
| `flow-nodes.html` | flows.json → transformFlowsData() | SVG node graph with live flow data |

## Executive Data Frameworks

| Persona | Page | Content |
|---------|------|---------|
| **C-SUITE** | `event_horizon.html` | Macro Horizon — structural policy shifts, supply-chain bottlenecks, regulatory implications. Board-ready. |
| **QUANTITATIVE** | `flow-nodes.html` | Flow Telemetry — capital velocity differentials, correlation coefficients, heat scores. Zero narrative fluff. |
| **EXECUTION** | `trades.html` | Action Triggers — directional bias, entry/stop levels, conviction ratings with ATR-derived stops. Trade-ready. |

## Unified Shell Pattern

Every sub-page MUST include:
```html
<link rel="stylesheet" href="./styles.css?v=25.0"/>
<script src="./i18n.js?v=25.0"></script>
<script src="./app.js?v=25.0"></script>
<!-- Hidden containers for boot() compatibility -->
<div style="display:none">
  <div id="heroConfidence"></div><div id="heroFlowTotal"></div>
  <div id="heroStoryCount"></div><div id="heroAssetCount"></div>
  <div id="heroBetTotal"></div><div id="anchorGrid"></div>
  <div id="trackRecord"></div><div id="signalGrid"></div>
  <div id="flowsList"></div><div id="mastheadMeta"></div>
  <div id="heroLayerCount"></div><div id="anchorCount"></div>
</div>
```

### Masthead (identical on all pages)
- Crossed bulavas SVG + "La Gazzetta di Kyiv" link to `./`
- Product nav: Stories, Flows, Horizon, Flow Nodes, Trades, Signal, Track
- Lang switcher: EN / RU buttons with `i18n.switchLang()`

### Unified Footer (mandatory on EVERY sub-page)
```html
<footer style="border-top:1px solid var(--divider);padding:32px 0 24px;margin-top:48px;">
  NAVIGATE:
    → Horizon (Geopolitical chokepoints)
    → Flow Nodes (Capital network graph)
    → All Stories (Full intel feed)
    → All Trades (Position dashboard)
  GAZZETTA:
    About · Methodology · Data Sources · Privacy · Terms
  Kyiv · Since 2025
</footer>
```

## Anti-Pattern: CSS Stylesheet Fragmentation

**Symptom:** CSS changes not reaching all pages. Some pages look different from others.

**Root cause:** Different sub-pages reference different stylesheet paths:
- `styles.css?v=22.18` (some pages)
- `styles.3755c776.css` (other pages)
- `styles.css` unversioned (standalone pages)

**Fix:** All pages → `styles.css?v=<current_version>`. Run after every version bump:
```bash
for f in *.html; do
  sed -i '' 's|styles\.[a-f0-9]*\.css|styles.css|g' "$f"
  sed -i '' 's|styles\.css"|styles.css?v=CURRENT"|g' "$f"
done
```

## Anti-Pattern: Standalone Static Pages

**Symptom:** `event_horizon.html` and `flow-nodes.html` had 1,000+ lines of standalone HTML with inline CSS and hardcoded data. Zero connection to the live data feed.

**Fix:** Rewrite as thin shells that load `app.js` and filter/transform the central data feed. The pages went from 1,230 and 1,190 lines to 283 and 1,404 lines respectively, with the bulk of the file being the SVG graph renderer for flow-nodes.

## Dynamic Page Rewrite Checklist

When converting a standalone page to a dynamic derivative:
1. Replace inline CSS with `<link rel="stylesheet" href="./styles.css?v=N>"`
2. Add `<script src="./i18n.js?v=N"></script>` + `<script src="./app.js?v=N"></script>`
3. Add hidden container divs for boot() compatibility
4. Replace hardcoded masthead with the standard `.masthead` header
5. Replace minimal footer with the unified NAVIGATE/GAZZETTA footer
6. Add a `<main class="product-page">` container with a `#newsCol` element (if rendering story cards)
7. Add inline `<script>` for page-specific filtering/rendering logic that runs after boot()
8. Add full SEO metadata (canonical, OG, Twitter, hreflang alternates, ld+json)
9. Copy root file → site/ → deploy to GCS
10. Verify via `browser_navigate` + `browser_console`
