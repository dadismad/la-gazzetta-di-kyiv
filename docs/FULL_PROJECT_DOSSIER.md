# La Gazzetta di Kyiv — Full Project Dossier

> Compiled for Grok handoff. Last updated: 2026-06-02 (Hermes session update).
> Author: dadismad / Alexander Solianin

---

## 1. Project Identity

**Name:** La Gazzetta di Kyiv
**Tagline:** Narrative intelligence website + ingestion pipeline
**Type:** European narrative-intelligence newspaper (digital)
**Mission:** Deliver high-frequency, investment-oriented narrative intelligence with clear action paths, confidence, and risk invalidation.
**Vision:** Operate as an autonomous digital newspaper with institutional-grade reliability and cross-channel consistency.

**Primary coverage doctrine:**
- Geopolitical transformation
- Technological convergence
- Financial narratives
- Strategic power shifts
- Energy transitions
- AI civilisation change
- Cross-asset implications
- Narrative-driven market psychology

**Editorial paradigm (6 theses — June 2026 update):**
1. China tech ascendancy outcompetes US profit-driven model
2. US petrodollar system in structural decline (BRICS, de-dollarization, debt spiral)
3. EU fragmenting via immigration stress, economic stagnation, regulatory overreach
4. Tech convergence (AI+robotics+fusion+biotech+space) creating discontinuity
5. Blockchain agentic economy is killer app for crypto (stablecoins as rails for autonomous AI agents)
6. Longevity is largest addressable market in human history

All content filtered through this thesis-driven conviction framework. Not neutral journalism.

**Target feel:** Financial Times × Monocle × The Economist — with Palantir-like operational clarity and wartime European realism.

**Anti-style constraints (DO NOT):**
- No crypto/neon startup aesthetics
- No exaggerated futurism
- No generic SaaS dashboard language

---

## 2. Repositories & Sync

### Primary (pureciclismo — upstream, Hermes session works here)
- **URL:** https://github.com/pureciclismo/gazzetta-di-kyiv
- **Language:** Python
- **Created:** 2026-05-21
- **Default branch:** `main`

### Mirror (dadismad)
- **URL:** https://github.com/dadismad/la-gazzetta-di-kyiv
- **Language:** Python
- **Created:** 2026-05-25

### Bidirectional Sync
Both repos run an identical GitHub Actions workflow (`.github/workflows/bidirectional-sync.yml`) that:
- Triggers on `push` to `main`, every 5 minutes via cron, and manual dispatch
- Merges peer commits into the other repo
- Has a loop guard to prevent ping-pong between bot commits

---

## 3. Deployment

**Platform:** GitHub Pages
**Workflow:** `.github/workflows/refresh-and-deploy.yml`
**Triggers:** Push to `main` + manual dispatch
**Deployment gates (in order):**
1. `ui_contract_check.py` — validates UI schema compliance
2. `brandbook_enforcer.py` — enforces brand book visual/editorial rules
3. `claims_container_guard.py` — validates narrative object integrity
4. **CEO hard gate** — checks `ceo_status.json` (state != 'blocked') + `deploy_canary_report.json` (passed = true)
5. Stamp build metadata (commit SHA, build time) into frontend
6. Upload to GitHub Pages
7. `production_smoke_check.py` — verifies live deployment health

---

## 4. Site Structure

```
site/
├── index.html              # Main homepage — narrative terminal
├── capital.html            # Capital markets desk
├── contacts.html
├── cooperation.html
├── data.html               # Data desk
├── ops.html                # Operations page
├── research.html
├── privacy.html
├── app.js                  # Frontend engine — loads JSON, renders stories
├── styles.css              # Main stylesheet
├── styles-modern.css       # Modern variant
├── variant-modern.html     # Modern homepage variant
├── robots.txt
├── sitemap.xml
├── api/v1/                 # API data endpoints (narrative objects JSON)
├── data/                   # Static data assets
└── media/                  # Media assets
    └── geopolitics-markets-wealth-pleasure-bg.jpg  # floral ornament image
```

