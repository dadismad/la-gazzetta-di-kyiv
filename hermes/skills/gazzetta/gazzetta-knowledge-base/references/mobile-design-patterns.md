# Mobile Design Patterns — Gazzetta di Kyiv

Condensed from focus group sessions (June 2026). Both agents independently agreed on every decision below.

## Breakpoints

| Width | Behavior |
|-------|----------|
| >800px | Desktop: grid layout, sidebar sticky, photos right, full masthead |
| ≤800px | Tablet: single column, sidebar hidden, 📊 toggle visible, tagline hidden |
| ≤600px | Phone: photos move LEFT (`order: -1`), tighter card padding, brand icons visible |
| ≤400px | Small phone: compact masthead, photo 55×40px, bulava at 14px |

## Photo Placement

**Consensus: Photos on LEFT of text on mobile.** Reasons:
- Thumb obscuration: right side is covered during one-handed scrolling → photos on left avoid this
- Z-pattern scanning: left anchor creates visual rhythm during vertical scroll
- Sector signalling: a 70×50px photo on the left edge acts as a domain-identifier before the headline

**Implementation**: CSS `order: -1` on `.card-photo` inside the flex `.card-body`. DOM stays `text → photo`, CSS reverses to `photo → text`.

**Anti-pattern**: Never `display: none` photos on mobile. This is what the old ≤500px breakpoint did — it stripped visual identity entirely, producing a wall of identical-looking cards with no domain differentiation.

## Bet&Benefit Toggle

**Consensus: Bottom-right FAB or sticky-masthead button. Bottom-of-page static placement rejected.**

Best implementation: 📊 button in `.masthead-right` (sticky, always visible). On tap → bottom sheet overlay with slide-up animation, max-height 70vh, rounded top corners. `body { overflow: hidden }` when open.

The asset panel itself is `display: none` on desktop sidebar when ≤800px. Both the desktop sidebar and mobile bottom sheet source from the same `renderAssets()` function — the bottom sheet is a separate `<div class="bb-sheet-body">` populated by JS.

## Brand Signatures

- **Bulava (inline SVG)**: NEVER hidden. The SVG is 20×24px viewBox — an orb-head mace (circle r=5 + shaft + decorative rings + cross finial). Color: `var(--gold-dark)` with 0.8 opacity. Scales to 16×20px (≤600px) → 14×18px (≤400px). Do NOT use unicode ⚔⚔ (crossed swords) — that is historically inaccurate for Khmelnytsky. Use the SVG.
- **⚜ (Machiavelli)**: Hidden below 400px only. Scales from 16px → 13px → 11px. Color: `var(--gold-dark)` with 0.7 opacity
- **Name**: DM Serif Display, scales from 20px → 17px → 15px → 14px

## Card Typography

| Element | Desktop | ≤600px | ≤400px |
|---------|---------|--------|--------|
| Headline (h3) | 17px | 15px | 13px |
| Lead headline | 19px | 16px | 14px |
| Sector label | 7px | 8px | 8px |
| Summary | 12px | 11px | 10px |
| Detail text | 13px | 11px | 11px |
| Card padding | 8px 12px | 6px 10px | 5px 8px |

## Mobile-Specific CSS Needs

```css
/* Always include these for mobile card interaction */
-webkit-tap-highlight-color: transparent;  /* body */
-webkit-tap-highlight-color: rgba(200,164,78,0.15);  /* cards — gold tint on tap */

/* Bottom sheet animation */
@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

/* Body scroll lock when sheet is open */
body.bb-open { overflow: hidden; }
```

## Focus Group Verdict Pattern

Both the Mobile-First Reader and Design-Sensitive Reader personas should independently agree on: (1) photo placement, (2) toggle location, (3) brand visibility. When they disagree, default to the Mobile-First Reader's preference on placement/ergonomics and the Design Reader's preference on visual details.
