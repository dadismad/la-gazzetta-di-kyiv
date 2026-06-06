# Event Horizon — Research Brief & Page Architecture

## Origin: The Chokepoints Paradigm

### Core Book Concept

Based on the research of "Chokepoints" (the White House geopolitical-economic strategy framework, associated with analysts like Peter Harrell, Elizabeth Rosenberg, and the Carnegie/CFR school), the core thesis is:

**The modern US economic statecraft arsenal uses cross-border pressure points — "chokepoints" — as substitute weapons where kinetic military options are too costly or escalatory.**

Key chokepoint categories:

1. **Financial Chokepoints** — SWIFT exclusion, USD clearing access, correspondent banking restrictions, sovereign debt market denial. The dollar-based financial system is the primary weapon — cutting an adversary off from USD settlement is the nuclear option of economic statecraft.

2. **Technology/Export Control Chokepoints** — EAR (Export Administration Regulations), BIS Entity List, semiconductor fab equipment restrictions, advanced AI chip controls. These create "technology denial zones" that degrade adversarial military-technological capacity over time.

3. **Energy Chokepoints** — Strait of Hormuz, Malacca Strait, Suez Canal, Turkish Straits, Panama Canal. Physical transit points that, when controlled or threatened, create immediate commodity price shockwaves.

4. **Supply Chain Chokepoints** — Rare earth processing (China), semiconductor fabrication (Taiwan), pharmaceutical intermediates (India/China), critical minerals processing. Leverage points in globalized production networks.

5. **Sanctions as Precision Weaponry** — OFAC SDN listings, secondary sanctions, sectoral sanctions, license revocation. Increasingly targeted rather than blanket — but the threat of escalation is the true weapon.

**The core insight for trading:** Every chokepoint activation creates an immediate, measurable price dislocations in connected assets. The transmission is not slow or gradual — it happens in the first 15-60 minutes after the announcement, during which institutional desks are executing while retail is still reading headlines.

---

## How Professional Trading Desks Monitor This

### Tier 1: Sell-Side "Situation Rooms" (Goldman Sachs, JPMorgan, Morgan Stanley)

- **Dedicated geopolitical desks** within the macro trading floor — typically 3-6 analysts + 1-2 strategists
- **Physical setup:** 3-6 monitor wall per station. Left screen: news/alert feeds. Center: execution terminals (Bloomberg TOMS, trading blotter). Right: live P&L/risk dashboards
- **Key construct: The "Geopolitical Risk Matrix"** — a real-time grid mapping active geopolitical events x affected asset classes, color-coded by estimated market impact (Green/Yellow/Red/Black)
- **Runbooks** — Pre-written playbooks for 30-50 geopolitical scenarios: "Russia invades Ukraine > long energy, short RUB, short European equities, long defense." Updated quarterly by the geopolitical strategy team.

### Tier 2: Buy-Side "Markets Rooms" (Bridgewater, Renaissance, Citadel, Point72)

- **Event-driven macro desks** that treat geopolitical events as volatility catalysts, not fundamental shifts
- **Key construct: The "Event-to-Price Waterfall"** — a decision tree mapping: Event > Asset 1 direction (t=0-15m) > Asset 2 contagion (t=15-60m) > Second-order effects (t=1-4h)
- **Sentiment-to-position monitors** — Natural language processing (NLP) on official statements (White House press pool, Treasury readouts, Kremlin statements, PBOC communications) scored for hawkish/dovish deviation from previous posture
- **Cross-border flow visualization** — Real-time TIC data (Treasury International Capital), EPFR global fund flows, SWIFT message volumes, FX fixing data — all normalized into a single "geopolitical risk appetite" score

### Tier 3: Independent / Family Office "War Rooms" (Brevan Howard, Caxton, Tudor)