### Homepage Layout (June 2026 — updated)
- **Masthead:** "La Gazzetta di Kyiv" + statement: *"People do not react only to facts. People react to stories they collectively believe about those facts."* — with navigation links (Geopolitics | Markets | Wealth | Pleasure) underneath
- **Decorative strip:** Full-bleed floral image band (`.topnav`, 140px, no text — purely ornamental)
- **Ornament divider:** Narrow image strip (`.ornament-strip`, 24px) between decorative band and main content
- **Left panel:** "Stories in Play" — expandable narrative cards (lead story + stack)
- **Right panel:** "Narrative Focus" — Influence, Stakes, Bet & Benefit
- **Footer:** Telegram | Reddit links

### Frontend Engine (`app.js`)
- Fetches narrative data from `data/stories_in_play.json`
- Renders story cards with: title, thesis, contradiction, how-it-moves-markets, main actors, market path, playbook (entry, invalidation, next-24h)
- Confidence levels: High (≥75), Medium (≥60), Measured (≥45), Low
- Each story is expandable (click to reveal playbook depth)
- Bet container maps stories to asset profiles with tickers (BZ=F, TLT, DXY, SOXX, QQQ, etc.)
- Profiles include: ticker, name, if_right, if_wrong, trigger, horizon, risk level
- Mobile responsive with smooth scroll on expand

---

## 5. Data Pipeline (scripts/)

### Core pipeline (`scripts/run_pipeline_v2.sh`):
1. `collect_multisource.py` — multi-source ingestion
2. `analyze_narratives_v2.py` — narrative analysis & structuring
3. `publish_quality_gate_v22.py` — quality gate
4. `prepare_publish_payloads_v2.py` (v3.0) — prepare content for distribution with: Telegram Rapid Intelligence Terminal format, Reddit Narrative Lab format, social distribution logging, CTA rotation tracking, word-count guardrails, verified human detail integration
5. `pipeline_audit.py` — final audit

### Reddit pipeline (`scripts/agentic_research_publish_cycle.sh`):
1. `run_pipeline_v2.sh` (full pipeline)
2. `devvit_only_pipeline.py` — Devvit-specific flow
3. `reddit_post_nlp_audit.py` — NLP quality audit (up to 3 retries + autofix)
4. `reddit_payload_autofix.py` — auto-fix failures
5. `ceo_reddit_report.py` — CEO report with permalink evidence

### Telegram payload specs (v3.0):
1. Opening signal (1 line)
2. Immediate implication (regime + risk state)
3. Actionable interpretation (1–3 bullets)
4. Verified human detail (ledger-entry citation)
5. Continuity link + next trigger
6. CTA
Target: 50–160 words.

### Reddit/Narrative Lab payload specs (v3.0):
1. Context (regime + data provenance)
2. Dominant narrative (actors + incentives)
3. Contradiction (consensus vs evidence gap)
4. Second-order implications
5. Strategic interpretation (24–72h + invalidation)
6. Verified human detail (ledger citation)
7. Discussion prompt
8. CTA + evidence links
Target: 140–260 words.

---

## 6. Operational Oversight (ops/)

_(unchanged — 27 files across overseers, CEO orchestration, production reliability, and supporting modules)_

---

## 7. Data Model & Contracts

### Narrative Object (canonical schema)
**Core mandatory fields:**
- `narrative_id`
- `title`
- `claim`
- `contradiction`
- `implications` (industry + asset)
- `invalidation_trigger`
- `confidence_score` + `confidence_label`
- `capital_flow_3d_estimate`
- `actors`
- `sectors`
- `evidence_urls`
- `continuity_link` (prior update + next trigger)
- `narrative_stage` (spark | validate | deepen | update)
- `publish_window` (morning / evening)
- `verified_human_detail` (ledger ID + source URL)
- `website_cta`

