# LA GAZZETTA DI KYIV — STITCH PROMPTS
## Google Stitch Master Blueprint · Diplomatic Ledger v29.0 · June 2026

This file contains six hyper-detailed prompts for Google Stitch to generate layout architecture blueprints. Each prompt is self-contained. Run them sequentially.

---

## STITCH PROMPT 1: FRONTPAGE — THE STREAM

Generate a mobile-first, single-column institutional newspaper frontpage for "La Gazzetta di Kyiv" — a geopolitical capital flow intelligence publication. This is the primary reader experience. Every reader arrives on a phone.

### Layout Specifications

**Canvas:** 375px wide (mobile portrait), scaling to 680px max-width centered on desktop. Single column. No sidebars. No multi-column layouts.

**Vertical Order (top to bottom):**

1. MASTHEAD (48-64px height): Centered publication name "La Gazzetta di Kyiv" in Playfair Display, crimson (#8B0000), size equivalent to 1.8em. To the left: a small gold (#D4AF37) fox-and-lion SVG symbol (Machiavelli). To the right: crossed bulavas SVG (Hetman's maces). Below name: 1px solid gold horizontal rule spanning full width. Right-aligned: three uppercase crimson nav links in Inter 13px with 0.12em letter-spacing — HOME, ARCHIVE, ABOUT. Background: warm archival paper (#FAF9F6).

2. DOMAIN NAVIGATION: A horizontal row of 8 pill-shaped navigation links. Each pill: 1px gold border (#D4AF37), uppercase Inter 11px 600-weight text, 5px vertical by 12px horizontal padding, 6px gap between pills. Wrapping allowed on narrow screens. Pills read: DOLLAR DECLINE, ENERGY SOVEREIGNTY, DEGLOBALIZATION, CHINA ASCENT, SPACE ECONOMY, GENE EDITING, TECH CONVERGENCE, WEALTHY SPORTS. Bottom of nav strip: 1px solid gold rule.

3. HEAT MAP SECTION: 8 circular bubble buttons arranged in a wrapped flex row, centered. Bubbles are sized proportionally to aggregate capital volume (48px to 140px diameter). Each bubble contains: ticker code (top, Inter 10px), narrative label (center, Inter 9px), compact capital total (bottom, Inter 11px bold). Bubble colors by average contradiction gap: grey neutral (<40), amber warm (40-64), gold hot (65-79), crimson pulsing (80+). Section background is warm paper. Section bottom: 1px gold rule.

4. TRADER FEED — THE STREAM: A continuous vertical list of intelligence cards. Each card:

   - Background: warm paper (#FAF9F6)
   - Left border: 2px solid gold (#D4AF37)
   - Bottom border: 1px solid gold — this is the separator between cards
   - Internal padding: 14px top, 16px horizontal, 20px bottom
   - Zero border radius. Zero box shadow.

   Card internal structure (top to bottom):
   - Header row: Ticker badge (Inter 10px uppercase, light grey background) on left, time-ago timestamp (Inter 10px, slate grey) on right
   - Headline: Playfair Display 16px, weight 600, charcoal (#1A1C1A), line-height 1.3
   - "MEDIA CONSENSUS" row: Uppercase label (Inter 9px, muted), followed by body text (Inter 14px) on pale grey (#F8F8F8) background with gold left border
   - "MARKET REALITY" row: Uppercase label, followed by body text on warm gold tint (#FFF8E7) background with gold left border
   - DEGEN EDGE badge: Label "Degen Edge" + score badge. Three variants: DIVERGENT (crimson pulsing, "Market ignoring news"), CONVERGENT (calm gold, "Trend Confirmed"), WATCHING (slate, "Gap narrowing")
   - CAPITAL BAR: 3px height, grey background, gold fill proportional to capital volume, right-aligned label showing dollar amount ("$12.4B at stake")

5. FOOTER: Centered, Inter 11px, slate grey. Links: About, Telegram, Reddit, "Kyiv · Since 2025". Top: 1px gold rule.

6. BASELINE: Centered below footer, Inter 9px, muted grey: "La Gazzetta di Kyiv · Diplomatic Ledger v29.0 · [timestamp] · [N] stories · 8 narratives"

### Typography System
- Display/Headlines: Playfair Display (Google Fonts)
- Body/Metadata/UI: Inter (Google Fonts)
- All financial figures: Inter with tabular lining
- Body: 16px minimum, 1.5 line-height
- Headlines: 16px, weight 600, 1.3 line-height

### Color System
- Background: #FAF9F6 (warm archival paper)
- Primary text: #1A1C1A (deep charcoal)
- Structural gold: #D4AF37 (borders, separators, capital bars)
- Crimson: #8B0000 (masthead name, BREAKING tier, negative trends)
- Dark navy: #1A1F2E (overlays only)
- Slate: #747878 (secondary text)
- Muted: #9CA3AF (tertiary text)

### Shape Rules
- Zero border radius on everything. Sharp corners. Ink on paper.
- No box shadows. Ever.
- No gradients except Roman Purple overlay.
- Gold ONLY as structural element — never as decorative fill.

### Interaction
- Bubbles: tap to open full-screen narrative overlay (Roman Purple gradient modal with all stories in that domain)
- Nav pills: tap to filter feed to specific domain
- Cards: no hover effects on mobile. On desktop: subtle gold-dark left border on hover.
- Overlay close: button + backdrop tap + Escape key

---

## STITCH PROMPT 2: NARRATIVE TRACKING PAGE

Generate a single narrative tracking page for La Gazzetta di Kyiv. This page tracks the lifecycle, velocity, and institutional penetration of economic claims within one domain (e.g., "Dollar Decline").

### Layout Specifications

**Canvas:** Same as frontpage — 375px mobile, 680px max desktop.

**Vertical Order:**

1. MASTHEAD (identical to frontpage)

2. NARRATIVE HEADER: Domain title in Playfair Display, 24px, charcoal, centered. Below: aggregate stats row — total capital volume (Inter 48px bold in dynamic gold color by gap tier), story count, average contradiction gap. Ticker badge in gold-bordered pill.

3. TIMELINE: A minimalist structural timeline rendered with crisp line work instead of boxes. Vertical axis: time (newest at top). Horizontal bars represent individual stories. Bar width = capital volume (log scale). Bar color = contradiction gap tier. Left-aligned headline text on each bar. No boxes. Lines only.

4. VELOCITY CHART: A small inline chart showing narrative activity over time (stories per day for last 30 days). Rendered as thin gold bars (1px) on warm paper. No chart junk. No gridlines. Just the signal.

5. STORY LIST: Identical card format to frontpage stream. Filtered to this narrative only.

6. FOOTER + BASELINE (identical to frontpage)

---

## STITCH PROMPT 3: CAPITAL FLOWS PAGE

Generate a capital flows tracking page for La Gazzetta di Kyiv. This is an institutional dashboard displaying physical stockpiling data vs. official market consensus.

### Layout Specifications

**Canvas:** 375px mobile, 680px max desktop.

**Vertical Order:**

1. MASTHEAD (identical)

2. PAGE HEADER: "Capital Flows" in Playfair Display 24px. Subtitle: "Physical settlement vs. market consensus" in Inter 14px, slate.

3. FLOW TABLE: Clean vertical financial table using Inter with strict tabular lining figures. Columns:
   - Flow ID (monospace, 11px)
   - Asset (Inter 12px)
   - Direction (IN/OUT badge, gold/crimson)
   - Volume (tabular figures, Inter 13px 600, right-aligned)
   - Source (Inter 11px, slate)
   - Age (time-ago, Inter 11px)
   Rows separated by 1px gold rules. Alternating row backgrounds: warm paper / warm paper + 2% darken. No zebra stripes in different colors.

4. DISCREPANCY MARKERS: Rows where physical settlement diverges from market consensus by >20% get a crimson left border (2px) and a contradiction score badge.

5. FOOTER + BASELINE (identical)

---

## STITCH PROMPT 4: CONTRADICTIONS PAGE

Generate a contradictions intelligence page for La Gazzetta di Kyiv. This is a high-contrast interface designed specifically around the Contradiction Index (0-100 scale).

### Layout Specifications

**Canvas:** 375px mobile, 680px max desktop.

**Vertical Order:**

1. MASTHEAD (identical)

2. PAGE HEADER: "Contradiction Index" in Playfair Display 24px. Subtitle: "Where official narratives and capital flows diverge" in Inter 14px.

3. CONTRADICTION BARS: A vertical stack of horizontal tracking bars — one per narrative domain. Each bar:
   - Gold expands RIGHT (market agreement, CONVERGENT, gap < 35)
   - Crimson expands LEFT (systemic market dissonance, DIVERGENT, gap > 65)
   - Neutral grey in the middle (WATCHING, gap 35-65)
   - Bar height: 8px
   - Domain label left-aligned (Inter 11px uppercase)
   - Aggregate gap score right-aligned (Inter 13px 600)
   - Bars separated by 1px gold rules

4. TOP DIVERGENCES: A ranked list of the 10 highest-gap stories. Each entry: rank number (Playfair Display 20px, crimson), headline (Inter 14px), gap score badge, capital volume, domain tag.

5. NARRATIVE BREAKDOWN: Per-domain card showing: domain name, average gap, trend arrow (up/down/flat last 24h), story count, total capital at stake.

6. FOOTER + BASELINE (identical)

---

## STITCH PROMPT 5: ASSET PRICING PAGE

Generate a macro asset pricing matrix page for La Gazzetta di Kyiv. This page traces cross-asset vulnerabilities triggered by geopolitical movements.

### Layout Specifications

**Canvas:** 375px mobile, 680px max desktop.

**Vertical Order:**

1. MASTHEAD (identical)

2. PAGE HEADER: "Asset Pricing" in Playfair Display 24px. Subtitle: "Cross-asset vulnerability matrix" in Inter 14px.

3. C-SCORE EXPLAINER: Brief text block explaining the Contradiction Score (C-Score): a 0-100 metric measuring the gap between official narrative and capital flow reality. Inter 14px, charcoal.

4. ASSET MATRIX: A clean table with Inter tabular lining. Columns:
   - Asset/Ticker (Inter 12px, 600)
   - Narrative (Inter 11px)
   - Current Price (tabular, 13px)
   - Change % (tabular, 13px, green up / crimson down)
   - C-Score (contradiction score, 0-100, gold-to-crimson gradient bar)
   - Projected Impact (USD billions, tabular, Inter 13px 600)
   - Domain tag (gold-bordered pill)
   Rows separated by 1px gold rules.

5. VULNERABILITY MAP: A minimalist visualization showing which assets are most exposed to which geopolitical narratives. Rendered as thin connector lines between asset names and narrative domains. Gold lines = high exposure. Grey lines = monitoring. No boxes.

6. FOOTER + BASELINE (identical)

---

## STITCH PROMPT 6: THE SIGNAL PAGE — THE CONVERGENCE ENGINE

Generate the Signal page for La Gazzetta di Kyiv. This is the ultimate multi-dimensional vertex of the platform. It demonstrates where disparate data vectors coalesce into an explicit trading or betting thesis.

### Layout Specifications

**Canvas:** 375px mobile, 680px max desktop.

### Design Philosophy

This page must project maximum institutional authority. It uses archival text formats to outline highly asymmetric investment strategies. It is the convergence of four data streams: narrative lifecycles, physical capital anomalies, high contradiction indexes, and mispriced assets.

### Vertical Order:

1. MASTHEAD (identical)

2. PAGE HEADER: "The Signal" in Playfair Display 24px, crimson. Subtitle: "Convergence Engine — where vectors coalesce" in Inter 14px, slate.

3. CONVERGENCE SUMMARY: A single, dense paragraph in Inter 16px, charcoal, with gold left border (2px). This is the lead — the single most important convergence signal currently active. Below it: C-Score, capital volume at stake, assets involved, narrative domains.

4. FOUR-VECTOR PANEL: A 2x2 grid (stacks to 4 rows on mobile). Each cell:
   - VECTOR 1: Narrative Lifecycle — timeline of the dominant narrative, from emergence to saturation. Rendered as a thin gold line with markers at key events.
   - VECTOR 2: Physical Capital Anomalies — satellite tracking, tank farm monitoring, dark pool volume. Rendered as crimson deviation bars against grey consensus lines.
   - VECTOR 3: Contradiction Index — the 0-100 score, shown as a large gold/crimson split bar with precise numeric readout.
   - VECTOR 4: Mispriced Assets — assets where market price and capital flow signal diverge by >2 standard deviations.

   Each cell has: vector label (Inter 11px uppercase, slate), primary metric (Inter 24px 600, charcoal or crimson), secondary context (Inter 13px, slate).

5. THE THESIS: An archival-format text block. Inter 16px, charcoal. Gold left border (2px). This is the explicit trading or investment thesis derived from the convergence of the four vectors. It states:
   - What the market believes (consensus)
   - What the flows show (reality)
   - The contradiction gap
   - The asymmetric payoff structure
   - The time horizon
   - Suggested position sizing (as percentage of portfolio)
   - Risk factors that would invalidate the thesis

   This block uses dense, institutional language. No marketing. No hedging. No "could" or "might." Quantified probabilities where possible.

6. SUPPORTING EVIDENCE: A feed of the specific stories, flows, and price data that feed into the thesis. Each item is a compressed version of the trader card format (ticker + headline + gap score).

7. HISTORICAL SIGNALS: A small section showing the last 3 Signal theses, with their outcomes (validated/invalidated, profit/loss if applicable). Rendered as a compact table.

8. FOOTER + BASELINE (identical)

### Typography on This Page
- The Thesis block uses Inter 16px, line-height 1.7 (slightly more generous than body text for sustained reading of dense argumentation)
- Financial figures: Inter tabular lining, 13px
- Vector metrics: Inter 24px 600
- Labels: Inter 11px uppercase, 0.08em letter-spacing

### Color on This Page
- The gold/crimson split bar is the dominant visual element
- No decorative color anywhere — gold and crimson appear ONLY where data demands them
- The thesis block is charcoal text on warm paper — no background tint, no border except the 2px gold left rule

---

## GLOBAL RULES FOR ALL STITCH PROMPTS

1. Every page uses the identical masthead and footer components from Prompt 1.
2. Warm paper (#FAF9F6) background on every page. No exceptions.
3. Zero border radius. Zero box shadows. Everywhere.
4. Gold (#D4AF37) is structural only — never decorative.
5. Crimson (#8B0000) is alert only — masthead name, BREAKING tier, negative data.
6. Dark navy (#1A1F2E) is overlay only — modals, navigation drawers.
7. All typography: Playfair Display for headlines, Inter for everything else.
8. All pages share the cryptographic baseline fingerprint at the bottom.
9. Mobile-first: design for 375px, scale to 680px max.
10. Pages must look like they belong to the same publication — unified visual language across all six blueprints.