- **Leaner setup** — 1-2 geopolitical analysts per desk, heavily augmented by automated monitoring systems
- **Key construct: The "Crisis Monitor"** — A curated alert system that monitors 15-20 key government websites, press pools, executive orders, and regulatory filings. When a new sanctions package is published, NLP parses it and maps affected entities to the firm's holdings within 60 seconds
- **The "Diplomatic Telegraph"** — Private signal services (Eurasia Group, Oxford Analytica, Control Risks, GRI) that provide human-analyzed geopolitical risk assessments, delivered 30-60 minutes before mainstream media picks them up

---

## Data Feeds & Monitoring Constructs Used by Pros

### Real-Time Alert Feeds (Latency: 0-30 seconds)

| Feed | Content | Cost Tier | Latency |
|------|---------|-----------|---------|
| Bloomberg Terminal (BRFLW, ALLQ, NI) | Official statements, executive orders, sanctions filings | 3009330093$ | <5s |
| Reuters Eikon News | Global wire service, government pool reports | 3009330093 | <10s |
| DTCC CTM/Trade Information Warehouse | CDS clearing, sanctions screening alerts | 3009330093$ | Near-real |
| WhiteHouse.gov Press Pool | Executive orders, statements, readouts | Free | ~30s |
| OFAC SDN List RSS / API | New sanctions designations | Free | ~15m |
| Federal Register | Executive orders & regulatory actions | Free | ~24h |
| State Dept / Treasury Press Releases | Official USG policy announcements | Free | ~2m |
| European Commission Sanctions Map | EU sanctions tracker | Free | ~30m |

### Market Impact Data Feeds (Latency: 0-60 seconds)

| Feed | Purpose | Cost |
|------|---------|------|
| Real-time FX fixing data (ECB, PBOC) | Capital flow proxy via settlement volumes | 3009330093$ |
| Gold/silver spot + futures (COMEX/LBMA) | Crisis hedging barometer | 30093 |
| CDS spreads (Markit, CMA) | Sovereign credit risk — sanctions impact | 3009330093 |
| Energy futures (Brent, WTI, TTF, JKM) | Supply shock pricing | 30093 |
| Bond yields + yield curve (Treasury, Bund, JGB, Gilt) | Flight-to-safety vs flight-from-risk rotations | 30093 |
| Equity index futures (ES, NQ, STOXX, NK) | Macro risk-on/risk-off gauge | 30093 |
| VIX / VIX futures | Tail-risk pricing | 30093 |
| Options skew (25-delta RR) | Tail hedging activity | 30093$ |

### Analytical / Private Intelligence (Latency: 30 min - 24h)

| Service | Specialty | Cost |
|---------|-----------|------|
| Eurasia Group | Country risk, political scenario analysis | 3009330093$ |
| Oxford Analytica | Deep-dive geopolitical briefs | 3009330093$ |
| GRI (Geopolitical Risk Intelligence) | Sanctions-specific intelligence | 3009330093$ |
| Stratfor (RANE) | Global security risk monitoring | 3009330093 |
| Control Risks | Operational risk, security assessments | 3009330093$ |
| Chatham House / CFR | Academic policy analysis | Free/$ |
| Atlantic Council / CEPA | Ukraine/Russia/Eurasia expertise | Free |

### The Professional Dashboard Architecture

A typical professional trading desk geopolitical dashboard has these zones:



---

## The "Event Horizon" Page — Concept Architecture

### Name Rationale

"In astrophysics, the event horizon is the boundary beyond which events cannot affect an observer. In geopolitics-and-markets, it's the boundary where a political decision becomes a priced asset move — the point of no return between what governments *announce* and what markets *price*."

### Page Thesis Statement (displayed at top)

> *"Professional trading desks monitor geopolitical 'chokepoints' — financial pressure points where government decisions create immediate, measurable market dislocations. This page shows you what the pros see: the collision between geopolitical pressure events and capital market reactions, updated in real time. You don't need a Bloomberg terminal. You need conviction."*

---

### Section Architecture

#### SECTION 1: The Chokepoint Barometer (Top Hero)