**Contract file:** `data/contracts/article_contract_v1.json`

### Confidence System
| Threshold | Label |
|-----------|-------|
| ≥ 0.75 | High |
| ≥ 0.60 | Medium |
| ≥ 0.45 | Measured |
| < 0.45 | Low |

### Asset Profile Mapping (in `app.js`)
Built-in profiles: oil (BZ=F), shipping (BDRY), US bonds (TLT), US dollar (DXY), semiconductors (SOXX), megacap tech (QQQ), autos (CARZ), batteries (LIT), LNG (UNG), prediction markets (COIN), default (SPY).

### Human Detail Ledger
Location: `data/human_detail_ledger.md`
5 seed entries: OpenAI (800M weekly users), ECB (restrictive stance, 4.1% inflation), Ukraine Reconstruction (EU €50B Facility), Oil Markets (Brent $68-74 range), BRICS Summit (11 members, GDP > G7 PPP).

### CTA Library
Location: `data/cta_library.json`
Platforms: X, Telegram, Reddit — 5 rotating phrases per platform with `{website_url}` template.

### Social Distribution Log
Location: `data/social_distribution_log.jsonl`
Tracks every post: narrative_id, channel, timestamp, CTA used, framing pattern, evidence URLs, word count. Used for CTA rotation (avoid reuse within 7 posts per platform) and feedback-loop analytics.

---

## 8. Cross-Channel Distribution

### Platform Roles
| Platform | Role | Primary Window |
|----------|------|----------------|
| **Website** | Home base / narrative terminal | Always live |
| **X (Twitter)** | Detonation — curiosity spike + authority framing | Morning 06:30 |
| **Telegram** | Reinforcement — real-time intelligence wire | Morning 06:30–10:00 |
| **Reddit** | Laboratory — hypothesis testing + community signal | Midday 12:00–15:00 |

### Narrative Intensity Ladder (daily)
1. **Spark** → X (morning) — trigger curiosity + contradiction
2. **Validate** → Telegram (morning) — reinforce signal + actionable interpretation
3. **Deepen** → Reddit (midday) — hypothesis testing + discussion
4. **Update** → Telegram + X if needed (evening) — continuity + new trigger

### Post Rules (universal)
- No copy-paste across platforms
- Includes continuity reference + "what to watch next"
- Exactly one website CTA per post
- Evidence links required for claims/projections
- Verified human detail mandatory (ledger entry)
- X: max 275 chars

### Social Distribution SOP
Reference: `docs/SOCIAL_DISTRIBUTION_SYSTEM.md`
Full SOP: `docs/CROSS_CHANNEL_EDITORIAL_SOP.md`

---

## 9. Brand System

**Palette (strict):** #F7FAFF · #3E6FAE · #10233F · #6BB6FF
**Typography:** Compact operational UI scale (8–10 body, 10 headings on command surfaces)
**Layout:** Line-based, low-friction, minimal framing, high scanability

**Voice & Tone:**
- Clear, literate, concise
- Professional, calm, non-hype
- No repetitive phrasing across modules
- No crypto/neon aesthetics
- Restrained, elegant, minimal, editorial-first

**Full brand book:** `docs/BRAND_BOOK.md`

---

## 10. Operating Model

### Cron-Executed Pipeline (June 2026 — active)
Three active Hermes cron jobs on a staggered 2x/day cadence:

| Time | Job | What | Model |
|------|-----|------|-------|
| 06:00 / 18:00 | `gazzetta-website-refresh` | Data pipeline → push to Pages | N/A (script-only) |
| 06:30 / 18:30 | `gazzetta-telegram-post` | Read payload → send to channel | deepseek-v4-pro |
| 06:45 / 18:45 | `gazzetta-reddit-autopost` | Research + Devvit publish cycle | deepseek-v4-pro |

