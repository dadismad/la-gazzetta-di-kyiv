# Alpha Board UI (v31.0, June 2026)

## Overview
Five-tab SPA replacing the original 4-tab layout. The Alpha tab hosts Catalyst-Flow-Trade cards.

## Tab Structure
Stream | Alpha | Capital Flows | Contradictions | About

## Alpha Board Components

### HTML Location
`build_frontend.py` template, after `<!-- VIEW 1: THE STREAM -->` closing `</main>`, before `<!-- VIEW 2: CAPITAL FLOWS -->`

### CFT Card Design
- Glass-morphism: `bg-surface/80 backdrop-blur-sm border border-gold/20 border-l-2 border-l-gold`
- 3-column responsive grid: `grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6`
- Gap meter bar: colored bar proportional to `catalyst_gap` (crimson ≥65, gold ≥40, gold-dim <40)
- Trade pills: `font-label-xs uppercase tracking-wider border border-outline`
- Domino pills: `domino-pill` class with data-target attribute, event delegation click handler
- Narratives with `cft: null` hidden entirely

### JS Rendering
- `renderAlphaView()` — iterates `NARRATIVES`, builds cards for active CFT data
- Wraps `window.switchTab` to trigger render on Alpha tab activation
- Domino event delegation: `#alpha-grid` click listener on `.domino-pill` elements, `scrollIntoView({behavior:'smooth',block:'center'})`

### Data Source
`NARRATIVES` array injected from `__NARRATIVES_JSON__`, each entry now carries `cft` sub-dict from `build_cft_block()` helper.

## Mobile Masthead Fix
- Font: `text-[16px] leading-[20px] sm:text-[20px] sm:leading-[26px] md:text-headline-lg-mobile`
- Icons: `hidden sm:inline` on pest_control and gavel spans
- Fits "LA GAZZETTA DI KYIV" on single line at 375px width

## Pitfalls
- JS escaping in patch tool: inline onclick with escaped quotes gets double-escaped. Use data attributes + event delegation instead.
- CDN cache: browser may serve stale HTML even after GCS deploy + CDN invalidation. Use cache-bust URL param for verification.
