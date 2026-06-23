# Mobile CSS Overhaul Pattern — v22.30

Applied June 2026 after a 3-persona iPhone focus group audit found the site scored 3/10 on mobile UX.

## Key Findings (3/3 consensus)

- 30/34 touch targets fail Apple HIG 44×44px minimum
- 42+ elements under 12px font size
- All sections expanded by default (21 content items on 390px screen)
- Hero wastes 25% of mobile viewport with branding
- Nav links at 10-11px, CTA links at 15px height

## CSS Pattern

```css
/* Phone (≤600px) — mobile-first overhaul */
@media (max-width: 600px) {
  /* Layout: full-width stacking */
  .hints-lobby, .layout, .product-page { max-width: 100%; padding: 0 8px 16px 8px; }
  .hero { padding: 12px 10px 10px !important; }
  .hero-headline { font-size: 16px !important; }

  /* Masthead: compact 2-row */
  .masthead { padding: 6px 10px; flex-wrap: wrap; }
  .masthead-tagline { display: none; }
  .lang-switch { min-width: 44px; min-height: 44px; font-size: 13px; padding: 10px 14px; }

  /* Container headers: 48px tap targets */
  .container-header {
    min-height: 48px !important; padding: 10px 12px !important;
    cursor: pointer; user-select: none;
    -webkit-tap-highlight-color: rgba(0,0,0,0.05);
  }
  .container-header:active { background: #E5E7EB; }
  .container-title { font-size: 13px !important; }

  /* Collapse defaults */
  .container.collapsible:not(.expanded) .container-body { max-height: 0; opacity: 0; padding: 0; }

  /* Teaser items: 44px min-height */
  .teaser-item { min-height: 44px; padding: 10px 8px; font-size: 13px; }
  .teaser-full-link { min-height: 44px; line-height: 44px; font-size: 13px; }

  /* Flow rows: bigger taps */
  .flow-row { min-height: 44px; padding: 8px 10px; }
  .flow-expand-hint { width: 24px; height: 24px; }

  /* Footer: 44px tap targets */
  .footer a { min-height: 44px; display: inline-flex; align-items: center; }
}
```

## Non-Negotiables

- Minimum font size on mobile: 12px (body 16px)
- Minimum touch target: 44×44px (Apple HIG)
- Maximum sections expanded by default: 1 (Stories only)
- Hero padding: ≤12px
- No horizontal scroll at 390px viewport
- Collapse arrows: ≥18×18px visible SVG
- Active state feedback on all tappable elements
