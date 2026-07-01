---
name: gazzetta-knowledge-base
description: Captures everything learned during Gazzetta di Kyiv development. Design evolution, content principles, voice guide, proven patterns, and reusable assets. Load this skill when starting any Gazzetta-related work to get immediate context on what works.
version: 1.17.0
author: Hermes Agent
created_by: agent
---

# Gazzetta di Kyiv — Learned Knowledge & Proven Patterns

Everything we've discovered through iteration, focus groups, and user feedback.
Load this skill at the start of any Gazzetta session. It's the institutional memory.

## Reference Files
- `references/cco-cdo-agent-architecture.md` — Sprint 7-9: CCO (multi-platform distribution) + CDO (design auditor) agent architecture. Cloud Run Jobs, curation engine, Telegram formatting rules, platform formatter pitfalls, secret mount workaround, Secret Manager key registry. June 2026.
- `references/rd-agent-architecture.md` — Sprint 11: Autonomous R&D Agent (gazzetta-rd-sweep-weekly). Cloud Run Job + Scheduler, 3-track research scope, Phase 1/2 rollout (Issues → Draft PRs), GitHub fine-grained PAT requirements, branch naming convention, PR template, Multi-Lens risk synthesis guardrails (PAT exfiltration, force-push, merge conflicts, supply-chain). Dockerfile.rd-agent build pattern. June 2026.
- `references/systems-architecture-audit.md` — Full architecture map, frontend critical rendering path, data quality diagnostics, SPOF mapping, and performance baseline. Run the data quality one-liner before any pipeline debugging session to rule out total collapse (amount_b=$0, confidence=0 across all stories). June 2026.
- `references/amount-fabrication-pipeline.md` — Amount fabrication root cause: context_amount() fallback, approve_draft.py 5.0 default, db_to_json.py scaling. Fix chain across fetch_intel.py, approve_draft.py, db_to_json.py. June 2026.
- `references/ru-page-fix-pattern.md` — RU page recovery playbook: i18n path detection, ru_sync_gate ordering, relative path trap with /ru/ subdirectory, unhashed ref deployment. June 2026.
- `references/flow-nodes-debugging.md` — Flow Nodes SVG rendering debug: null DOM element crash chain, app.js injection into standalone pages, verification checklist. June 2026.
- `references/event-horizon-recovery.md` — Standalone page truncation: patch() can lose closing `</script>` tags on self-contained pages. Git recovery + CORS proxy pattern for Yahoo Finance tickers. June 2026.
- `references/data-backfill-procedure.md` — Pace and confidence backfill recipes: run backfill_pace.py, import compute_confidence from generate_flows.py, post-backfill direct deploy pattern. June 2026.
- `references/market-regime-generation.md` — Market regime JSON generation from flows data: Money Flow / Top Heavy / Bond Fear indicators. Recipe for when file is 404. June 2026.
- `references/divergence-trade-hooks.md` — v23.22 divergence computation spec: narrative-price gap formula, label thresholds, Kobeissi/ZeroHedge display format
- `references/ui-implementation-patterns.md` — Sprint 1-2 UI patterns: always-visible share row, hamburger nav drawer, mobile tap integrity (D9), word-break headlines. June 2026.
- `references/gcp-cloud-run-migration.md` — Sprint 3 GCP Cloud Run migration: architecture, IAM roles, Dockerfile, cloud_entrypoint.py, Cloud Run Job vs Service, Artifact Registry, package naming, GCS cache headers, scheduler OAuth. June 2026.
- `references/cloud-entrypoint-db-persistence.md` — Sprint 4 DB persistence fix: cloud_entrypoint.py reads from wrong path (`public/data/` → `data/`), ensure_db_ready() seeding pattern, import_json_to_db re-sync after pipeline. June 2026.
- `references/sprint4-flow-dimensions.md` — Sprint 4 Portfolio Manager upgrades: Duration/Counterparty/Scale fields on all 199 flows, compute_flow_dimensions.py pipeline integration, app.js rendering, test_platform.py assertions. June 2026.
- `references/chief-architect-agent.md` — Sprint 4 Chief Architect Agent: Cloud Run service URL, AMEND context-aware tuning, deterministic pre-checks (R1/R3/R5), review workflow, secret mount pattern. June 2026.
- `references/operational-governance-june2026.md` — SOP v1.2 (9 rules), Design Guidelines v1.0 (18 rules), deploy_routine.sh (active crontab, 3 mitigations), pipeline corrections, CSS 404 root cause. June 2026. As of Sprint 3 (2026-06-12), the local crontab is deactivated in favor of GCP Cloud Run. See `references/gcp-cloud-run-migration.md`.
- `references/batch-html-corruption-june2026.md` — Batch processing corruption: read_file line-numbered output embedded in files, inline script tag destruction. Fix pattern: re.sub line number stripping + git restore for lost blocks. June 2026.
- `references/mobile-design-patterns.md` — Breakpoints, photo placement, Bet&Benefit toggle, brand signatures, typography scale
- `references/pipeline-architecture.md` — Script chain, analyzer v2.2 changes, audit v2.2 checks, data sources, article contract
- `references/telegram-channel-deletion.md` — How to delete all messages from a Telegram channel via Bot API
- `references/wall-street-audit-june2026.md` — Wall Street professional audit (PM + Quant + S&T Desk) of all 6 products. Product grades, critical issues, CRO verdict, theft-worthy features, persona pack spawn pattern.
- `references/geopolitical-risk-audit-june2026.md` — Geopolitical risk analyst audit of the full product. 4/10 verdict, raw data extraction of all 690 stories, China-bias analysis, ticker dominance (FXI/KWEB/MCHI = 95% of verifications), missing geo-coverage (incl. Russia-Ukraine absence), contingency ticket for reporting and analysis.
- `references/file-management-architecture.md` — Canonical source rules, root/site split, directory structure, deploy pipeline
- `references/frontend-hardening-june2026.md` — RU nav i18n (data-i18n on nav-group-label), onclick→data-action migration, duplicate DOM ID fix pattern, getJSON retry logic, -webkit- CSS prefix bulk-add. June 2026.
- `references/deployment-pitfalls-june2026.md` — GCS edge cache, CSS duplicate rules, vision model hallucination, root/site file duplication. June 2026.
- `references/cron-recovery-procedure.md` — Step-by-step recovery when scheduler restart wipes all cron jobs. Symptoms, recreation commands, post-recovery checklist. June 2026.
- `references/data-pipeline-audit.md` — Systematic audit methodology: phantom script detection, cron output verification, data flow tracing, bridge pattern
- `references/multi-vector-architecture.md` — Multi-vector narrative scoring: 12-vector DeepSeek prompt engineering, 0.40 container threshold, 0.30 Domino threshold, assemble/merge/classify pipeline, Alpha Board frontend, CDN deployment. June 2026.\n- `references/pipeline-architecture.md` — **CURRENT** v3.0 SQLite-backed architecture: DB tables, scripts, crons, shipit stages, test gate
- `references/fresh-story-pipeline-recovery.md` — **v27.1** Recovery when front-page stories are stale: fetch_intel + bulk_approve + full_json rebuild + contradiction_score fix + SQLite json_valid trap. June 2026.
- `scripts/verify_reality.py` — Three-lens post-deploy verification (retrospective/introspective/extrapolative). Run after every deploy. Non-zero exit = reality gap detected.
- `references/sprint1-2-ui-architecture.md` — Sprint 1-2 UI changes (June 2026): share visibility, tap targets D9, word-break, hamburger nav drawer, deploy workflow, version tags.
- `references/cco-cdo-sprint7-8-pitfalls.md` — Sprint 7-8 CCO/CDO deployment pitfalls: qualitative confidence schema, Telegram HTML parse mode, gcloud secret redaction, Dockerfile.agents build, import shadowing. June 2026.
- `references/multi-vector-scoring-architecture.md` — Phase 8: 12-vector narrative scoring via DeepSeek prompt engineering. Proportionality constraint, full-market context pattern, dry-run verification, GCP IP recovery.
- `references/multi-vector-scoring-design.md` — **Phase 8 design decision.** Multi-vector narrative scoring replacing 1:1 tagging. DeepSeek prompt schema (narrative_scores dict), proportionality constraint, multi-container assignment (threshold >=0.40), DeepSeek json_object mode requirements, full file inventory for the refactor. June 2026.
- `references/cft-blocks-june2026.md` — **Phase 8.5 CFT data layer.** Catalyst-Flow-Trade block computation in build_frontend.py. build_cft_block() function, multi-vector catalyst selection, Domino ripple extraction (0.25 threshold), capital formatting, data structure for Phase 9 app.js rendering. June 2026.
- `references/alpha-board-phase9.md` — **Phase 9 Alpha Board rendering.** Client-side CFT card rendering in build_frontend.py. renderAlphaView() function, domino pill interaction (data-target + event delegation pattern to avoid escape-drift), 5-tab architecture, glass-morphism card design, mobile bottom nav. June 2026.

