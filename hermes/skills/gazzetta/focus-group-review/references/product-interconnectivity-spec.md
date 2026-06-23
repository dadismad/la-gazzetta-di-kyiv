# Product Interconnectivity Audit — June 2026

## Proven Persona Combination
- **Product Architect (Bloomberg Terminal)** — designed cross-product linking (SECF→DES→FLOW→OMON→MSG)
- **UX Architect (Bloomberg/FT)** — cross-product navigation UX, information scent patterns

## Key Findings

### Current State: 21 missing cross-links across 6 products
Story→Flows, Story→Trades, Story→Signal, Story→Track, Story→Horizon: all missing
Flows→Stories, Flows→Trades, Flows→Signal, Flows→Track, Flows→Horizon: all missing
Trades→Stories, Trades→Flows, Trades→Signal, Trades→Track: all missing
Track→Stories, Track→Trades, Track→Flows, Track→Signal: all missing
Horizon→Flows, Horizon→Stories, Horizon→Trades, Horizon→Track: all missing

### P0 Cross-Links (highest impact, lowest effort)
1. Stories cfHint → Flows: make capital_flow text clickable (data + infrastructure already exist)
2. Flows → Stories: STORIES_CACHE already built, add "View Story" links
3. Signal dashboard content + bidirectional deep-links

### Cross-Link Pill Pattern
- Green border-left: flow links
- Gold border-left: trade links  
- Blue border-left: story links
- Mobile: tap-to-reveal, 32px min tap targets, bottom-sheet for panels

### "The Nexus" Global FAB
- Fixed bottom-right 48px button (gold on dark)
- Desktop: right panel slides in (320px)
- Mobile: bottom sheet slides up (70vh)
- Shows related content across all 5 products for current context

### Alpha Checklist Single-Page View
- Desktop 1440px: 2-column grid (main content + signal/track sidebar)
- Mobile 390px: stacked sections with sticky headers
- Shows top items from all 5 products compressed into one scrollable view

### "3-Second Scent Test"
Every cross-link must pass: in 3 seconds of looking, the user knows exactly what clicking will do.
