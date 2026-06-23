# Hero Stat Tooltip Pattern — CSS-Only Implementation (June 2026)

## Pattern

Three hero stats (DIVERGENCES, TOP VELOCITY, LAST FLOW) each have a `?` tooltip icon. Hover reveals a white bubble with the stat description. Pure CSS via `::after` pseudo-element — no JavaScript needed. The same pattern is used by `.container-help` elements elsewhere on the site.

## HTML Structure

```html
<a href="./signal.html" class="hero-ind" id="heroContradictions">
  <span class="hero-ind-value">199</span>
  <span class="hero-ind-label">DIVERGENCES</span>
  <span class="hero-ind-context">Where news narrative and capital flows disagree — the edge</span>
  <span class="hero-stat-tooltip"
        data-tooltip="Active divergences between news narrative direction and capital flow direction. Higher count = stronger mispricing signal. Cross-referenced against OSINT sources and EPFR flow data."
        aria-label="More info about divergences">?</span>
</a>
```

## CSS

```css
.hero-stat-tooltip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px; height: 20px;
  border-radius: 50%;
  border: 1.5px solid #D4AF37;
  color: #D4AF37;
  font-family: "Inter", sans-serif;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  position: relative;
  margin-left: 6px;
  flex-shrink: 0;
  transition: all 0.15s;
  background: transparent;
  user-select: none;
  min-width: 44px; min-height: 44px;  /* WCAG touch target */
}

.hero-stat-tooltip:hover {
  background: #D4AF37;
  color: #FFFFFF;
}

/* Tooltip bubble */
.hero-stat-tooltip[data-tooltip]:hover::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: calc(100% + 12px);
  left: 50%;
  transform: translateX(-50%);
  background: #FFFFFF;
  color: #111827;
  font-family: "Source Serif 4", Georgia, serif;
  font-size: 11px;
  line-height: 1.5;
  padding: 10px 14px;
  border-radius: 6px;
  border: 1px solid #D4AF37;
  white-space: normal;
  width: 280px;
  max-width: 90vw;
  z-index: 300;
  pointer-events: none;
  text-align: left;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* CSS arrow pointing down to the ? icon */
.hero-stat-tooltip[data-tooltip]:hover::before {
  content: "";
  position: absolute;
  bottom: calc(100% + 4px);
  left: 50%;
  transform: translateX(-50%);
  border: 8px solid transparent;
  border-top-color: #D4AF37;
  z-index: 301;
  pointer-events: none;
}
```

## Stat Descriptions

| Stat | Tooltip Text |
|------|-------------|
| DIVERGENCES | "Active divergences between news narrative direction and capital flow direction. Higher count = stronger mispricing signal. Cross-referenced against OSINT sources and EPFR flow data." |
| TOP VELOCITY | "Fastest capital flow velocity detected this cycle. Measured vs 4-week rolling average. Higher velocity signals institutional urgency and potential regime change." |
| LAST FLOW | "Largest single capital inflow detected this cycle. Sourced from EPFR Global and Morningstar Direct. Sector and regional breakdown available in the full flow dashboard." |

## Mobile

On viewports <640px, the tooltip shifts to right-aligned to avoid clipping:
```css
@media (max-width: 640px) {
  .hero-stat-tooltip[data-tooltip]:hover::after {
    left: auto; right: 0; transform: none;
    width: 260px; max-width: 85vw;
  }
  .hero-stat-tooltip[data-tooltip]:hover::before {
    left: auto; right: 18px; transform: none;
  }
}
```

## Verification

```js
// In browser_console:
document.querySelectorAll('.hero-stat-tooltip').length  // must be 3
document.querySelector('.hero-stat-tooltip').getAttribute('data-tooltip').length  // must be >20
getComputedStyle(document.querySelector('.hero-stat-tooltip')).border  // must include gold rgb(212,175,55)
```
