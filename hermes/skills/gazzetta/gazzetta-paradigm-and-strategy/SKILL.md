---
name: gazzetta-paradigm-and-strategy
description: Core editorial paradigm, business structure, data pipeline sources, and platform-specific strategies for Gazzetta di Kyiv — a thesis-driven narrative intelligence media organism.
version: 1.0.0
author: Hermes Agent
created_by: agent
---

# Gazzetta di Kyiv — Paradigm & Strategy

This skill encodes the foundational editorial paradigm, multi-platform business structure, data pipeline source architecture, and platform-specific content strategies. Reference: `gazzetta-di-kyiv/docs/PARADIGM_AND_STRATEGY_REFINEMENT_V1.md`.

Platform publishing format specs: `references/publishing-payload-v3-format.md` — Telegram (6-block Rapid Intelligence Terminal) and Reddit (8-block Narrative Laboratory) format blueprints with word-count guardrails, CTA rotation rules, and human-detail ledger integration.
Reddit API credentials setup (for Google-linked accounts, script app creation, OAuth flow): `references/reddit-api-credentials.md`.

**Design system** (see `gazzetta-editorial-writer` skill, `references/site-design-spec.md`):
- Color: gold `#C8A44E` + sky blue `#4A8FCC` + paper white `#FEFCF5`
- Typography: DM Serif Display (headlines) + Source Serif 4 (body) + Inter (labels only)
- Layout: contradiction-first with "What They Say / What's Happening" format
- Density: front page is a scanning surface — multi-column headline grid, masthead under 60px
- Quality gate: run `focus-group-review` skill before shipping design changes

**Editorial workflow** (see `gazzetta-editorial-writer` skill):
- LLM-driven content production replacing template-based Python scripts
- Platform-adapted voice: Telegram (signal), Reddit (discussion), Website (record)
- Anti-taxonomy rules: zero "narrative acceleration," "second-order effects," "transmission effects"
- Cross-cycle memory via `editorial_state.json`

Website design: `gazzetta-website` skill — gold/blue/white newspaper-magazine aesthetic, contradiction-first layout ("What They Say / What's Happening"), Six Theses visible, anti-patterns for dark/terminal designs.

## Content Architecture: Dossiers, Alerts & Narrative Philosophy

### Macro Dossiers (Permanent Context Layer)
Instead of writing perishable news articles, the platform builds permanent, semi-dynamic Macro Dossier pages for each of the 12 core narratives (e.g., `/dossier/energy-sovereignty`). These are NOT articles — they are institutional investment memos:

- **Structural Thesis** — 500-word explanation of the macro regime. LLM-drafted, you-approved. Stored in `data/dossiers/<narrative-slug>.md`. Does not change cycle-to-cycle.
- **Key Actors & Tickers** — Why specific tickers map to this narrative. Auto-updated from `narratives.json`.
- **Data Baselines** — Live FRED, CFTC, and capital flow data embedded directly into the dossier. Auto-injected by `build_frontend.py` on every pipeline cycle.

Dossiers are accessed from narrative tags on story cards, filter pills, and sidebar narrative names — NOT as a 5th tab. They compound in value over time.

### Contradiction Alerts (Deep-Dive Threshold — GAP ≥ 80)
Editorial bandwidth is deployed ONLY when data demands it. When a story triggers GAP ≥ 80 (violent dislocation between media consensus and capital reality), the platform auto-generates a Contradiction Alert:

- Titled like a research brief: **"Contradiction Alert: Market Mispricing in the [Narrative] Narrative"**
- 500-800 word expanded analysis with full Media vs. Market comparison + linked dossier context + trade setup
- Rendered as a visually distinct card variant on The Stream (burgundy background tint, "CONTRADICTION ALERT" badge)
- Auto-tagged via `contradiction_synthesizer.py` with `alert: true` in stories.json
- This fires ~5-10 times/week — sustainable, not a content mill

### Narrative Naming: Mechanism → Destination Philosophy
Narratives are named for the DESTINATION capital is moving TOWARD, not the mechanism or risk it's fleeing. Investors allocate to capture structural reality, not speculate on raw tools.