### 5-Loop Enterprise Model (design)
1. **Ingestion** (every 30m) — collect, dedup, score sources, publish candidate set
2. **Content Build** (06:30, 18:30) — generate narrative objects with required fields
3. **Representation Sync** (after Loop 2) — render website + package X variants + payloads
4. **Verification** (every 15m) — live endpoint + renderability + content-visibility assertions
5. **Governance** (every 2h) — score pipelines, detect regressions, pause on failure

### KPI Contracts
- Availability target: ≥ 99%
- Non-empty claims: required
- Narrative actionability: required fields present
- Publish cadence: morning + evening fulfilled

### Publish States
`draft` → `reviewed` → `approved` → `published` → `verified`

### Block Conditions
- Missing mandatory narrative fields
- Duplicate wording across panels
- No claims on front page
- Renderability failed
- Missing verified human detail (ledger ID + source URL)
- Missing continuity link or next-trigger statement
- Missing CTA or multiple CTAs
- Evidence links missing where claims/projections are present
- Cross-platform near-duplication within same cycle

---

## 11. Editorial Governance

### Desk Structure
1. **Editor-in-Chief** (CEO oversight) — standards, final publication policy
2. **Morning Desk** (06:00–09:00) — overnight market narrative reset
3. **Evening Desk** (18:00–21:00) — close-of-day positioning + next-session setup
4. **Product Desks:** Homepage Narrative, Data, Newsletter, Adjacent Products

### Daily Content Packages (required twice daily)
1. Front page narrative set (non-repetitive cards)
2. Narrative Focus with actionable setup + invalidation
3. Data Desk metrics and projection context
4. Newsletter bundle per direction:
   - Emerging Tech
   - Convergence Points (AI × energy × semis × defence × mobility)
   - Investment Implications (industry + asset watchlist)

### Full governance docs:
- `docs/EDITORIAL_GOVERNANCE_PLAN.md`
- `docs/OPERATING_MANDATE.md`
- `docs/AUTONOMOUS_MEDIA_BUSINESS_PLAN.md`
- `docs/GRAND_OPERATING_MAP.md`

---

## 12. Current Infrastructure & Tech Stack

| Component | Status |
|-----------|--------|
| **GitHub Pages** | Active — auto-deploys from `main` |
| **GitHub Actions** | 2 workflows running (sync + deploy) |
| **Python 3.11** | All scripts |
| **Hermes Agent v0.14.0** | Orchestration layer (Telegram gateway, cron, skills) |
| **Data storage** | JSON files in `data/` directory (git-tracked) |
| **CLI scripts** | Bash wrappers in `scripts/` |
| **DeepSeek V4 Pro** | Primary LLM (deepseek provider, 1M context window) |
| **Groq** | STT only (Whisper via free tier) |

### Hermes Cron Jobs (active, June 2026)
- `gazzetta-website-refresh-v22-2xday` — Data pipeline at 06:00 + 18:00 (script-only, no LLM)
- `gazzetta-hourly-narrative-review` — Telegram posting at 06:30 + 18:30 (deepseek-v4-pro)
- `gazzetta-agentic-nlp-guarded-autopost-8h` — Reddit autopost at 06:45 + 18:45 (deepseek-v4-pro)
- 4 paused jobs retained (gazzetta-reddit-ingestion, gazzetta-phase3-daily-brief, gazzetta-devvit-only-pipeline, x-health-watchdog)

### Hermes Skills (relevant)
- `frontend-image-slot-integration` (v2.0.0) — Image placement, ornament strips, between-container patterns
- `gazzetta-paradigm-and-strategy` (v1.0.0) — Core editorial paradigm, business structure, data pipeline sources, platform strategies
- `hermes-provider-switching` (v1.1.0) — Provider/model switching with billing path awareness

---

## 13. Key Documents (docs/)

