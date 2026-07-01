# Phase 9: Alpha Board — CFT Rendering Layer

**Date:** June 2026
**Scope:** `build_frontend.py` — client-side JS rendering of Catalyst-Flow-Trade blocks
**Status:** Deployed to local, pending production deploy

## Architecture

The Alpha Board is a 5th tab view in the Gazzetta SPA. It renders one CFT card per narrative with active catalyst data (non-null `cft` field in `NARRATIVES` JSON). Empty narratives are hidden entirely — no "no signal" filler cards.

```
Tabs: Stream | Alpha | Capital Flows | Contradictions | About
```

## Data Flow

1. `build_frontend.py` computes CFT data via `build_cft_block()` during build
2. CFT dict is injected into each narrative entry in `__NARRATIVES_JSON__`
3. Client-side `renderAlphaView()` reads `NARRATIVES`, filters for non-null `cft`
4. Generates HTML string for each card, injects into `#alpha-grid`

## CFT Card Structure

Each card has:
- **Header:** narrative title, story count, phase label, GAP badge (crimson for >=65, gold otherwise)
- **Gap meter:** proportional gold bar (`<div>` with percentage width)
- **3-column grid (Catalyst | Flow | Trade):**
  - Catalyst: headline text
  - Flow: `capital_fmt` (e.g. "$4.2B") + "at stake" label
  - Trade: ticker pills (`border border-outline`) + asset class tags (`bg-surface-container`)
- **Domino spillover:** clickable pill buttons with narrative title + score

## Domino Pills — Interaction Pattern

**Critical pattern to avoid escape-drift with patch() tool:**

Do NOT use inline `onclick` with escaped quotes in JS-generated HTML. The patch() tool double-escapes backslashes, breaking JavaScript syntax.

Use this pattern instead:
```javascript
// Button: data-target attribute for target element ID
'<button class="domino-pill" data-target="cft-' + nid + '">' + title + '</button>'

// Event delegation on the grid container
document.getElementById('alpha-grid').addEventListener('click', function(e) {
    var pill = e.target.closest('.domino-pill');
    if (!pill) return;
    var targetId = pill.getAttribute('data-target');
    if (targetId) {
        var el = document.getElementById(targetId);
        if (el) el.scrollIntoView({behavior: 'smooth', block: 'center'});
    }
});
```

## Tab Architecture

5 tabs with hash routing (`#stream`, `#alpha`, `#capital`, `#contradictions`, `#about`).

`switchTab()` wrapper renders Alpha view on tab activation:
```javascript
var origSwitchTab = window.switchTab;
window.switchTab = function(name) {
    origSwitchTab(name);
    if (name === 'alpha') renderAlphaView();
};
```

## Mobile Bottom Nav

5 buttons: Stream, Alpha, Capital, Matrix, About.
`switchTab` mobile nav array: `['stream','alpha','capital','contradictions','about']`

## Visual Design

- Grid: `grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6`
- Cards: `bg-surface/80 backdrop-blur-sm border border-gold/20 border-l-2 border-l-gold`
- Gap meter: gold `h-1` bar with crimson for BREAKING (>=65)
- Ticker pills: `px-2 py-0.5 font-label-xs uppercase tracking-wider border border-outline`
- Domino pills: `border border-gold/30 text-gold-accessible hover:border-gold`
- Domino threshold: 0.30 (raised from 0.25 backend threshold for cleaner UI)

## Empty State

When no narratives have active CFT data:
```
"No active catalysts" — centered, muted, no cards rendered
```

## Files Modified

- `build_frontend.py` — 5 patches (tab button, view container, renderAlphaView JS, hash routing, mobile nav)
- No template changes needed — CFT data flows through existing `__NARRATIVES_JSON__` payload
