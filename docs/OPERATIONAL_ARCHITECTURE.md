# Gazzetta di Kyiv -- Operational Architecture & Editorial Doctrine
## Pre-Launch Readiness Assessment | v1.0 | June 2026

---

## TABLE OF CONTENTS

**PART I -- Editorial Paradigm & Management Architecture**
1.1 The Contradiction-First Thesis
1.2 Six-Domain Editorial Structure
1.3 Newsroom Operating Model
1.4 Quality Governance Framework

**PART II -- Pipeline Architecture & Execution Workflow**
2.1 Data Ingestion Layer
2.2 Enrichment & Classification Chain
2.3 Compilation & Build Pipeline
2.4 Deployment Architecture
2.5 Autonomous Agent Ecosystem

**PART III -- Storytelling Methodology**
3.1 Narrative Architecture
3.2 The Contradiction Engine
3.3 Voice Registers & Lexical Discipline
3.4 Numerical Precision Standards
3.5 Asset-Anchored Story Construction

**PART IV -- Content & Context Strategies**
4.1 Platform-Specific Content Formatting
4.2 Distribution Cadence & Channel Strategy
4.3 Audience Segmentation & Funnel Architecture
4.4 Competitive Positioning

**PART V -- Organizational Hierarchy**
5.1 Role Architecture
5.2 Decision Authority Matrix
5.3 Inter-Role Communication Protocols

**PART VI -- Temporal Cadence & Systemic Implications**
6.1 The 10-Minute Heartbeat
6.2 Daily Editorial Cycle
6.3 Weekly Strategic Layer
6.4 Failure Propagation & Cascading Effects
6.5 Self-Healing Mechanisms

**PART VII -- Pre-Launch Readiness Checklist**

---

## PART I -- EDITORIAL PARADIGM & MANAGEMENT ARCHITECTURE

### 1.1 The Contradiction-First Thesis

**Core proposition:** Financial markets price narratives. Capital flows reveal reality. The gap between the two is the investable signal.

Gazzetta di Kyiv operates on a single organizing principle: **contradiction is the primary unit of editorial value.** Every story, every data point, every editorial decision is filtered through the lens of narrative-vs-flow divergence. We do not predict. We expose.

The newspaper is built on five foundational theses (the "Five Pillars") which serve as the interpretive framework for all content:

| Pillar | Thesis | Capital Flow Signal |
|--------|--------|---------------------|
| China Ascendancy | China leads 57 of 64 ASPI-tracked critical tech domains; deployment tempo, not invention, drives value | Cross-border tech capital flows, semiconductor supply chain investment, rare earth export controls |
| US Petrodollar Decline | USD reserves fell from ~85% (1970s) to ~58% today; BRICS+ local-currency settlement accelerating | Central bank gold purchases, yuan-real settlement volume, Treasury auction bid-to-cover ratios |
| EU Institutional Mismatch | Non-national residents ~10% of EU population; rightward electoral shifts + Migration Pact strain create predictable fragmentation | EUR/USD parity pressure, EU sovereign spread divergence, defense spending reallocation |
| Tech Convergence & Abundance | Fusion (CFS SPARC 2027, Helion 2028), humanoid robotics, agentic AI, longevity biotech are altering the sources of economic value | Venture capital allocation shifts, energy commodity price suppression risk, labor substitution velocity |
| Blockchain Agentic Economy | RWA tokenization grew from $6B (Jan 2025) to $31B+ (June 2026); AI agents receiving on-chain mandates | Stablecoin issuance growth, DeFi TVL composition shift, institutional custody infrastructure buildout |

**Operational rule:** Every story must reference at least one pillar where materially relevant. Stories that cannot be mapped to any pillar are classified as "unpillared" and undergo editorial review for pillar assignment or archival.

### 1.2 Six-Domain Editorial Structure

Content is classified into six mutually exclusive, collectively exhaustive (MECE) domains. These replace the legacy INTEL/ALPHA binary system and represent the newspaper's editorial topology:

| Domain | Scope | Example Story Types |
|--------|-------|---------------------|
| **Monetary Order** | Central bank policy, currency dynamics, sovereign debt, inflation, reserve composition | Fed rate path divergence, BRICS settlement infrastructure, Japanese yen intervention |
| **Energy & Resources** | Fossil fuels, critical minerals, nuclear, renewables, commodity supply chains | OPEC+ quota compliance, rare earth export restrictions, uranium spot price |
| **Technology & AI** | Semiconductor architecture, AI model capabilities, compute infrastructure, agentic systems | TSMC Arizona yield rates, GPU export controls, autonomous agent deployment |
| **Information & Narrative** | Media ecosystems, information warfare, platform governance, narrative amplification | X algorithm changes, Telegram channel growth, state media coordination patterns |
| **Biosecurity & Health** | Pandemic preparedness, longevity biotech, pharmaceutical supply chains, GLP-1 economics | mRNA platform diversification, antibiotic resistance surveillance, clinical trial capital flows |
| **Flashpoints** | Active conflicts, geopolitical escalation, sanctions, military deployments | Taiwan Strait transits, Black Sea grain corridor, Arctic basing |

**Cross-cutting theses** (American Decline, China Ascendancy, EU Fragmentation) are applied as tags -- they span domains and create inter-domain narrative threads. A story in Energy & Resources tagged "China Ascendancy" and a story in Technology & AI with the same tag form a connected narrative arc visible to readers via tag-based filtering.

**Container behavior:** All six domain containers start collapsed on the front page. Each shows a hint line (story count, last update timestamp, dominant direction). Click to expand reveals story cards with contradiction scores, capital flow annotations, and thesis tags. This architectural choice serves two purposes: (a) it presents a scannable intelligence dashboard for institutional readers who monitor multiple domains simultaneously, and (b) it respects the reader's attention as a scarce resource, only surfacing detail on demand.

### 1.3 Newsroom Operating Model

The newsroom is designed for a lean team augmented by autonomous AI agents. The six-role structure assumes 1-3 human operators supported by a constellation of Cloud Run agents, systemd timers, and LLM-powered editorial tools:

