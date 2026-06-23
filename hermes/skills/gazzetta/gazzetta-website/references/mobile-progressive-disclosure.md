# Mobile Progressive Disclosure — Research Findings (June 2026)

## Industry Pattern: Hint-Then-Expand

All three major finance apps use the same core mechanic: condensed preview (1-3 lines or key metrics), tap reveals full content.

### Pattern Analysis

| App | Closed State | Expanded State | Animation |
|-----|-------------|----------------|-----------|
| **FT** | Headline (16pt) + 1-line summary + key stat callout. ~80dp. | Slide-in panel from bottom with full article | Panel slide + elevation |
| **Robinhood** | Ticker + headline (1 line) + source + timestamp. ~60dp. | Inline expand: 3-5 sentence summary + "Read on [source]" link | CSS height 300ms ease-out |
| **Bloomberg** | Horizontal-scroll cards: headline (2-line max) + source + timestamp. | Full article as new page with sticky header + progressive "Continue reading" gate | Card shrink → cross-fade → article |

### The TL;DR + Hook Formula

```
LINE 1: [WHO] + [WHAT] + [KEY NUMBER]
LINE 2: [WHY IT MATTERS — the implication]
```

**Character budget:** 130 chars total across 2 lines (65/line) for phones < 375px. Up to 160 chars on 414px+.

**Rules:**
- Lead with the number — financial users scan for data first
- One sentence per line — cards truncate at ~60 chars
- Never passive voice on line 1 — active is scan-readable
- Line 2 = "so what" — users need context to decide if they care
- End line 2 with an implication — creates curiosity gap for tap
- Include a proper noun on line 1 — establishes credibility

### Navigation for 5+ Sections

**Recommended: Horizontal Pills Bar** (FT/Bloomberg pattern).
- Scrollable pill/tab bar below masthead
- Each pill = product name (1-2 words)
- Active pill gets filled background + accent color
- Exactly 5 products fit without overflow

### Data-Heavy Card Pattern

```
CLOSED: [KPI] [Δ%] [micro-chart]
TAP →  [KPI] [Δ%] [micro-chart] (stays)
       [Grid: Open/High/Low/Close/Vol]
       [Mini table]
       [Link: "Full analysis →"]
```

Top-level: 1-3 numbers max (the "reason to look").
Second level: 5-8 data points structured.
Third level: Full detail page.

### Sources

- Bloomberg mobile app UX patterns
- Financial Times mobile progressive disclosure
- Robinhood KPI-first card design
- NN/Group progressive disclosure principles
- Apple HIG touch target guidelines (44×44pt minimum)
