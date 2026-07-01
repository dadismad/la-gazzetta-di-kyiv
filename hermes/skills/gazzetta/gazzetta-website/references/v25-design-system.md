# Gazzetta Website — v25.0 Design System Changes (June 11, 2026)

## Masthead — 300% Title, Top-Right Aligned
- `.masthead-name` font-size: `3em` (was `var(--φ-lg)`)
- Text aligned right (`text-align: right; margin-left: auto; order: 10`)
- Brand marks (bulava + caduceus) remain left as visual anchors
- Masthead uses `align-items: flex-start` for top alignment
- Tyrian purple gradient + gold hairline stroke unchanged

## Navigation — 3 Master Dropdown Accordions
- Replaced `<nav class="product-nav">` (7+ inline links) with `<nav class="master-nav">`
- Three dropdowns: `INTEL ▾`, `ALPHA ▾`, `MENU ▾`
- Dark-themed panels (`background: #1A1F2E`, gold borders)
- Vanilla JS toggle: click trigger → toggle `.open` class, outside click → close all
- Sticky below masthead (`top: 56px`)

## Container "?" Tooltip Badges
- `<span class="container-help" data-tooltip="...">?</span>` on every container
- Circular 18px badge, dark tooltip on hover via `::after` pseudo-element
- Tooltip: 280px wide, dark background, gold border, 11px font

## Trade Hooks — DELETED
- Entire `#sideHooks` section removed from `index.html`
- FULL SIGNAL gate (Telegram CTA) remains

## Freshness — Relocated to Signal Page
- FRESHNESS sidebar removed from homepage
- Moved to `signal.html` (Alpha sub-page)

## Intel/Alpha Container Parity
- Unified `.col-intel` and `.col-alpha` container styles
- Both use: Playfair Display titles, Source Serif 4 body, italic descriptions

## Deploy Commits
- `3bce90e`: v25.0: Masthead 300% title, 3-dropdown nav, container tooltips, trade hooks deleted, freshness->signal, Intel/Alpha parity
- `6bb5a63`: Update ops report with Sprint 1 Virtual Team decisions and change log