## Design Evolution (What We Learned)

### Phase 1: Beige Broadsheet → Rejected
- Beige/cream paper background, gold-blue trim, Playfair Display + Inter
- **Verdict:** Too "wedding blog" — decorative but not authoritative. Inter is anonymous tech-font.

### Phase 2: Dark Terminal → Rejected
- Dark Bloomberg-style (#0a0e14 background, blue accents)
- **Verdict:** Wrong aesthetic entirely. "Cyberpunk terminal without proven efficacy." User explicitly said NO to dark terminal.

### Phase 3: Gold/Blue/White Newspaper → Foundation
- Gold masthead (#C8A44E), sky blue accents (#4A8FCC), white paper (#FFFDF8)
- DM Serif Display + Source Serif 4 + Inter (labels only)
- **Verdict:** Correct palette. Correct fonts (after DM Serif Display replacement of Playfair).
- **Key insight:** Gold = truth/value. Sky blue = vision/horizon. White = clarity.

### Phase 4: Ultra-Dense Grid → Functional but Wrong Format
- 3-column headline grid, 52px masthead, no sidebar
- **Verdict:** Too scattered. User wanted vertical scanning, not grid scanning.

### Phase 5: Vertical List + Asset Panel → Current
- Single-column news (left) + asset ticker panel (right, 260px)
- Sticky asset panel with 7 tickers
- Khmelnytsky anchoring the masthead + rotating Italian thinkers

### Phase 6: Bet&Benefit + Crossed Maces + Domain Photos (June 2026)
- "Market Pulse" renamed to "Bet&Benefit" — sets aggressive positioning expectation
- Each asset gets 2h horizon projection: projected price + volume change with bullish/bearish bias
- Masthead: ⚔⚔ (crossed maces — Khmelnytsky) left of name, ⚜ (Machiavelli) permanently right of name (static, no longer rotating)
- Domain-specific photos (100×70px) right of each story card — geopolitics/markets/tech/wealth/pleasure
- Unsplash CDN for photos with lazy loading + error fallback (hide on fail)
- Card layout: flex row (text left, photo right)

### Phase 7: Mobile-First Redesign (June 2026)
- Focus-group-driven: both agents independently agreed on every design decision
- Photos move **LEFT** of text on mobile (CSS `order: -1`), sized 70×50px → 55×40px at smallest
- Bet&Benefit panel hidden on mobile sidebar, accessible via 📊 FAB toggle in sticky masthead → bottom sheet overlay with slide-up animation
- Brand signatures: ⚔⚔ always visible (down to 12px at 400px), ⚜ visible down to 400px (11px)
- Four breakpoints: >800px (desktop sidebar), ≤800px (tablet, hide sidebar, show toggle), ≤600px (phone, photos left, tighter cards), ≤400px (small phone, compact)
- Cards tightened at each breakpoint: padding, font sizes, photo dimensions all scale down
- See `references/mobile-design-patterns.md` for full focus group findings and CSS patterns

### Phase 10: Polished Chrome + Density Optimization (June 2026)
- **Focus group (Metallic Design Specialist + Information Density Specialist):** Brighter, more metallic palette + tighter information containers
- **Palette replaced:** emerald/teal-navy/crimson → brushed brass/white gold/polished chrome/liquid mercury/ruby chrome
- Background: #E8EDF5 (polished chrome — bright silver-white)
- Cards: #F7F4EF (white gold — warm champagne-silver)
- Primary accent: #C9A962 (brushed brass — warm burnished gold)
- Secondary accent: #9BB5D4 (liquid mercury — cool silver-blue)
- Danger: #D64040 (ruby chrome — bright metallic crimson)
- Success: #00C9A7 (polished emerald)
- Text: #2C3E50 (dark gunmetal) on bright surfaces
- **Aesthetic:** "Bulgari flagship at noon — polished chrome walls, white gold display cases, brushed brass accents"
- **Density optimized:** card padding 8px→5px, layout padding 14px→10px, gaps 8px→5px, masthead 43px→34px
- Results: 79% info density per card (+12pp), 4 cards above fold (+33%), 6 sidebar rows (+20%)

## Content Principles

### Voice: Three Registers (Phase 9)

Gazzetta speaks in three registers, selected per story type:
- **THE CLAIM** — "$15K degens. You. Now. Action. Contempt for consensus." Direct address, short sentences, action verbs. Default for crypto and THE PLAY OF THE DAY.
- **THE BRIEF** — "$50K+ semi-pros. Ticker-first, number-dense, thesis-driven." Jargon without apology. Default for macro/rates/markets.
- **THE DISPATCH** — "Institutional-adjacent. Dense, confident, almost arrogant." Multi-asset, historical parallels, payout claims. Default for geopolitics/corruption/defense/energy.

Full spec: load `gazzetta-capital-flows`, reference `references/voice-registers.md`.

**Ambition signal words (use):** claim, capture, seize, front-run, rotate into, extract, edge, asymmetry, conviction, the board, structural, flow-confirmed, institutionally-ignored
**Ambition killers (ban):** "opportunity," "potential," "could be," "we believe," "significant" (use the number)

### Language: Zero Taxonomy Words
NEVER use these banned phrases:
- "Narrative acceleration"
- "Second-order effects remain underpriced by consensus"
- "Transmission effects"
- "Repricing whipsaws"
- "Mention-share drops below 7d baseline"
- "Cross-source confirmation pending"

ALWAYS use:
- Named actors (US Central Command, not "policy actors")
- Specific events (Kuwait airport struck, not "infrastructure targeting threshold crossed")
- Geographic specificity (not "energy corridor" — say "Strait of Hormuz")
- Concrete numbers (not "significant" — say "$1 trillion" or "seven dead")

### Structure: Contradiction-First
Every story = They Say vs Reality.
- They Say: the consensus claim, quoted or paraphrased
- Reality: the specific event, data point, or evidence that contradicts it
- The gap IS the story

### Density: Maximum Information Per Viewport
- Masthead ≤ 50px
- No decorative banners, no subtitle, no "about" paragraph in masthead
- Stories are headlines + one summary line. Click to expand.
- Sidebar/panel is functional (assets), not decorative

## Paradigm Lens (Refined — see `gazzetta-paradigm-and-strategy` skill for full doctrine)

The central thesis: **multipolar civilisational transition** driven by asymmetric technological execution, institutional strain in the Western system, and abundance technologies altering value and leverage. Five pillars + evidence texture in `docs/PARADIGM_LENS_v2026-06-03.md`.

Key operational rules from the refined lens:
- Every narrative must reference at least one pillar where materially relevant
- Confidence bands (high/medium/low) + invalidation triggers mandatory for lead stories
- **Invention ≠ Execution** — always distinguish discovery from deployment at scale
- Capital-flow implication required on every story: what gets repriced, who benefits

## Italian Thinker System

| Sector | Figure | Icon | Core Insight |
|--------|--------|------|-------------|
| geopolitics | Machiavelli | ⚜ | Power is perception |
| markets | Pareto | ⚖ | Elites circulate, 80/20 governs |
| tech | Marinetti | ⚡ | Speed is the only morality |
| wealth | Vico | 🏛 | History moves in cycles |
| ukraine/resistance | Mazzini | ✦ | Nations are ideas before borders |
| culture/pleasure | D'Annunzio | ✧ | Aesthetics are the first battlefield |
| justice/accountability | Beccaria | ⚖ | Law is a contract, not a weapon |
| ideology/media | Gramsci | ◈ | Who controls the story controls the room |

Khmelnytsky (⚔⚔ — crossed maces, left of name) is permanent — anchors Kyiv. Machiavelli (⚜, right of name) is permanent too — no longer rotates.

## Workflow Ecosystem

### Active Skills
- `gazzetta-paradigm-and-strategy` — Editorial paradigm, six theses, platform formats
- `gazzetta-editorial-writer` — LLM-driven content production for Telegram/Reddit/Website
- `gazzetta-capital-flows` — Capital flow methodology (Mike Green thesis), PDR, political corruption framework, voice registers, THE ANCHOR spec, tutorial cuts
- `gazzetta-website` — Design system, v20 pure white palette (#FFFFFF), typography (DM Serif Display 20-22px), THE ANCHOR spec (14 assets with ATR stops), computed confidence, track record, capital.html methodology. Pitfall: precision/numerical changes require CFA+PM+Fintech professional review BEFORE deploy.
- `gazzetta-precision-pipeline` — 8-dimension precision scoring, professional personas (CFA/PM/Fintech through gambler's lens), audit workflow for numerical changes. Run before any deploy that touches ATR, confidence, stop, or data logic.
- `hermes-capability-maximization` — Operational excellence: v4-pro for all, reasoning_effort=high, max parallelism, self-audit
- `agent-cooperation-network` — Secure agent-to-agent communication (MCP server, Ed25519 identity, A2A, defense)
- `focus-group-review` — Multi-persona design/content audits
- `content-analysis-loop` — Analyzes every post/story for patterns, feeds back into editorial
- `gazzetta-knowledge-base` — This skill. Institutional memory.

### Active Cron Jobs (5 of 12 restored, June 11 2026)

**As of Sprint 3 (2026-06-12), the `gazzetta-product-factory` and `gazzetta-health-check` local cron jobs are DEACTIVATED. The pipeline now runs on GCP Cloud Run Jobs triggered by Cloud Scheduler every 10 minutes. See `references/gcp-cloud-run-migration.md`.**

**All 12 cron jobs were silently wiped by a scheduler restart on 2026-06-11 (gateway PID survived, `jobs.json` cleared). See `references/cron-recovery-procedure.md` for the full recovery playbook.**

Currently active (recreated from knowledge base descriptions):
- `gazzetta-product-factory` — **Unified pipeline** every 60m: fetch_intel → intel_to_stories → approve_draft → generate_flows → db_to_json → shipit → health_check. `no_agent=true` script mode. Script: `~/.hermes/scripts/gazzetta_product_factory.sh`
- `gazzetta-health-check` — Every 30m: curl homepage, count stories/flows, verify pages. `no_agent=true` script mode. Script: `~/.hermes/scripts/gazzetta_health_check.sh`
- `gazzetta-ceo-overseer` — Every 15m: page quality + frameless compliance. LLM-driven (v4-flash). Skill: `gazzetta-ceo-overseer`
- `gazzetta-market-data` — Every 6h: market pipeline chain. `no_agent=true` script mode. Script: `~/.hermes/scripts/gazzetta_pipeline_chain.sh`
- `daily-session-review` — Daily 22:00. LLM-driven (v4-pro). Skill: `daily-session-review`

**Still to restore (7 jobs):** hourly-narrative-review, focus-group-quality-gate, living-stories-enrich, x-health-watchdog, link-intelligence-synthesis, phase3-daily-brief, editorial-style-audit. All merged into product-factory in previous consolidation — the factory script covers their core functionality.

### Telegram Channel
- Channel: `@LaGazzettadiKyiv` (ID: `-1003990434181`)
- Bot: `@Stocchibot` — admin with `can_delete=True`, `can_post=True`
- Technique for bulk deletion: see `references/telegram-channel-deletion.md`

### X.com Integration
- Account: @GazzettadiKyiv (ID: 2059326509177765888)
- Status: Connected via xurl CLI + OAuth 2.0. Read/search works. Posting needs $5 credit purchase at developer.x.com
- Guide: docs/X_COM_INTEGRATION.md

### Data Stores
- `data/publish/stories.json` — Concrete stories for website (the source of truth)
- `data/content_analysis/store.jsonl` — Analyzed content patterns
- `data/content_analysis/index.json` — Pattern summary
- `data/editorial_state.json` — Cross-cycle memory

### Reference Files
- `references/mobile-design-patterns.md` — Focus group consensus on mobile UX: photo placement, Bet&Benefit toggle, breakpoints, anti-patterns
- `references/telegram-channel-deletion.md` — Technique for bulk-wiping a Telegram channel via Bot API (post-probe → ceiling → iterative delete)

### Design System
- Palette: Emerald #00B894, Crimson #D63031, Teal-Navy #0F2027 (bg), Frosted Glass #E8EDF2 (cards), Chrome #A0B4C8
- Inspiration: Casino (Scorsese) × Casino Royale (Bond) × Ballad of a Small Player (Macau 2025)
- Display font: DM Serif Display (headlines, masthead)
- Body font: Source Serif 4 (text, summaries)
- Label font: Inter (only at 7-9px, uppercase, tracking)
- Layout: news left (flex column) + THE ANCHOR right (260px sticky)
- Masthead: 48px, sticky, emerald-bottom-border

## Proven Patterns (from content analysis)

1. **Contradiction headline + named actor + data point = highest engagement**
2. **Sharp voice (+ conviction) outperforms neutral observer tone**
3. **Stories aligned with thesis framework get reused more**
4. **Named events + geographic specificity = strongest attention hooks**
5. **Thesis-aligned framing (US decline, EU fragmentation) gives ideological coherence**

## Verification Protocol — Live URL Truth (v23.23, June 2026)

**CRITICAL RULE: Never report success based on local file writes. Verify live public URLs.**

The #1 cause of false-positive success reports: trusting browser snapshots that capture initial DOM before JavaScript renders content. The `stories.html`, `index.html`, and all product pages load content dynamically via `app.js` → `boot()`. A browser snapshot taken before JS execution shows 11 elements and looks broken. The page IS fine — the snapshot is lying.

**Verification checklist (every deploy):**
1. `curl -sI https://www.lagazzettadikyiv.com/` → HTTP/2 200
2. `curl -sI https://lagazzettadikyiv.com/` → HTTP/2 200 (bare domain)
3. `curl -sI https://www.lagazzettadikyiv.com/ru/` → HTTP/2 200
4. `curl -s https://www.lagazzettadikyiv.com/data/stories.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['generated_at'], len(d.get('stories',[]))+1)"` — verify JSON freshness
5. Browser console: `document.querySelectorAll('#newsCol .card').length` — must return 30+ cards
6. Browser console: `document.getElementById('newsCol').innerHTML.length` — must be >100K chars
7. No `$88B` in live HTML: `curl -s https://www.lagazzettadikyiv.com/ | grep -c '\$88'` → 0
8. Sector amounts all unique: `curl -s https://www.lagazzettadikyiv.com/ | grep -oE '\$[0-9,.]+[BM]' | sort -u | wc -l` → 5+ unique values

**Self-audit after any success claim:** re-run steps 4-8. If any fail, the deploy is NOT successful.

## UX v23.22+ — Divergence-Driven Trade Hooks & Action Windows

### Trade Hooks: Narrative-Price Divergence Format (replaces raw percentages)

**Before (worthless):** `CRYPTO ↓ OUT 50%` — meaningless percentage, no institutional value.
**After (institutional):** `CRYPTO · DIVERGENT · ↓ 50.0%` — Kobeissi/ZeroHedge style.

**Computation:** `gap = |narrativeForce − priceForce|` where:
- `narrativeForce = directionSign × confidence` (direction: ±1, confidence: 0-1)
- `priceForce = clamp(|priceDeltaPct| / 100, -1, 1)`
- Price data from `market_prices.json` (keyed by asset class: crypto, equities, commodities, etc.)

**Labels:** `gap > 0.5` → `DIVERGENT` (red #DC2626) · `gap > 0.25` → `LAGGING` (amber #D97706) · `gap ≤ 0.25` → `ALIGNED` (green #059669)

### Freshness: Action Window Labels (replaces timer)

**Before (worthless):** `8m ago` — a timer, not actionable.
**After (trader-value):** `[HOT ALPHA]` / `[ACTIVE WINDOW]` / `[DELAYED REACTION]` / `[STALE]`

| Age | Label | Color | Meaning |
|-----|-------|-------|---------|
| <60m | `[HOT ALPHA]` | Red #DC2626 | Tradeable edge window |
| 60m-4h | `[ACTIVE WINDOW]` | Amber #D97706 | Still valid |
| 4h-24h | `[DELAYED REACTION]` | Gray #6B7280 | Consensus may have caught up |
| >24h | `[STALE]` | Light gray #9CA3AF | Historical only |

**Both features implemented in `app.js`** via `updateTradeHooks()` and `updateHeroIndicators()`.

### SENTIMENT → Divergence Percentage

The sidebar SENTIMENT section now shows **aggregate divergence percentage** (not inflow ratio).
Format: `64% · Divergence · 12 flows`

## Drawbacks & Pitfalls We've Hit

- Delegation/subagents default to OpenAI (gpt-5.3-codex) which hits quota → set delegation.provider=deepseek + clear delegation.api_key
- **Delegation API key mismatch:** If `delegation.api_key` holds an OpenAI key (`sk-pro...`) while `delegation.provider` is deepseek, subagents silently fall back to OpenAI and hit quota. Fix: `hermes config set delegation.api_key ""` to inherit from `.env` DEEPSEEK_API_KEY
- GitHub Pages CDN caches aggressively (max-age=600) → push empty commits to force rebuild; always increment `?v=N` on CSS/JS in index.html
- **Fabricated Unsplash photo IDs don't work** — only use proven URLs from the sector pool or Wikimedia Commons. If you guess a photo ID, it will silently fail with `naturalWidth: 0`
- analyze_narratives_v2.py produces template language → bypass with LLM-written stories.json
- Memory fills up fast (2200 char limit) → be selective, remove stale entries
- **Credentials accidentally pushed to git** — never use `git add -A` without checking what's staged. Sensitive files must live under `secure/` (gitignored). If a credential leaks, force-rotate immediately
- **Precision changes ship with silent bugs** — v20.16 had 4 bugs caught by professional review: settlement loop missing (critical), ADA target inverted, stake unit label wrong, WATCH assets getting BUY stops. Always run CFA+PM+Fintech audit via `delegate_task` before deploying any numerical/logic change.
- **CCO: Qualitative confidence mapping** (June 2026): The `confidence` field in stories.json is a qualitative string ("low"/"medium"/"high"), not a numeric percentage. The cco_curate.py impact formula requires numeric confidence. Fix: QUALITATIVE_MAP in cco_curate.py maps low=35, medium=65, high=85. If all curated counts are 0 despite loaded stories, check this map and the field name (`confidence` not `confidence_pct`).
- **CCO: Telegram Markdown parse_mode 400 errors** (June 2026): Story headlines contain special characters (`$`, `%`, `+`, `_`) that break Telegram's Markdown parser, causing HTTP 400 Bad Request. Fix: use `parse_mode: "HTML"` with entity escaping (`& → &amp;`, `< → &lt;`, `> → &gt;`). Bold text via `<b>` tags instead of `**`.
- **CCO: `--body` arg mismatch causes X.com draft failures** (June 2026): The cco_entrypoint.py passes `--body` to all platform formatters, but cco_x.py doesn't accept `--body` — only `--headline`, `--they-say`, `--reality`, `--source`, `--contradiction`, `--confidence`, `--asset`. Result: silent subprocess crash with empty stderr. Fix: remove `--body` from base args, add per-platform.

- **YouTube Shorts with disabled subtitles** — `youtube-transcript-api` returns TranscriptsDisabled for some Shorts. Don't waste time on ffmpeg/whisper extraction loops. Derive insight from title, comments, channel context. The user sends Shorts for thesis connection.
- **Root/site file duplication causes silent drift** — 17 HTML/JS/CSS files exist in both project root AND `site/`. Root = edit target, `site/` = deploy target. Only `index.html` currently differs, but any edit to root without copying to `site/` won't deploy. Cron auto-deployer (`gazzetta_deploy_to_gcs.sh`) syncs `site/` → GCS every 15min. Rule: after ANY edit to root `app.js`, `styles.css`, or `index.html`, immediately `cp` to `site/` before deploying. See `references/file-management-architecture.md`.
- **data/ directory is a dumping ground** — 84 entries, 43 operational JSONs (overseers, audits, brandbook, incidents) mixed with actual data files. `data/flows.json` is stale (Jun 5 17:36) while `site/data/flows.json` is current. The `data/` dir holds source-of-truth for stories but `site/data/` holds deploy artifacts. These diverge silently.
- **Triple script locations** — `scripts/` (39 files, 5821 LOC), `ops/` (34 files, 1212 LOC), `~/.hermes/scripts/gazzetta_*` (20 files). Unknown which is canonical. Cron jobs reference the `~/.hermes/scripts/` versions.
- **Git merge conflict on generated artifacts** — `site/data/stories.json` has `UU` status. Generated files in `site/data/` should be `.gitignored`.
- **generate_flows.py direction normalization** — Stories with `capital_flow` dicts had multi-word direction strings ("Structural rotation from US hyperscalers to European cloud providers...") that bypassed the "inflow"/"outflow" filter. Fixed with `normalize_direction()` function using keyword detection on word boundaries. 3 of 8 flows were invisible in the count before this fix.
- **generate_flows.py data source** — Was reading from `site/data/stories.json` (15 stories, only 6 with CF data). Changed to `data/stories.json` (23 stories, 16 with CF dicts). This was the root cause of generic "$1B flowing into equities" headlines.
- **Denomination parsing false match** — "PROCUREMENT" contains "M" but is not "MILLION". Changed from substring `.includes("M")` to word-boundary regex `\bMILLION\b|\bM\b(?!\w)`. Same for billion: `\bBILLION\b|\bB\b`.
- **heroStoryCount overwrite** — `updateMastheadFlows()` was setting `heroStoryCount` to `total_flows_tracked` (8-12) every 5 minutes, overwriting actual DOM story count (23). Removed the overwrite line.
- **Deploy cron silently stuck** (June 2026): Even `no_agent=true` script crons can enter a state where `next_run_at` passes without execution. `last_status` still shows `ok` from prior run. Manual trigger: `cronjob(action='run', job_id='f9a24ed64aa5')`. Detection: compare `last_run_at` vs expected cadence.
- **CRITICAL: `db_to_json.py` osint exclusion filter** (June 2026): ... [existing content]
- **CRITICAL: Draft status mismatch — `pending_review` vs `pending`** (June 2026): ... [existing content]
- **CRITICAL: `contradiction_score` sort buries fresh stories (v27.1 June 2026).** `db_to_json.py` sorts by `contradiction_score DESC` before `generated_at DESC`. New stories created with default score=50 sort AFTER old stories with score=75, regardless of timestamp. The frontend teaser only shows the first 20 — fresh content is invisible. Fix: set `contradiction_score=75` on newly created stories to match existing story scores. Detection: check `stories.json` first 5 entries vs today's date — if all are >24h old but DB has fresh stories, the sort is burying them. Full recovery: `references/fresh-story-pipeline-recovery.md`.
- **CRITICAL: SQLite `json_valid()` stricter than Python `json.loads()` (v27.1 June 2026).** Python's `json.loads('')` succeeds (returns empty string as a JSON value), but SQLite's `json_valid('')` returns 0. The `db_to_json.py` ORDER BY uses `json_extract(full_json, ...)` which crashes the ENTIRE query with "malformed JSON" if ANY row fails `json_valid()`. Always verify with `SELECT COUNT(*) FROM stories WHERE json_valid(full_json)=0` after bulk operations. Fix: `UPDATE stories SET full_json='{}' WHERE json_valid(full_json)=0`. Python `json.loads()` alone is insufficient verification.
- **Stale hashed script references across multiple pages** (June 2026): `build_hashed_assets.py` rewrites `<script src="./app.js">` → `<script src="./app.2d0b5f18.js">` in HTML files. When you later switch BACK to unhashed refs, 4 product pages (flows/signal/trades/track) still had old hashes like `app.f5a9f3f5.js`. The hashed files were deleted from GCS, causing 404s. Fix: `grep -rn 'script.*\\..*\\.js' *.html` to find all stale hashed refs, then standardize to unhashed. ALWAYS check ALL HTML files after changing hash strategy — not just index.html.
- **Unhashed deployment breaks /ru/ completely** (June 2026): When using unhashed script refs, the `/ru/` directory needs explicit copies of `app.js`, `i18n.js`, `styles.css`, `i18n_ru.json`, and `data/`. The `ru_sync_gate` only copies HTML pages, not runtime assets. See `references/ru-page-fix-pattern.md` Bug 4.
- **Hardcoded VM paths break local execution** (June 2026): Scripts hardcode /opt/gazzetta-di-kyiv/data. Fix: use GAZZETTA_HOME env var pattern. Export GAZZETTA_HOME for local runs.

- **Mobile masthead name overflow** (June 2026): 26px uppercase + tracking-widest + icons overflows 375px phones. Fix: responsive font cascade text-[16px] sm:text-[20px] md:text-headline-lg-mobile. Hide icons below 640px with hidden sm:inline.

- **Adding fields to narratives JSON requires zero template changes** (June 2026): The build_frontend.py injects data via __NARRATIVES_JSON__ placeholder. New fields added to the Python dict automatically flow to the client. No HTML template edits needed.

- **Governor loads DEEPSEEK_KEY but never exports to subprocess environ** (June 2026): `governor.py` loads `DEEPSEEK_KEY = _secret("gazzetta-deepseek-key")` from GCP Secret Manager into a Python variable, but subprocesses (`contradiction_synthesizer.py`) read `DEEPSEEK_API_KEY` from `os.environ`. The subprocess call `env={**os.environ, ...}` only passes what's in os.environ. Fix: add `os.environ["DEEPSEEK_API_KEY"] = DEEPSEEK_KEY` immediately after the secret loading line in governor.py. Symptom: `[synthesis] FAIL(1) ... ERROR: DEEPSEEK_API_KEY not set` despite governor showing `[secret] loaded gazzetta-deepseek-key`.

- **Production .env left at 777 root:root** (June 2026): After migration, `/opt/gazzetta-di-kyiv/.env` had world-writeable permissions owned by root. This is a credential exposure risk on a web-facing VM. Fix: `sudo chown gazzetta:gazzetta /opt/gazzetta-di-kyiv/.env && sudo chmod 600 /opt/gazzetta-di-kyiv/.env`. The systemd service runs as User=gazzetta, so 600 is sufficient. Apply this to ALL credential files in the project root.
- **GCP VM ephemeral IP cycling** (June 2026): GCP VMs on ephemeral IPs can change addresses after stop/start or preemption. Symptoms: SSH timeout to the IP in `~/.ssh/config`, `gcloud compute instances describe` shows a different `natIP`. Fix: (1) `gcloud compute instances describe gazzetta-prod --zone=us-central1-a --format='value(networkInterfaces[0].accessConfigs[0].natIP)'` to get current IP, (2) update `~/.ssh/config` Host entry. The SSH key (`~/.ssh/google_compute_engine`) stays the same — only the IP changes. Use `ssh -i ~/.ssh/google_compute_engine -o StrictHostKeyChecking=no alexstocchi@<new-ip>` to test before updating config. (`gcloud compute target-https-proxies update --ssl-certificates=NEW_CERT`), it takes 5-15 minutes before the new cert is served. The `gcloud` API confirms the update immediately but CDN edge nodes cache the old cert. Verify with `echo | openssl s_client -connect domain:443 -servername domain 2>&1 | grep CN=`. If the old CN still shows, wait longer. Do NOT report success until `curl -sI https://domain/` returns HTTP/2 200.
- **GCS cache header enforcement**: `shipit.sh` can overwrite manually-set cache headers during `gsutil rsync`. After deploy, force critical files: `gcloud storage objects update gs://BUCKET/index.html --cache-control="no-store, must-revalidate"` and `gcloud storage objects update "gs://BUCKET/data/**.json" --cache-control="private, no-store"`.
- **macOS `date -Iseconds` incompatibility in shell scripts**: GNU `date -Iseconds` is not available on macOS (BSD date). `gazzetta_product_factory.sh` used this for log timestamps — all log entries showed `date: illegal option -- I` but script continued (each command had `|| true`). Fix: replace all `date -Iseconds` with `date -u '+%Y-%m-%dT%H:%M:%SZ'`. Any new shell script targeting the cron environment must use macOS-compatible date syntax.
- **Phantom scripts → fabricated cron output** — 6 of 7 scripts referenced in cron prompts didn't exist on disk (June 2026). All 17 crons still reported `last_status=ok`. LLM agents told to `python3 scripts/build_site.py` fabricate `{"ok":true}` instead of surfacing FileNotFoundError. Fix: script existence audit + convert deterministic crons to `no_agent=true` script mode.
- **Disconnected pipeline → static site** — Telegram monitor collected real intel every 30m (Iran strikes, BTC crash, SpaceX IPO) but saved to `telegram_intel/latest.json` — never became stories. Stories.json stayed at 18 entries while intel had 3 fresh actionable stories. Fix: `intel_to_stories.py` bridge + `pipeline_chain.sh`.
- **Identical regeneration → functionally static** — Same 18 stories → same 12 flows → same 79% confidence every hour. Site appeared updated (fresh timestamps) but content never changed. Fix: bridge brings new stories → new flows emerge naturally.
- **CRITICAL: GCS edge cache serves stale content for up to 1 hour** (June 2026): gsutil cp updates the bucket object immediately, but the public HTTP endpoint caches with `max-age=3600`. Curl without cache-bust parameter returns stale HTML/CSS. Fix: `gsutil -m setmeta -h "Cache-Control:no-cache, max-age=0" gs://BUCKET/*.html gs://BUCKET/*.css` and always re-cp with `-h "Cache-Control:no-cache, max-age=0"`. Verify with `curl -sI URL | grep cache`.
- **CRITICAL: GCS edge cache blocks same-hour verification — hashed deploy bypass** (June 2026): Even `Cache-Control:no-store` setmeta doesn't reliably bypass the edge CDN. The reliable workaround: (1) hash assets: `AH=$(shasum -a 256 public/app.js | cut -c1-8)` (2) upload with immutable cache: `gsutil -h "Cache-Control:public, max-age=31536000, immutable" cp public/app.js gs://BUCKET/app.$AH.js` (3) update ALL HTML file refs: `sed -i '' 's/app\.js/app.'$AH'.js/g' public/*.html` (4) upload HTML with no-cache: `gsutil -h "Cache-Control:no-store, max-age=0" cp public/*.html gs://BUCKET/`. Never delete old hashed assets — they may be referenced by cached HTML on edge nodes. Verify: `curl -s https://BUCKET/app.$AH.js | grep -c "expected-string"` returns >0. Always export `CLOUDSDK_CONFIG=/Users/alexstocchi/.config/gcloud` before gsutil commands.
- **patch() tool double-escapes backslashes in JS template strings** (June 2026): When patching JavaScript files containing `'\\n'` (backslash-n in string concatenation), the patch() tool doubles the escape sequences — `\\\\n` becomes `\\\\\\\\n` and `\\\\'` becomes `\\\\\\\\\\\\'`. This introduces syntax errors because `\\\\\\'` is parsed as backslash + terminating quote. The JS `node -c` check catches this immediately. Recovery: use terminal + Python raw-string replacement: `content.replace('\\\\\\\\n', '\\\\n').replace("\\\\\\\\\\\\'none", "\\\\'none")`. NEVER fix these with patch() — it compounds the escaping. The `\\\\'` fix is especially critical on `onerror` attributes: `onerror="this.parentElement.style.display=\\\\'none\\\\'"` → fix to `onerror="this.parentElement.style.display=\\'none\\'"`.
- **CRITICAL: Deleting old CSS from GCS breaks sub-pages with cached HTML** (June 2026): When you delete old hashed CSS files from GCS, sub-pages whose HTML is cached by the edge still reference those deleted files → pages load with ZERO styles → user sees broken/unstyled layout. Fix: NEVER delete old CSS from GCS without first updating ALL HTML files on GCS. Or: overwrite old hashed files with latest content instead of deleting.
- **CSS duplicate rules outside @media queries silently override fixes** (June 2026): The CSS had two sets of masthead rules — the first (correct) and a second set at line ~1076 that existed OUTSIDE any @media block as bare global CSS. The later rules won via cascade. read_file pagination truncated the 2600-line CSS file, hiding the duplicate. Fix: `grep -n "selector" styles.css` to find all occurrences before editing any rule.
- **browser_vision and vision_analyze hallucinate colors** (June 2026): Both vision models consistently reported a "dark bar" and "white text on dark background" when computed styles proved `rgb(255,255,255)` background and `rgb(139,0,0)` text. Trust `browser_console` with `getComputedStyle()` for color/layout verification — the DOM doesn't lie. Vision is backup, not primary.
- **Project reorganized — root/site duplication resolved** (June 2026): 25 HTML files and 5 CSS/JS files existed in both root and site/. Root copies were stale, never deployed. All root duplicates DELETED. site/ is now the SOLE source of truth. archive/ holds 5 unique old HTML files. docs/audits/ holds 8 old reports. scripts/ consolidated. Root went from 67→16 entries.
- **translate_content.py hangs the pipeline** (June 2026): The pipeline_chain.sh step `translate_content.py` timed out at 300s, blocking `build_site.py`. Workaround: run `build_site.py` separately after pipeline times out, or skip translate_content if RU pages are scorched-earth.
- **Redirect stubs cause test gate false failures**: `build_site.py` can leave product pages (stories.html, flows.html, signal.html, trades.html, track.html) as meta-refresh redirect stubs (~372 bytes) — `<meta http-equiv="refresh" content="0;url=./#stories"/>`. The test gate (`test_platform.py`) expects body text >100 chars and links to styles.css, which stubs lack. Root HTML files remain intact — the stubs are in `site/` only. Fix: `cp stories.html flows.html signal.html trades.html track.html story.html site/` before running `shipit.sh`. Check: `wc -c site/stories.html` — if <1000 bytes, the page is a stub, not full content.
- **RU page: three stacked bugs make /ru/ a dead page**: (1) `detectLang()` in `i18n.js` ignores URL path — visiting `/ru/` still defaults to `en` because it only checks localStorage + browser language. (2) `ru_sync_gate` in `shipit.sh` ran BEFORE hash stage — copied `site/index.html` with OLD script refs, then hash stage only updated EN index. (3) All paths are relative (`./i18n.xxx.js`, `./data/`), resolving under `/ru/` where the files don't exist. Fixes: add `pathname.match(/^\/ru(?:\/|$)/i)` to detectLang(), move ru_sync_gate to AFTER hash stage (Stage 3.1), deploy hashed JS/CSS + i18n_ru.json + data/ to GCS `/ru/` directory. Full playbook in `references/ru-page-fix-pattern.md`.
- **Event Horizon: standalone page truncation by patch()** (June 2026): `patch()` on self-contained HTML pages with inline `<script>` blocks can silently drop trailing content — the closing `})();</script></body></html>` and the `init()` call. Symptoms: page shows 9 elements, no JS errors in console, `typeof initEventHorizon` → `undefined`. Recovery: `git show <good_commit>:event_horizon.html > event_horizon.html`, then re-apply patches. ALWAYS `tail -6` standalone pages after patching — if it doesn't end with `</html>`, the file is truncated. See `references/event-horizon-recovery.md`.
- **CRITICAL: Batch HTML processing via read_file corrupts files with line number prefixes** (June 2026): `read_file()` returns content with `LINE_NUM|CONTENT` format. When this output is used as source for `write_file()`, line number prefixes become permanently embedded in all HTML files. Additionally, batch scripts that strip `<script` tags to clean up hashed references will also destroy opening `<script>` tags of inline JavaScript blocks — raw JS text appears in HTML without wrappers, causing test gate failures for "null" and "[]". Recovery: strip line numbers with `re.sub(r'^\s*\d+\|\s*', '', line, count=1)` and restore lost script blocks from git. Prevention: use `open(path).read()` in execute_code scripts instead of `read_file()` for content that will be written back. See `references/batch-html-corruption-june2026.md`.
- **CORS proxy for Yahoo Finance on standalone pages** (June 2026): Event Horizon fetches live tickers from `query1.finance.yahoo.com` which blocks browser CORS. Fix: prepend `https://corsproxy.io/?` + `encodeURIComponent(yahooUrl)`. The comment in the original code said "uses corsproxy.io free tier" but the code directly called Yahoo without the proxy — add it. CoinGecko API (`api.coingecko.com/api/v3/simple/price`) works without proxy. For production, consider a server-side price fetcher that writes to `market_prices.json`.
- **Flow Nodes: null DOM element crash blocks entire inline JS**: Two null-element crashes prevented the SVG graph from rendering: (A) `document.getElementById('cn-theme-toggle')` returns null → `.addEventListener()` throws TypeError. This happened before `init()` was set up, blocking all graph initialization. (B) `render()` sets `.textContent` on `cn-last-updated`, `cn-total-tracked`, `cn-node-count`, `cn-edge-count` — all missing from HTML. Fixes: null-guard all element access, remove app.js injection from standalone pages. Debug: test `document.getElementById('cn-nodes-layer').innerHTML = '<circle.../>'` to verify SVG DOM works. See `references/flow-nodes-debugging.md`.
- **CRITICAL: Nav dropdown toggle had NO JavaScript handler at all** (June 2026): The INTEL/ALPHA dropdown buttons in the masthead had zero JavaScript. The CSS defines `.nav-dropdown.open .nav-dropdown-panel { display: block; }` and `.nav-dropdown.open .nav-dd-arrow { transform: rotate(180deg); }` — but nothing in `app.js` toggled the `.open` class. The dropdown was a dead component since it was introduced. Fix: `wireNavDropdowns()` function that (1) toggles `.open` on click of `.nav-dropdown-trigger`, (2) closes other open dropdowns (single-open accordion), (3) closes all dropdowns on outside click. Must be called from `boot()` after `wireCollapsibleContainers()`.

- **CRITICAL: `<a>` inside `<button>` captures clicks and prevents dropdown toggle** (June 2026): The masthead template (`templates/header.html`) had `<a href="./stories.html">INTEL</a>` nested inside `<button class="nav-dropdown-trigger">`. This is invalid HTML — the `<a>` click navigates away instead of letting the button's click handler fire. Even after adding `wireNavDropdowns()`, the `<a>` would still win the click race and navigate to stories.html. Fix: replace `<a>` with `<span>` in the dropdown trigger buttons in `templates/header.html`, then run `build_site.py` to inject into all 21 HTML pages.

- **Template edit → build_site.py → hash → manifest → HTML ref update workflow** (June 2026): Editing `templates/header.html` does nothing until `build_site.py` runs and injects it into all `public/*.html` files via the `COMPONENT:HEADER:START/END` sentinel markers. After build: (1) `shasum -a 256 app.js | cut -c1-8` for new hash, (2) `cp app.js app.NEWHASH.js`, (3) `sed -i '' 's/app\.[a-f0-9]\{8\}\.js/app.NEWHASH.js/g' *.html`, (4) update `build-manifest.json`, (5) `gsutil rsync` to deploy. Skipping any step results in stale JS being served.

- **Nav fragmentation — each page has its own hardcoded nav** (June 2026): The 6 HTML pages (index.html, stories.html, flows.html, signal.html, trades.html, track.html) each have independently-coded `<nav class="product-nav">` blocks. Stories.html and track.html had only 5 links (missing HORIZON and FLOW NODES). Flows/signal/trades had `event-horizon.html` (hyphen) while the actual file is `event_horizon.html` (underscore). Index.html called it "Nodes" while others called it "Flow Nodes". Fix: standardize all 6 pages to identical 7-link nav. Verify with `grep -c 'nav_horizon\|nav_flow_nodes' site/*.html` — every page must show 2 matches. After any nav change, check ALL pages, not just the one you edited.
- **Hero indicator ID mismatch — `updateHeroIndicators()` targets wrong element**: The JS function `updateHeroIndicators()` looks for `#heroDivergence` but the HTML element has `id=\"heroContradictions\"`. Result: hero shows \"— CONTRADICTIONS\" (dash, no number). Same pattern can affect `#heroLastInflow` vs `#heroFreshness` (JS handles both via fallback). After ANY change to hero indicator IDs, verify: `grep -n 'heroDivergence\\|heroContradictions\\|heroTopVelocity\\|heroLastInflow\\|heroFreshness' app.js index.html` — IDs must match between JS querySelector and HTML id attribute. Quick fix: change JS line `document.getElementById('heroDivergence')` → `document.getElementById('heroContradictions')`. Stage 2.6 (`ru_sync_gate`) only copies basic pages (about, capital, data, methodology, sources, terms, robots.txt, sitemap.xml) — NOT `index.html`. Result: `/ru/` returns 404 after deploy. Fix: `cp site/index.html site/ru/index.html` before GCS upload. The site uses client-side i18n so the English content is correct — the JS toggles language dynamically.
- **Stale hashed script references after direct deploy** (June 2026): When deploying via `gsutil rsync` directly (skipping shipit's `build_hashed_assets` stage), HTML files still reference hashed filenames like `app.2d0b5f18.js` that don't exist on GCS. Result: JS never loads — 0 teasers, hero dashes, `populateTeasers` undefined. Fix: standardize all script refs to unhashed `app.js`/`i18n.js` across ALL pages before direct deploy. Check: `grep 'app\\.[a-f0-9]\\{8\\}\\.js' site/*.html` — any hit means stale hashes that need replacement.
- **CRITICAL: Hashed CSS overwrites are invisible to browser — always re-hash** (Sprint 10, June 2026): Uploading new CSS under an EXISTING hashed filename (e.g., `gsutil cp styles.css gs://BUCKET/styles.6d32f5c7.css`) updates the GCS object — curl confirms the new content is served. But the browser's internal CSSOM cache holds the parsed rules from the first load of that URL. On subsequent page navigations the browser reuses the cached CSSOM without re-fetching, even with `Cache-Control:no-store`, because the `<link>` URL hasn't changed. Symptom: curl shows your fix, but `browser_console` → `getComputedStyle(el).display` still returns the old value. Detection: `curl -s URL/styles.HASH.css | grep "your-new-rule"` finds it, but `browser_console` → check the actual CSS rule via `document.styleSheets[].cssRules[]` shows the stale version. **Fix:** ALWAYS run `build_hashed_assets.py` after CSS/JS changes — it generates a NEW hash (e.g., `styles.6d32f5c7.css` → `styles.09c3d81d.css`), rewrites all 21 HTML file references, and the browser treats the new filename as a fresh resource. **Never** `gsutil cp` updated content under the old hash — the browser will never see it. This is a CLIENT-SIDE browser cache problem distinct from the GCS edge cache pitfall.
- **CRITICAL: stories.json `confidence` field is qualitative, not numeric** (June 2026): The field `confidence` in stories.json contains string values `"low"`, `"medium"`, `"high"`, `"medium_low"`, `"very_low"` — NOT numeric percentages. There is no `confidence_pct` field (it's `None` for all 245 stories). Any agent that filters or ranks stories by confidence MUST map qualitative tiers to numeric values first: `high→85, medium_high→75, medium→65, medium_low→50, low→35, very_low→15`. `contradiction_score` is on 0-100 integer scale, not 0-1 float — normalize by dividing by 100. Curation formula: `impact = (contradiction_score / 100) * (confidence_numeric / 100)`. See `references/cco-cdo-sprint7-8-pitfalls.md`.\n- **Telegram Bot API parse_mode=Markdown returns HTTP 400 on story headlines** (June 2026): Headlines contain `+`, `%`, `$`, `_`, `*` characters that are unescaped Markdown control characters. Telegram's Markdown parser rejects the entire message. Fix: use `parse_mode=HTML` with HTML entity escaping (`&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`). Wrap headlines in `<b>` tags instead of `**`. See `references/cco-cdo-sprint7-8-pitfalls.md`.\n- **gcloud `--set-secrets` strips `:latest` suffix, preventing secret mounts** (June 2026): The tool layer redacts `:latest` from `gcloud run jobs update --set-secrets=ENV=secret:latest`, causing `"No secret version specified"` error and leaving the job with 0 secrets mounted. Workaround: export job YAML via `gcloud run jobs describe --format=yaml`, add the `env` block with `valueFrom: secretKeyRef: {name: secret-name, key: latest}`, then apply with `gcloud run jobs replace`. See `references/cco-cdo-sprint7-8-pitfalls.md`.\n- **`gcloud builds submit` does not accept `-f Dockerfile.alt`** (June 2026): The `-f` flag is rejected. Workaround: create a separate build directory containing only the alternate tag's Dockerfile renamed to `Dockerfile` plus its context files, then run `gcloud builds submit --tag IMAGE build_dir/`. See `references/cco-cdo-sprint7-8-pitfalls.md`.\n- **Local `import subprocess` shadows global import when placed inside `if` block** (June 2026): A redundant `import subprocess` inside a successful-path `if` block creates a local binding that shadows the top-level `import subprocess`. When the `if` block is skipped (e.g., pipeline failure path), `subprocess` is unbound in the failure handler, causing `cannot access local variable`. Fix: remove redundant imports inside conditional blocks — use the top-level import.\n- **db_to_json.py now auto-computes confidence when stuck at flat values** (June 2026): When a story's `confidence_pct` is 50, 65, or 75 (the old flat defaults), `db_to_json.py` now calls `compute_confidence()` from `generate_flows.py` dynamically. This means confidence diversity is maintained across ALL pipeline runs — no more manual backfills needed after each `db_to_json.py` execution. The computation uses: amount_b, pace_multiplier, positioning, contradiction_score, and source. If `compute_confidence` fails (import error, missing fields), it falls back to the existing value without crashing. To verify: check that stories.json has >5 unique confidence values after any pipeline run.: Stories stuck at flat 1.0 pace or 50% confidence can be backfilled without re-running the full pipeline. Pace: run `python3 scripts/backfill_pace.py` which derives pace from story content (horizon, urgency keywords, contradiction score, asset class). Confidence: import `compute_confidence` from `generate_flows.py` and iterate stories where `confidence_pct == 50` — it uses 5 factors (amount, pace, positioning, contradiction, source quality) to produce 25-100 range. Both scripts operate on `data/stories.json` directly. After backfill, deploy via `gsutil rsync` (not shipit) to avoid `db_to_json.py` overwriting the hand-edited data.

### Phase 11: Casino Floor → Salon Privé → Antique Cream (June 2026)
- **5 palette iterations in one session** — the user rejected teal-navy, polished chrome, casino-floor white/red/blue, and salon-privé dark/gold before settling on the current palette
- **Focus group mandated:** 3-persona audit revealed broken CSS, brassy gold, and missing visual hierarchy
- **Final palette:** Antique cream (#F5F1E8) page, pure white cards, antique gold (#C9A96E), vermilion (#C41E3A) stops, dark navy masthead (#1A2440)
- **THE ANCHOR redesigned:** BUY/SELL/WATCH pills, entry→target arrows, stop levels, conviction badges (HIGH/MED/LOW). 7 assets: SPX, NVDA, BRENT, DXY, GOLD, BTC, 10Y
- **Collapsed cards REMOVED:** Broken CSS syntax error made them non-functional. Restored default display (summary + play always visible, detail expandable on click)
- **Key learning:** UNILATERAL DESIGN CHANGES WITHOUT FOCUS GROUP VALIDATION CAUSE REGRESSIONS. Every palette/layout/typography change must be validated by 3+ personas before implementation.
- See `gazzetta-website/references/design-tokens.md` for current exact values

### Phase 12: Precision Hardening (June 2026 — v20.16–v20.17)
- **Computed confidence model:** Replaced all hardcoded "70% confidence" strings with 4-factor `computeConfidence()` — flow magnitude + pace + positioning + contradiction. Effective range ~60-95%. Aggregate displayed in hero as 5th stat.
- **ATR-based volatility-adjusted stops:** All 14 ANCHOR_ASSETS use `computeATRStop()` — entry ± (entry × ATR% × multiplier). Ranges: DXY 0.6%×3.0, BTC 2.5%×2.0, SOL 5.5%×2.0. Displayed as "Stop $X · N×ATR".
- **Track record system:** Daily localStorage snapshots with `settlePredictions()` loop. Resolves on target/stop cross or 7-day expiry. Displays win rate, total P&L, expectancy.
- **Methodology page:** `site/capital.html` — EPFR/Morningstar, formulas, limitations, disclaimer.
- **Professional review workflow established:** Any precision change MUST be audited by CFA + PM + Fintech personas through gambler's lens BEFORE deploy. Spawn as parallel `delegate_task` subagents. v20.16 audit found 4 bugs including critical settlement loop missing.
- **YouTube Shorts without transcripts:** Derive insight from title/comments/historical context. Don't get stuck on extraction — user sends Shorts for thesis connection, not verbatim content.
- **Capital Destination Analysis:** New dimension — track flow destination quality (vanity vs. productive investment signal). 1971 Persepolis celebration = canonical example ($200M+ imperial vanity while 50% illiteracy → revolution in 8 years).

## Design System — Current State (v20 — Pure White)

- **Palette:** Page #FFFFFF (pure white), Cards #FFFFFF, Gold #D4AF37, Ink #1A1D28, Divider #E5E7EB
- **Masthead:** pure white bg, gold name (#D4AF37) at 22px DM Serif Display, 2px gold bottom border
- **Headlines:** 20-22px DM Serif Display, dark ink on white cards
- **THE ANCHOR:** 14 assets (7 tradFi + 7 crypto) with BUY/SELL/WATCH pills, entry→target, **ATR-adjusted stops** displayed as "Stop $X · N×ATR", conviction badges
- **5 collapsible containers:** Flows → Anchor → Signal → Track Record → Stories
- **Hero:** 5 stats — Stories tracked, Capital tracked ($XB), Assets positioned, Total at stake ($XK), Model confidence (computed %)
- **Methodology page:** `site/capital.html` documents all formulas and data sources
- **Focus group rule:** ALL design changes require focus group validation BEFORE implementation
- **Professional review rule:** ALL precision/numerical changes require CFA+PM+Fintech audit BEFORE deploy

## Pipeline Architecture (Phase 4 — SQLite-backed)

Migrated from flat JSON to SQLite in June 2026. The database (`gazzetta.db`) is now the source of truth; `db_to_json.py` compiles static JSON for the JAMstack frontend. See `gazzetta-sqlite-pipeline` skill for full schema, scripts, and pitfalls.

Three ingestion paths feed gazzetta.db:
- **Telegram Monitor** → `intel_to_stories.py` (INSERT into stories table)
- **OSINT Collector** → `fetch_intel.py` (12 RSS feeds across 5 categories: central_bank, financial_news, geopolitical, asymmetry_blog, sovereign_yields, political_arbitrage → drafts table → `approve_draft.py` promotes to stories)
- **Manual drafts** → direct INSERT or `approve_draft.py`

Compilation: `db_to_json.py` queries SQL → writes `data/stories.json` + `data/flows.json`
Deploy: `shipit.sh` (7 stages: db_to_json → build_site → hash → GCS → verify → report → git)

Key cron jobs: `gazzetta-osint-collector` (fetch_intel, every 2h, no_agent), `gazzetta-continuous-capital-flows` (pipeline_chain.sh, 60m, no_agent), `gazzetta-deploy-to-gcs` (shipit.sh, 60m, no_agent).

## Infrastructure Tools (v22.28+, June 2026)

### Architect V2 — Modules 4 & 6 (June 2026)

Self-healing pipeline expansion. See `references/gcp-cloud-run-migration.md` (Architect V2 section) and `references/chief-architect-agent.md` (Architect V2 Expansion).

- **Module 4 (Auto-Revert):** `scripts/auto_revert.py` + `cloud_entrypoint.py` hook. Telegram alert on pipeline failure via Bot API token in Secret Manager. GCS sync blocked automatically.
- **Module 6 (Memory Synthesis):** `scripts/memory_synthesizer.py` runs as a separate Cloud Run Job daily at 02:00 UTC. Reads `pipeline-run-log.jsonl` from GCS, generates `DRAFT_SKILL_UPDATE.md`.

### Architect V2 — Executive Board Expansion: CCO, CDO & R&D Agents (June 2026)

Three Cloud Run agents deployed as downstream consumers of the pipeline. See `references/cco-cdo-sprint7-8-pitfalls.md` for deployment pitfalls and data schema notes. See `references/rd-agent-architecture.md` for the R&D agent.

- **CCO (Chief Content Officer):** `scripts/cco_entrypoint.py` → Cloud Run Job `cco-distributor` (every 30m). Reads stories.json from GCS, ranks by contradiction impact score (contradiction_score/100 * confidence_numeric/100), posts top 3 to Telegram @LaGazzettadiKyiv via Bot API (HTML parse mode). Draft scaffolding for Reddit, X.com, Newsletter saved to `cco_drafts/` in GCS. Idempotency via `cco_drafts/posted_stories.jsonl`. Image: `gazzetta-agents:latest`.
- **CDO (Chief Design Officer):** `scripts/cdo_audit.py` → Cloud Run Job `cdo-auditor` (every 2h). Opens live website via Playwright (headless Chromium), runs getComputedStyle() checks against DESIGN v26.1 tokens at 3 breakpoints (desktop 1280px, tablet 768px, mobile 400px). Verification Pyramid enforced: getComputedStyle primary, screenshot secondary. Reports saved to `cdo_audits/` in GCS. Image: `gazzetta-agents:latest`.
- **Dockerfile.agents:** Python 3.11-slim + Playwright + Chromium + google-cloud-storage. Built separately from pipeline to keep pipeline image lean. Build pattern: create a build directory with Dockerfile (standard name) + scripts, run `gcloud builds submit --tag IMAGE build_dir/`.
- **Secret mount workaround:** gcloud `--set-secrets` strips `:latest`. Use `gcloud run jobs describe --format=yaml`, add `secretKeyRef` block, `gcloud run jobs replace`.
- **Seven Cloud Schedulers active:** gazzetta-pipeline-cron (*/10), memory-synthesizer-cron (0 2 * * *), cco-distributor-cron (*/30), cdo-auditor-cron (0 */2 * * *), cco-newsletter-daily-cron (0 6 * * *), cco-newsletter-weekly-cron (0 6 * * 1), gazzetta-rd-sweep-weekly-cron (15 6 * * 1).

- **R&D Agent (Chief Research Officer):** `scripts/rd_entrypoint.py` → Cloud Run Job `gazzetta-rd-sweep-weekly` (Monday 06:15 UTC). 3-track research scope (Navigation UI, Capital Flow APIs, Distribution ROI). Phase 1: GitHub Issues only (read-only token). Phase 2: Draft PRs (Contents:write + Pull requests:write). Self-upgrading mechanism via research → recommendation → PR → C-Suite approval. Image: `gazzetta-rd-agent:latest`. Dockerfile: `Dockerfile.rd-agent` (python:3.11-slim + git + google-cloud-storage + google-cloud-secret-manager + httpx + beautifulsoup4). No Playwright/Chromium needed. Schedule offset 15 min from pipeline to avoid overlap. Research outputs saved to `gs://BUCKET/rd_research/<track>/<date>.json`. See `references/rd-agent-architecture.md`.

### shipit.sh — 7-Stage Deploy Pipeline
Root script (`bash shipit.sh`). Stages:
1. **intel_to_stories** — ingest latest Telegram intel → stories.json (.venv/bin/python)
2. **Local sync** — copy canonical HTML/CSS/JS from root → site/
3. **build_site** — sync data/ → site/data/ + generate API endpoints
4. **build_hashed_assets** — SHA256-hash CSS/JS, rewrite HTML references, write manifest
5. **GCS deploy** — gsutil rsync + cache-policy setmeta (immutable hashed, 0s HTML, no-store JSON)
6. **Live verification** — curl headers from lagazzettadikyiv.com
7. **Deploy report** — generate site/deploy_report.txt (timestamp, commit, story count, ETag) → upload to GCS
8. **Git sync** — add → commit → push to origin/main

All Python steps use `.venv/bin/python`. Config paths from `config.yaml`.

### Semantic Triangulation Engine (v2.0, June 2026)
Major architecture upgrade: loosely-coupled JSON silos → unified semantic graph. Every entity declares bidirectional links. See `gazzetta-website` skill for full architecture, schema contract, entity extraction maps, time-decay model, multi-persona blocks, and pre-deploy enhancements.

### UX v2.0 Additions (June 2026)
- **Categorized capital flows**: Flows teaser aggregates into 3 categories (Sovereign, Systemic Liquidity, Speculative) defined in `config.yaml`. Each card shows net direction, velocity, flow count. Links to `flow-nodes.html`.
- **Hero hook indicators**: Three dynamic indicators (contradictions, top velocity, freshness) in hero section. Populated by `updateHeroIndicators()` from flows data.
- **Services utility grid**: Persona-driven value-prop cards (C-Suite → stories, Quant → flow-nodes, Trader → trades) below teaser containers.
- **Escape-drift workaround**: When `patch()` fails on JS files with "Escape-drift detected", use `execute_code` to call `hermes_tools.patch()` directly. Recipe in `gazzetta-website/references/escape-drift-patch-workaround.md`.
Run at session start and after any significant change. Exit code 1 = drift detected.
- **§0 Tasks**: Count open/closed items from tasks.md
- **§1 Git**: branch, commit, behind/ahead vs origin/main
- **§2 Data**: story count, last_updated, newest story timestamp, flow count (in/out)
- **§3 Live**: HEAD request to lagazzettadikyiv.com — status, Last-Modified, ETag, Cache-Control
- **§4 Drift**: Compare local vs live timestamps (>5min = drift), check build-manifest age (>60min = stale)
- **§4.5 Pre-deploy**: Check working tree cleanliness, verify critical HTML elements exist in site/ (hero section, product-nav, containers, onboarding). If elements missing → exit 1, block deploy.
- **§5 Truth**: Summary line — git, stories, flows, live status, drift status

### safe_git.py — Pre-Commit Auto-Backup
Call before destructive git operations (checkout, reset, revert). Detects uncommitted changes → auto-copies all modified files to `.backup/<timestamp>/`. `.backup/` is gitignored.

### config.yaml — Central Configuration
Single source of truth for: site metadata, paths, data_files (13 entries), pages (21 entries), assets (6 entries), GCS settings, cache policies, feature flags. Scripts import dynamically via `yaml.safe_load()`.

### Regression Recovery Pattern
When features disappear after a branch switch:
1. `git diff main..<safety-branch> --stat` to identify missing files
2. `git checkout <safety-branch> -- <files>` to restore from safety branch
3. Update `config.yaml` and `shipit.sh` with any new pages/assets
4. Run `refresh_context.py` → verify pre-deploy check passes → `shipit.sh`
- **collect_multisource.py** — Pulls RSS, Reddit, and future API sources from `data/config/data_sources_v2.json` (38 sources across 7 categories)
- **analyze_narratives_v2.py (v2.2)** — Paradigm-lens tagging via keyword matching across 5 pillars. Every setup gets `paradigm_pillar` + `paradigm_label`. NO taxonomy language — claim templates per pillar, concrete contradictions, actor-anchored invalidation triggers
- **pipeline_audit.py (v2.2)** — Checks: artifact freshness, source diversity (active/configured ratio), paradigm coverage (flags uncovered pillars), anti-template sweep (scans stories.json for banned phrases)
- **Data contracts:** `article_contract_v1.json` defines required fields, optional fields (paradigm_implications, confidence, invalidation_trigger, capital_flow_implication, asset_claim, image_url), and banned phrases
- **Source registry:** `data_sources_v2.json` with `paradigm_relevance` scoring (0–1) per source category
- Reddit API credentials (all 5 `REDDIT_*` vars) are MISSING from `.env` — `r/LaGazzettadiKyiv` cannot be managed until configured

## Delegation Configuration (Critical)
- Config is at `delegation.*` in `~/.hermes/config.yaml`
- **Capability maximization directive (June 2026):** All models → deepseek-v4-pro (primary, subagents, cron). reasoning_effort=high. Capability > cost efficiency. Skills: `hermes-capability-maximization`, `agent-cooperation-network`.
- Provider: deepseek, Model: deepseek-v4-pro, reasoning_effort: high
- `max_concurrent_children: 3`, `max_spawn_depth: 1`, `child_timeout_seconds: 600`
- Cron jobs also use v4-pro. All gazzetta cron jobs migrated from v4-flash.

## Vision Configuration (June 2026)
- Configured via `auxiliary.vision` in `config.yaml`
- Provider: openai (GitHub Models API uses OpenAI-compatible endpoint)
- Base URL: `https://models.inference.ai.azure.com`
- Model: `gpt-4o-mini`
- Key: GitHub classic PAT (`gho_...`) stored in config.yaml `auxiliary.vision.api_key`
- **Known limitation:** gpt-4o-mini via GitHub Models refuses to analyze screenshots containing desktop UI with other apps visible (content policy). Works for direct image URLs and base64-encoded standalone images. For website screenshots, use a dedicated browser window with only the target site visible, or use `vision_analyze` tool with direct image URLs.
- Setup command: `hermes config set auxiliary.vision.{provider,base_url,model,api_key} value`
