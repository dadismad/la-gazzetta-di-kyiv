# Mobile Viewport Recalibration — Gazzetta Frontend

## When This Matters
The Gazzetta frontend is a single 640KB SPA compiled by `build_frontend.py`. It uses Tailwind CDN with Stitch DESIGN.md tokens. Mobile viewport breakage occurs when:

- Masthead "LA GAZZETTA DI KYIV" wraps to two lines
- Tab navigation buttons overflow horizontally
- Story cards break out of viewport bounds
- Tables (Capital Flows, Phase Matrix) have no scroll wrapper
- Fixed bottom nav overlaps last content card
- Font sizes are too large for dense data on small screens

## Root Causes (Identified June 2026)

### Masthead Wrapping
- `font-headline-lg-mobile` = 26px fixed at all breakpoints
- `tracking-widest` (0.1em letter-spacing) inflates rendered width
- `gold-outline` (`-webkit-text-stroke: 1px`) adds visual bulk
- `white-space: normal` (default) allows wrapping
- Available width at 375px viewport: ~279px after menu + spacer buttons
- Actual rendered width: ~340px → overflows by 61px

### Tab Navigation
- `font-metadata-sm` (13px) on buttons with no `whitespace-nowrap`
- Long labels "account_balance Capital Flows" wrap inside 166px buttons
- `w-max` on container can exceed viewport

### General Font Scale
- `font-headline-md` = 22px on all breakpoints — headlines consume 5-6 lines on mobile
- `font-body-md` = 16px — dense body text crowds small screens
- No responsive breakpoints on font sizes

## Fixed Pattern (Applied June 2026)

### Masthead Fix
```html
<!-- Before -->
<h1 class="font-headline-lg-mobile text-headline-lg-mobile uppercase tracking-widest text-roman-purple gold-strikethrough gold-outline">La Gazzetta di Kyiv</h1>

<!-- After -->
<h1 class="text-lg sm:text-xl md:text-2xl font-bold uppercase tracking-tight sm:tracking-widest text-roman-purple gold-strikethrough md:gold-outline whitespace-nowrap leading-none" style="font-family:'Playfair Display',Georgia,serif;">La Gazzetta di Kyiv</h1>
```
Key changes:
- Fluid font: `text-lg sm:text-xl md:text-2xl` (18px → 20px → 24px)
- `whitespace-nowrap` prevents wrap
- `md:gold-outline` — only on desktop (text-stroke blurs mobile text)
- Icons: `text-base sm:text-lg md:text-xl` — scale with text
- `flex-shrink` on container to prevent squeeze

### Tab Navigation Fix
```html
<div class="flex px-2 sm:px-margin-horizontal gap-0 w-max max-w-full min-w-full" id="tab-nav">
  <button class="tab-btn px-2 py-2 sm:px-4 sm:py-3 text-xs sm:text-metadata-sm uppercase tracking-wider whitespace-nowrap min-h-tap-target-min" data-tab="capital">
    <span class="material-symbols-outlined align-middle mr-1 text-xs sm:text-sm">account_balance</span>
    <span class="hidden sm:inline">Capital</span>
  </button>
</nav>
```
Key changes:
- `whitespace-nowrap` on each button
- `hidden sm:inline` on text labels — icons only on mobile
- Short labels: "Capital" instead of "Capital Flows"
- Reduced padding: `px-2 py-2` on mobile

### Global Font Downscale
```css
/* All font utilities get sm: breakpoint */
text-sm sm:text-body-md       /* body: 14px → 16px */
text-xs sm:text-metadata-sm    /* metadata: 12px → 13px */
text-[10px] sm:text-label-xs   /* labels: 10px → 12px */
text-base sm:text-lg md:text-headline-md  /* headlines: 16px → 18px → 22px */
```

### Viewport Containment
- All articles: `overflow-x-hidden`
- All tables: wrap in `<div class="overflow-x-auto hide-scrollbar -mx-2 sm:mx-0">`
- Table minimum widths: `min-w-[600px]` (capital), `min-w-[500px]` (phase)
- Cross-asset grid: `grid-cols-1 sm:grid-cols-2 md:grid-cols-4`

### Bottom Nav Clearance
- All view containers: `pb-20 sm:pb-stack-space-lg`
- Compensates for 56px fixed bottom nav on mobile

## Verification Checklist
- Set browser viewport to 375px width
- Masthead: single line, no wrapping
- Tab buttons: no horizontal overflow, icons only
- Story cards: headline fits in viewport, no horizontal scrollbar
- Capital Flows table: scrolls within container, not page
- About phase table: scrolls within container
- Bottom nav: does not overlap last card