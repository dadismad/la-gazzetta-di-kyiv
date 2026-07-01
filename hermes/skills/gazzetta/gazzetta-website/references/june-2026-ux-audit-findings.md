# June 2026 UX Audit — Findings & Fixes

## Material Symbols Font: The opsz Axis Requirement

The site uses `Material+Symbols+Outlined` via Google Fonts CDN. The URL must include ALL four axes:

```
CORRECT: family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200
BROKEN:  family=Material+Symbols+Outlined:wght,FILL@100..700,0..1
```

Symptom of missing `opsz`: icons render at 0x0 pixels. Elements show correct `font-family: "Material Symbols Outlined"` but `offsetWidth=0`. Raw ligature text (`auto_stories`, `sync_alt`, etc.) appears as visible prose.

**Required CSS rule:**
```css
.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  display: inline-block;
  line-height: 1;
}
```

**Verification:** `document.querySelector('.material-symbols-outlined')?.offsetWidth` must be > 0.

## DOM Ordering Rule: Masthead Before Sidebar

The `<aside id="desktop-sidebar">` (Narrative Exposure + Fragility Index) MUST appear AFTER `<header>` (masthead) in DOM order. When the sidebar is the first `<body>` child, mobile viewports render it as inline content above the masthead — producing incomprehensible ticker walls before the brand identity.

Fix: move the `<aside>` block from before the main content `<div>` to INSIDE it, placed after `</header>` and before `<!-- TAB NAVIGATION -->`.

## Cross-Current Coalescence Aggregation

When the same narrative target triggers both REINFORCING and COMPLICATING signals within the tracking window, merge them into a single "CROSS-CURRENT CONVERGENCE" card instead of two identical-looking parallel cards.

**Card design:**
- Header: `swap_horiz` icon + "CROSS-CURRENT CONVERGENCE" label
- Body: "[Narrative] is being pulled in opposite directions simultaneously — X signals reinforcing, Y signals complicating"
- Side-by-side columns (`grid-cols-1 md:grid-cols-2`):
  - Left: gold `trending_up` "Reinforcing (N)" with supporting stories
  - Right: crimson `trending_down` "Complicating (N)" with supporting stories
- Single-direction alerts (all reinforcing OR all complicating) keep the original "CAPITAL CONVERGENCE" format

**Backend logic** (in `build_frontend.py` coalescence section):
```python
target_signals = {}  # key: target -> {"reinforces": [...], "complicates": [...]}
# Populate both directions per target
# If len(reinforcing) >= 3 AND len(complicating) >= 3 -> cross_current type
# Else if either >= 3 -> single type
```

## Inline JS Template Fragility

The story card HTML is rendered client-side via inline JavaScript using concatenated string templates:
```javascript
return '<article>' +
  '<div class="...">' + content + '</div>' +
  '</article>';
```

Inserting new HTML blocks into these concatenated chains is extremely fragile. The `</div>` closing-tag chain must remain exact. Three attempts to add a source attribution footer (A3) all caused silent JS syntax errors (`Unexpected token '<'`) because the closing div structure broke.

**Pattern for safe additions:** Use post-render DOM manipulation instead of modifying the template string:
```javascript
// AFTER cardsEl.innerHTML = ... 
Array.from(cardsEl.querySelectorAll('article')).forEach(function(a) {
  var footer = document.createElement('div');
  footer.className = 'source-footer ...';
  footer.innerHTML = '...';
  a.appendChild(footer);
});
```

## Focus Group Results (5 Personas, June 2026)

Combined score: 6.3/10 — CONDITIONAL PASS. Full report: `gazzetta-grand-master-ux-plan.md` in `~/.hermes/audits/`.

Consensus issues (flagged by 3+ of 5 personas):
1. No methodology disclosure — GAP scores are a black box
2. Overwhelming jargon density — "Parallel Stack", ticker symbols, zero explanations
3. Gold-on-white contrast FAIL — #D4AF37 on #FAF9F6 = 2.00:1 (WCAG AA requires 4.5:1)
4. Article cards have no visual boundaries — wall of text with zero container differentiation
5. "decouples from" appears in ~80% of headlines — language rot
6. No onboarding/site identity — visitors can't figure out what the site IS
7. Divergence Map visual uniformity — all items look identical regardless of GAP severity

Unanimous praise (preserve these):
- Burgundy/gold masthead identity
- The Lefevre Filter concept
- Narrative Lifecycle table design
- Playfair Display + Inter typography
- Native `<details>` expandable cards