| Role | Function | Human/AI Split |
|------|----------|----------------|
| **Managing Editor** | Editorial vision, final approval on lead stories, corrections oversight, paradigm enforcement | Human-led, AI-supported via editorial dashboards |
| **Flow Data Editor** | 199-flow database integrity, schema enforcement, amount fabrication detection, sector total reconciliation | AI-executed, human-reviewed |
| **Intelligence Curator** | RSS/Telegram/API monitoring, initial story flagging, contradiction detection, two-source verification | AI-executed (fetch_intel.py), human-sampled |
| **Story Editor** | Narrative construction from intelligence, voice register selection, headline crafting, body composition | AI-generated (enrichment chain), AI-curated (CCO agent), human-approved for lead stories |
| **Quantitative Signal Analyst** | Asymmetry score computation, conviction probability modeling, price-narrative delta triangulation, track record settlement | AI-executed (db_to_json.py enrichment), human-audited weekly |
| **Technical Lead** | Pipeline architecture, deployment governance, autonomous agent orchestration, incident response | Human-strategic, AI-executive |

**Quality gates enforced by role:**

- **Two-source rule:** No story publishes with fewer than two independent sources. Intelligence Curator enforces at ingestion; Story Editor verifies at compilation.
- **Sub-2-hour intel-to-publish** for breaking stories (Flashpoints domain). Timer starts at first source detection; automated escalation if threshold approached.
- **Sub-2 corrections per 100 stories** as institutional credibility threshold. Managing Editor reviews every correction for systemic root cause.

### 1.4 Quality Governance Framework

**Standard Operating Procedure (SOP v1.1)** -- enacted after the CSS 404 production outage of 2026-06-12 -- establishes eight binding operational rules that govern all code changes, deployments, and verification:

**R1: Zero Blind Patching** -- No regex-based find-and-replace on HTML, CSS, or JavaScript. Every edit uses exact string matching with syntax validation. Rationale: the CSS 404 outage was caused by a path variable pointing to a non-existent gsutil binary, which a regex edit could never have caught.

**R2: Safe State Development** -- One change, one verification, one commit. Multiple overlapping patches to the same file without intermediate testing caused the duplicate script tag bug that silently killed all container rendering.

**R3: Human-in-the-Loop Deployment** -- No deploy to GCS without explicit C-Suite approval. This is non-negotiable and enforced by the `auto_revert.py` module which blocks forward deploys when triggered.

**R4: File Boundary Integrity** -- `public/` is the deploy directory. `data/` is the content source. `scripts/` is logic. `templates/` is shared component source. Crossing boundaries without explicit cross-reference creates silent drift.

**R5: Credential Hygiene** -- Only one authenticated gsutil binary has write access. Using any other produces a 401 that appears as a silent failure.

**R6: SVG Dimension Failsafe** -- All SVGs carry explicit `width` and `height` attributes matching their `viewBox`. Without this, a CSS load failure causes SVGs to explode to viewport width.

**R7: Verification Pyramid** -- From gold standard to least reliable: (1) browser_vision + getComputedStyle, (2) browser_console, (3) browser_snapshot, (4) curl, (5) git log. If it cannot be confirmed via browser screenshot with live computed styles, it is not confirmed.

**R8: Zero-Symbol Communication** -- No emojis, unicode icons, or ASCII art in any C-Suite communication. Plain text and standard markdown only. Status: PASS/FAIL/NOTE/WARNING.

