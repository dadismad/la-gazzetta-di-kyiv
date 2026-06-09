# CSS Token Reference — Gazzetta di Kyiv

> Design tokens defined in styles.css :root. Pure white frameless design with 1px dividers.
> Typography: Playfair Display (headlines), Source Serif 4 (body), Inter (labels).

## Color Tokens

| Token | Value | Purpose |
|-------|-------|---------|
| --bg | #FFFFFF | Pure white everywhere |
| --white | #FFFFFF | Card backgrounds |
| --card-bg | #FFFFFF | Story/flow card backgrounds |
| --blue | #2563EB | Links, interactive, clickable |
| --green | #059669 | Casino green - buy signals, inflows |
| --red | #DC2626 | Casino red - sell signals, outflows |
| --gold | #D4AF37 | 24K gold - accents, masthead name |
| --gold-light | rgba(212,175,55,0.10) | Subtle gold tint |
| --ink | #111827 | Near-black - all body text |
| --ink-light | #6B7280 | Grey - secondary text |
| --ink-muted | #9CA3AF | Muted grey - tertiary text |
| --divider | #E5E7EB | Light divider line |
| --card-border | #E5E7EB | 1px card borders |

## Typography Tokens

| Token | Value | Usage |
|-------|-------|-------|
| --display | Playfair Display, Georgia, serif | Headlines, masthead, hero |
| --body | Source Serif 4, Georgia, serif | Body text, story content |
| --sans | Inter, -apple-system, sans-serif | Labels, nav, data |

## Spacing Scale (Golden Ratio)

| Token | Formula | Rough Value |
|-------|---------|-------------|
| --phi | 1.618 | Golden ratio multiplier |
| --phi-sm | calc(1rem / 1.618) | ~0.618rem |
| --phi-md | 1.618rem | ~1.618rem |
| --phi-lg | calc(1rem * 1.618 * 1.618) | ~2.618rem |
| --phi-xl | calc(1rem * 1.618 * 1.618 * 1.618) | ~4.236rem |

## Design Principles

1. **Pure white** - Every background including masthead is #FFFFFF
2. **Frameless** - No box shadows, no rounded corners, no background fills
3. **1px dividers only** - Visual separation via --divider (#E5E7EB) borders
4. **Three-type system** - Display serif for headlines, body serif for reading, sans for UI
5. **Signal colors** - Casino green/red for financial direction, blue for interaction
6. **Gold accent** - Reserved for masthead name and high-value indicators

## Masthead Design

- Shimmering Tyrian gradient on name
- 0.4px translucent gold stroke
- Gold: #D4AF37 with rgba backing

## Version

v22.5 — Crossed Bulavas Purple, Invisible Gold, Gradients
