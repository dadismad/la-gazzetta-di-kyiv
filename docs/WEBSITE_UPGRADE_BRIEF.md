# Website Upgrade Brief: La Gazzetta di Kyiv

## 1. Current State Audit

Before prescribing changes, we must acknowledge the baseline functionality of the current Single Page Application (SPA).

**What Works (Do Not Break):**

- **Sidebar NMC & Leaderboard:** The terminal accurately surfaces the macroeconomic capital ($9.31T across 12 narratives) anchored to specific narratives. NMC data injection into the sidebar and GAP Leaderboard was completed June 25, 2026.
- **CFT Cards (Media vs. Capital):** The core comparison mechanic is structurally sound and effectively highlights the divergence between institutional capital and media noise.
- **Client-Side Filtering:** The static filtering mechanism by tier and origin works without requiring backend queries.
- **Tab Architecture:** 4 tabs (The Flow, Tactical Bets, Capital Flows, Contradictions, About) provide logical content separation.

**What is Weak (Target Areas):**

- **Story Card Density:** The current vertical listing of narrative stories lacks spatial efficiency. Cards are wide single-column blocks that require excessive scrolling.
- **Mobile Layout:** The application degrades poorly on smaller viewports, making the dense data cards difficult to parse.
- **Tactical Bets Tab:** The organization within this tab lacks the rigorous structure of the GAP Leaderboard. CFT blocks could benefit from tighter density.
- **GAP Visualization:** Currently conveyed only through a border-left color and a raw number. A visual bar would improve scanability.
- **Phase Indicators:** The `narrative_phase()` top_gap logic is deployed in the backend but not visually expressed in the frontend card styling.

## 2. Target Experience

The frontend must reflect an institutional radar. Every design decision must serve the data.

1. **Scannable:** Users must absorb the macro environment in seconds. Strict compartmentalization enforces visual boundaries and cognitive chunking.
2. **Data-Dense:** White space is a tool for grouping, not decoration. Maximize the signal-to-noise ratio.
3. **Transparent:** The UI reflects reality. If a data pipeline is empty, the UI displays "$0M" — never a polished loading placeholder.
4. **Editorial, Not Flashy:** The terminal relies on typography, layout, and raw data to communicate authority. No superficial animations or generic iconography.

## 3. Stack Decision (ADR)

**Decision:** We will strictly maintain the current static architecture.

**Rationale:** The site is a static SPA compiled entirely by `build_frontend.py` and deployed directly to Google Cloud Storage. Introducing JavaScript frameworks (React, Vue) or build steps (Webpack, Vite) would break the deployment simplicity and introduce massive rewrite overhead to the existing 1,651-line compilation script.

**Implementation:**
- **Layout:** Native CSS Grid (`display: grid`).
- **Logic:** Vanilla JavaScript strictly limited to state toggles and client-side filtering.
- **Data:** Injected at compile time via Python.

## 4. Priority Changes (Phased Execution)

### Phase 1: High-Signal Visual Cues (Current Focus)

- **NMC Surfacing:** Already complete on sidebar and GAP Leaderboard (June 25). Remaining: surface NMC on individual story cards and the narrative crosshair.
- **GAP Bar Visualization:** Expand the existing border-left color coding into a pure CSS divergence bar. Python injects `<div style="width: [GAP]%; background: var(--phase-color);"></div>` at compile time.
- **Phase Color-Coding:** Wire the deployed `top_gap` backend logic to the UI, applying distinct visual states:
  - CRITICAL SHIFT (≥80): High-contrast crimson border, full opacity
  - ACTIVE DIVERGENCE (≥70): Gold border, full opacity
  - BUILDING TENSION (≥50): Muted gold, slightly reduced opacity
  - MATURE/STABLE (<50): Grey border, reduced opacity

### Phase 2: Bento Grid Restructure

- Migrate story cards and narrative blocks to a responsive CSS Grid system (`grid-template-areas`) to fix density and mobile layout issues.
- Re-engineer the HTML template sections within `build_frontend.py`.
- Target: 12-column grid foundation with cards spanning 3, 4, or 6 columns based on priority.

### Phase 3: Personalization (On Hold)

- **Condition:** Do not initiate until a verifiable, active user base exists.
- Implement localStorage pinning logic for narrative prioritization and client-side grid reordering.

## 5. What Stays (Untouched Components)

To manage scope and prevent feature creep, the following elements will not be rewritten or fundamentally altered during this upgrade cycle:

- Sidebar navigation structure
- The primary 5-tab architecture
- The raw data format of the CFT cards
- The static filter bar
- GCS deployment pipeline
- `build_frontend.py` Python data-loading and JSON injection logic
