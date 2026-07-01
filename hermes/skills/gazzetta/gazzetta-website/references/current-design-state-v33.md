# Current Design State (v33.0 — June 2026)

**The SKILL.md core design principles are outdated (v30.0). Refer to this file for current state.**

## Visual Identity

| Element | Value |
|---------|-------|
| Background | #0A0A0F (dark terminal) |
| Body text | #E6E4E0, 13px Inter |
| Card headlines | 14px Inter, 600 weight, #E6E4E0 |
| Data fields | 11px JetBrains Mono (.gap-score, .capital-num, .price-mono) |
| Masthead name | Roman purple, Playfair Display, uppercase, tracked |
| Gold accents | #D4AF37 — masthead border, card tier borders, GAP LEADERBOARD header |
| BREAKING zone | #7F1D1D (burgundy, NOT crimson #8B0000) |
| Emerald | #10B981 for allocation percentages (.allocation-pct) |
| BREAKING pulse | 6s gapPulse animation on article[data-gap-high="true"] |

## Card Layout (Rule of 3 Lines)

Collapsed state shows:
1. Source tier + recency + GAP score
2. Headline
3. Trade thesis line (direction ticker @ entry | Stop: X | Target: Y) or "No active thesis"

Full dispatch (they_say / reality / capital / narrative) hidden behind `unfold_more` toggle in `<details class="card-drawer">`.

## Key CSS Classes

- `.font-body-md` — 13px body text
- `.font-headline-md` — 14px card headlines
- `.font-label-xs` — 11px labels
- `.gap-score` — JetBrains Mono, GAP numeric values
- `.capital-num` — JetBrains Mono, capital amounts
- `.price-mono` — JetBrains Mono, price data
- `.allocation-pct` — Emerald #10B981, JetBrains Mono, allocation percentages
- `.glass-panel` — Sticky header backdrop blur

## Build Architecture

- Single file: `scripts/build_frontend.py` generates `public/index.html`
- All CSS is inline `<style>` block — NO external stylesheet
- Tailwind CDN loaded via `<script>` for utility classes
- Material Symbols loaded via Google Fonts for icons
- Deploy: `gsutil cp public/index.html gs://www.lagazzettadikyiv.com/index.html`

## What Changed from v30.0 (White Design)

- Background: #FFFFFF → #0A0A0F
- Card backgrounds: White → Dark surface containers
- Masthead symbols: Fox&Lion/bulavas SVGs → Material Symbols icons (pest_control, gavel)
- Crimson BREAKING: #8B0000 → #7F1D1D
- Font: Playfair Display → Inter (body), Playfair (masthead only), JetBrains Mono (data)
- Added: Card collapse (Rule of 3 Lines), GAP Leaderboard, Decay Clock, Verified badge
- CSS: All in inline `<style>`, Tailwind CDN cascade (see references/tailwind-cdn-cascade.md)