| Old (Mechanism) | New (Destination) | Rationale |
|---|---|---|
| Gene Editing | Longevity & Bioreality | Lifespan expansion + systemic medical reshoring, not CRISPR tools |
| Dollar Decline | Sovereign Liquidity Migration | Where capital flees TO (hard assets, alternative reserves), not what it leaves |
| Deglobalization | Industrial Reshoring & Defense Hegemony | Physical capital construction + defense manufacturing being BUILT |
| Crypto Reserve | Decentralized Capital Architecture | Institutional treasury reserves + digital liquidity rails, not "crypto" |
| AI Chips | Compute Hegemony & Intelligence Infrastructure | The destination: infrastructure dominance, not the component |
| Commodity Supercycle | Physical Resource Revaluation | Structural revaluation of raw materials, not academic "supercycle" terminology |
| Rate Cycle | Liquidity Regime Transition | Central bank pivot dynamics as regime change, not mechanical "cycle" |
| Space Economy | Orbital Industrialization & Defense | Commercial + military orbital infrastructure being constructed |
| Tech Convergence | Enterprise Intelligence Consolidation | AI/cloud/legacy fusion into unified intelligence stacks |
| Wealthy Sports | Sports Asset Financialization | Institutional PE/sovereign wealth capturing franchise equity |

Permanent names (already destination-framed): **Energy Sovereignty**, **China Ascent**

> Full Identity Report: `references/institutional-identity-report.md`

## Core Paradigm (the lens through which all content is filtered)

The central thesis is a **multipolar civilisational transition** driven by asymmetric technological execution, fiscal and institutional strain in the legacy Western system, and the emergence of abundance technologies that fundamentally alter the sources of economic value and geopolitical leverage. Full doctrine: `docs/PARADIGM_LENS_v2026-06-03.md`.

1. **China Ascendancy — Execution Over Invention** — China leads in 57 of 64 ASPI-tracked critical tech domains. 15th Five-Year Plan (2026–2030) prioritises fusion, aerospace, biotech, AI convergence. The distinction between who invents and who deploys at national-strategic tempo is the key capital-flow signal.
2. **US Petrodollar Decline** — USD reserves fell from ~85% (1970s) to ~58% today (IMF COFER). BRICS+ local-currency settlement, yuan-real and rupee-oil pacts accelerating. Track triggers for reserve diversification acceleration, not just the trend.
3. **EU Self-Destruction — Institutional Mismatch** — Non-national residents ~10% of EU population. Foreign-born ~64M by 2025. Rightward electoral shifts + Migration Pact strain. Frame as institutional mismatch with 21st-century realities — not collapse, fragmentation along predictable fault lines.
4. **Tech Convergence — Abundance as Decisive Variable** — Fusion (CFS SPARC 2027, Helion 2028), SMRs, humanoid robotics, agentic AI, space economy ($1.8T by 2035), longevity biotech ($8.5B funding). Every narrative must surface second-order capital-flow consequences of energy abundance and labour substitution.
5. **Blockchain Agentic Economy — Rails for Machine Economies** — RWA tokenisation: $6B (Jan 2025) → $31B+ (June 2026). AI agents receiving on-chain mandates. Stablecoins as rails, agents as operators, tokenised assets as cargo. Not retail crypto — infrastructure for post-human-scale capital markets.
6. **Longevity** — Gene therapy, GLP-1s, epigenetic reprogramming targeting aging itself. Largest addressable market in human history.

## Business Structure

