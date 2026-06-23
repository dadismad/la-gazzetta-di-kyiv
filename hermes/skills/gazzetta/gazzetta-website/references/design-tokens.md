# Gazzetta Website — Design Tokens v22.2

Current as of June 2026. Pure white page, Tyrian purple + gold masthead, serif typography.
Deployed at `pureciclismo.github.io/gazzetta-di-kyiv/site/`, repo at `/Users/alexstocchi/projects/gazzetta-di-kyiv/`.

## CSS Custom Properties

```css
:root {
  --bg:        #FFFFFF;   /* Pure white everywhere */
  --white:     #FFFFFF;
  --card-bg:   #FFFFFF;

  --blue:      #2563EB;   /* Sharp blue — links, interactive */
  --green:     #059669;   /* Casino green — buy signals, inflows */
  --red:       #DC2626;   /* Casino red — sell signals, outflows */
  --gold:      #D4AF37;   /* 24K gold — accents, icons */
  --gold-light: rgba(212,175,55,0.10);

  --ink:       #111827;   /* Near-black — all body text */
  --ink-light: #6B7280;   /* Grey — secondary text */
  --ink-muted: #9CA3AF;   /* Muted grey */

  --divider:   #E5E7EB;   /* Light divider */
  --card-border: #E5E7EB;

  --display: 'DM Serif Display', Georgia, serif;
  --body:    'Source Serif 4', Georgia, serif;
  --sans:    'Inter', -apple-system, sans-serif;
}
```

## Masthead

| Element | Value |
|---------|-------|
| Background | `#FFFFFF` |
| Bottom border | `2px solid var(--gold)` |
| Name fill | `#990024` (Tyrian purple — sRGB, Fiorentina Viola inspired) |
| Name stroke | `1.5px #F5D76E` (bright gold "golden lining") |
| Name font | DM Serif Display, var(--φ-lg) (~26px) |
| Bulava icons | `color: var(--gold)` (#D4AF37) |
| Machiavelli quill | `color: var(--gold)`, opacity 0.7 |
| Tagline | Source Serif 4, 12px italic, var(--ink-light) |
| Meta (date) | Inter, 13px, 500, var(--ink-light), uppercase |

## Typography (current)

**FONT-SIZE FLOOR: 11px.** No text element may use a font-size below 11px. This was enforced 2026-06-10 (88 violations bumped, 7.5px–10px → 11px). WCAG AA requires minimum readable text size for accessibility, and retail/older users cannot read sub-11px elements.

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| Masthead name | DM Serif Display | var(--φ-lg) | 400 | #990024 + gold stroke |
| Masthead tagline | Source Serif 4 | 12px | italic | var(--ink-light) |
| Masthead meta (time/date) | Inter | 13px | 500 | var(--ink-light) |
| Container title | Inter | 11px | 700 uppercase | var(--ink) |
| Story headline (h3) | DM Serif Display | 20px | 400 | var(--ink) |
| Lead story headline | DM Serif Display | 22px | 400 | var(--ink) |
| Capital flow claim | Source Serif 4 | 12px | 600 | var(--ink) |
| Story summary | Source Serif 4 | 12px | 400 | var(--ink-light) |
| Category tag | Inter | 11px | 700 uppercase | var(--gold) |
| THE PLAY label | Inter | 11px | 700 uppercase | var(--gold) |
| THE PLAY text | Source Serif 4 | 11px | italic | var(--ink-light) |
| Anchor symbol | Inter | 11px | 700 | var(--ink) |
| Anchor pill (BUY/SELL/WATCH) | Inter | 11px | 600 | — |
| Anchor conviction badge | Inter | 11px | 700 uppercase | — |

## Layout

Single column, max-width 1000px, no sidebar. Five collapsible containers.
Hero: compressed (16px pad, 20px H1), 5 stats, CTA buttons.
Cards: #FFFFFF background, 1px #E5E7EB borders, φ-spacing.

**FRAMELESS CONTRACT**: No decorative border-radius. No decorative box-shadow. Borders are 1px #E5E7EB dividers only. Functional circle elements (avatars, status dots) may use `border-radius: 50%`. Enforced 2026-06-10 (24 border-radius → 3 functional, 7 box-shadows → 0).

## Color History

| Version | Masthead name fill | Stroke | Date |
|---------|-------------------|--------|------|
| v17 | var(--gold) #C9A96E | none | ~May 2026 |
| v20.20 | #8EC8E8 (light sky blue) | 1.2px #D4AF37 | ~early June 2026 |
| v22.1 | #C8ECF8 (brighter sky blue) | 1.5px #F5D76E | June 2026 |
| **v22.2** | **#990024 (Tyrian purple)** | **1.5px #F5D76E** | **June 2026** |
