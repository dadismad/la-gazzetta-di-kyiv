# HERMES DESIGN AND PRODUCT GUIDELINES
# Gazzetta di Kyiv — v1.0 — Ratified 2026-06-12
#
# This document governs all product architecture, UX design, and content
# representation decisions. It was produced through an internal simulation
# of three domain experts analyzing the live site. Read this file before
# modifying any UI, UX, or product structure.

---

## SECTION A: PRODUCT ARCHITECTURE (CPO Audit)

### Expert 1: Chief Product Officer — Institutional Fintech

**Finding 1: Disconnected Product Surfaces**

The site presents five intelligence products (Stories, Flows, Trades, Signal,
Track Record) as isolated pages with no unified navigation or user journey.
A user landing on the homepage sees teaser cards that link to separate full
pages. There is no "flow" between products — no breadcrumb, no related-content
cross-linking in the UI, no progressive disclosure that leads the user from
raw intelligence to actionable trade.

The three audience tiers (C-Suite, Quantitative, Execution) are presented
as service cards on the homepage but have no persistent presence elsewhere.
A C-Suite user who navigates to /stories.html has no indication they are in
the "INTEL" layer and no pathway to the "ALPHA" layer.

**Strategy: The Funnel Architecture**

All five products must be organized into a two-layer funnel that mirrors
the existing INTEL/ALPHA taxonomy:

```
LAYER 1: INTEL (Observation)
  Stories  — narrative intelligence, who benefits, who loses
  Flows    — capital movement, velocity, direction

LAYER 2: ALPHA (Action)
  Signal   — stories x flows triangulation, divergence detection
  Trades   — entry/stop/conviction from signal data
  Track    — verifiable outcome ledger
```

Every page must include:
- A persistent layer indicator (INTEL or ALPHA badge)
- Cross-layer navigation (INTEL pages link to relevant ALPHA products)
- A "You are here" breadcrumb in the masthead

**Finding 2: The Bet-and-Benefit Thesis Is Invisible**

The core value proposition — "contradiction-first capital flow intelligence"
— appears only in the hero headline and meta description. It is not reinforced
anywhere in the content rendering. A user scrolling through 200+ story headlines
sees raw news aggregation, not contradiction analysis.

**Strategy: Contradiction-First Content Architecture**

Every story card must surface the contradiction explicitly:
- Headline: What happened
- Contradiction line: "Narrative says X. Capital flows say Y."
- Flow indicator: Direction + magnitude + velocity
- Action prompt: Link to related signal or trade

### Product Alignment Rules

| Rule | Description |
|------|-------------|
| P1 | Every page belongs to exactly one layer (INTEL or ALPHA) |
| P2 | Every page must show its layer badge prominently |
| P3 | INTEL pages must link to related ALPHA products |
| P4 | Story cards must surface the contradiction, not just the headline |
| P5 | The service cards (C-Suite/Quant/Execution) must appear on every page |
| P6 | Navigation must expose the full product hierarchy, not just 3 links |

---

## SECTION B: UI/UX DESIGN SYSTEM (Lead Architect Audit)

### Expert 2: Lead UI/UX Architect

**Finding 1: Container Integrity Is Inconsistent**

The `.container` class is applied to sections throughout the site, but:
- Some containers are collapsible, others are not — with no visual distinction
- The "How We Serve You" container has `background:transparent;border:none`
  which breaks the visual rhythm
- Container headers vary in structure (some have subtitles, some have counts,
  some have arrows)
- The tooltip badge (?) pattern is applied inconsistently

**Strategy: Unified Container Specification**

Every `.container` must follow an identical structural template:

```
SECTION.container[.collapsible]
  DIV.container-header
    SPAN.container-title      (required)
    SPAN.container-subtitle    (optional, for counts)
    SPAN.container-arrow       (required for collapsible)
    SPAN.container-help        (optional, for tooltips)
  DIV.container-desc           (optional, single-line description)
  DIV.container-body           (required, content area)
```

**Finding 2: Typography Lacks Hierarchy**

The site uses three typefaces (Playfair Display, Source Serif 4, Inter) but
applies them inconsistently:
- Story headlines on /stories.html are H3 elements at a uniform size with no
  visual distinction between breaking news, analysis, and market data
- Container titles use inconsistent font sizes
- No visual distinction between INTEL-layer and ALPHA-layer headings

**Strategy: Typographic Scale**

```
Element          | Font              | Size    | Weight | Color
-----------------|-------------------|---------|--------|----------
Page title (H1)  | Playfair Display  | 28px    | 400    | #111827
Layer heading    | Inter             | 11px    | 700    | #6B7280 (uppercase, tracked)
Container title  | Source Serif 4   | 16px    | 600    | #111827
Story headline   | Source Serif 4   | 14px    | 600    | #111827
Contradiction    | Source Serif 4   | 13px    | 400    | #6B7280 (italic)
Body text        | Source Serif 4   | 15px    | 400    | #111827
Meta / labels    | Inter             | 10px    | 500    | #9CA3AF (uppercase, tracked)
Navigation       | Inter             | 13px    | 700    | #8B0000 (uppercase, tracked)
```