41 documents total. Highlights:
- `OPERATING_MANDATE.md` — Executive operating mandate (v2)
- `BRAND_BOOK.md` — Brand book: vision, mission, voice, visual system
- `SOCIAL_DISTRIBUTION_SYSTEM.md` — Cross-platform narrative distribution architecture
- `CROSS_CHANNEL_EDITORIAL_SOP.md` — QA gates, cadence, block conditions
- `EDITORIAL_GOVERNANCE_PLAN.md` — Desk structure, content packages
- `PARADIGM_AND_STRATEGY_REFINEMENT_V1.md` — **NEW (June 2026)**: 6-thesis editorial lens, 5 Telegram channel structure, 4 newsletters, 40 data sources, White Pill format, monetization funnel
- `GRAND_OPERATING_MAP.md` — Operating model with KPI contracts
- `AUTONOMOUS_MEDIA_BUSINESS_PLAN.md` — Full autonomous business model
- `REDDIT_ACCESS_RESILIENCE_PLAYBOOK_V1.md` — Reddit access resilience
- `DEVVIT_AUTONOMOUS_BRIDGE_RUNBOOK_V1.md` — Devvit autonomous bridge
- `x-automation-governance.md` — X/Twitter automation governance
- `UNIFIED_MEDIA_POLICY.md` — Unified media policy

---

## 14. Data Directory Structure

```
data/
├── config/
│   └── data_sources_v2.json
├── contracts/
│   └── article_contract_v1.json
├── audit/                    # Pipeline audit outputs
├── nios/                     # Narrative intelligence objects
├── normalized/               # Normalized data
├── processed/                # Processed data
├── publish/                  # Ready-to-publish payloads (telegram_latest.md, reddit_latest.md)
├── x/                        # X/Twitter data
├── human_detail_ledger.md    # Verified human detail entries (5 seed records)
├── cta_library.json          # CTA rotation phrases by platform
├── social_distribution_log.jsonl  # Per-post distribution log (narrative_id, channel, CTA, word count)
├── *.json                    # Runtime state files (30+ files)
└── source_registry_ranked.csv/json
```

---

## 15. Channels

- **Website (primary):** https://pureciclismo.github.io/gazzetta-di-kyiv/ (GitHub Pages)
- **Website (mirror):** https://dadismad.github.io/la-gazzetta-di-kyiv/ (GitHub Pages)
- **Telegram:** https://t.me/LaGazzettadiKyiv — previously posted (msg #46, June 2, 14:20)
- **Reddit:** https://www.reddit.com/r/LaGazzettadiKyiv/ — Devvit app v0.0.33 deployed (June 2, 14:20)
- **X (Twitter):** Via xurl CLI — accounts for Newspaper X + Chief Editor X

---

## 16. Environment & Secrets

Stored in `~/.hermes/.env` (Hermes home) and `.env.reddit.template` (in repo).
Requires:
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_PASSWORD`
- `REDDIT_USERNAME`
- `DEEPSEEK_API_KEY`
- `GROQ_API_KEY` (STT)

---

## 17. Current Status (as of 2026-06-02, end of Hermes session)

**Operations:** 3 active cron jobs running 2x/day pipeline (data → Telegram → Reddit). Published to both channels successfully today.

**Infra:** Both repos exist and are bidirectionally synced. Cron-controlled auto-commit + push.

**Site:** Full newspaper terminal with: statement + nav under logo, decorative floral image band, halved ornament strip, narrative cards, asset mapping, institutional design.

**Pipeline:** 5-stage ingestion → analysis → quality → payload (v3.0 with full editorial alignment) → audit chain.

**Governance:** Multi-layer (brand → UI → claims → CEO gate) before deploy.

**Content:** Human detail ledger seeded with 5 entries. CTA rotation active. Social distribution log running.

**Paradigm:** Strategy refinement completed — 6-thesis editorial lens, 4-newsletter business model, 40-source data pipeline architecture defined.

**Next:** Implement newsletter infrastructure, create thematic Telegram channels, rebuild ingestion pipeline with new sources, launch the White Pill weekly edition.
