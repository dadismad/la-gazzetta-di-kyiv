# Phase 8 Design System (Current — June 2026)

## Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| Surface (body bg) | `#0A0A0F` | Full-page background |
| Text primary | `#E6E4E0` | Body text, card content |
| Text muted | `#747878` | Metadata, timestamps, secondary labels |
| Gold | `#D4AF37` | Masthead strikethrough, borders, GAP Leaderboard headings, ACTIVE zone borders |
| Gold accessible | `#8C7123` | WCAG AA gold for headings |
| Burgundy | `#7F1D1D` | BREAKING zone borders, decay-critical fill, gapPulse keyframes |
| Crimson (legacy) | `#8B0000` | DEPRECATED — replaced by burgundy. Still appears in some hardcoded JS template literals (BREAKING zone header border-left at line 970 of build_frontend.py) |
| Emerald | `#10B981` | Allocation percentages, Verified badge text |
| Slate border | `#1E293B` | Card borders, footer separators |
| Surface container | `#141418` | Attribution footer background, zone header backgrounds |
| Orange focus | `#B45309` | Focus-visible rings (WCAG 2.4.7) |

## Typography

| Element | Font | Size | Weight | Line-height |
|---------|------|------|--------|-------------|
| Body text | Inter | 13px | 400 | 1.5 |
| Card headlines (h3) | Inter | 14px | 600 | 1.35 |
| Masthead (h1) | Playfair Display | 14px mobile / 20px desktop | 700 | — |
| Labels/filter pills | Inter | 11px | — | — |
| Data fields (.gap-score, .capital-num, .ticker-mono, .price-mono) | JetBrains Mono | — | — | — |
| Allocation pct (.allocation-pct) | JetBrains Mono | — | — | — |

## Font Loading

All from Google Fonts CDN in `<head>`:
- `Inter:wght@400;500;600`
- `Playfair+Display:wght@600;700`
- `JetBrains+Mono:wght@400;500;600`
- `Material+Symbols+Outlined`

## Animations

| Animation | Duration | Target | Purpose |
|-----------|----------|--------|---------|
| `gapPulse` | 6s ease-in-out infinite | `article[data-gap-high="true"]` | Pulsing burgundy/gold border on BREAKING cards |
| `decayPulse` | 4s ease-in-out infinite | `.decay-critical` fill | Pulsing opacity on expired edge decay |
| `fadeIn` | 0.2s ease | `details[open] > .details-content` | Drawer expand animation |

## Zone System

| Zone | Border-left | Icon | Text color | Description |
|------|-------------|------|------------|-------------|
| BREAKING | 4px `#7F1D1D` | `warning` | `#7F1D1D` | GAP > 50 |
| ACTIVE | 2px `#D4AF37` | `trending_up` | `#D4AF37` | GAP 20-50 |
| SETTLING | 1px `#444748` | `check_circle` | `#747878` | GAP < 20 |

## Sticky Radar

- Position: `sticky` at ≤768px viewport
- Top offset: 56px (masthead height)
- Background: `rgba(10,10,15,0.85)` with `backdrop-filter: blur(12px)`
- Border-bottom: `1px solid rgba(255,255,255,0.05)`

## Card Structure (Rule of 3 Lines)

1. **Line 1**: Source tier + feed source + time ago + GAP score
2. **Line 2**: Headline (h3, 14px)
3. **Line 3**: Trade setup (collapsed) + Share button + Expand button
4. **Drawer** (hidden): they_say / reality / capital / narrative context

## Attribution Footer

Dark-theme footer attached to cards with `data-source-feed`:
- Background: `#141418`
- Source name (title case, no FEED_SOURCE: prefix)
- Verified badge: emerald `#10B981` text on `emerald-500/10` background
- Icon: `database` with `aria-hidden="true"`

## Share Button

Uses `window.shareStory(btn)` global function — reads from `article.dataset`:
- `data-headline`, `data-capital`, `data-gap`, `data-direction`, `data-ticker`, `data-entry`
- Web Share API with clipboard fallback
- Temporary `check` icon feedback on copy

## Body Tag

`<body class="bg-surface font-body-md text-on-surface antialiased">`
No inline `style` attribute — all styling via CSS classes.