**What it is:** A single, sweeping visual indicator of "Geopolitical Pressure" — the aggregate tension level across all monitored chokepoints.

**Display:** A horizontal gauge/spectrum bar, gradient from Green (Low Pressure) > Yellow (Elevated) > Orange (High) > Red (Critical) > Black (Crisis). Needle position computed from:
- Number of active sanctions/trade actions
- Executive orders signed in last 30 days
- Diplomatic language scoring (NLP-derived from official statements)
- Energy price volatility (Brent + TTF 7-day IV)
- CDS spread widening (selected sovereigns: RU, CN, IR, UA)

**Data sources:** Static analysis imported via data JSON. Rendered as SVG/CSS gauge.

**Frequency:** Updated on each site rebuild (currently ~15min).

#### SECTION 2: Active Chokepoints Dashboard

**What it is:** A grid of currently active geopolitical pressure points, each rendered as a card showing:
- Chokepoint name (e.g., "Russian Energy Sanctions", "Taiwan Semiconductor Export Controls")
- Category badge (Financial / Technology / Energy / Supply Chain / Sanctions)
- Current status (Active / Escalating / De-escalating / New)
- Target asset class (Oil, USD, Treasuries, EUR, JPY, Gold, Semis, etc.)
- Price impact (estimated daily move attributable to this chokepoint)
- Alert level (Watch / Monitor / Caution / Active / Crisis)
- Last updated timestamp

**Data source:** event_horizon.json — populated by AI analysis pipeline scanning for chokepoint-related events.

#### SECTION 3: The Transmission Matrix

**What it is:** Two-axis table/grid:
- Y-axis: Active geopolitical events
- X-axis: Affected asset classes
- Cells: Directional impact arrows (up, down, sideways) with intensity (1-3 arrows), color-coded

#### SECTION 4: Event Timeline (The Waterfall)

**What it is:** A reverse-chronological timeline of chokepoint-related events and their immediate market reactions.

**Each entry shows:** Timestamp (relative + absolute), Flag emoji, Event description, Market impact (asset + move + timeframe), Source link.

#### SECTION 5: The Pros' Monitor (Professional Dashboard Recreation)

**Four sub-panels:**

| Panel | Content |
|-------|---------|
| LEFT: Alert Feed | Live feed of last 15 chokepoint-related alerts with severity badges |
| CENTER-LEFT: Price Impact | 12 most chokepoint-sensitive assets with price, daily change %, chokepoint exposure score |
| CENTER-RIGHT: Scenario Runbook | 3-5 active "If [Event] then [Trade]" scenarios |
| RIGHT: Risk Barometer | 6-key-metric snapshot: VIX, Gold/$, CDS spreads, yield curve slope, oil backwardation |

#### SECTION 6: Conviction Imposer (Bottom CTA)

**Components:** "The Signal" summary box, 2-3 concrete trade ideas, watchlist builders, Telegram CTA.

---

### Implementation Strategy

#### Phase 1 (MVP)

1. event_horizon.html — single self-contained page with all sections
2. data/event_horizon.json — static feed, updated by AI pipeline every cycle
3. CSS: Extend existing styles.css with new event-horizon-* classes
4. JS: Vanilla JS fetching JSON, rendering all sections, live price fetch
5. Navigation: Add "Event Horizon" to product nav bar

#### Phase 2 (Enhancements)

1. WebSocket live updates
2. Animated transmission matrix
3. Historical event replay (7-day scrub)
4. Chokepoint drill-down pages
5. Telegram push notifications for critical alerts

### Visual Design Direction

**Tone:** Command center aesthetic. Dark mode default (contrasting main site white).

**Color palette:**
- Background: #0F172A (slate-900)
- Card bg: #1E293B (slate-800)
- Text: #E2E8F0 (slate-200)
- Accents: #D4AF37 (existing gold), #2563EB (blue), #059669 (green), #DC2626 (red)
- Alert lines: #F59E0B (amber), #EF4444 (red), #10B981 (green)
