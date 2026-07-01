# Diplomatic Ledger — Complete Design Specification (v28.0)

Source: stitch_la_gazzetta_di_kyiv_mobile.zip / DESIGN.md
This is the canonical design spec for lagazzettadikyiv.com.

## Colors

| Token | Value | Usage |
|---|---|---|
| surface / background | `#FAF9F6` | Warm archival paper — base reading surface |
| on-surface / on-background | `#1A1C1A` | Deep charcoal — all body text |
| Gold | `#D4AF37` | Structural separators, data points, wealth signals |
| Gold (dark) | `#B8860B` | Borders, hover states |
| Crimson | `#8B0000` | Urgent market alerts, negative fiscal trends |
| Dark navy | `#1A1F2E` | Navigation overlays, menus, modal backdrops |
| Primary | `#000000` | Primary interactive elements |
| Secondary | `#735c00` | Secondary accents |
| Error | `#BA1A1A` | Error states |
| Surface container lowest | `#FFFFFF` | Highest elevation surface |
| Surface container low | `#F4F3F1` | |
| Surface container | `#EFEEEB` | |
| Surface container high | `#E9E8E5` | |
| Surface container highest | `#E3E2E0` | Lowest elevation surface |
| Outline | `#747878` | Borders |
| Outline variant | `#C4C7C7` | Subtle borders |

## Typography

| Token | Font | Size | Weight | Line Height | Use |
|---|---|---|---|---|---|
| display-xl | Playfair Display | 40px | 700 | 48px (1.2x) | Hero headlines |
| headline-lg | Playfair Display | 30px | 700 | 36px (1.2x) | Section headlines |
| headline-lg-mobile | Playfair Display | 26px | 700 | 32px | Mobile headlines |
| headline-md | Playfair Display | 22px | 600 | 28px | Story headlines |
| body-lg | Inter | 18px | 400 | 27px (1.5x) | Long-form body |
| body-md | Inter | 16px | 400 | 24px (1.5x) | Standard body |
| metadata-sm | Inter | 13px | 500 | 18px | Metadata, timestamps |
| label-xs | Inter | 12px | 600 | 16px | Labels, buttons |

Key rules:
- Headlines: tight 1.2x line-height ("tight-set newspaper feel")
- Body: generous 1.5x line-height ("deep reading on mobile")
- Numeric data: Always Inter with tabular lining figures

## Layout & Spacing

- Single-column fluid model, mobile-first
- 16px horizontal margins
- 8px baseline grid for vertical rhythm
- Headline-body gap: 16px
- Article/section gap: 32px OR gold 1px rule
- Minimum tap target: 48px

## Shapes

- **All corners: 0px (sharp)** — no rounding anywhere
- Buttons: 0px radius
- Input fields: 0px radius
- Data bars: 0px radius

## Elevation & Depth

- **NO shadows** — "ink on paper" aesthetic
- Depth via tonal layering (surface container hierarchy)
- Depth via line work (gold rules)

## Components

### Buttons
- Text-based with bottom 2px Gold border, OR solid Primary blocks
- Labels: metadata-sm (13px, 500 weight)
- No rounding

### Lists (News Feed)
- Traditional news-feed style
- Each item separated by 1px Gold rule
- Headlines: headline-md (22px Playfair Display)

### Chips/Tags
- Rectangular boxes, 1px Slate border
- No background fill

### Input Fields
- Single 1px bottom border (no box)
- Labels above in label-xs
- Error: Crimson label color

### Cards
- **Do NOT use traditional cards**
- Use sections defined by vertical spacing and gold rules

### Data Visualizations
- Impact Bars: 4px tall rectangular track
- Contradiction Meter: center-aligned bar — Gold right (positive), Crimson left (negative)

## Navigation

- Overlays/Dropdowns: Dark navy `#1A1F2E` background
- Creates depth distinction from paper reading surface
- No shadows, no rounded corners on dropdown panels

## Brand Voice

- Style: Minimalism + Editorial Authority
- Emotional response: "Calm urgency" — news is critical, delivery is stable
- No decorative images — every element serves the text
- Metaphor: Modern diplomatic cable with the permanence of a well-set book