| Asset | Purpose | Cadence |
|-------|---------|---------|
| Website | Intelligence terminal, data endpoints, long-form | Continuous |
| X/Twitter | Detonation layer — contradiction + curiosity, 275-char max | 3x/day (06:30, 12:00, 18:30) |
| Telegram main (@GazzettaDiKyiv) | Geopolitical narrative intelligence + cross-asset | Event-driven + 3x/day |
| Telegram ChinaTechConvergence | China tech ascendancy, 5YP, rare earths, semiconductors | 3x/day |
| Telegram EnergyAbundanceWatch | Fusion, SMR, solar, battery, energy disruption | 3x/day |
| Telegram EUFractureSignals | EU fragmentation, immigration, institutional strain | 3x/day |
| Telegram AgenticCapital | Blockchain rails, RWA tokenisation, AI agent economy | 3x/day |
| Telegram SpaceFrontier | Space economy, orbital infrastructure, satellite services | 3x/day |
| Telegram LongevityEdge | Longevity biotech, clinical pipelines, investable platforms | 3x/day |
| Reddit r/LaGazzettadiKyiv | Hypothesis laboratory — drafts before website finalisation | 2x/day |
| Newsletter: Tech Convergence & Betting | Emerging tech + how to invest | Weekly |
| Newsletter: Longevity Edge | Healthspan + investment thesis | Bi-weekly |
| Newsletter: Space Economy | Orbital infrastructure + energy | Bi-weekly |
| Newsletter: The White Pill | Positive tech breakthroughs, counter-narrative to doomscrolling (Gorrell format) | Weekly |

No cross-platform copy-paste permitted. Every channel gets a distinct angle. Full placement strategies: `docs/PLACEMENT_STRATEGIES_v2026-06-03.md`.

## Platform Content Formats

> **Implementation:** Content produced by `gazzetta-editorial-writer` skill. All articles must conform to `data/contracts/article_contract_v1.json`. Full placement strategies: `docs/PLACEMENT_STRATEGIES_v2026-06-03.md`.

### X/Twitter (max 275 chars — detonation format, OUTBOUND ONLY)
X.com is used for outbound posting only — not data collection (API credits too expensive for inbound polling). Account: @GazzettadiKyiv (ID: 2059326509177765888, app: GazzettadiKyivX). Post format: [Contradiction]. [Named actor] + [specific event] = [what gets repriced]. [Single link to website or newsletter]. Never longer than 275 characters. Morning spike at 06:30 EET — one high-conviction observation.

### Telegram (50-160 words — intelligence wire)
Signal → Implication → Actionable bullets (3 max) → Human detail → Continuity → CTA. Six thematic sub-channels each get channel-specific framing (ChinaTechConvergence, EnergyAbundanceWatch, EUFractureSignals, AgenticCapital, SpaceFrontier, LongevityEdge).

### Reddit (140-260 words — hypothesis laboratory)
Context → Narrative → Contradiction → Second-order → Strategy → Human detail → Discussion prompt → CTA. Long-form drafts posted for community feedback BEFORE website finalisation. Must end with READY_FOR_DEVVIT_POST.

### White Pill Newsletter (growth engine)
Opener (mind-expanding observation) → Lead breakthrough → 3–5 rapid-fire breakthroughs → "Why this changes the game" → Forward calendar → CTA. Evidence-based optimism, modelled on Brandon Gorrell's high-signal format. Primary growth engine and on-ramp to the main terminal.

## Data Pipeline Sources

Inbound data sources are Telegram intel monitor + RSS feeds + Polymarket prediction markets. 
X.com is **outbound posting only** (too expensive for data collection — ~100 req/mo on free tier burns fast).

For editorial lenses, load:
- `gazzetta-event-driven-trading` — retail event trading playbook for Bet&Benefit pills
- `gazzetta-prediction-market-trading` — Polymarket odds as leading indicators, betting society dynamics

## Reddit Growth & Monetization

Reddit is the primary top-of-funnel acquisition channel. The full growth strategy is documented in `references/reddit-growth-strategy.md` — covering posting cadence, cross-promotion rules, content formats, conversion funnel design, and timeline to first paying subscribers. Key points:

- **Target subreddits:** r/investing, r/stocks, r/CryptoCurrency, r/geopolitics, r/economics, r/wallstreetbets
- **Cadence:** 6-7 posts/week across 4+ subreddits with tailored headlines per sub
- **Funnel:** Reddit post → free newsletter (Substack/Beehiiv) → 7-day paid trial → $9/mo or $89/yr
- **Timeline:** First 10 paid subscribers by week 5-6, 50+ by week 12, 100+ by month 4
- **Unique angle:** Contradiction-first geopolitical capital flow analysis — underserved in the Reddit ecosystem

## Monetization Funnel
Free (X/Reddit/Telegram) → Website → Free newsletter → Paid newsletters ($15-30/mo) → Premium ($100/mo: API access + private channel + strategy calls)