**Design Compliance Gate (CDO Auditor):** Runs every 2 hours against the live site via headless Chromium. Checks masthead color, font sizes (body >= 16px, metadata >= 12px), touch targets (>= 44px), gold-on-white contrast (#B8860B minimum 3.18:1 for text, #D4AF37 for borders only), keyboard focus outlines, and container integrity at three breakpoints (desktop 1280px, tablet 768px, mobile 400px). Violations: 0 = PASS, 1-3 = WARN, 4+ = FAIL with Telegram alert.

---

## PART II -- PIPELINE ARCHITECTURE & EXECUTION WORKFLOW

### 2.1 Data Ingestion Layer

Three ingestion paths feed the central database (`gazzetta.db`, SQLite with WAL mode and 5000ms busy timeout):

**Path A: OSINT Collector (fetch_intel.py)**
- 12 RSS feeds across 5 categories: central bank communications, financial news wires, geopolitical analysis, asymmetry-focused blogs, sovereign yield data
- Runs every 30 minutes via Cloud Scheduler trigger
- Output: `drafts` table entries with source URL, headline, extracted body, publication timestamp
- Circuit breaker: 3 retries with exponential backoff + random jitter on API timeouts

**Path B: Telegram Intelligence Monitor**
- Monitors 6 Telegram channels for real-time event detection
- Extracts named actors, geographic references, asset mentions, and contradiction signals
- Runs every 30 minutes
- Output: `intel` table entries with structured metadata

**Path C: Manual Injection**
- Direct INSERT into `stories` table or via `approve_draft.py` promotion pipeline
- Used for editor-sourced content, tip submissions, and partner feeds

**Draft promotion (approve_draft.py):** Promotes drafts from `drafts` table to `stories` table. Applies classification (container assignment, thesis tagging), generates initial contradiction score (default 75 to ensure visibility in sort order), and constructs `full_json` payload with all 28 required fields. The 28-field contract is non-negotiable -- missing fields cause pipeline crashes downstream.

**Ingestion quality controls:**
- URL deduplication via `story_urls` index
- `json_valid()` SQLite constraint check before bulk operations
- Empty `full_json` rows set to `'{}'` to prevent query-wide malformed JSON errors
- OSINT source filtering: `source LIKE 'osint%'` excluded from live compilation
- Draft status normalization: `pending_review` standardized to `pending`

### 2.2 Enrichment & Classification Chain

Before stories reach the frontend, they pass through a sequential enrichment chain. Each script reads from and writes to `gazzetta.db`, layering computational analysis onto raw ingestion:

```
intel_to_stories.py
  -> decay_stories.py          (time-decay freshness scoring)
    -> validate_stories.py     (28-field completeness check, repair missing fields)
      -> enrich_editorial_stories.py  (source labeling, thesis extraction, entity tagging)
        -> enrich_market_data.py      (price data enrichment, asset class mapping)
          -> enrich_multi_persona.py  (multi-perspective analysis blocks)
            -> generate_flows.py      (capital flow extraction, direction normalization)
              -> db_to_json.py        (compilation to static JSON)
```

**Key enrichment computations:**

| Computation | Formula | Output |
|-------------|---------|--------|
| Asymmetry Score | \|Sentiment - PriceDelta\| x 50 | 0-100 score + diagnostic trace |
| Conviction Probability | Multi-factor: contradiction base + source corroboration + freshness + confidence tier | 50-95% range, ALPHA tier >= 85% |
| SLS v2.0 (SHA256) | flow_total x tier_fraction x pillar_bonus x (0.85 + SHA256[:12]/16^12 x 0.30) | Unique amount per story, floor $50M |
| Time Decay | Exponential model based on hours since publication | Freshness coefficient 0.0-1.0 |
| Sector Totals | Sum of all flow amounts per asset_class | Used for WAI v2.0 amount derivation |

**Critical enrichment bug (v2.0, June 2026):** `compile_containers()` reads `full_json` directly and passes it through with minimal processing. The enrichment chain is NOT part of the v2.0 pipeline by default -- it must be explicitly included. Without it, all 377 stories on the live site showed `asymmetry_score: null`. The correct pipeline chain inserts enrichment between ingestion and compilation.

### 2.3 Compilation & Build Pipeline

**db_to_json.py** -- The compilation engine. Reads from `gazzetta.db` (stories + flows + story_flow_links tables), computes enrichments, and writes static JSON files consumed by the JAMstack frontend:

- `data/stories.json` -- v2.0 6-container format with `containers`, `all_stories`, `tags_index`
- `data/flows.json` -- 199-tracked-flow database with direction, amount, velocity, sector

**Atomic write protocol:** Stories are written to a `.tmp.json` file, validated for structure integrity, then atomically renamed via `os.replace()`. This prevents partial writes from corrupting the live frontend during concurrent reads.

**build_site.py** -- The assembly engine. Injects template components (header, footer, navigation, containers) into 21+ HTML files using sentinel markers (`<!-- COMPONENT:NAME:START/END -->`). Generates hashed assets via `build_hashed_assets.py` for cache-busting. Applies CDN timestamp cache bust (`?t=<unix_timestamp>`) to every CSS/JS import.

**Sort order criticality:** Stories are sorted by `contradiction_score DESC` then `generated_at DESC`. New stories created with default score 50 sort AFTER old stories with score 75, regardless of timestamp. The frontend teaser displays only the first 20 stories -- fresh content becomes invisible. Mitigation: set `contradiction_score=75` on all newly created stories to maintain visibility parity.

**Hashed Asset Self-Nuke (deploy_routine.sh cleanup order):** `deploy_routine.sh` historically ran `build_hashed_assets.py` (creating `app.fa4839a6.js`), then immediately ran cleanup that matched and deleted the newly generated hashed files. HTML referenced hashed filenames that never reached GCS. Fix: move cleanup BEFORE hashing. Never run cleanup after hash generation.

**Duplicate Script Tags (footer template vs build_site.py):** `templates/footer.html` contained `<script src="./app.js">` AND `build_site.py` injected the same tag. Result: `app.HASH.js` loaded twice, IIFE executed twice, second execution found `window.Gazzetta` already defined and aborted silently -- 0 containers rendered, no console errors. Fix: remove `app.js` from footer template, keep only `i18n.js`.

### 2.4 Deployment Architecture

The deployment system has been migrated from local cron to Google Cloud Platform. The primary pipeline runs entirely on GCP:

```
Cloud Scheduler gazzetta-pipeline-cron (*/10 min)
  -> HTTP trigger
Cloud Run Job gazzetta-pipeline (europe-west1)
  -> cloud_entrypoint.py:
    1. Fetch DEEPSEEK_API_KEY from Secret Manager
    2. Download gazzetta.db from GCS (or seed fresh from stories.json)
    3. Stage 0: fetch_intel.py -- pull RSS feeds, write drafts
    4. Run deploy_routine.sh:
       Stage 0.2: bulk_approve + db_to_json + compute_flow_dimensions
       Stage 1: build_site
       Stage 2: test_platform (BLOCKING gate)
       Stage 3: build_hashed_assets
       Stage 4: sync public/ -> GCS (57 files)
    5. Upload gazzetta.db back to GCS
```

**Docker image architecture (two images):**

| Image | Dockerfile | Contains | Cloud Run Job |
|-------|-----------|----------|---------------|
| `gazzetta-pipeline:latest` | `Dockerfile` | scripts/, templates/, public/, data/, deploy_routine.sh, cloud_entrypoint.py | `gazzetta-pipeline` |
| `gazzetta-agents:latest` | `Dockerfile.agents` | CCO/CDO scripts, Playwright + Chromium | `cco-distributor`, `cdo-auditor` |

**Critical Docker pitfall:** `Dockerfile` line 22-26 does `COPY data/ /app/data/` and `COPY public/ /app/public/` -- the state of BOTH directories at BUILD TIME is frozen into the container. Every template or CSS change requires a Docker rebuild AND a Cloud Run job update. Stale bundled JSON with 4-day-old `generated_at` causes pipeline ABORT at the test gate with zero external indication.

**GCS deployment protocol:**
- Hashed assets (CSS/JS): `Cache-Control: public, max-age=31536000, immutable`
- HTML files: `Cache-Control: no-cache, max-age=0`
- JSON data files: `Cache-Control: private, no-store`
- After deploy: force-update critical file cache headers via `gcloud storage objects update`

**Deployment gate (test_platform.py):**
- Poison value detection (no `$0.0`, no `undefined` in HTML)
- Data integrity (stories.json, flows.json -- must have `generated_at`, must be <24h old)
- HTML structure (all pages present, CSS/JS hash consistency)
- Asymmetry formula correctness (5 test vectors)
- Asset badge gate (CSS `.asset-badge` class defined)
- Sector amount uniqueness validation
- If gate fails -> deploy ABORTS -> Telegram alert via auto_revert.py

### 2.5 Autonomous Agent Ecosystem

Seven Cloud Run Jobs run on independent Cloud Scheduler triggers, forming a distributed editorial operations system:

| Agent | Schedule | Function |
|-------|----------|----------|
| `gazzetta-pipeline` | Every 10 min | Primary pipeline: ingest -> enrich -> compile -> build -> deploy |
| `cco-distributor` | Every 30 min | Content curation & multi-platform distribution (Telegram, Reddit drafts, X.com drafts) |
| `cdo-auditor` | Every 2 hours | Design compliance audit via Playwright/Chromium at 3 breakpoints |
| `gazzetta-rd-sweep-weekly` | Monday 06:15 UTC | Autonomous R&D: 3-track research scope, files GitHub Issues, creates draft PRs |
| `memory-synthesizer` | Daily 02:00 UTC | Reads pipeline-run-log.jsonl from GCS, generates DRAFT_SKILL_UPDATE.md |
| `cco-newsletter-daily` | Daily 06:00 UTC | Curates top stories for daily newsletter compilation |
| `cco-newsletter-weekly` | Monday 06:00 UTC | Compiles weekly thematic newsletter editions |

**Agent hierarchy:** The pipeline agent is the sovereign -- all other agents are downstream consumers. CCO reads stories.json from GCS (post-deploy), CDO audits the live site (post-deploy), R&D exists on a weekly cycle independent of the 10-minute heartbeat.

---

## PART III -- STORYTELLING METHODOLOGY

### 3.1 Narrative Architecture

Every Gazzetta story follows a fixed narrative architecture designed to surface the contradiction between consensus narrative and capital flow reality. The architecture has five mandatory components:

**1. HOOK (50-80 characters)**
Notification-optimized opening line. Data-driven suspense drawn from: contradiction score tier, capital flow direction and amount, sector or event keyword. Never uses questions. Always declares a tension.

Example: "Markets price a soft landing at 92% probability. Treasury flow data shows the largest 3-week exodus from 10Y notes since October 2023."

**2. THEY SAY / CONSENSUS**
The prevailing narrative, quoted or paraphrased with attribution. This establishes the baseline against which the contradiction is measured. Must cite a specific source (analyst note, central bank communication, media consensus, market pricing).

**3. REALITY / CONTRADICTION**
The specific event, data point, or capital flow that contradicts the consensus. This is the evidentiary core of the story. Every claim links to a source. Format: Named actor + specific event + measurable delta.

**4. CAPITAL FLOW IMPACT**
What gets repriced, who benefits, what the flow data reveals about positioning. Contains: asset class, direction (inflow/outflow), amount (SHA256-unique, WAI v2.0 computed), sector allocation, counterparty type.

**5. CONTRADICTION METADATA**
Machine-readable diagnostic trace attached to every story: asymmetry score with formula breakdown, conviction probability with factor decomposition, entity tags (actors, geography), thesis pillar mapping, time-decay freshness coefficient.

### 3.2 The Contradiction Engine

**Asymmetry Score v2.0 -- Mathematical Delta Formula:**

```
Score = |Sentiment - PriceDelta| x 50
```

Where:
- **Sentiment** (range [-1, 1]) = story's `capital_flow.direction`: inflow -> +confidence/100, outflow -> -confidence/100, neutral -> 0
- **PriceDelta** (range [-1, 1]) = `tanh(24h_price_change_pct / 5)` from cached `market_prices.json`

**Tier thresholds:**
- >= 80: MAX ASYMMETRY (gold badge) -- narrative and price moving in opposite directions with high magnitude
- >= 65: HIGH -- significant divergence, institutional attention warranted
- >= 40: MODERATE -- measurable gap, monitoring threshold
- < 40: LOW -- narrative and price broadly aligned

**Example:** Mastercard headline +0.9 bullish sentiment, stock down 5% (-0.76 tanh-normalized). Score = |0.9 - (-0.76)| x 50 = 83. MAX ASYMMETRY.

**Diagnostic trace** (attached to every story for auditability):
```json
{
  "asymmetry_score": 83,
  "asymmetry_tier": "MAX ASYMMETRY",
  "asymmetry_diagnostic": {
    "sentiment": 0.90,
    "price_delta": -0.76,
    "formula": "ABS((0.90 - -0.76) * 50) = 83",
    "ticker": "MA"
  }
}
```

**Conviction Probability -- Multi-Factor Model:**

```
conviction = min(95, max(50, contradiction_base + source_bonus + freshness_bonus + confidence_bonus))
```

Tiers: ALPHA >= 85% (gold), HIGH 75-84% (blue), MODERATE 60-74% (grey). Effective range 50-95% -- the 50% floor reflects the irreducible uncertainty of any single-source narrative analysis.

**SLS v2.0 -- Story-Level Scaling with SHA256 Uniqueness Guard:**

The $88B monotony problem (63% of stories displaying identical capital flow amounts) was solved with deterministic uniqueness:

```
amount_b = flow_total x tier_fraction x pillar_bonus x uniqueness_mult
uniqueness_mult = 0.85 + (SHA256(story_id)[:12] / 16^12) x 0.30
```

Range: [0.85, 1.15]. Entropy: 2.8 x 10^14. Floor: $50M. Result: 377 unique amounts, zero duplicates.

**WAI v2.0 -- Weighted Asset Influence with Sector Totals:**

Rather than using individual flow amounts (which cluster stories around the largest single flow), WAI uses aggregate sector totals:

```
flow_total = sector_totals[asset_class]
amount_b = flow_total x tier_fraction x pillar_bonus x uniqueness_mult
```

Tier fractions: BREAKING 0.12, DEVELOPING 0.08, ACTIVE 0.03, SETTLING 0.005.

### 3.3 Voice Registers & Lexical Discipline

Gazzetta speaks in three registers, selected per story type and platform:

**THE CLAIM** -- "$15K degens. Direct address. Short sentences. Action verbs. Contempt for consensus."
Default for crypto, THE PLAY OF THE DAY, and X.com detonation posts. Characteristics: second-person address, imperative mood, maximum density.

**THE BRIEF** -- "$50K+ semi-professionals. Ticker-first. Number-dense. Thesis-driven. Jargon without apology."
Default for macro, rates, and markets content. Characteristics: third-person, technical register, assumes domain fluency.

**THE DISPATCH** -- "Institutional-adjacent. Dense, confident, almost arrogant. Multi-asset. Historical parallels."
Default for geopolitics, corruption, defense, and energy. Characteristics: third-person omniscient, multi-paragraph architecture, cross-domain threading.

**Lexical discipline -- Ambition Signal Words (USE):**
claim, capture, seize, front-run, rotate into, extract, edge, asymmetry, conviction, the board, structural, flow-confirmed, institutionally-ignored

**Lexical discipline -- Ambition Killers (BAN):**
"opportunity," "potential," "could be," "we believe," "significant" (use the number). Never use: "narrative acceleration," "second-order effects remain underpriced by consensus," "transmission effects," "repricing whipsaws," "mention-share drops below 7d baseline," "cross-source confirmation pending"

**Named Actor Rule:** US Central Command, not "policy actors." Kuwait airport struck, not "infrastructure targeting threshold crossed." Strait of Hormuz, not "energy corridor." Seven dead, not "significant casualties."

### 3.4 Numerical Precision Standards

Every number displayed on the frontend must be traceable to its source through the following audit chain:

**Precision Dimensions (1-10 scale, target):**

| Dimension | What It Measures | Target |
|-----------|-----------------|--------|
| Data Provenance | Source traceability, update cadence, timestamp integrity | 8+ |
| Projection Verifiability | Can past projections be checked against outcomes? | 7+ |
| Internal Consistency | Do numbers match across containers? Do totals sum? | 9+ |
| Statistical Rigor | Are confidence levels computed or hardcoded? | 6+ |
| Position Sizing | Can you derive bet size from conviction + stop distance? | 7+ |
| Track Record | Historical predictions with realized P&L | 5+ |
| Execution Readiness | Entry/stop/target specificity | 8+ |

**Trade Hook R:R Filtering:** Sidebar trade hooks compute `R:R = |target - entry| / |entry - stop|`. Hooks with R:R < 2.0 are hidden -- only high-quality setups survive. Rendering tiers: RR-ELITE (>= 3.5:1, green), RR-STRONG (>= 2.5:1, blue), RR-VIABLE (>= 2.0:1, grey).

**Track Record Settlement:** `build_track_record.py` queries gazzetta.db for stories older than 48h, compares narrative sentiment direction against actual price delta from market_prices.json. CORRECT when narrative and price directions match. INCORRECT when they oppose. INDETERMINATE when either is zero. Output: `site/data/track_record.json` with win rate, total realized alpha, success velocity.

**Freshness 2.0 -- Market Correlation:** Freshness is not temporal ("8 minutes ago") but market-correlated. CRITICAL: >= 2 price-narrative contradictions detected or max asymmetry >= 65. ACTIVE: average asymmetry >= 35. DORMANT: default. Displayed as action window labels: [HOT ALPHA] (< 60m), [ACTIVE WINDOW] (60m-4h), [DELAYED REACTION] (4h-24h), [STALE] (> 24h).

### 3.5 Asset-Anchored Story Construction

Every story that touches a tracked asset must include:

1. **Asset Identification:** Ticker, asset class, sector
2. **Entry Point:** Current price or narrative entry level
3. **Direction Signal:** Inflow/outflow with confidence annotation
4. **Contradiction Gap:** Narrative-vs-price delta with tier
5. **Stop Level:** ATR-adjusted: `entry x (1 - atr_pct x stop_atr_mult)`
6. **Capital Flow Amount:** SHA256-unique, WAI-weighted, tier-fractioned
7. **Counterparty:** Sovereign, institutional, speculative, or retail
8. **Duration:** Intraday, tactical (days), strategic (weeks), structural (months)
9. **Invalidation Trigger:** What would prove the thesis wrong

---

## PART IV -- CONTENT & CONTEXT STRATEGIES

### 4.1 Platform-Specific Content Formatting

No cross-platform copy-paste. Every channel receives a distinct angle and format:

**Website (Intelligence Terminal):**
- Long-form stories with full contradiction architecture
- Interactive data: flow nodes graph, track record settlement, live ticker tape
- All 6 domain containers with expand/collapse
- Methodology page with full mathematical framework
- Sources page with data pipeline traceability
- Format: Contradiction-first ("What They Say / What's Happening")

**X.com / Twitter (Detonation Layer, max 275 characters):**
- Format: [Contradiction]. [Named actor] + [specific event] = [what gets repriced]. [Single link]
- Cadence: 3x/day (06:30, 12:00, 18:30 EET)
- One high-conviction observation per post
- Outbound posting only -- not used for data collection (API credits too expensive)

**Telegram Main Channel (@GazzettaDiKyiv):**
- Format: HOOK (50-80 chars, data-driven suspense) -> STORY (consensus vs reality block + capital flow impact) -> LINK (story anchor URL)
- Parse mode: HTML (not Markdown -- headlines contain `$`, `%`, `+`, `_` that break Markdown parser)
- Freshness filter: blocks posts older than 12 hours (exit code 2)
- Idempotency via `posted_stories.jsonl`

**Six Thematic Telegram Sub-Channels:**
- ChinaTechConvergence: China tech ascendancy, 5YP, rare earths, semiconductors
- EnergyAbundanceWatch: Fusion, SMR, solar, battery, energy disruption
- EUFractureSignals: EU fragmentation, immigration, institutional strain
- AgenticCapital: Blockchain rails, RWA tokenization, AI agent economy
- SpaceFrontier: Space economy, orbital infrastructure
- LongevityEdge: Longevity biotech, clinical pipelines

**Reddit r/LaGazzettadiKyiv (Hypothesis Laboratory):**
- Format: Context -> Narrative -> Contradiction -> Second-order -> Strategy -> Human detail -> Discussion prompt -> CTA
- Word count: 140-260 words
- Long-form drafts posted for community feedback BEFORE website finalization
- Must end with READY_FOR_DEVVIT_POST

**Newsletters (4 tiers):**
- Tech Convergence & Betting (weekly)
- Longevity Edge (bi-weekly)
- Space Economy (bi-weekly)
- The White Pill -- positive tech breakthroughs, counter-narrative to doomscrolling (weekly, Brandon Gorrell format)

### 4.2 Distribution Cadence & Channel Strategy

```
TIME      | ACTION
----------|--------------------------------------------------
Every 10m | Pipeline runs: ingest -> enrich -> compile -> deploy
Every 30m | CCO distributes top 3 contradiction-impact stories to Telegram
          | Intelligence monitor scans 6 Telegram channels for events
Every 2h  | CDO auditor checks design compliance at 3 breakpoints
          | Living Stories T2 micro-updates (Jaccard similarity, zero LLM cost)
06:00     | Daily newsletter compilation
06:15     | Weekly R&D sweep (Monday only)
06:30     | X.com morning detonation post
12:00     | X.com midday detonation post
18:30     | X.com evening detonation post
02:00     | Memory synthesizer runs (daily)
```

**Telegram channel distribution matrix (7 channels, event-driven + scheduled):**

| Channel | Cadence | Voice |
|---------|---------|-------|
| @GazzettaDiKyiv (main) | Event-driven + 3x/day | Geopolitical narrative intelligence |
| ChinaTechConvergence | 3x/day | Technology ascendancy focus |
| EnergyAbundanceWatch | 3x/day | Energy disruption thesis |
| EUFractureSignals | 3x/day | Institutional fragmentation |
| AgenticCapital | 3x/day | Blockchain/AI agent infrastructure |
| SpaceFrontier | 3x/day | Orbital economy |
| LongevityEdge | 3x/day | Clinical pipeline intelligence |

### 4.3 Audience Segmentation & Funnel Architecture

**Tier 1 -- Free (Top of Funnel):**
X.com posts -> Reddit discussions -> Telegram channels -> Website
Objective: Establish contradiction-first brand identity, drive to website

**Tier 2 -- Free Newsletter (Middle of Funnel):**
Website signup -> Beehiiv/Substack free tier -> 4 newsletters
Objective: Demonstrate analytical depth, create email habit

**Tier 3 -- Paid Newsletter ($15-30/mo, Bottom of Funnel):**
Free newsletter -> 7-day paid trial -> Premium content
Objective: Convert analytical consumers to paying subscribers

**Tier 4 -- Premium ($100/mo, Institutional):**
Paid subscribers -> API access + private channel + strategy calls
Objective: Serve institutional capital allocators

**Target subreddits for acquisition:** r/investing, r/stocks, r/CryptoCurrency, r/geopolitics, r/economics, r/wallstreetbets
**Growth timeline:** First 10 paid subscribers by week 5-6, 50+ by week 12, 100+ by month 4

### 4.4 Competitive Positioning

Gazzetta operates in a unique gap: **original capital flow data + compelling editorial voice.** No competitor owns this intersection.

**Primary competitive models:**
- **Doomberg** (#1 reference) -- branding, wit, Substack model, meme-worthy identity
- **Lyn Alden** (#2) -- educational depth, methodology transparency, trust-building
- **Kobeissi Letter** -- X-first distribution, chart cards, track record marketing
- **ZeroHedge** -- contradiction-first pioneer (emulate the framing, not the tone)

**Gazzetta's differentiable edge:**
1. Evidence-based contradiction -- every claim links to a source
2. East European authenticity -- Kyiv-anchored perspective on multipolar transition
3. 199 tracked capital flows -- proprietary data, not repackaged consensus
4. Mathematical transparency -- every score has a formula, every formula has a diagnostic trace
5. Autonomous pipeline -- 10-minute heartbeat enables real-time contradiction detection

---

## PART V -- ORGANIZATIONAL HIERARCHY

### 5.1 Role Architecture

The organization operates as a hybrid human-AI newsroom with clear authority gradients. The hierarchy is structured around decision rights, not headcount.

```
                    MANAGING EDITOR (Alex Stocchi)
                    Strategic direction, final approval, paradigm enforcement
                                   |
            +----------------------+----------------------+
            |                      |                      |
    TECHNICAL LEAD          FLOW DATA EDITOR        STORY EDITOR
    Pipeline architecture   Data integrity          Narrative construction
    Deployment governance   Schema enforcement      Voice register selection
    Agent orchestration     199-flow database       Headline crafting
    Incident response       Amount validation       Body composition
            |                      |                      |
            +----------------------+----------------------+
            |                      |                      |
    INTELLIGENCE CURATOR   QUANTITATIVE SIGNAL     CCO AGENT (autonomous)
    RSS/Telegram monitoring  ANALYST               Multi-platform distribution
    Contradiction detection  Asymmetry computation  Content curation
    Two-source verification  Conviction modeling    Telegram/Reddit/X.com
    Initial flagging         Track record           Newsletter compilation
                                   |
                            CDO AGENT (autonomous)
                            Design compliance audit
                            WCAG AA enforcement
                            Breakpoint verification
```

### 5.2 Decision Authority Matrix

| Decision | Authority | Consultation Required | Veto Power |
|----------|-----------|----------------------|------------|
| Editorial paradigm change | Managing Editor | All roles | Managing Editor (sole) |
| Lead story selection | Managing Editor | Story Editor + Intelligence Curator | Managing Editor |
| Voice register assignment | Story Editor | Quantitative Signal Analyst | Managing Editor |
| Contradiction score threshold | Quantitative Signal Analyst | Flow Data Editor | Managing Editor |
| Pipeline architecture change | Technical Lead | All roles | Technical Lead (with Managing Editor override) |
| GCS deployment | Technical Lead | Managing Editor (C-Suite approval) | Managing Editor (R3: non-negotiable) |
| Database schema migration | Flow Data Editor | Technical Lead | Technical Lead |
| Design system change | Managing Editor | CDO Auditor + Focus Group | Managing Editor |
| SOP amendment | Managing Editor | Technical Lead | Managing Editor |
| Platform distribution cadence | CCO Agent (autonomous) | Story Editor | Managing Editor |
| Amount fabrication flag | Flow Data Editor (autonomous) | None -- automatic abort | Flow Data Editor |

### 5.3 Inter-Role Communication Protocols

**Human-to-Agent:**
- Managing Editor -> CCO Agent: Override curation via GCS-persisted editorial directives
- Managing Editor -> CDO Agent: Update DESIGN_TOKENS via `context_memory.json`
- Technical Lead -> Pipeline Agent: Code changes via GitHub -> Docker rebuild -> Cloud Run job update
- Flow Data Editor -> Pipeline Agent: Schema migrations via DB migration -> GCS upload -> pipeline cycle

**Agent-to-Human:**
- Pipeline Agent -> Managing Editor: Telegram alerts on gate failure, auto_revert triggers, stale JSON detection
- CDO Agent -> Managing Editor: FAIL status (4+ violations) triggers immediate Telegram alert
- CCO Agent -> Managing Editor: Idempotency log available via `cco_drafts/posted_stories.jsonl` on GCS

**Agent-to-Agent:**
- Pipeline Agent -> CCO Agent: `stories.json` on GCS (post-deploy) is the interface contract
- Pipeline Agent -> CDO Agent: Live website URL is the interface contract
- Memory Synthesizer -> All agents: `DRAFT_SKILL_UPDATE.md` on GCS as shared learning repository

**Escalation path:** Any agent detecting a blocking condition -> Telegram alert to Managing Editor -> if no response within 2 cycles -> escalate to Technical Lead via secondary channel

---

## PART VI -- TEMPORAL CADENCE & SYSTEMIC IMPLICATIONS

### 6.1 The 10-Minute Heartbeat

The 10-minute Cloud Scheduler trigger is the system's cardiac rhythm. Every cycle:

1. Cloud Scheduler fires HTTP request to Cloud Run Job
2. `cloud_entrypoint.py` bootstraps: fetches API key, downloads DB from GCS
3. `fetch_intel.py` Stage 0: pulls 12 RSS feeds (90-second timeout, non-blocking -- failure doesn't abort pipeline)
4. `deploy_routine.sh` executes the remaining stages sequentially
5. `test_platform.py` runs the blocking gate -- if it fails, NOTHING deploys
6. `sync_public()` uploads to GCS via google-cloud-storage SDK
7. DB uploaded back to GCS as persistence checkpoint

**Implication of the 10-minute cadence:** Any bug that enters the pipeline will deploy within 10 minutes. Any fix takes at minimum 10 minutes to reach production. The Docker rebuild cycle adds 5-8 minutes. Total fix-to-production latency: 15-20 minutes minimum. This creates a window of vulnerability for CSS/JS bugs that the CDO auditor detects on its 2-hour cycle -- a design regression can persist for up to 2 hours before automated detection.

### 6.2 Daily Editorial Cycle

```
02:00 UTC -- Memory Synthesizer: reads pipeline-run-log.jsonl, generates DRAFT_SKILL_UPDATE.md
06:00 UTC -- Newsletter compilations trigger
06:15 UTC -- Weekly R&D sweep (Monday only)
06:30 EET -- X.com morning detonation post (first editorial action of the day)
12:00 EET -- X.com midday post
18:30 EET -- X.com evening post
```

The daily cycle begins with automated synthesis (02:00), moves through compilation (06:00), and opens with the morning X.com post (06:30 EET). Editorial decisions made during the European morning cascade into the full day's distribution cadence.

### 6.3 Weekly Strategic Layer

```
Monday 06:15 UTC -- R&D Agent: 3-track research sweep, files GitHub Issues
Monday 06:30 EET -- Weekly newsletter editions publish
Weekly -- Managing Editor reviews: track record settlement, correction rate, source diversity
```

The R&D agent operates on a weekly cycle, buffered from the 10-minute heartbeat. Research recommendations are filed as GitHub Issues, creating an auditable paper trail. Phase 2 (Draft PRs) requires Contents:write + Pull requests:write permissions -- gated by C-Suite approval.

### 6.4 Failure Propagation & Cascading Effects

**Single-point-of-failure map:**

| Component | Failure Mode | Detection Latency | Cascading Impact |
|-----------|-------------|-------------------|------------------|
| Cloud Scheduler | Job not triggering | 10 minutes (missed cycle) | Pipeline stalls; site freezes at last successful deploy |
| Cloud Run Job | Container crash, OOM | 10 minutes (execution failure) | Same as scheduler failure |
| DeepSeek API | Rate limit, auth error | Immediate (API call fails) | fetch_intel.py Stage 0 fails non-blocking; pipeline continues without new intel |
| GCS bucket | Write permission error | Immediate (gsutil 403) | Deploy fails; auto_revert triggers Telegram alert |
| gazzetta.db on GCS | Corrupted download | test_platform.py gate | Pipeline ABORTS; no deploy; site stays at last good state |
| Docker image | Stale bundled JSON | test_platform.py generated_at > 24h | Pipeline fails every 10 minutes at gate; site frozen |
| CDO Auditor | Design tokens mismatch | 2 hours (audit cycle) | Silent design regression; no automated detection |
| CCO Distributor | Telegram API 400 | 30 minutes (distribution cycle) | Content not posted; stories accumulate unread |
| SQLite DB on VM | json_valid() failure | Immediate (query crash) | db_to_json.py fails; pipeline ABORTS |

**The stale-HTML feedback loop (critical failure pattern):** `templates/footer.html` contains a hardcoded old hash reference -> every 10-minute cycle injects that footer into all 22 HTML pages -> `sync_public()` uploads HTML referencing the old hash -> live site loads old pre-fix JS. Manual GCS fixes get overwritten within 10 minutes. Fix requires BOTH: (a) update `templates/footer.html` with current hash, (b) ensure `deploy_routine.sh` calls `build_hashed_assets.py` instead of deleting hashed assets.

**The Docker stale JSON trap (silent multi-day failure):** `Dockerfile` freezes JSON data at build time. If `db_to_json.py` fails, stale `flows.json` with 4-day-old `generated_at` persists. `test_platform.py` freshness check (< 24h) aborts every pipeline run. Site frozen for 4 days with zero external indication. Fix: purge all .json files at container build time.

### 6.5 Self-Healing Mechanisms

**Circuit Breaker (circuit_breaker.py):** 3 retries with exponential backoff + random jitter on API timeouts. Injected into `fetch_market_data.py` and `fetch_intel.py`.

**Atomic Write Protocol:** `.tmp.json` -> validate -> `os.replace()`. Prevents partial writes from corrupting live frontend.

**SQLite WAL Mode:** Write-Ahead Logging with 5000ms busy timeout. Prevents database-locked errors from concurrent access by multiple pipeline stages.

**Auto-Revert (auto_revert.py):** Detects pipeline failure -> sends Telegram alert -> blocks forward deploy. Does NOT revert files (the name is misleading). Serves as a circuit breaker, not a rollback mechanism.

**Pipeline Checkpoint:** `gazzetta.db` uploaded to GCS after every successful pipeline cycle. If the container crashes, the next cycle downloads the last-good DB and resumes from checkpoint.

**CDO Auditor Recovery:** When design tokens mismatch, update `DESIGN_TOKENS` in `cdo_audit.py`, rebuild agents image, update CDO auditor job, re-execute. Design token loading from `context_memory.json` (v28) reduces this to a JSON edit without Docker rebuild.

---

## PART VII -- PRE-LAUNCH READINESS CHECKLIST

### Pipeline Integrity

- [ ] `gazzetta-pipeline` Cloud Run Job executing successfully (check: `gcloud run jobs executions list --job=gazzetta-pipeline --region=europe-west1 --limit=1`)
- [ ] `test_platform.py` passing all gates (no poison values, data < 24h, all pages present)
- [ ] Docker image contains NO stale JSON files (purge at build time)
- [ ] `gazzetta.db` exists on GCS and passes `json_valid()` on all rows
- [ ] Circuit breaker retry logic active in fetch scripts
- [ ] Atomic write protocol active in db_to_json.py
- [ ] SQLite WAL mode enabled with busy_timeout=5000ms

### Agent Ecosystem

- [ ] `cco-distributor` posting to Telegram successfully (check: `posted_stories.jsonl` on GCS)
- [ ] `cdo-auditor` passing at all 3 breakpoints (0 violations = PASS)
- [ ] `gazzetta-rd-sweep-weekly` executing on schedule
- [ ] `memory-synthesizer` generating DRAFT_SKILL_UPDATE.md
- [ ] All 7 Cloud Scheduler triggers active and firing on schedule

### Content Quality

- [ ] All 6 domain containers populated with stories
- [ ] Asymmetry scores non-null for ALL stories (curl verification: `Null scores: 0`)
- [ ] Conviction probabilities non-null for ALL stories
- [ ] Capital flow amounts all unique (monotony detection pass)
- [ ] Sector totals match flow-by-id sums
- [ ] No $5.0B default amounts in circulation
- [ ] HTML entities unescaped (zero `&#039;` in headlines)
- [ ] Source labels present on stories ([LIVE-DATA] / [CALC-EST])

### Design Compliance

- [ ] Body font size >= 16px across all pages
- [ ] Metadata font size >= 12px
- [ ] Touch targets >= 44px height (masthead-home-link, nav-dropdown-trigger, hero-btn, hero-ind)
- [ ] Gold text on white uses #B8860B (3.18:1 contrast minimum)
- [ ] Gold borders/accents use #D4AF37 (no contrast requirement for decorative elements)
- [ ] Keyboard focus outlines visible on all interactive elements (`outline: 2px solid #2563EB`)
- [ ] All 6 containers start collapsed with ARIA-expanded attributes
- [ ] Masthead: white bg, name #8B0000 at 1.8em, gold 2px bottom border, caduceus + bulavas
- [ ] SVGs have explicit width/height attributes matching viewBox

### Distribution Readiness

- [ ] Telegram Bot API token active and posting to @LaGazzettadiKyiv
- [ ] HTML parse mode working (no Markdown 400 errors on special characters)
- [ ] Idempotency log preventing duplicate posts
- [ ] Freshness filter active (blocks stories > 12h)
- [ ] X.com account @GazzettadiKyiv configured for outbound posting (OAuth 2.0)
- [ ] Reddit r/LaGazzettadiKyiv accessible (Devvit CLI configured)
- [ ] Newsletter platform (Beehiiv/Substack) connected
- [ ] CCO curation formula using QUALITATIVE_MAP for confidence mapping (low=35, medium=65, high=85)

### Infrastructure

- [ ] VM gazzetta-prod RUNNING (gcloud compute instances describe)
- [ ] GCS bucket serving HTTPS with valid SSL certificate
- [ ] Cache-Control headers correct per file type (hashed=immutable, HTML=no-cache, JSON=no-store)
- [ ] Secret Manager: DEEPSEEK_API_KEY and TELEGRAM_BOT_TOKEN both accessible
- [ ] Artifact Registry: both Docker images (gazzetta-pipeline, gazzetta-agents) at :latest
- [ ] Cloud Run service accounts have necessary IAM roles (storage.objectAdmin, secretmanager.secretAccessor)

### Editorial Readiness

- [ ] Paradigm lens documented and distributed to all agents
- [ ] Voice register guide accessible to Story Editor
- [ ] Banned phrase list loaded into validation pipeline
- [ ] Two-source rule enforced at ingestion
- [ ] Correction rate tracking system active
- [ ] Track record settlement running (build_track_record.py)
- [ ] Methodology page (capital.html) complete with all formulas
- [ ] Sources page complete with data pipeline traceability

### Operational Governance

- [ ] SOP v1.1 acknowledged by all human operators
- [ ] R3 (Human-in-the-Loop Deployment) non-negotiable established
- [ ] R7 (Verification Pyramid) understood -- getComputedStyle is gold standard
- [ ] R8 (Zero-Symbol Communication) enforced for C-Suite
- [ ] Incident response runbook accessible (CSS 404 outage reference)
- [ ] Bug catalog (19 documented bug classes) available for debugging
- [ ] Cron recovery procedure documented and tested
- [ ] Deployment approval workflow established (C-Suite -> Technical Lead -> deploy)

---

*This document constitutes the operational architecture and editorial doctrine of La Gazzetta di Kyiv. All agents, pipelines, and human operators are bound by its specifications. Amendments require Managing Editor approval with Technical Lead consultation.*

*Version 1.0 | June 2026 | Prepared for pre-launch readiness assessment*