**Finding 3: Spacing System Is Ad-Hoc**

The CSS uses hardcoded pixel values for padding, margin, and gap with no
discernible rhythm. Some values: 8px, 10px, 12px, 14px, 16px, 20px, 24px,
28px. There is no base unit.

**Strategy: 4px Base Spacing Scale**

All spacing must use multiples of 4px:
- xs: 4px (icon-to-text gap)
- sm: 8px (inline element gap)
- md: 12px (card internal padding)
- lg: 16px (container padding, section gap)
- xl: 24px (section separation)
- 2xl: 32px (major section break)
- 3xl: 48px (page-level separation)

### Design System Rules

| Rule | Description |
|------|-------------|
| D1 | Every container follows the unified structural template |
| D2 | All spacing uses the 4px scale — no ad-hoc pixel values |
| D3 | Typography follows the scale above — no deviations |
| D4 | Collapsible containers must show an arrow indicator |
| D5 | Gold (#D4AF37) is reserved for: masthead border, CTAs, active/selected states |
| D6 | Dark red (#8B0000) is reserved for: masthead name, navigation links |
| D7 | Near-black (#111827) is the only body text color |
| D8 | Container background is always #FFFFFF with 1px #E5E7EB border |

---

## SECTION C: CONTENT REPRESENTATION (Managing Editor Audit)

### Expert 3: Managing Editor — Macroeconomics

**Finding 1: Raw Data Without Context**

The /stories.html page renders 200+ headlines as a flat list. Each story shows:
- Headline (sourced from OSINT/Reuters)
- Flow amount (e.g., "$0.05B tech")
- Link to full intelligence report

Missing from every story card:
- The contradiction: what is the gap between narrative and flow?
- The time context: when was this detected? Is it new or stale?
- The magnitude context: is $0.05B significant or noise for this sector?
- The related signal: has this contradiction generated a trade idea?

**Finding 2: The Contradiction-First Thesis Is Buried**

The About page states: "Our editorial method is contradiction-first: every
story exposes the gap between what they say and where money moves."

But the story rendering does not expose this gap. The user must click through
to a "full intelligence report" to see any contradiction analysis. The
headline-only presentation makes the site indistinguishable from a news
aggregator.

**Strategy: Inline Contradiction Rendering**

Every story card must render as a four-line structure:

```
HEADLINE: [OSINT headline — what happened]
CONTRADICTION: [Narrative claims X. Capital flows show Y. The gap is Z.]
FLOW: [$AMOUNT SECTOR DIRECTION — with velocity indicator]
ACTION: [Link to related signal] [Link to full report]
```

**Finding 3: The "Follow the Money" Narrative Is Not Visualized**

The site has flow data ($ amounts, directions, sectors) but no visual
representation. Users must parse text to understand capital movement.
A simple directional indicator (arrow + color) would reduce cognitive load
by an estimated 60%.

**Strategy: Directional Flow Indicators**

| Direction | Visual | Color |
|-----------|--------|-------|
| Inflow    | → text  | #047857 (green) |
| Outflow   | → text  | #DC2626 (red) |
| Neutral   | → text  | #6B7280 (gray) |

Flow cards must also show:
- Sector tag (e.g., "tech", "commodities", "equities")
- Velocity indicator (e.g., "2.4x 4-week avg")
- PDR (Passive Discovery Ratio) where available

### Content Representation Rules

| Rule | Description |
|------|-------------|
| C1 | Every story card must include: headline, contradiction, flow, action |
| C2 | Flow amounts must include sector context and velocity |
| C3 | Directional indicators must use color coding (green/red/gray) |
| C4 | No raw data without inline context — every number must have a comparator |
| C5 | The "contradiction" line is mandatory — never render a story without it |
| C6 | Breaking/live stories must be visually distinct from historical/archived |

---

## SECTION D: IMPLEMENTATION PRIORITIES

### Immediate (Next Deploy Cycle)

1. **Unified container structure**: Refactor all `.container` instances across
   21 HTML files to use the standard template (D1, D2)
2. **Story card redesign**: Modify `app.js` `renderNewsCol()` to render the
   four-line contradiction-first card structure (C1, C4, C5)
3. **Navigation overhaul**: Replace 3-link masthead with full product hierarchy
   exposing both INTEL and ALPHA layers (P6)

### Short-Term (Within 1 Week)

4. **Persistent layer badges**: Add INTEL/ALPHA indicator to every page (P1, P2)
5. **Cross-layer linking**: INTEL pages link to ALPHA products, and vice versa (P3)
6. **Typography standardization**: Apply the typographic scale across all pages (D3)
7. **Spacing refactor**: Replace all ad-hoc pixel values with 4px-scale variables (D2)

### Medium-Term (Within 2 Weeks)

8. **Flow visualization**: Add directional indicators with color coding (C3)
9. **Service card persistence**: C-Suite/Quant/Execution cards on every page (P5)
10. **Velocity and PDR rendering**: Surface flow metadata inline (C2)

---

## AMENDMENT HISTORY

| Date | Version | Change |
|------|---------|--------|
| 2026-06-12 | v1.0 | Initial guidelines — CPO + UX Architect + Managing Editor audit |
