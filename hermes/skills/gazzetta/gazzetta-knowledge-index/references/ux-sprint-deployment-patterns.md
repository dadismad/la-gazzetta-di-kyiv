# Phase 3 UX Sprint — Deployment Patterns (June 22, 2026)

## Mobile Breakpoints (768px + 390px)

Injected into `build_frontend.py` inline `<style>` block after the `@keyframes` rule:

```css
@media (max-width:768px){
  #desktop-sidebar{display:none!important}
  .md\:ml-72{margin-left:0!important}
  .tab-btn{font-size:11px;padding:8px 10px;min-height:44px}
  main{padding-left:12px!important;padding-right:12px!important}
  .grid-cols-1,.md\:grid-cols-2,.xl\:grid-cols-3{grid-template-columns:1fr!important}
  #cta-banner{flex-direction:column;align-items:flex-start;gap:8px}
  footer{font-size:11px;padding:16px 12px}
}
@media (max-width:390px){
  #tab-nav{flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch}
  .tab-btn{font-size:10px;padding:6px 8px;white-space:nowrap}
  h3{font-size:16px!important}
  .font-body-md{font-size:14px!important;line-height:20px!important}
}
```

## Glossary Tooltip Engine

60+ entries in a `GLOSSARY` JS object covering every ticker symbol (QQQ, SMH, FXI, etc.), narrative label, scoring term, and conceptual term. Wired via `data-ticker` and `data-narrative` attributes on sidebar links, Capital Flows table, and About phase table. Hover/tap triggers show a black tooltip with gold left border. Auto-wires on page load and after every tab switch via `window.switchTab` wrapper.

## Focus Rings (WCAG 2.4.7)

```css
button:focus-visible,a:focus-visible,[role="button"]:focus-visible,details summary:focus-visible{
  outline:2px solid #B45309;outline-offset:2px
}
```

## OG Tags + Twitter Cards + Favicon

Inline SVG favicon (burgundy square with gold 'G'):
```html
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='12' fill='%238B0000'/><text x='50' y='65' text-anchor='middle' font-family='Georgia,serif' font-size='52' font-weight='bold' fill='%23D4AF37'>G</text></svg>"/>
```

## CTA Banner

Dismissible banner with Telegram link, sessionStorage-persisted dismissal. Inserted between tab nav and main content in build_frontend.py.

## Copy-Link Button

Per-story card button that copies `{origin}/?story={story_id}` to clipboard with "Copied" feedback. Uses `navigator.clipboard.writeText()`.

## Tactical Horizon Radar

Collapsible `details` element with 3-column grid (BTC/ETH/Equities). Color-coded: crimson left border for alert (coiled_spring, local_top_risk, contrarian_buy), amber for warning (defensive_posture, cooling_off), green for safe (steady, trend_continuation). Rendered from `DERIVATIVES` JS constant injected at build time from `derivatives.json`.
