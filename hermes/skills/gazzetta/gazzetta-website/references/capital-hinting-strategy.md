# Capital Hinting Strategy — Research & Implementation

Derived from an information-scent deep-dive (Pirolli & Card, 2026), competitor pattern analysis (Bloomberg/FT/Yahoo Finance), and UX literature on progressive disclosure. Applied to Gazzetta di Kyiv v22.9+.

## Core Principles

1. **Information Scent** — Users evaluate proximal cues (headlines, metadata, micro-indicators) to estimate the cost/reward of engaging. Strong scent = specific signals that shrink the "curiosity gap" just enough to prompt action.
2. **Progressive Disclosure** — Show structure and magnitude, not the payload. "There's $3.2B at play here" is a hint; "the full flow breakdown is inside" is the payload.
3. **Curiosity Gap** — Tease *what kind* of value is inside without revealing the conclusion. Show count, direction, magnitude, time — but never the actual fact or trade idea.

## Competitor Patterns

- **Bloomberg Terminal**: Color-coded LEDs for data freshness, green/red arrows for direction, ticker chips with change %.
- **FT.com**: "FT 950" token for premium content, "15 min read" labels, inline sector tags.
- **Yahoo Finance**: Mini sparkline graphs next to headlines, % chips with green/red arrows.
- **The Economist**: Section badges (Leaders, Briefing), byline-less authority, chart count indicators.

Common thread: **proximity** — indicators live next to the content they describe, not hidden in menus or tooltips.

## Anti-Patterns (What Not To Do)

- **Clutter**: More than one chip/indicator per item on mobile.
- **Spoiling the reveal**: Showing the full conclusion or numeric value in the teaser.
- **False promises**: Chart icon when there's no chart, "Key insight" label on filler content.
- **Heavy styling**: Shadows, borders, backgrounds break the frameless aesthetic.

## Gazzetta Implementation (v22.9)

Two micro-hints were implemented, both frameless (color + opacity + typography only):

### `.cf-hint` — Story Card Capital Magnitude Chip
- **Location**: Next to headline in collapsed story card, before the contradiction tier badge
- **Content**: `$3.2B ↓` or `$1.0B ↑`
- **Styling**: 9px, 700 weight, opacity 0.65. Green (#059669) for inflows ↑, red (#DC2626) for outflows ↓
- **Title attribute**: "Capital flowing into/out of [sector]"
- **What it hints**: "This story has capital flow data of this magnitude and direction"
- **What it doesn't reveal**: The full claim, the projected amount, the institutional positioning, the trade idea

### `.flow-linked-story-hint` — Flow Item Story Link Indicator
- **Location**: Next to the expand chevron in collapsed flow item header
- **Content**: `↳` character
- **Styling**: 10px, opacity 0.4, ink-muted
- **Title attribute**: "Linked story — expand to see"
- **What it hints**: "This flow is connected to a story — click to see which one"
- **What it doesn't reveal**: The story title, the headline, the contradiction

## Information Scent Verification

The `.cf-hint` chip passes the Pirolli & Card test:
- **Proximal**: Lives in the headline row, directly adjacent to the content it augments
- **Specific**: Shows exact amount and direction, not a vague "has data" badge
- **Teasing**: Users see "$3.2B ↓" and want to know WHY capital is flowing out — they expand the card
- **Non-spoiling**: The full claim ("$3.2B flowing out of equities — projected +$5.1B change at 80% confidence") is revealed on expand

## Future Extensions

- **Color intensity gradient**: Larger amounts could use deeper opacity (e.g., $10B+ at opacity 0.85, $1B at 0.45)
- **Velocity indicator**: Show a pace multiplier chip (e.g., "×2.3") for flows moving faster than normal
- **Data freshness dot**: Green dot (updated <1h), yellow (<1d), gray (older) next to each story card
