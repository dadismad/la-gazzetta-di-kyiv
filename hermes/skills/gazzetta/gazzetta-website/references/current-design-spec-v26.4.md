# Gazzetta di Kyiv — Current Design Spec (v26.4 — June 2026)

## Masthead
- **Name**: Solid `#8B0000` dark red (NOT gradient/shimmering purple). Font: Playfair Display, 3em.
- **Symbols**: Caduceus LEFT, crossed bulavas RIGHT. Must appear on EVERY page.
- **Nav**: INTEL, ALPHA, MENU as simple text links in `.masthead-right` (NOT in dark nav bar, NOT dropdowns).
- **Gold line**: `border-bottom: 2px solid var(--gold)` below masthead.

## Layout
- **Single column**: `grid-template-columns: 1fr; max-width: 960px;`
- **NO sidebars**: `.col-alpha`, `.col-context` = `display: none`
- **Frameless cards**: NO box-shadow, NO border-radius on cards
- **Pure white**: `#FFFFFF` everywhere, no off-white tints

## Card Borders
- ALL cards use `border-left: 2px solid var(--gold)` — hero-ind, side-section, svc-card
- `.teaser-item:hover` adds `border-left: 2px solid var(--gold)` on hover

## Hero Section
- Headline: 26px Playfair Display, centered
- Subtitle: "Track capital flows, trade the contradictions, and follow the money through 5 intelligence products — from narrative reports to verifiable bets." (14px, centered, max 640px)
- 3 indicators: Divergences, Top Velocity, Last Flow — horizontal pills with gold left borders
- UNLOCK FULL SIGNAL button: dark (#111827) background, white text, links to Telegram

## Story Cards
- NO sector chips (`.teaser-chip` removed from rendering)
- Format: `$50M Headline text... · time ago`
- Amounts < $1B → M format (e.g. `$50M`, not `$0.05B`)
- Amounts ≥ $1B → B format with 1 decimal (e.g. `$14.8B`)
- 14px font, 10px padding, 6px gap between cards

## Font Floor
- Minimum 11px anywhere. No ≤9px fonts.
- Labels: 12px minimum (hero-ind-label, side-section-label, svc-persona)

## Fixes Applied (v26.3 Pipeline)
- They Say/Reality dedup (>70% overlap triggers differentiation)
- Asset class detection: tech-first ordering, 26 keywords across 6 sectors
- Confidence floor for micro-flows
