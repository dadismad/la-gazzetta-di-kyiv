# Institutional Terminal Design Standards
## La Gazzetta di Kyiv — Phase 8 (June 22, 2026)

---

## Core Identity

The terminal is an **institutional-grade geopolitical-finance intelligence platform** for professional traders, portfolio managers, and financial journalists. NOT a consumer news app. NOT a crypto dashboard.

Every design decision must pass the gate: *"Would a Bloomberg Terminal user or Reuters Eikon analyst find this credible?"*

---

## Typography

### Font Stack

| Role | Font | Size | Weight |
|------|------|------|--------|
| Body text, summaries | Inter | 13px (0.8125rem) | 400 |
| Card headlines | Inter | 14px | 600 |
| Source lines, timestamps | Inter | 11px | 500 |
| Badges, tags | Inter | 10px | 600 |
| Section headers | Inter | 16px | 700 |
| **Data points (GAP, prices, tickers, capital)** | **JetBrains Mono** | 11px | 500 |
| Masthead | Playfair Display | 20px | 700 |

### Why JetBrains Mono for data

Monospace fonts eliminate proportional-width ambiguity in numeric columns. A trader scanning GAP:72 vs GAP:95 needs instant pattern recognition — monospace ensures the digits align.

### Mobile safeguard

Keep original larger sizes on viewports < 768px for touch readability. Institutional density is for desktop.

---

## Color Palette

### Base

| Element | Color | Usage |
|---------|-------|-------|
| Background | `#0A0A0F` | Full page background |
| Card surface | `#141418` | Story cards, panels |
| Borders | `#1E293B` | Thin slate — hard geometric separation |
| Body text | `#E6E4E0` | All prose, headlines |
| Muted text | `#747878` | Timestamps, secondary labels |

### Signal Colors

| Element | Color | Usage |
|---------|-------|-------|
| BREAKING zone, divergence | `#7F1D1D` (muted burgundy) | Zone headers, GAP > 50 borders, alert badges |
| ACTIVE signals, gold accent | `#D4AF37` | ACTIVE zone borders, leaderboard mid-tier |
| SETTLING noise | `#444748` | Low-signal cards, muted borders |
| Capital inflows, allocation % | `#10B981` (emerald) | Positive flow indicators, position sizes |
| Capital outflows | `#EF4444` (red) | Negative flow indicators |

### Why muted burgundy instead of crimson

`#8B0000` (crimson) triggers visual alarm — appropriate for a missile warning, not a market signal. `#7F1D1D` (burgundy) directs attention without causing panic. Traders scan dozens of BREAKING signals daily — the color should distinguish, not startle.

### Pulse animation

- GAP > 70 cards: subtle pulse, **6-second cycle** (not 3s)
- Decay critical: **4-second cycle** (not 2s)
- Slower pulses = less cognitive load = more professional

---

## Card Architecture — Rule of 3 Lines

### Collapsed State (default)

Every story card in the stream shows exactly 3 lines:

```
Line 1: [TIER 1] via BLOOMBERG · 4H AGO · GAP 72
Line 2: SpaceX IPO slide deepens as space ETFs drop 3%+
Line 3: SHORT ROKT @ $24.30 / SL $26.10 / TP $20.50 [1.25%]  ▸
```

- Line 1: Source tier badge + feed source + timestamp + GAP score — all on one line, monospace for GAP
- Line 2: Headline — clean, 14px, Inter medium
- Line 3: Trade setup in monospace — direction, ticker, entry, stop, target, allocation % in emerald
- `▸` button toggles full dispatch drawer

### Expanded State (on click)

The `▸` unfold_more button opens a `<details>` drawer containing:
- Media Consensus (they_say) — left column
- Market Reality (reality) — right column
- Capital volume, narrative context, tier tag — footer row

### What was removed from collapsed cards

- Narrative container title (redundant — already identified by source line)
- Capital bar (replaced by allocation % on trade line)
- "Gap: N" tag (moved into source line)
- DIVERGENT/CONVERGENT duplicate badge (kept only the tier indicator)
- Share button (reduced to icon-only, no text label)

---

## Anti-Patterns — Never Do

- **Never** use emoji or Unicode icons in any response or UI element (per C-Suite SOP R8)
- **Never** use consumer-gamification patterns (swipe gestures, "pin" curation, like/bookmark counts)
- **Never** use Social Media share buttons (Facebook/Twitter icons) — institutional traders share via Signal/Telegram/WhatsApp. Use Web Share API (`navigator.share`) to trigger native OS share sheet.
- **Never** use "current levels" in trade theses — always cite exact limit prices from market data
- **Never** describe the UI as needing "fixing" or "chaos" — it's clinical and professional, not broken. Improvements are refinements, not corrections.
- **Never** change the background color — `#0A0A0F` is correct. Proposals for `#090D16` are a 0.05% luminance delta with zero visual impact.
- **Never** replace Inter with "non-generic" fonts — Inter is a professional UI typeface used by Stripe, GitHub, and Figma.

---

## Telegram Broadcast Rules

- **GAP > 50 only** — BREAKING zone stories with active trade theses
- **Narrative throttle**: 4-hour cooldown per narrative. Same narrative won't post again within 4h unless GAP jumps by 15+ points
- **Trade thesis required**: Stories without `trade_thesis` are suppressed regardless of GAP
- **Throttle state persisted** to `public/data/telegram_throttle.json`
- No more than 2 posts per governor cycle (MAX_POSTS=2)

---

## Narrative Coalescence

The DeepSeek synthesis prompt receives a `CURRENT PLATFORM STATE` block injected from `flows.json`:

```
CURRENT PLATFORM STATE (narrative saturation):
  dollar_decline: 45 stories, avg GAP 38, capital $244.4B, direction short
  energy_sovereignty: 52 stories, avg GAP 65, capital $0.6B, direction long
  ...
```

This enables:
- **Saturation weighting**: GAP on saturated narratives (30+ stories) scored lower
- **Clustering detection**: 3+ similar theses = "narrative intensification" not novel
- **Redundancy avoidance**: If consensus direction is SHORT URA, don't generate another identical SHORT URA
- **Contrarian amplification**: If headline genuinely contradicts consensus, GAP bumped +10-15

Do NOT expect the LLM to identify "structural trend reversals" — that requires quantitative backtesting.
