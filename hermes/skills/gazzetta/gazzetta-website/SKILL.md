---
name: gazzetta-website
description: Design and build the Gazzetta di Kyiv website — v33.0 white metallic (#FFFFFF body, white glass panels), Playfair+Inter typography, DarkGoldenrod (#B8860B) gold accents, crimson BREAKING, 12-narrative taxonomy, GAP Leaderboard.
version: 31.1.0
author: Hermes Agent
created_by: agent
---

# Gazzetta di Kyiv — Website Design (v30.0)

## Core Design Principles

1. **Pure White Everywhere** — Body: #FFFFFF. Cards: #FFFFFF. Masthead: #FFFFFF. Containers: #FFFFFF. Everything white. Differentiate containers via thin 1px #E5E7EB borders and subtle box-shadow (0 2px 12px rgba(0,0,0,0.06)). Card hover shifts to #F9FAFB. The user INSISTS on pure white — DO NOT use #F8FAFE or any off-white tint anywhere.
2. **VISIBLE Golden Accents** — Gold (#D4AF37) must be prominent: 2px gold border-bottom on masthead, gold-tinted card borders with 2px gold left edge on every card, gold hover shadows. NOT "invisible" or subtle. The user will ask "where are the golden linings" if gold is not immediately visible.
3. **Masthead: Symbols Flank Name** — Machiavelli Fox&Lion (LEFT, 20x40 SVG, gold #D4AF37). Crossed bulavas (RIGHT, 28x38 SVG, two maces +-42deg, gold). Name #8B0000 22px Playfair. CSS: .masthead-machiavelli, .masthead-bulavas. Template: templates/header.html.
4. **Constellation Layout** — 2-column staggered CSS grid with φ-spacing (1.618). Lead story spans full width. Non-lead cards stagger vertically. Single column, max-width 1000px. No sidebar. No empty spacer. Mobile: collapses to single column.
5. **Shimmering Tyrian Purple Masthead Name** — Masthead name uses **Playfair Display** (v22.9+), a Bodoni-inspired
4. **Caduceus Emblem (v22.7+)** — The right-side masthead emblem is a **Caduceus of Mercury** — the winged staff with intertwined serpents, universal symbol of commerce, trade, and information flow. It replaces the Machiavelli fox (v22.9–22.5) and the balance scale (v22.6, brief intermediate). The Caduceus directly represents the business: commerce (capital) + movement (flow) + messaging (intelligence) — all three components of "capital flow intelligence." Rendered in gold (#D4AF37) with 1.8px staff, 1.3px wings, 1.2px serpents, and subtle head circles (opacity 0.5). Class: `.masthead-caduceus`. Sizing: 28×40px CSS (28×40 viewBox), ~65% of name cap height. Pairs heraldically with crossed bulavas (both staff-form, gold). Mobile: 14×22px @ 600px, 12×18px @ 400px. **Never revert** to `.masthead-fox` (Machiavelli) or `.masthead-balance` — the Caduceus is locked after a 3-persona focus group validated it as the only symbol conveying commerce + flow + intelligence simultaneously.
5. **User-Benefit Container Names** — Container headers use one-sentence user-oriented descriptions, not structural labels. Each container has a descriptive sentence visible when collapsed, hidden when expanded.
6. **Lucide-Standard SVG Icons Only** — All UI icons must come from Lucide (lucide.dev). Spec: 24×24 viewBox, stroke-width 2px, stroke-linecap="round", fill="none", stroke="currentColor". Never use emoji, Unicode characters, or custom hand-drawn geometry. **Exception:** The Caduceus and bulava SVGs are custom heraldic emblems, not UI icons — they live outside the Lucide rule.
7. **Capital Hint System (v22.9+)** — Two micro-indicators visible in collapsed card/flow views, based on information scent theory (Pirolli & Card):
   - **`.cf-hint`** on story cards: a tiny chip next to the headline showing `$3.2B ↓ tech` (red) or `$1.0B ↑ defense` (green). 9px, 700 weight, opacity 0.65. Shows capital direction + magnitude + **sector** at a glance — no need to hover. The sector suffix (`cf.asset_class`) was added in v22.12 so users see WHAT is flowing WHERE in the collapsed card view. JS in `cfHint` generation in `livingCardHTML()`.
   - **`.flow-linked-story-hint`** on flow items: a `↳` icon (10px, opacity 0.4, ink-muted) next to the chevron, hinting that this flow links to a story.
   Both are frameless — color, opacity, and typography only. No backgrounds, no borders, no shadows. They tease what's inside without spoiling the payload.
8. **Conventional Share Row** — Each expanded card shows a row of 5 visible icon buttons: Copy link, X, Facebook, Telegram, Reddit. 28×28px each, inline-flex, `border: 1px solid #E5E7EB`, hover fills `var(--ink)` with white icon. No dropdown, no toggle. Buttons appear only in expanded view. This replaces the v20.17 single-share-dropdown (Bloomberg/FT pattern) — the user directed conventional visible buttons for broader distribution.

This skill governs the visual identity and structural design of the Gazzetta di Kyiv website (pureciclismo.github.io/gazzetta-di-kyiv). The site is a contradiction-first narrative intelligence engine. Every design decision serves the mission: deliver thesis-driven narrative intelligence through the gap between consensus and reality.

## Story Card Structure (v20.20)

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| Masthead name | Playfair Display | var(--φ-lg) | 400 | Shimmering gradient (see references/shimmering-masthead.md) + 0.4px rgba(245,215,110,0.45) stroke |
| Masthead tagline | Source Serif 4 | 12px | italic | var(--ink-light) |
| Masthead meta (time/date) | Inter | **13px** | **500** | var(--ink-light) |
| Container title | Inter | 11px | 700 uppercase | var(--ink) |
| Story headline (h3) | Playfair Display | 20px | 400 | var(--ink) |
| Lead story headline | Playfair Display | 22px | 400 | var(--ink) |
| Capital flow claim (first line) | Source Serif 4 | 12px | 600 | var(--ink) |
| Story summary | Source Serif 4 | 12px | 400 | var(--ink-light) |
| Category tag | Inter | 8px | 700 uppercase | var(--gold) |
| They say / Reality | Source Serif 4 | 11px | — | — |
| THE PLAY label | Inter | 8px | 700 uppercase | var(--gold) |
| THE PLAY text | Source Serif 4 | 11px | italic | var(--ink-light) |
| Story date (`<time>`) | Inter | 9px | 400 uppercase | var(--ink-muted) |
| Anchor symbol | Inter | 11px | 700 | var(--ink) |
| Anchor pill (BUY/SELL/WATCH) | Inter | 9px | 600 | — |
| Anchor conviction badge | Inter | 7px | 700 uppercase | — |

### Contradiction Tier Badge (v22.10+)

The raw "Tension 50" number was killed by a retail-user focus group (3/3 personas found it incomprehensible). Replaced with a self-explanatory **tier badge** — no hover required, works on mobile:

| Tier | Score | Color | Label | Meaning |
|------|-------|-------|-------|---------|
| `.tier-badge.contradicted` | 67-100 | Red (#DC2626) | **CONTRADICTED** | Narrative actively inverts reality — high-conviction trade signal |
| `.tier-badge.divergent` | 34-66 | Amber (#B45309) | **DIVERGENT** | Material gap between narrative and reality — potential opportunity |
| `.tier-badge.aligned` | 0-33 | Muted gray | **ALIGNED** | Narrative and reality roughly agree — lower trading edge |

CSS: 7.5px uppercase, 700 weight, letter-spacing 0.06em, thin 1px border, subtle background. The score number is shown inside a `.tier-score` span at 0.5 opacity — context, not the primary signal. The word IS the explanation. Old `.contradiction-score` class and `::before { content: "Tension " }` pseudoelement are removed. Never reinstate raw tension numbers — the focus group was unanimous.

The JS is in `livingCardHTML()` and `updateStoryCard()`:
```
const cs = calcContradictionScore(story);
const tier = cs >= 67 ? 'contradicted' : cs >= 34 ? 'divergent' : 'aligned';
// → <span class="tier-badge ${tier}">CONTRADICTED <span class="tier-score">72</span></span>
```

## Page Structure (v23.5 — Three-Column Golden Ratio Grid)

The homepage now uses a 3-column CSS Grid layout based on φ = 1.618: **21% ALPHA sidebar | 61% INTEL main thread | 18% CONTEXT/META sidebar**. Full specification in `references/three-column-golden-ratio-grid.md`.

```
┌──────────────────────────────────────────┐
│  La Gazzetta di Kyiv                     │
│  Capital moves markets. We track it.     │
│  [INTEL Stories Flows Horizon Nodes]     │  ← Grouped nav with .nav-group-label
│  [ALPHA Signal Trades Track]             │
├──────────────────────────────────────────┤
│  HERO: The stories that move markets —   │
│  before they move prices.                │
│  [5 Contradictions] [2.4× Velocity] [age]│  ← JS-populated hero hook indicators
├──────────────────────────────────────────┤
│  ── INTEL ──                             │  ← Black badge (#111827), white text
│  What's happening — and where the money  │
│  is actually going.                      │
│  ▸ Stories (expanded default)            │
│  ▸ Capital Flows (collapsed)             │
├──────────────────────────────────────────┤
│  ── ALPHA ──                             │  ← Gold badge (#C8A44E), white text
│  Strategic positioning derived from      │
│  the intel — where to act.               │
│  ▸ Trade Ideas (collapsed)               │
│  ▸ The Signal (collapsed)                │
│  ▸ Track Record (collapsed)              │
└──────────────────────────────────────────┘
```

**Layer CSS classes:** `.layer-header` (flex, align-items:baseline, gap:12px, 1px divider border-top). `.layer-label` (sans-serif, 11px, 800 weight, 0.14em letter-spacing, uppercase, 2px 8px padding). `.intel-header .layer-label` = black bg, white text. `.alpha-header .layer-label` = gold bg, white text. `.layer-desc` (serif, 13px, italic, ink-muted).

**Navigation groups:** `.nav-group-label` spans (8px, 700 weight, 0.12em letter-spacing, uppercase, muted). First group label gets `margin-left: 6px`. Nav links: Stories, Flows, Horizon, Nodes (INTEL) · Signal, Trades, Track (ALPHA).

**Five containers (all collapsed by default except Stories):**
1. **Stories** — INTEL layer. Expanded by default. Story cards with timestamps, They Say/Reality, THE PLAY. Share row.
2. **Capital Flows** — INTEL layer. Collapsed. Flow items with $XB amounts, velocity, confidence.
3. **Trade Ideas** — ALPHA layer. Collapsed. 14 assets with entry/target/stop, conviction.
4. **The Signal** — ALPHA layer. Collapsed. Triangulation scores from stories×flows×trades.
5. **Track Record** — ALPHA layer. Collapsed. Settled bet P&L, win rate.

```
┌──────────────────────────────────────────┐
│  La Gazzetta di Kyiv                     │  ← .masthead (Tyrian purple + gold stroke)
│  Capital moves markets. We track where   │
│  it's going.          [Updated: date]    │  ← 13px meta, right-aligned
├──────────────────────────────────────────┤
│  HERO: The stories that move markets —   │  ← Compressed hero (16px pad, 20px H1)
│  before they move prices.                │
│  [Read today's stories] [Telegram] [Reddit]
│  [N Stories] [$XB tracked] [14 assets]   │
│  [$XK track record] [Confidence]           │
├──────────────────────────────────────────┤
│  ▸ What the capital is saying            │  ← Container 1: STORIES (front door)
│    Today's narratives, decoded.          │
├──────────────────────────────────────────┤
│  ▸ Where the smart money is going        │  ← Container 2: FLOWS (data behind stories)
│    Institutional flow data with velocity.│
├──────────────────────────────────────────┤
│  ▸ Your trades this week                 │  ← Container 3: ANCHOR
│    14 assets · entry/target/stop         │
├──────────────────────────────────────────┤
│  ▸ The Signal · Flow × Bet × Event       │  ← Container 4: TRIANGULATION
│    Cross-container synthesis             │
├──────────────────────────────────────────┤
│  ▸ Track Record · Verifiable bets        │  ← Container 5: TRACK RECORD
│    Win rate · P&L · expectancy           │
└──────────────────────────────────────────┘
```

**Five containers (all collapsed by default, v20.20 order):**
1. **What the capital is saying** — Story cards with timestamps, capital flow claims, They Say/Reality contradiction, THE PLAY trade idea. Conventional share row (5 buttons). Stories are the FRONT DOOR — narratives first, data second.
2. **Where the smart money is going** — 7+ flow items with computed confidence, $ amounts, projections, institutional positioning (dynamic, polled every 5 min from flows.json).
3. **Your trades this week · Bet & Benefit** — PDR gauge + 14 asset rows (7 tradFi + 7 crypto) with BUY/SELL/WATCH pills, entry→target, ATR-based volatility-adjusted stops, conviction badges.
4. **The Signal · Flow × Bet × Event** — Triangulation scores (0-100) cross-referencing Stories (C1), Flows (C2), and ANCHOR (C3). Synthesis layer.
5. **Track Record** — Daily prediction snapshots with settlement logic.

**Hero section (v22.15+):** Compressed (16px padding, was 24px). Headline: "The stories that move markets — before they move prices." Subtitle: descriptive benefit statement. Five stats: Stories, Capital tracked, Assets positioned, Track record, **Confidence** (shows percentage + ↑ bullish / ↓ bearish direction arrow, color-coded green/red). Simple — one number, one meaning. The tier badge system (HIGH/MEDIUM/LOW) was removed in v22.15 after feedback that "82% ↑ HIGH" was redundant and confusing for regular users. CSS in `#heroConfidence` — green for bullish, red for bearish. JS in `updateHeroConfidence()` uses `el.innerHTML = pct + '%' + arrow`.

**Layout:** Single column, max-width 1000px. No sidebar. No empty spacer.

## Story Card Structure (Expanded)

Each card, in order:
1. **Capital flow claim** (bold, first visible line): "$X.XB flowing into/out of [asset] this week — projected +$Y.YB change at 70% confidence"
2. **Category tag** + update badge + time-ago
3. **Headline** (Playfair Display, 20-22px)
4. **Summary** (reality text displayed on expand)
5. **THEY SAY / REALITY** (two-line contradiction, revealed on expand)
6. **CAPITAL FLOW block** (3 lines: claim, projected, institutional positioning)
7. **THE PLAY** (actionable trade: ticker, direction, stop, target)
8. **Photo** (80×56px, right-aligned, loading="lazy")
9. **Evolution timeline** (lazy-loaded on click, hidden by default)

## Data Flow

- `site/data/flows.json` — Capital flow data with sentiment meter (inflow/outflow ratio + contextual scale). Generated by `scripts/db_to_json.py` (reads DB flows table, NOT generate_flows.py). Cron: `51c1bb776729` every 60min runs `scripts/generate_flows.py`.
- `site/data/stories.json` — Story data from editorial pipeline + intel_to_stories. Every story now has `generated_at` and `capital_flow` regardless of pipeline source (v23.0 enrichment stage). **v23.12:** Every `capital_flow` dict now carries `source_label` (`[LIVE-DATA]` for telegram_intel sources, `[CALC-EST]` for editorial/estimated flows). Injected by `db_to_json.py` via permanent source-check logic (not post-hoc patch — survives regeneration).
- `site/api/v1/signal.json` — Triangulation signals (35 entries, aggregate score). Generated by `scripts/generate_signal_api.py` in shipit.sh Stage 1.5.
- `site/api/v1/trades.json` — Anchor trade positions (13 tradFi + crypto). Generated by `scripts/generate_trades_api.py` in shipit.sh Stage 1.5.
- JS bootstrap order (v22.8): collapsible containers → render anchor → render track record → **fetchFlows()** (loads flows.json, renders flows + glossary + hero confidence) → start flows polling → fetch stories.json → render story cards → render triangulation → start stories polling → update cumulative stats.
- Methodology: `site/capital.html` — EPFR/Morningstar sources, confidence formulas, ATR stop derivation, triangulation, limitations, disclaimer.
- Share functions: `copyShareLink(card)`, `shareToX(card)`, `shareToFacebook(card)`, `shareToTelegram(card)`, `shareToReddit(card)` — each opens platform share dialog. No more `wireShareControls()` or dropdown menus.

## Deployment (v22.24+): GCS + Three-Tier Cache + Content Hashing

The site is deployed via GCS bucket with a three-tier cache architecture. Content-hashed assets (styles.3412707c.css) enable immutable 1-year caching. Query string cache busting (?v=22.22) is fully eliminated.

| Component | Detail |
|-----------|--------|
| **Primary domain** | `www.lagazzettadikyiv.com` |
| **Bucket** | `gs://www.lagazzettadikyiv.com` (Google Cloud Storage, static website) |
| **CDN** | GCP Cloud CDN (Load Balancer fronting the bucket) |
| **Deploy script** | `shipit.sh` — canonical deploy (7-stage pipeline: intel → sync → build → hash → deploy → verify → report + git push) |
| **Deploy cron** | `f9a24ed64aa5` (every 60min, script-only) — runs `shipit.sh` via `gazzetta_deploy_to_gcs.sh` wrapper. Was every 15min raw gsutil rsync — upgraded June 2026 after the cron was found overwriting manual deployments. |
| **Lifecycle** | Auto-delete objects untouched for 30 days (prevents hashed asset bloat) |

**Three-tier cache:**
```
TIER 1 (hashed CSS/JS):  Cache-Control: public, max-age=31536000, immutable
TIER 2 (HTML pages):     Cache-Control: public, max-age=0, must-revalidate
TIER 3 (JSON data):      Cache-Control: private, no-store (+ ?t=Date.now() on fetch)
```

**Deploy workflow (v22.24+, updated v22.42 — shipit.sh is canonical):**
```bash
# Single-command deploy (replaces ALL old workflows):
bash shipit.sh
```
`shipit.sh` runs the full 7-stage pipeline: intel_to_stories → local sync (root→site/) → build_site → build_hashed_assets → GCS deploy + setmeta per cache tier → live verification (curl headers) → generate deploy_report.txt + sync to GCS → git push. All Python execution uses `.venv/bin/python`.

**Configuration (v22.42+):** Central `config.yaml` at project root — site metadata, paths, data files, assets, pages, GCS deployment, cache policies, and feature flags. Scripts (`intel_to_stories.py`, eventually all) import dynamically via PyYAML. No more hardcoded paths scattered across scripts.

**Project tracking (v22.42+):** `tasks.md` at project root contains structured checklist of active development goals across 4 phases (Infrastructure, Configuration Decoupling, Script Modernization, Automated Deployment Reports). `refresh_context.py` §0 displays open/completed task counts at session start.

**Deploy report (v22.42+):** `deploy_report.txt` generated on every deploy and synced to GCS. Live at `https://www.lagazzettadikyiv.com/deploy_report.txt`. Contains: UTC timestamp, git commit hash, live story count, ETag, Last-Modified header, deploy status.

Full architecture reference: `gazzetta-interpret-review-execute` → `references/three-tier-cache-architecture.md`
The old GitHub Pages deployment (`pureciclismo.github.io/gazzetta-di-kyiv`) still exists but is NOT the canonical URL. Do not deploy to GitHub Pages unless explicitly asked.

## Mobile Responsive Design (v22.17+)

Mobile breakpoint: 600px. Key fixes applied June 2026 after focus group found 4/10 UX:
- Hierarchical disclosure: collapsed containers + subtle expand previews
- Font floor: 12px minimum. No 10px elements on mobile.
- Touch targets: 44px minimum per Apple HIG.
- No horizontal overflow: overflow-x:hidden on body.
- Full mobile overhaul v22.30: see `references/mobile-css-overhaul-v22.30.md`

- **Overflow prevention**: `html, body { overflow-x: hidden; max-width: 100vw }` + all major containers constrained to viewport width
- **Single-column cards**: `.card-head { flex-direction: column }` at mobile
- **Collapsible containers**: `.container-body { overflow: hidden; max-height: 0 }` — actually hides content (was `overflow: visible` pre-v22.17)
- **Font floor**: Tags/severities 10px, claims 11px, headlines 16px, body 13px, hero labels 9px, hero values 15px
- **Touch targets**: Share buttons 38×38px, container headers 42px, lang switches 32×28px, hero CTA 40px
- Desktop-only: `max-width: 1000px` single column; no sidebar

Known issue: Card elements rendered by JS with inline styles may resist CSS override. The `max-width: 100vw` sledgehammer on all containers is the nuclear option.

**Traditional finance (7):** SPX, NVDA, BRENT, DXY, GOLD, BTC, 10Y
**Crypto (7):** ETH, SOL, XRP, BNB, ADA, DOGE

Each with: price, change, BUY/SELL/WATCH pill, entry→target range, **ATR-based volatility-adjusted stop** (computed as `entry ± entry × ATR% × multiplier`, displayed as "Stop $X · N×ATR"), conviction badge (HIGH/MED/LOW).

ATR percentages are approximate 14-day values: NVDA 3.5%, SPX 1.2%, DOGE 6.5%, DXY 0.6%. Multipliers range 2.0-3.0× depending on volatility regime. WATCH assets get no stop (returns null).

Plus: Stablecoin Supply ($172B), Exchange Netflow (-$890M 7d outflow), Aggregate Funding Rate (-0.01%), PDR gauge.

## Computed Confidence Model (v20.16+)

The "70% confidence" string was replaced with a 4-factor model:
```
confidence = min(50 + flow_magnitude + pace + positioning + contradiction, 95)
```
- Flow magnitude: $5B+ = +15, $3-5B = +12, $1-3B = +8
- Pace: 3×+ = +12, 2-3× = +10, 1.5-2× = +7
- Positioning: accumulating = +10, distributing = +8, hedging = +5
- Contradiction: score ≥70 = +8, 50-69 = +5

Effective range ~60-95%. Aggregate confidence displayed in hero as 5th stat.

## Track Record System (v20.16+)

- Daily snapshots of all 14 ANCHOR_ASSETS to localStorage
- `settlePredictions()` resolves bets when current price crosses target/stop or >7 days old
- Displays: win rate, total P&L%, expectancy, avg win/loss
- Methodology and limitations documented at `site/capital.html`

## i18n Translation — Dynamic DOM Pitfall (v22.18 fix)

**Critical bug:** `applyTranslations()` runs once at page load via `i18n.init()`. But story cards, flow items, anchor positions, and signal verdicts are **dynamically inserted after init** — those elements' `data-i18n` attributes are NEVER processed. This is the root cause of "translations broken" on dynamically rendered content.

**Fix (one line):** Call `window.i18n.applyTranslations()` after every major DOM render cycle:
- After `appendStoryCard()` loop in boot() — both living stories and stories.json paths
- After `renderCapitalFlows()` in `fetchFlows()`
- After any `.innerHTML` assignment that includes `data-i18n` attributes

Pattern: `if (window.i18n && window.i18n.applyTranslations) window.i18n.applyTranslations();`

## Product Page Architecture (v22.18+)

Site decomposed from single-page (5 collapsible containers) into product pages + hints lobby:

| URL | Product | Container | Data Source |
|-----|---------|-----------|-------------|
| `/` | Hints Lobby | 5 teaser cards | `/api/v1/home/summary.json` |
| `/stories.html` | Stories | Full newsCol | `stories.json` / `stories_ru.json` |
| `/flows.html` | Flows | Full flowsList | `flows.json` / `flows_ru.json` |
| `/trades.html` | Trades | Full anchorGrid | `asset_claims_latest.json` |
| `/signal.html` | Signal | Full signalGrid | `intelligence_objects.json` + live triangulation |
| `/track.html` | Track Record | Full trackRecord | `publish_manifest.json` |

Each product page shares: masthead + product nav + i18n.js + app.js + styles.css + footer.
Front page is now a **hints lobby** — 5 cards with live stats, each linking to its product page. No inline content.
Product nav CSS: `.product-nav` with gold underline on active page.

The site supports English (default) and Russian via a lightweight i18n system. The pattern has three layers:

### Layer 1: Static HTML text
Elements with `data-i18n="key"` attributes are translated by `i18n.js` on page load. The `i18n_ru.json` file contains **122 translation keys** (v22.15). Language preference is stored in `localStorage` (`gazzetta_lang`).

### Layer 2: Dynamic content (stories, flows)
`app.js` loads language-specific data files: `stories.json` (EN) or `stories_ru.json` (RU). The `getDataPath()` and `getFlowsPath()` functions append `_ru` suffix when `i18n.lang === 'ru'`. Russian data files are generated by `scripts/translate_content.py` in the pipeline chain using the DeepSeek API, **batched in chunks of 20** to avoid response truncation (124 texts overflowed a single API call). Falls back to English copy if API key unavailable.

**DeepSeek API key location:** Not in `~/.hermes/.env`. Available via the `custom_providers` Hermes env var: `json.loads(os.environ['custom_providers'])[1]['api_key']` (the entry with `'deepseek'` in `name`).

### Layer 3: Inline labels in app.js
All hardcoded English strings in app.js use `i18n.t('key', 'English fallback')`. Labels covered: CAPITAL FLOW, THE PLAY, tension tiers (MAX/HIGH TENSION, BUILDING, CONSENSUS), share button titles, flow inflows/outflows, "stories" count, "Projected further flow", confidence/pacing text, They Say/Reality, EXTREMUM/WINNER/LOSER/IDIOT/GENIUS, severity (CRITICAL/HIGH/ELEVATED), triangulation verdicts (MAX/HIGH CONVICTION, MODERATE, WATCH), time labels (just now, m ago, h ago, d ago, Today), loading messages, Linked story/Position bet. The `i18n_ru.json` file must include ALL keys used by app.js — missing keys show English fallback.

### Race condition (v20.25 — partially resolved)
app.js renders before `i18n.init()` completes fetching translations from the network. On first page load after language switch, inline labels may briefly show English before `i18n.t()` resolves. The `i18nReady` event + `waitForI18n()` pattern exists in local code but the deployed `i18n.js` lacks it. Acceptable tradeoff — labels resolve on next render cycle. Full fix: deploy updated `i18n.js` with `_ready` flag and `i18nReady` event, then add `await waitForI18n()` to app.js bootstrap.

### Runtime crash: `extremum` field format change (v20.27)
**The `extremum` field in newer stories is an OBJECT (`{type, description}`), not a pipe-delimited string.** The `extremumLineHTML()` function calls `.split('|')` on it — this crashes boot() with `TypeError: extremumStr.split is not a function`, silently preventing ALL story cards from rendering. No console error text, just 5 empty `exception` entries. Fix (v20.27): add `typeof extremumStr === 'object'` guard at the top of `extremumLineHTML()` that renders objects as `TYPE: description.slice(0,120)`. Check with `python3 -c "import json; d=json.load(open('site/data/stories.json')); print([type(s.get('extremum')).__name__ for s in d['stories']])"` — if any return `dict`, the guard is needed.

### Data Pipeline Truncation (v22.15 fix)

**Root cause:** Two truncation points in the pipeline cut text at hard character limits with no word-boundary awareness:

1. `intel_to_stories.py` line 76: `projected = (benefit_text or event_text)[:200]` — projected text cut mid-word
2. `generate_flows.py` line 199: `headline = claim[:120]` — headlines cut at 120 chars mid-word
3. Stories' `capital_flow.claim` and `capital_flow.projected` fields inherit truncation from source data

The 7 mid-word cuts Mike Green found on June 6, 2026 (ort, blo, dron, go, st, bon, ho) all trace to these two lines.

**Fixes applied (v22.15):**
- `intel_to_stories.py`: word-boundary truncation — find last space before 200 chars, append `…` if truncated
- `generate_flows.py`: same word-boundary logic for headlines at 120 chars; safety net for pre-existing truncated projected fields (find last period/comma > 100 chars and trim)

### i18n Build-Time Validation (v22.15+)

**Script:** `scripts/validate_i18n.py` — extracts all `data-i18n` keys from HTML + `i18n.t()` keys from JS, diffs against locale JSONs, fails (exit 1) if coverage < 100%.

Run as `GAZZETTA_ROOT=/path python3 scripts/validate_i18n.py`. Wire into every deploy pipeline.
See `references/i18n-ci-validation.md` for full integration spec.

### i18n.t() at definition time vs render time — critical pitfall (v22.15+)

Calling `i18n.t()` inside a `const` or top-level variable declaration evaluates the translation ONCE at script parse time. If the user switches language later, the const's value is STALE — it still shows the old language. This is invisible in English mode but silently breaks Russian.

**Wrong pattern (killed in v22.15):**
```js
const LABELS = {
  buy: i18n.t('buy', 'BUY'), // Evaluated once — never updates on lang switch
};
```

**Right pattern: store keys, translate at render time:**
```js
const POSITION_VARIANTS = {
  'accumulating': [
    { key: 'pos_accumulating_1', fallback: 'Institutions buying — net inflow' },
  ]
};
function positionLabel(positioning) {
  const v = variants[idx];
  return i18n.t(v.key, v.fallback); // Evaluated every render → always current
}
```

For getter properties that need live translation:
```js
ANCHOR_PDR = { get regimeLabel() { return i18n.t('pdr_regime_passive','Passive Discovery'); } };
```

This poisoned POSITION_VARIANTS, ANCHOR_PDR.regimeLabel, and anchor card pill/badge labels until v22.15 — all showed English in Russian mode because `i18n.t()` ran once at definition time.

### Template literal bug: `' + i18n.t(...) + '` inside backticks
When converting hardcoded strings to `i18n.t()` calls, NEVER use `' + i18n.t('key','fallback') + '` inside a backtick template literal — it breaks JS syntax (mismatched quotes inside `${}` template expressions). Always use `${i18n.t('key','fallback')}` inside backticks. Example: `<div>Loading evolution timeline...</div>` inside a template literal must become `<div>${i18n.t('loading_timeline','Loading evolution timeline...')}</div>`, NOT `<div>' + i18n.t(...) + '</div>`. This bug is silent in `node --check` (the `+` is syntactically valid outside template literals) but causes runtime syntax errors that prevent boot(). Use Python scripts via terminal for bulk string replacements — the patch tool struggles with escape-heavy JS.

### CDN caching gotcha (critical — v20.25 fix)
The `index.html` hardcodes `<script src="./app.js?v=20.XX">`. **Every deploy MUST bump this version number** or browsers serve the old cached `app.js` — which means no inline label translations, no new i18n keys, no cache-busting `getJSON()`. Check current version: `grep 'app.js?v=' site/index.html`. GCS now uses `max-age=0, must-revalidate` for HTML/JS/CSS, but the `?v=` parameter is still needed to break browser cache on repeat visitors. For data files (`stories_ru.json`, `flows_ru.json`), `getJSON()` appends `?t=Date.now()` to bypass CDN.

### Dual-domain verification
- `pureciclismo.github.io/gazzetta-di-kyiv` — GitHub Pages, deploys within 60s of git push. **Verify here first** to confirm commits are good.
- `www.lagazzettadikyiv.com` — GCS bucket behind HTTPS LB, the canonical domain. **Verify second** — CDN lag up to 1h for data files (max-age=3600), though HTML/JS/CSS are instant (max-age=0).
- If GitHub Pages has a feature but the custom domain doesn't → GCS deploy needed, not a code problem.

### Pipeline integration
`translate_content.py` runs as step 3.5 in `pipeline_chain.sh` (after flows, before build). It reads `stories.json`, translates key fields (headline, they_say, reality, thesis) via DeepSeek API, and writes `stories_ru.json` + `flows_ru.json` to both `data/` and `site/data/`. Without an API key, it copies English as placeholder.

### Race condition
app.js renders before `i18n.init()` completes fetching translations. On first page load, inline labels show English. On subsequent loads (after i18n caches), translations apply before render. The `i18nReady` event + `waitForI18n()` pattern was attempted but abandoned due to CDN deployment complexity. Acceptable tradeoff for static site.

- `references/dual-pipeline-field-mismatch.md` — Two story generation pipelines (intel vs editorial writer) produce different field sets. Story-app.js time badges fail on editorial stories lacking `generated_at`. Story IDs exceed URL limits. Detection commands and fixes.

## Technical Notes

- **Live site:** `https://www.lagazzettadikyiv.com` (GCS bucket `gs://www.lagazzettadikyiv.com`). Apex `lagazzettadikyiv.com` 301→ www via wwwizer.
- Repo: `/Users/alexstocchi/projects/gazzetta-di-kyiv/` — `site/` subdirectory is what gets deployed.
- **NOT** `~/.hermes/hermes-agent/gazzetta-di-kyiv/` (that's the Hermes internal copy) and **NOT** `~/lagazzettadikyiv/` (that's the Devvit Reddit app — separate project).
- `build_site.py` syncs pipeline outputs from `data/publish/` to `site/data/`.
- **GCS CDN caches HTML for 300s (5 min, reduced from 3600s in v22.12).** After deploy, old HTML may serve for up to 5 minutes. Verify with `gsutil cp gs://www.lagazzettadikyiv.com/index.html -`, not browser.
- No frameworks — vanilla HTML5 + CSS + JS.
- Collapsible container JS: `wireCollapsibleContainers()` toggles `.expanded` class on `.container.collapsible` elements.
- Story accumulation: `capturedStoryIds` Set prevents duplicate rendering; new cards insert at top via `el.insertAdjacentHTML('afterbegin', html)`.
- Hero confidence now passes `aggregate_direction` ("bullish"/"bearish") from flows.json — JS appends ↑ or ↓ arrow.
- Flow positioning derived from direction+magnitude in `generate_flows.py` (≥$3B = accumulating/distributing, else hedging). Fixed in v22.8 — previously all flows defaulted to "hedging" because stories' `capital_flow` dicts lacked a `positioning` key.

### story-app.js Scope Fragility — FIXED (v23.8)

**Symptom (was):** Story page stuck at "Loading intelligence report…" with empty console exceptions. Any new variable or function declaration in story-app.js scope silently broke rendering.

**Root cause:** Monolithic `init()` function with massive template literal. `catch(e){}` blocks swallowed all errors.

**Fix (v23.8): Namespace migration to `window.Gazzetta`.** Moved global variables into `Gazzetta.UI`, `Gazzetta.Data`, `Gazzetta.State` sub-namespaces. Future modules can be added without colliding with the global scope:

```javascript
window.Gazzetta = window.Gazzetta || {};
Gazzetta.State = {};    // capturedStoryIds, STORIES_CACHE, flowsData
Gazzetta.UI = {};       // byId
Gazzetta.Data = {};     // getJSON, getDataPath, getFlowsPath
Gazzetta.Story = {};    // init, renderIntelReport (story-app.js)
```

**Verification:** `browser_console` → `window.Gazzetta` exists with populated sub-namespaces. No global variable leaks beyond browser built-ins.

**Backward compatibility:** All existing function calls (`byId()`, `getJSON()`, etc.) still work at global scope. The namespace is additive.

### Story-as-Intel-Report Page (v22.16+)

Each story has a dedicated immersive page at `story.html?id=<story_id>`. This is the product's core UVP — an intel report format nobody else does.

**Files:** `site/story.html` (page template), `site/story-app.js` (dedicated renderer), story page CSS section in `styles.css`.

**Layout (UX Director wireframe, June 2026 focus group):**
1. Sticky masthead: ← Dashboard | La Gazzetta di Kyiv | EN/RU
2. Intel header: category tag, severity, date, tension tier badge
3. Headline (Playfair Display, 28px)
4. Photo (full-width, max 360px)
5. INTEL BRIEF — story summary paragraph
6. THE PLAY — green left-border box, portfolio implication text, catalysts
7. THEY SAY / REALITY — 2-column grid (amber/red left-border boxes), collapses to single column on mobile
8. CAPITAL FLOW — blue left-border box: $XB amount, confidence %, direction, claim, projected, positioning
9. EXTREMUM — grey left-border box: tail-risk scenario
10. Share row — 4 icon buttons (Copy, X, FB, Telegram)
11. Bottom nav: ← Back to Dashboard | Story N of M | Next Story →

**Data flow:** `story-app.js` reads `?id=` from URL, fetches `stories.json` (or `stories_ru.json` for RU), renders single story, provides prev/next navigation cycling through all stories.

**How stories link in:** Story card headlines on the main page (`index.html`) are wrapped in `<a href="./story.html?id=...">` links. Expanded cards show a "Full intelligence report →" button linking to the story page.

**CSS classes:** `.story-masthead`, `.story-page`, `.intel-report`, `.intel-header`, `.intel-meta`, `.intel-headline`, `.intel-photo`, `.intel-brief`, `.intel-play`, `.intel-contradiction`, `.intel-they-say`, `.intel-reality`, `.intel-capital-flow`, `.intel-extremum`, `.intel-share`, `.share-btn`, `.story-nav`, `.intel-report-link` (on main page cards).

## Flow Nodes Page (v22.36+) — Dark Command Center

The flow-nodes page (`flow-nodes.html`) is a standalone power-user data visualization tool. It is deliberately DIFFERENT from the editorial site:

- **Standalone architecture**: No shared `app.js`, no `i18n.js`, no `styles.css`. Self-contained CSS + JS in the HTML file (~1160 lines v22.42). Loads `data/flow_nodes.json` directly via `fetch()`.
- **Dark theme default**: `#0F172A` background with card surfaces at `#1E293B`. Dual-theme via CSS custom properties — `body.cn-light` toggles to `#F8FAFC` white with `#FFFFFF` cards. Toggle button ☀/☽ persists per-session only (no localStorage).
- **6 node types**: Governmental (gold rectangle), Institutional (blue diamond), Corporate (green rounded square), Retail (violet circle), Crypto (amber hexagon), Cross-Border (red octagon). Each has a distinct SVG path shape.
- **23 edges**: Bezier curves with arrowheads. Green=inflow, red=outflow. Dashed=low confidence (<60%). Edge width scales with amount.
- **Edge labels**: SVG text at cubic bezier midpoints showing "$XB ↑" or "$XB ↓".
- **Detail panel**: 340px slide-out aside. Sources/destinations DERIVED from edges dynamically (grouped by source/target node label). Shows delta badges ("↑ $0.6B vs 7d"), sparkline charts (6-week trend, labeled "modeled from flow data" — NOT "simulated"), and clickable story links (`./story.html?id=X`).
- **Keyboard shortcuts**: 1-6 filter by node type, Esc close panel, ←↑↓→ navigate nodes, 0 reset filter.
- **Legend filter**: Clicking legend item highlights only that type's nodes and connected edges.
- **Product nav**: Full site navigation bar matching other product pages. Flow Nodes is active tab.
- **Methodology link**: Thesis paragraph includes `<a href="./capital.html">Methodology →</a>` for trust.
- **Data model** (`data/flow_nodes.json`): 13 nodes with subtypes (e.g. `central_bank_reserve`, `sovereign_wealth_fund`, `regulatory_crypto`), metrics with delta fields, 6-week history arrays. 23 edges with `flow_type` and `data_source` attribution.

### Flow Nodes — Mobile Responsive Design (v22.42)

3-tier responsive breakpoints derived from focus group audit (Mobile UX Researcher + Degen Trader + 55yo Retail, 3/3 consensus):

**Breakpoint 1: ≤768px** — Tablet/mobile transition
- SVG text scaled up: node labels 13px, amounts 10px, sub-labels 9px, edge labels 10px
- Touch targets: close button 44×44px, theme toggle 40×36px, nav links min-height 36px
- Legend items min-height 36px with 6px padding
- Mobile filter bar (`.cn-mobile-filters`) becomes visible — 7 tap-friendly buttons replacing hidden keyboard shortcuts
- Panel max-height 45vh as bottom sheet with overflow scroll
- Masthead badge hidden, thesis h1 15px

**Breakpoint 2: ≤480px** — iPhone SE/compact phones
- Nav links 9px font, tighter gaps
- Legend items 9px font, tighter padding
- Masthead name 13px

**Touch/hover safety pattern:**
```css
/* Touch: always works */
.cn-node-group:active .cn-node-shape,
.cn-node-group.active .cn-node-shape { stroke-width: 2.5; }

/* Hover: only on pointer devices (not touch) */
@media (hover: hover) {
  .cn-node-group:hover .cn-node-shape { stroke-width: 2.5; }
  .cn-nav a:hover { color: var(--cn-text); }
  .cn-legend-item:hover { color: var(--cn-text); }
}
```

**Font floor:** No text element below 9px at any breakpoint (was 7px sub-labels, 8px edge labels). Mobile filter buttons min-height 36px. Legend shapes 14px at ≤768px (was 12px).

**Mobile filter bar** (`.cn-mobile-filters`): 7 inline buttons (Gov/Inst/Corp/Retail/Crypto/X-Border/All) with `display:none` on desktop, `display:flex` at ≤768px. Each button triggers the corresponding legend item click. Active filter gets colored border via `typeColor()`. Scrollable horizontally.

**Detail panel on mobile:** Full-width (100%), max-height 45vh, independent scroll. Close button enlarged to 44×44px for fat-finger safety.

**Sparkline label:** "modeled from flow data" (was "simulated" — trust killer caught by 55yo retail investor).

Reference: `references/flow-nodes-mobile-audit-v22.42.md` — full 3-persona audit report with per-element touch target measurements, font size violations, and fix documentation.

## Semantic Triangulation Engine (v2.0 — June 2026)

The site's core architecture was upgraded from loosely-coupled data silos to a unified semantic graph where every entity declares bidirectional links. Stories reference flows they impact; flows trace back to narrative drivers; positions derive from both.

### Architecture

```
Telegram Intel Monitor (30m)
        │
        ▼
intel_to_stories.py v2.0
├── extract_entities() — 4 maps (assets, geographies, actors, instruments), 100+ keywords
├── compute_time_decay() — exponential decay formula
├── generate_multi_persona() — C-Suite / Quant / Degen blocks
└── Cross-reference: impacted_flows[] via flow_id lookup
        │
  ┌─────┼─────┐
  ▼     ▼     ▼
stories  flows  positions
.json   .json  (future)
  │      │      │
  └──┬───┴──┬───┘
     ▼      ▼
  GRAPH CONTRACT (schemas/triangulation_schema.json)
     │
     ▼
  UI TRIANGULATION (app.js)
  ├── .teaser-linked — ↔ N flows, ⚡ N bets
  ├── .freshness-ago — time-decay % badge
  └── multi_persona.* blocks in JSON
```

### Schema Contract (`schemas/triangulation_schema.json`)

JSON Schema (draft 2020-12) enforcing bidirectional references:

| Entity | Required Field | Links To |
|---|---|---|
| Story | `impacted_flows[]` (min 1) | Flow IDs |
| Story | `associated_positions[]` | Position IDs |
| Story | `entity_tags` (assets, geos, actors, instruments) | Cross-reference index |
| Story | `time_decay` (half_life_hours, freshness, decay_curve) | Decay engine |
| Story | `multi_persona` (c_suite, quant, degen blocks) | Content rendering |
| Flow | `narrative_drivers[]` (min 1) | Story IDs |
| Flow | `linked_positions[]` | Position IDs |
| Flow Node | `connected_flows[]` | Flow IDs |
| Flow Node | `connected_stories[]` | Story IDs |
| Position | `derived_from_stories[]` | Story IDs |
| Position | `derived_from_flows[]` | Flow IDs |

Validation: `cross_references` object auto-generated with `orphan_stories`, `orphan_flows`, `orphan_positions` arrays and a `link_graph` adjacency map.

### Entity Extraction (`intel_to_stories.py` v2.0)

Four keyword maps scan raw text (headline + bet + event + benefit) for:

- **ASSET_MAP** (20 entries): BTC, ETH, SPX, WTI, BRENT, XAU, NVDA, TSLA, DXY, VIX, etc.
- **GEO_MAP** (28 entries): Iran, Israel, Ukraine, China, USA, EU, Lebanon, Kuwait, etc.
- **ACTOR_MAP** (35 entries): Federal Reserve, ECB, OPEC, BlackRock, Trump, Putin, Hezbollah, Ethena, etc.
- **INSTRUMENT_MAP** (12 entries): futures, options, spot, ETF, swaps, bonds, stablecoins, etc.

Output: `entity_tags: {assets: ["BTC","SPX"], geographies: ["Iran"], actors: ["OPEC"], instruments: ["futures"]}` per story.

### Time-Decay Model

```
freshness = e^(-ln(2) × hours_elapsed / half_life)
half_life = horizon_hours × confidence_bonus

Horizon       Half-life    Confidence bonus
1-6h          3h           high=1.5×, medium=1.0×, low=0.7×
6-24h         12h
24-72h        36h
1w+           84h
structural    720h (30d)
```

Rendered UI: freshness % badge on each story teaser item. Green >80%, gold 40-80%, muted <40%. Renewal triggers: `new_intel`, `price_breach`, `flow_confirmation`.

### Multi-Persona Content Blocks

Every story carries three audience-specific renderings:

| Block | Target | Focus | Style |
|---|---|---|---|
| `c_suite` | Macro Horizon | Structural, policy, supply-chain implications | Formal, board-ready |
| `quant` | Telemetry Feed | Raw data, velocity, correlations, z-scores | Zero narrative fluff |
| `degen` | Action Trigger | Direction, entry/stop/target, conviction | Emoji-rich, 4-line max |

Generated by `generate_multi_persona()` in `intel_to_stories.py` v2.0. The `degen.signal` sub-object carries machine-readable direction/entry/stop/target/conviction for direct feed into trading widgets.

### Dynamic Hyperlinking (app.js v2.0)

Story teaser items now display:
- **`↔ N flows`** — when `impacted_flows[]` is non-empty, linked to flow-nodes.html
- **`⚡ N bets`** — when `associated_positions[]` is non-empty, linked to trades.html
- **`XX% freshness`** — time-decay percentage badge, color-coded by age

CSS: `.teaser-linked { font-size: 9px; opacity: 0.65; color: var(--gold); }` plus `.freshness-ago` classes (`.freshness-recent`, `.freshness-today`, `.freshness-day`, `.freshness-stale`).

### Feedback Parser (`scripts/parse_feedback.py`)

Reads `feedback/focus_groups.md` (markdown log of user/prospect feedback), extracts entries by persona + priority + category, compiles structured JSON backlog to `data/feedback_backlog.json`. Category detection via keyword mapping (UI/UX, Data Freshness, Actionability, Analytics, Content Format, Distribution, Trust/Provenance). Run standalone or as pre-deploy gate.

### Product Requirements Document (`prd.md`)

Three personas (Quant, C-Suite, Degen) with feature matrix, data pipeline architecture diagram, design contract (border-radius:0, WCAG AA colors, font families), and quality gates. Update when adding features or changing UX. The PRD is the canonical source of product truth — not memory and not session history.

### Pre-Deploy Check Enhancements (refresh_context.py v2.0)

- **§4.5a:** Uncommitted files warning → points to `scripts/safe_git.py` for auto-backup
- **§4.5b:** Structural integrity — regex-verifies hero, product-nav, teaser containers, onboarding, storyFreshness, flowFreshness in compiled HTML
- **§4.5c:** Orphan detection — flags stories with no `impacted_flows[]` and no matching flow_id in flows.json
- **§4.5d:** Live product page 200 check — verifies HTTP 200 on all 7 product pages via urllib HEAD requests

## Services Utility Grid (v23.0 — Professional Redesign, No Emoji)

A persona-driven value-proposition section below the teaser containers. Three `.svc-card` elements — professional labels, no emoji icons, outcome-oriented descriptions.

| Card | Persona | Links To | Description |
|------|---------|----------|-------------|
| Macro Horizon | C-SUITE | `stories.html` | Structural policy shifts, supply-chain bottlenecks, regulatory implications. Board-ready context for capital allocators. |
| Flow Telemetry | QUANTITATIVE | `flow-nodes.html` | Capital velocity differentials, correlation coefficients, heat scores. Low-latency raw data. Zero narrative fluff. |
| Action Triggers | EXECUTION | `trades.html` | Directional bias, entry/stop levels, conviction ratings with ATR-derived stops. Ultra-concise, trade-ready. |

CSS: `.services-grid` (grid, auto-fit, minmax(220px, 1fr)). `.svc-card` (flex column, 1px divider border, hover gold border + pale gold bg). `.svc-persona` (sans 9px 700 uppercase muted). `.svc-title` (display 16px 600). `.svc-desc` (serif 12px ink-light). **No emoji icons.** IDs: `svcCSuite`, `svcQuant`, `svcTrader` (consistent persona-to-ID naming).

A persona-driven value-proposition section on the index page, below the 5 teaser containers. Three `.svc-card` elements, each linking to the most relevant product page:

| Card | Persona | Links To | Icon | Description |
|------|---------|----------|------|-------------|
| Macro Horizon | C-Suite | `stories.html` | 🏛 | Structural policy shifts, supply-chain bottlenecks, regulatory implications. Board-ready. |
| Flow Telemetry | Quant | `flow-nodes.html` | ⚡ | Low-latency raw data, velocity differentials, correlation coefficients. Zero narrative. |
| Action Triggers | Trader/Degen | `trades.html` | 🎯 | Directional bias, entry/stop levels, conviction ratings, divergence alerts. Ultra-concise. |

CSS: `.services-grid` (responsive grid, `grid-template-columns: repeat(auto-fit, minmax(200px, 1fr))`), `.svc-card` (frameless cards with 1px divider, gold border on hover). See `styles.css` for full rules.

**⚠ ID mismatch (audited June 2026):** The third card uses `id="svcDegen"` but the `.svc-persona` label reads "Trader" — the persona was renamed without updating the ID. If renaming personas, always update the HTML `id` attribute to match. Check: `grep -n 'id="svc' index.html` should have consistent persona-to-ID naming.

**Copy guidance:** Each `.svc-desc` should answer "what does this persona DO with this intelligence?" — not just "what's in it." Current copy is input-oriented (lists signals) rather than outcome-oriented (names the decision or action enabled).

## Hero Hook Indicators (v2.0+ — verified working v22.45)

Three `.hero-ind` anchor elements in the HTML: `#heroContradictions`, `#heroTopVelocity`, `#heroFreshness`. These are **JS-populated by `updateHeroIndicators()` in `app.js`** (lines 352-380), called from `fetchFlows()` at line 345.

**⚠ Verification pitfall:** These indicators show `—` in raw HTML/curl output because they're JavaScript-populated. `curl` returns static HTML with `—` placeholders. **Must verify with browser** or `browser_console` — not curl. The function IS in the live hashed JS and IS called correctly.

| Indicator | ID | Source | Live value (v22.45) |
|-----------|-----|--------|---------------------|
| Contradictions | `#heroContradictions` | Flows with confidence_pct < 70% | e.g., **5** |
| Top Velocity | `#heroTopVelocity` | Highest pace_multiplier across flows | e.g., **2.4×** |
| Freshness | `#heroFreshness` | `formatTimeAgo(flowsData.generated_at)` | e.g., **just now** |

**Browser verification:** `browser_navigate` → snapshot shows populated values. Contrast: `curl` → shows `—`.
**Conditional rendering:** If `flowsData` or `flowsData.flows` is falsy, the function returns early (line 353) — indicators remain `—`.

## Categorized Capital Flows (v2.0+)

The flows teaser on index no longer shows individual flow items. Instead, it aggregates flows into 3 high-level categories defined in `config.yaml`:

```yaml
flow_categories:
  sovereign:    { label: "Sovereign Flows", icon: "🏛", classes: [fixed_income, fx] }
  systemic:     { label: "Systemic Liquidity", icon: "⚡", classes: [equities, commodities] }
  speculative:  { label: "Speculative Arbitrage", icon: "🎯", classes: [crypto, defense, tech] }
```

Each category card shows: consolidated net direction (▲/▼ $XB), average velocity (⚡ X×), flow count. All cards link to `flow-nodes.html` for the full graph. The dedicated `flows.html` page retains granular per-flow data.

JS: `populateTeasers()` → Flows teaser section. The `CATEGORIES` const in app.js mirrors config.yaml (client-side can't read YAML). CSS: `.teaser-cat` with `.teaser-cat-icon`, `.teaser-cat-label`, `.teaser-cat-dir` (`.inflow`/`.outflow`), `.teaser-cat-vel`, `.teaser-cat-count`.

Container 2 ("Where the smart money is going") redesigned per Mike Green's PM spec from June 2026 focus group. Specification: numbers-first scannable table, $XB leads, velocity as acceleration factor, no narrative bloat.

**Old design:** Narrative-heavy expandable cards with long headlines, hidden detail sections, expand/collapse icons.

**New design:** Compact table rows — each flow is a two-line row:
- **Row 1 (main):** `$XB` amount → `↑ IN` / `↓ OUT` direction badge → `ASSET` class → `XX%` confidence → `↑1.8×` / `=1×` / `↓0.6×` pace → `SYMBOL BUY·HIGH` bet pill → catalyst count badge
- **Row 2 (detail):** compact headline text + positioning label

**CSS classes:** `.flow-row`, `.flow-row-main`, `.flow-amount`, `.flow-dir` (`.inflow`/`.outflow`), `.flow-asset`, `.flow-conf`, `.flow-pace`, `.flow-bet-pill-mini`, `.flow-row-detail`, `.flow-headline-compact`, `.flow-positioning`

**Velocity display rules:**
- `pace_multiplier >= 1.5` → `↑ X×` (accelerating)
- `pace_multiplier <= 0.7` → `↓ X×` (decelerating)
- otherwise → `= X×` (steady)

**JS rendering:** `renderCapitalFlows()` in app.js was rewritten — removed all expand/collapse logic, removed expanded story/bet detail sections, simplified to flat rows. Flow aggregation (`aggregateFlows()`) still runs before rendering for duplicate dedup.

## Gazzetta Namespace (v23.8+) — Scope Fragility Resolution

The story-app.js scope fragility (P3 defect) was resolved via a namespace migration pattern. All global variables and functions are now accessible through `window.Gazzetta`:

```js
window.Gazzetta = {
  UI:    { byId },                          // DOM helpers
  Data:  { getJSON, getDataPath, getFlowsPath, ANCHOR_ASSETS },  // Data fetching
  State: { capturedStoryIds, STORIES_CACHE, flowsData, initialized, storyCount },  // Runtime state
  Story: { init, renderIntelReport },        // Story page (loaded on story.html)
};
```

**Migration pattern (safe — no restructuring required):**
1. Add namespace object at top of JS file: `window.Gazzetta = window.Gazzetta || {}; Gazzetta.UI = {}; Gazzetta.Data = {}; Gazzetta.State = {};`
2. Alias existing functions into namespace: `Gazzetta.UI.byId = byId;`
3. Export runtime state at end of `boot()`: `Gazzetta.State.initialized = true; Gazzetta.State.storyCount = capturedStoryIds.size;`

**⚠ CRITICAL PITFALL — Temporal Dead Zone (TDZ) silent failure (v23.9 fix, June 2026).** The namespace aliasing code references `let`/`const` variables. If those lines execute BEFORE the variable declarations, EVERY reference throws `ReferenceError: Cannot access 'X' before initialization`. The error is swallowed by empty catch blocks → no console output → the entire JS pipeline silently dies. Symptoms: ALL hero indicators show `—`, ALL teaser containers show `—`, sidebar blank, buttons unclickable. The `Gazzetta` object exists but `Gazzetta.State` is an empty object `{}`.

**Root cause (v23.8):** Lines 20-21 of the original namespace block referenced `capturedStoryIds` and `STORIES_CACHE` before their `let`/`const` declarations at lines 55 and 28:
```javascript
// Line 20: TDZ! capturedStoryIds is let, declared at line 55
Gazzetta.State.capturedStoryIds = capturedStoryIds;
// Line 21: TDZ! STORIES_CACHE is const, declared at line 28
Gazzetta.State.STORIES_CACHE = STORIES_CACHE;
```

**Fix (v23.9):** Move namespace State assignments to AFTER all `let`/`const` declarations:
```javascript
// All declarations first
const STORIES_CACHE = {};
let capturedStoryIds = new Set();
// THEN namespace state assignments
Gazzetta.State.capturedStoryIds = capturedStoryIds;
Gazzetta.State.STORIES_CACHE = STORIES_CACHE;
```

**Verification after any namespace change:** `browser_console` → `window.Gazzetta` — check that UI, Data, State sub-objects exist with expected keys AND that `Gazzetta.State.flowsData` is populated after `boot()` completes. Also check `window.CAPITAL_FLOWS_DATA` is defined. If `Gazzetta.State` exists but has zero keys (empty object `{}`), a TDZ error killed `boot()` — check console for the specific variable name.

**Governance rule — NEVER report success without browser verification:** The TDZ bug survived through Phase 8 because I reported the namespace migration as "complete" based on `node --check` (syntax only) and `refresh_context.py` (static HTML checks only). Neither detects runtime JS failures. After any JS change, ALWAYS verify with `browser_navigate` + `browser_console` BEFORE reporting success. If the site shows `—` in hero indicators or teaser counts, the JS pipeline is dead regardless of what static checks say. See also `gazzetta-verify-deploy` skill §interactivity-verification.

## Asymmetry Score Architecture (v23.12+ — Mathematical Delta Formula)

The platform computes an **Asymmetry Score (0-100)** using a hard mathematical delta that measures the gap between narrative sentiment and actual price action. **Formula v2.0 (June 2026):**

```
Score = |(NarrativeSentiment [-1 to 1] - PriceActionVelocity [-1 to 1]) × 50|
```

| Component | Derivation | Range |
|-----------|-----------|-------|
| NarrativeSentiment | ±(confidence/100) — inflow→+, outflow→−, neutral→0 | [-1, 1] |
| PriceActionVelocity | tanh(change_pct / 5) — 5%→±0.76, 10%→±0.96 | [-1, 1] |

**Score tiers (updated thresholds):**
| Score | Tier | Meaning |
|-------|------|---------|
| ≥ 80 | MAX ASYMMETRY | Massive contradiction — institutional edge |
| ≥ 60 | HIGH ASYMMETRY | Significant divergence — trade opportunity |
| ≥ 40 | MODERATE | Some misalignment |
| < 40 | LOW ASYMMETRY | Market and narrative aligned |

Every score carries a **diagnostic trace** in `market_prices.json`:
```json
{
  "diagnostic_trace": {
    "narrative_sentiment": -0.80,
    "price_velocity": 0.40,
    "raw_delta": -60.0,
    "formula": "(-0.80 - 0.40) * 50 = |-60.0| = 60"
  }
}
```

**Math Sanity Check** (`test_platform.py` Round 8): 5 test vectors verify the formula produces correct scores. Reference: `references/math-sanity-check-v23.12.md`.

**Old formula (v23.9, deprecated):** Ad-hoc heuristic `if (narrative == price) { base = 30 - abs(pct)*3 } else { base = 50 + abs(pct)*5 + ... }`. This was replaced because it produced opaque scores with no mathematical traceability. The diagnostic traces and tanh normalization make the v2.0 formula auditable by quants.

## Alpha Lead-Gen Gate (v23.9+)

Monetization-prep pattern for gating premium data:

```css
.alpha-gated .gated-content { filter: blur(6px); opacity: 0.4; pointer-events: none; }
.gate-overlay { position: absolute; inset: 0; background: rgba(255,255,255,0.85); z-index: 2; }
.gate-cta { background: linear-gradient(135deg, #B8860B, #D4AF37); color: #FFFFFF; min-height: 44px; }
```

HTML pattern:
```html
<div class="side-section alpha-gated">
  <div class="gate-overlay">
    <span class="gate-hint">Entry zones & stop levels are gated</span>
    <a href="https://t.me/GazzettaDiKyiv" class="gate-cta">🔓 Unlock Full Signal →</a>
  </div>
  <div class="gated-content"><!-- blurred data --></div>
</div>
```

The CTA links to Telegram for the unlock key. Mobile: 44px touch target, 80% width.

## Mobile Horizontal Product Slider (v23.6+)

At ≤768px, `.product-nav` converts to a horizontal scroll slider with snap points. CSS pattern:
```css
.product-nav {
  display: flex; overflow-x: auto; scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch; gap: 4px;
  -ms-overflow-style: none; scrollbar-width: none;
}
.product-nav::-webkit-scrollbar { display: none; }
.product-nav a { scroll-snap-align: start; flex-shrink: 0; min-height: 36px; }
```

Expanding hint stats: `.expandable-stat` (inline pill, 1px border) → tap to reveal `.expandable-stat-body` with gold left-border. Pattern preserves information scent without cluttering mobile viewport.

## Alpha Layer Typography (v23.13+)

Alpha container headers use a high-contrast monospace font stack for institutional trading-terminal feel:
```css
.alpha-header .layer-label {
  font-family: 'JetBrains Mono', 'Roboto Mono', 'Courier New', monospace !important;
  font-weight: 900;
  letter-spacing: 0.16em;
}
```
INTEL retains sans-serif. This typographic split — serif editorial (Playfair Display) for INTEL, monospace trading-desk for ALPHA — reinforces the Two-World architecture visually.

## Right Sidebar Live Correlations (v23.13+)

The CONTEXT sidebar includes a Live Correlations section with 6 pairs (Oil/Gold, BTC/Gold, Oil/DXY, Bonds/Equities, BTC/SPX, Gold/DXY). Currently hardcoded HTML in index.html — roadmap is JS-populated from correlation_matrix.json. Includes disclaimer: "Directional proxy from 24h delta — full rolling correlation requires 30+ data points."

Hardcoded color tokens — no variables, no drift:
- **ALPHA**: `#B8860B` gold — `.alpha-header .layer-label` background, left border, `.nav-group-label:nth-of-type(2)` text color, `.alpha-header .layer-desc` text
- **INTEL**: `#0F172A` slate — `.intel-header .layer-label` background, left border

ALPHA nav label gets gold text distinct from INTEL muted gray. Immediate 3-second visual differentiation.

## Atomic Bilingual Output (v23.6+)

`db_to_json.py` writes to `data/en/` and `data/ru/` atomically, then syncs to `site/data/en/` and `site/data/ru/`. Backward-compatible `data/stories.json` retained. `test_platform.py` Round 6 checks EN↔RU story_id coverage (≤5 missing = warning, >5 = fatal).

## Anti-Patterns (NEVER DO THESE)

- ❌ Dark backgrounds on editorial/product pages — v20 is white metallic. The user explicitly demanded white backgrounds. **EXCEPTION:** `flow-nodes.html` uses a dark command-center theme (#0F172A) with dual-theme (light toggle via `.cn-light` class). This is deliberate — it's a power-user data visualization tool, not an editorial page. Dark theme is the default; light is available via the ☀/☽ toggle button.
- ❌ Sidebar columns or empty spacer divs — single column layout only
- ❌ Rounded corners over 2px, drop shadows, box shadows, gradients
- ❌ Dashboard widgets, gauges, sparklines, charts, canvas-rendered graphics
- ❌ Third-party JS chart libraries (chart.js, recharts, d3 canvas)
- ❌ "Bet&Benefit" name — it's THE ANCHOR
- ❌ "Portfolio implication" label — it's THE PLAY
- ❌ 2h projections — "horoscopes for traders" (killed by unanimous focus group)
- ❌ 7-pillar filter bar as public UI — editorial lens is INTERNAL
- ❌ Taxonomical category names (ABUNDANCE TECH, BLOCKCHAIN AGENTIC)
- ❌ Full story content visible by default — cards are COLLAPSED
- ❌ "Opportunity," "potential," "could be," "we believe" — ambition killers
- ❌ Data without source citation, trade idea without stop level
- ❌ `data-story-id` on non-story elements (flow items, sidebar rows) — WILL collide with card deduplication checks
- ❌ Shipping without bumping cache bust version (`?v=N`) — CDN serves stale files silently
- ❌ **Emoji or Unicode characters as UI icons** — 📋 ✈ 𝕏 ▾ ✓ and similar. Use Lucide-standard SVG icons ONLY: 24×24 viewBox, stroke="currentColor", stroke-width="2" (NOT 1.5), stroke-linecap="round", stroke-linejoin="round", fill="none". Emoji render inconsistently across OS, cannot be styled via CSS, are inaccessible, and look amateur. 
- ❌ **Custom hand-drawn SVG icons** — do not invent icon geometry. Always source from Lucide (lucide.dev). Specific icons: use `share2` for share (three connected dots), `link` for copy link (chain links), `twitter` for X, `send` for Telegram (paper plane), `linkedin` for LinkedIn, `chevron-down` for expand, `check` for resolved. Icons must be INSTANTLY recognizable — a user should know what it does before clicking.
- ❌ **Dropdown share menus** — the old pattern. v20.20 replaced them with a visible row of 5 icon buttons (Copy, X, FB, Telegram, Reddit). Each is 28×28px, no labels, hover-fills dark. Never use share-toggle + share-menu classes — they no longer exist in the codebase.
- ❌ **Raw tension numbers ("Tension 50")** — killed in v22.10 after a 3-persona focus group found them incomprehensible. The number alone gives no context (is 50 high? low?), requires a hover tooltip (dead on mobile), and all scores cluster 45-60 making them functionally identical. Use tier badges (CONTRADICTED/DIVERGENT/ALIGNED) instead. The old `.contradiction-score` CSS class, `::before { content: "Tension " }` pseudoelement, and `cursor: help` title-attribute dependency are all removed.
- ❌ **Onboarding popups or welcome modals** — ANY first-visit overlay that blocks content destroys institutional trust. The "Welcome to La Gazzetta di Kyiv" popup (v22.16) was removed in v23.12 by direct CEO order: "Delete the Modal. It destroys institutional trust." A professional intelligence terminal does not greet you with a tutorial. If onboarding is needed, use a dismissible bottom banner that does not block content. Never reinstate `#onboardingOverlay` or any equivalent first-visit modal. Verify with `grep onboardingOverlay index.html` — must return no matches.
- ❌ **Hardcoded live data in HTML** — ticker prices, flow sector totals, and entry/stops hardcoded in `index.html` go stale within hours. ALL dynamic numbers must be JS-populated from data endpoints. The live tickers sidebar was found serving 6-day-old prices (June 2026 audit) because `fetch_market_data.py` updated `market_prices.json` but `index.html` had baked-in values. Fix: regenerate index.html tickers during `shipit.sh` build, OR populate via app.js from `market_prices.json`. Verification: cross-reference live ticker values against `data/market_prices.json` — every discrepancy is a stale number.
- ❌ **Misleading entry/stop labels in the lead-gen gate** — the gated "FULL SIGNAL" section showed "SPX Entry $735" (the PRICE, not the entry) and "BTC Stop $58K" (stale estimate, not ATR-computed $63.8K). Entry labels must show the ACTUAL entry range (`$5,750–5,950`) from `ANCHOR_ASSETS`. Stops must be ATR-computed via `computeATRStop()`. Verify: `grep -A2 'FULL SIGNAL' index.html` — entry values must match `ANCHOR_ASSETS[].entry`, stop values must be ATR-computed.
- ❌ **Raw institutional jargon** — `accumulating`, `distributing`, `hedging` are meaningless to retail users. Always run positioning codes through `positionLabel()` before display. The old pattern was killed in v22.12. Use Smart Money labels (buying/selling/hedging) instead.
- ❌ **Fox or quill as masthead emblem** — replaced with Caduceus of Mercury (winged staff with serpents) in v22.7 after a 3-persona focus group. Use `.masthead-caduceus`. Never use `.masthead-fox` or `.masthead-balance`.
- ❌ **Flow conviction as hero stat label** — replaced with Confidence in v22.8 after a 3-persona retail focus group found it incomprehensible. The percentage now displays with a color-coded tier tag (HIGH/MEDIUM/LOW) via `.confidence-tier` CSS. Never revert.
- ❌ **Onboarding welcome modal** — the Welcome to La Gazzetta di Kyiv popup was permanently removed in v23.13. It destroyed institutional trust. Never reinstate any popup, modal, or overlay on the homepage. When removing a UI element that appears in refresh_context.py's pre-deploy structural integrity check (~line 192), update the check list to delete the now-removed element — otherwise every deploy is blocked with "MISSING in index.html." after a 3-persona retail focus group found it incomprehensible. The percentage now displays with a color-coded tier tag (HIGH/MEDIUM/LOW) via `.confidence-tier` CSS. `generate_flows.py` writes `aggregate_confidence_label: Confidence`. Never revert.

- ❌ **Hardcoded numbers in sidebar** — SPX Entry in the lead-gen gate must show the ANCHOR_ASSET entry price ($5,750), NOT the current market price ($735). BTC Stop must be ATR-computed: `entry * (1 - atr_pct * stop_atr_mult)`. Live tickers and flow sectors are hardcoded HTML — verify against market_prices.json and flows.json after every deploy. Any stale hardcoded number destroys institutional credibility.

## Pitfalls

**Visual verification ≠ text snapshot.** `browser_snapshot` shows DOM structure but NOT alignment, overflow, color, or wrapping. A masthead passes text snapshots while looking broken visually. When the user says "it's messy" or "why can't you see it," the text snapshot failed — use `browser_vision` with a specific question about the element.

**curl 200 ≠ page works.** HTML may reference stale hashed JS/CSS from CDN. Verify with `browser_console` that the CORRECT hash loaded, not just any hash.

**Site frozen/stale -> run Grounding Protocol first.** Capital flows generate every 60min via pipeline cron but the site may lag if the deploy cron is down or site/ is out of sync. First-line check: run `.venv/bin/python refresh_context.py` to detect drift. Quick sanity: `curl -s https://www.lagazzettadikyiv.com/deploy_report.txt` to see last deploy timestamp and story count. If drift detected -> `bash shipit.sh`. Verify deploy cron `f9a24ed64aa5` is active with `cronjob action=list`. Manual verification: `gsutil cp gs://www.lagazzettadikyiv.com/data/flows.json - | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[\"generated_at\"])"` — timestamp should be within the last hour.

**db_to_json.py JOIN overwrites story capital_flow amounts — mass copy-paste (v23.10 fix).** Lines 79-93 of `db_to_json.py` JOIN story_flow_links → flow table and UNCONDITIONALLY overwrite every story's `capital_flow` dict with the linked flow's values. If 20 stories link to the same $88B flow, all 20 show $88B regardless of their actual content. This is the root cause of the "all stories have the same amount" audit finding.

**Fix (v23.10): Two-tier preservation + default-override logic:**
```python
# Tier 1: Preserve story-derived amounts — never overwrite a non-zero, non-default value
# Tier 2: Override the known $5.0B default (intel_to_stories.py sentinel)
is_default_amount = (cf.get("amount_b") == 5.0 and not cf.get("_amount_derived"))
if not cf.get("amount_b") or is_default_amount:
    cf["amount_b"] = primary_flow["amount_b"]
```

The $5.0B is the hardcoded default in `intel_to_stories.py` — any story with exactly $5.0B and no `_amount_derived` flag gets its amount replaced by the linked flow's real amount. Stories with genuinely derived amounts (e.g., $2.7B from Home Sales) keep their values. Verification: `test_platform.py` Round 7 checks for EXTREME DRIFT (>20× ratio) between story amounts and flow amounts as data corruption signals, but allows normal drift as expected behavior after this decoupling.

**OSINT quality filter (v23.10).** Add SQL WHERE clause to `db_to_json.py` `compile_stories()` to filter low-quality placeholder stories at source:
```sql
WHERE (
    json_extract(full_json, '$.source') NOT LIKE 'osint%'
    OR json_extract(full_json, '$.source') IS NULL
)
```
OSINT stories from `osint_reuters_business` have no analytical value — raw headlines with trade_signal=N/A and conviction=None. They dilute the product's credibility when mixed with telegram_intel stories. Filter at the DB query level so they never enter the compiled JSON. Also update the lead selection (line 100: `lead = stories[0]`) to pick the highest non-OSINT story.

**Pipeline write-location — scripts MUST write to `data/`, NOT `site/data/` (v23.11).** `build_site.py` (shipit.sh Stage 2) copies files from `data/` → `site/data/`. If a script writes directly to `site/data/`, its output is silently destroyed when `build_site.py` copies the stale `data/` version over it. This killed the narrative brain: `analyze_narratives_v2.py` wrote fresh narratives to `site/data/narratives.json`, but Stage 2 overwrote it with the 2-week-old `data/narratives.json`. CDN served May 26 data. **Fix:** Always write pipeline outputs to `data/` first. `build_site.py` handles the sync. Verify: after deploy, `gsutil cat gs://www.lagazzettadikyiv.com/data/<file>.json` should show the current `generated_at` timestamp.

**CDN cache expiry — updated GCS metadata may not take effect immediately (v23.11).** Even after `gsutil setmeta` sets `max-age=0` on GCS objects, the CDN fronting the bucket may serve the OLD headers until the previous TTL expires. If a file was previously cached at `max-age=3600`, the CDN continues serving the old 3600 header for up to 1 hour. Symptom: `curl -I` on the public URL shows stale `max-age=3600` while `gsutil ls -L` on the GCS object shows the new `max-age=0`. **Fix:** Verify GCS origin first (`gsutil ls -L`), then wait for CDN expiry (up to 3600s for JSON files previously cached at 1h). For urgent verification, use a cache-busting query parameter: `curl -I "https://www.lagazzettadikyiv.com/data/file.json?t=$(date +%s)"`. The CDN respects no-cache parameters for revalidation fetches. Also, ensure `shipit.sh` Stage 4 sets `max-age=0, must-revalidate` on ALL `.json` files (not `private, no-store`), which was fixed in v23.11.

**Ticker deduplication in live tickers (v23.9).** Do NOT map two asset classes to the same yfinance ticker. Original TICKER_MAP had both `commodities→CL=F` AND `oil→CL=F` — this produced duplicate `CL=F` entries in the live tickers sidebar. Symptom: one ticker appears twice, consuming a slot that should show a unique asset (e.g., 9 visible tickers but only 8 unique). Fix: remove redundant mappings. If a specific instrument duplicates a category mapping, keep only the category-level mapping. Verify: `grep -c '>CL=F<' index.html` — must be exactly 1.

**Circular pipeline dependency — db_to_json overwrites generate_flows output (v22.45).** `shipit.sh` Stage 1 runs `db_to_json.py` which compiles flows.json from the DB's flows table. This OVERWRITES whatever `generate_flows.py` produced. If the DB flows table has stale data (pace=1.0, old amounts), the site shows stale flows even after regenerating. Fix: update BOTH the JSON file AND the DB flows table. Use `scripts/backfill_pace.py` pattern for data migrations. Verify with `gsutil cp gs://www.lagazzettadikyiv.com/data/flows.json - | python3 -c "import json,sys; from collections import Counter; d=json.load(sys.stdin); print(Counter(f['pace_multiplier'] for f in d['flows']))"` — if all 1.0, the DB flows table needs backfill.

**Pace derivation chain (v22.45 fix):** `pace_multiplier` flows through three systems that can conflict:
1. `intel_to_stories.py` derives pace from content → writes to stories' `capital_flow.pace_multiplier`
2. `backfill_pace.py` updates existing stories with derived pace
3. `db_to_json.py` line 79: `cf["pace_multiplier"] = cf.get("pace_multiplier") or primary_flow["velocity"]` — preserves story-derived pace, falls back to flow velocity only when story pace is 0/None
4. `generate_flows.py` reads `pace_multiplier` from stories → writes to flows
5. `db_to_json.py` (DB flows table) is the TRUE source of truth for deployed flows.json

If any link in this chain breaks, all flows revert to 1.0. Detection: check GCS origin isn't hiding behind CDN cache. Verify with direct `gsutil cp`.

**Deploy cron failing with "Cannot access bucket" → gcloud not in cron PATH.** Cron jobs run under a stripped environment. The `gcloud` and `gsutil` binaries live at `/Users/alexstocchi/lagazzettadikyiv/google-cloud-sdk/bin/`. The deploy script MUST export: `export PATH="/Users/alexstocchi/lagazzettadikyiv/google-cloud-sdk/bin:$PATH"` AND `export CLOUDSDK_CONFIG="/Users/alexstocchi/.config/gcloud"`. Without this, every cron deploy run fails silently. Verify with `cat ~/.hermes/cron/output/f9a24ed64aa5/*.md`.

**Story cards not rendering → check data-story-id collisions.** The most insidious v19 bug: flow items in CAPITAL FLOWS REPORT carried `data-story-id` attributes. The `appendStoryCard` deduplication check uses `document.querySelector('[data-story-id="..."]')` — which matched the flow items and silently skipped all story rendering. Fix: scope the check to `el.querySelector(...)` (inside `#newsCol` only) AND use a different attribute on non-card elements (`data-flow-story-id`). No JS error, no console warning — just zero stories.

**Data-i18n attribute coverage — silent translation gaps.** The i18n system only translates elements with `data-i18n="key"` attributes. If an HTML element lacks this attribute, it stays in English regardless of language switch — with zero console errors. The v22.15 audit found 16 elements (4 container titles, 4 container descriptions, 3 subtitles, 3 footer notes, PDR label, anchor notes) with hardcoded English and no `data-i18n`. Detection: `fetch(url, {cache:'reload'}).then(r => r.text()).then(h => (h.match(/data-i18n=/g)||[]).length)` — compare vs expected count. After any container label change, verify ALL container titles, subtitles, descriptions, and footer notes have `data-i18n` attributes.

**Homepage flowFreshness not populating → fetchFlows() guard too strict (v22.42).** The `fetchFlows()` call inside `boot()` was guarded by `if (byId('flowsList'))`. Homepage has `#flowsTeaserContent` (not `#flowsList`), so flows never loaded on initial page load — `flowFreshness`, `heroConfidence`, and `CAPITAL_FLOWS_DATA` all stayed empty until the 5-min polling interval fired. Fix: removed the guard — `await fetchFlows()` now always runs. Render functions inside it check for their own target elements, skipping gracefully on pages without them. Verify: homepage must show "updated Xm ago" in the flow teaser within 5s of page load.

**Timestamp freshness indicators (v22.44+, updated v22.45):** Every data-driven component must show when the data was last updated. Working indicators: `#flowFreshness` (in flows teaser header, populated by `renderCapitalFlows()` from `flows.json → generated_at`). Both use `formatTimeAgo()` for relative display ("updated 12m ago") with ISO timestamp in the `title` attribute. CSS: `.flow-freshness { font-size: 9px; }` with freshness color classes (`.freshness-recent` = green, `.freshness-today` = gold, `.freshness-day` = muted, `.freshness-stale` = faded). The masthead timestamp (`#mastheadMeta`) shows a live clock date/time on page load via `updateMasthead()` and can show living-story update info via `updateMastheadLiving()`.

**⚠ KNOWN GAPS (audited June 2026):**
- `#storyFreshness` exists in the HTML (`<span class="flow-freshness" id="storyFreshness">`) but is **never populated by any JS function** — no code in `app.js` references this ID. It renders permanently empty.
- Hero indicators (CONTRADICTIONS, TOP VELOCITY, FRESHNESS) ARE working — verified via browser in v22.45. They show `—` in curl because JS-populated — no `updateHeroIndicators()` function exists in `app.js`. All three render the placeholder `—` permanently.
- The services grid, trade ideas teaser, signal teaser, and track record teaser have **no freshness indicators** at all.

**Fix checklist when implementing (v22.45 status):**
1. ✅ Hero indicators — implemented and working. `updateHeroIndicators()` in app.js lines 352-380, called from `fetchFlows()` line 345.
2. Add `storyFreshness` population: in `populateTeasers()` or after `fetchFlows()` pattern, set `byId('storyFreshness').textContent = 'updated ' + formatTimeAgo(data.generated_at)`.
3. Add freshness spans to Trade Ideas, Signal, Track Record, and Services Grid containers.

When adding new data displays, always include a freshness indicator.

**Homepage teaser containers stuck at "—" → duplicate populateTeasers code with wrong IDs (v22.42).** Two populator paths existed: (1) broken inline code targeting `hintStoriesCount`, `hintFlowsAmount` etc. — none of these IDs exist in HTML, all assignments silently failed, (2) correct `populateTeasers()` async function targeting `teaserStoryCount`, `teaserFlowSub` etc. The broken inline code was a dead duplicate. Fix: removed broken `hint*` code; correct `populateTeasers()` handles all. Verify: `teaserStoryCount` must show e.g. "4 stories" not "—".

**Signal/Track teaser containers empty → DOM-scraping from other pages (v22.44 fix).** The Signal teaser used `document.querySelectorAll('#signalGrid .signal-card')` — `#signalGrid` only exists on `signal.html`, never on the homepage. The Track teaser used `document.getElementById('trackRecord')` — only exists on `track.html`. Both selectors returned null/empty on the homepage → containers rendered blank. This is a design anti-pattern: **homepage teasers must NEVER DOM-scrape from dedicated product pages.** Fix (v22.44): Signal teaser now uses `getJSON(getFlowsPath())` to derive regime badge, contradictions count, and top flow directly from the flows API. Track teaser uses `getTrackRecord()` from localStorage (win/loss stats + recent bets). The Stories and Flows teasers already used API data correctly. Trades teaser uses hardcoded `ANCHOR_ASSETS` (acceptable — it's a JS const, not DOM-scraping). Verify: all 5 homepage teaser containers must show non-empty content within 3 seconds of page load.

**GCS CDN revalidates every request (max-age=0, must-revalidate — set in v22.12).** After deploy, changes are instant. Verify with `gsutil cp gs://www.lagazzettadikyiv.com/index.html -`, not browser. If for any reason the CDN is serving stale content, re-apply metadata: `gsutil setmeta -h "Cache-Control:public, max-age=0, must-revalidate" gs://www.lagazzettadikyiv.com/index.html gs://www.lagazzettadikyiv.com/app.js gs://www.lagazzettadikyiv.com/styles.css`.

**execute_code read_file is DANGEROUS — TWO failure modes (CRITICAL v23.5).** The `execute_code` tool's `read_file()` is NOT safe for bulk edits. It has two independently catastrophic failure modes:

**Failure mode 1: Silent truncation (v23.0).** `read_file()` defaults to 500 lines. On a 2600-line styles.css, it silently returns 500 lines — writing those 500 lines back destroys 2100 lines. The truncation is invisible until `git diff --stat` shows massive deletions.

**Failure mode 2: Line-number embedding (v23.5).** `read_file()` returns content formatted as `LINE_NUM|CONTENT\n` (e.g., `153|  <div class="masthead">`). Writing this string directly via `write_file()` embeds line numbers into the file as literal text, producing content like `<div class="masthead">153|  <div class="masthead">`. The file is corrupted on-disk. If committed (via `shipit.sh` Stage 7), git stores the corrupted version, requiring `git checkout <previous-commit> -- <file>` to recover. The corruption is often invisible in cursory reads because the line numbers look like part of the formatting.

**The safe pattern:** Use `terminal()` for inline Python scripts that read/write files via standard `open()`. NEVER pass `execute_code`'s `read_file()` output to `write_file()`.

```bash
# SAFE: terminal + Python heredoc
python3 << 'PYEOF'
with open('index.html', 'r') as f:
    html = f.read()
# ... modifications ...
with open('index.html', 'w') as f:
    f.write(html)
PYEOF

# SAFE: sed for mass CSS fixes
sed -i '' 's/font-size: 7px/font-size: 10px/g' styles.css
sed -i '' -E 's/(font-size: )8px;/\110px;/g' styles.css
sed -i '' -E 's/border-radius: [34]px;/border-radius: 2px;/g' styles.css
```

After any file edit, verify: `grep -c 'LINE_NUM|' file.html` (should be 0 — catches line-number corruption), `wc -l file` (should match expected).

**test_platform.py regex pitfall (v23.5).** The regex `r'<(script|style)[^>]*>.*?</\1>'` with `re.DOTALL` fails to strip script tags from complex HTML files (e.g., event_horizon.html with inline JS). The poison-value scan flagged legitimate JS guards (`!== undefined`, `!== null`, `[]`) as failures. Fixed by switching to BeautifulSoup:

```python
soup = BeautifulSoup(html, 'html.parser')
for tag in soup.find_all(['script', 'style']):
    tag.decompose()
content = soup.get_text()
```

The `patch` tool frequently fails on `app.js` with "Escape-drift detected: old_string and new_string contain the literal sequence '\\\\\\\\\\\"' but the matched region of the file does not." This is a tool-call serialization artifact where quotes get prefixed with spurious backslashes. Solution: use `execute_code` to call the Python `hermes_tools.patch()` function directly, where the strings pass through unchanged. Full recipe: `references/escape-drift-patch-workaround.md`.

**Cron workdir misconfiguration → half the pipeline runs against wrong repo.** The most devastating silent failure discovered in v22.11: 5 of the 10 Gazzetta cron jobs had `workdir` set to `~/.hermes/hermes-agent/gazzetta-di-kyiv/` (the Hermes internal copy) instead of `/Users/alexstocchi/projects/gazzetta-di-kyiv/` (the actual project). Both directories have `scripts/` with the same filenames, so the jobs ran without errors — but against stale/missing data. The telltale sign: Phase 3 daily brief returning `NoneType`/`Broken pipe` errors, and flows/devvit pipelines producing content that looked correct but was days old. Diagnosis: `cronjob action=list` → check `workdir` field on every Gazzetta cron. The correct project root is `/Users/alexstocchi/projects/gazzetta-di-kyiv/`. The old path `~/.hermes/hermes-agent/gazzetta-di-kyiv/` is now a **symlink → canonical path** (converted June 2026 after phantom-script audit). When creating new crons for Gazzetta, ALWAYS set `workdir=/Users/alexstocchi/projects/gazzetta-di-kyiv`. If updating crons, also update any hardcoded paths in the `prompt` field.

**Phantom scripts → silently fabricated cron output.** Cron jobs that tell LLM agents to `python3 scripts/X.py` will ALWAYS produce `{"ok": true}` even when the script doesn't exist. The LLM fabricates plausible JSON rather than surfacing a FileNotFoundError. Discovered June 2026: 6 of 7 scripts were missing, all 17 crons reported ok. Detection: script existence audit (see gazzetta-ceo-overseer, check 7). Fix: reconstruct scripts or update cron prompts. NEVER trust cron output alone — verify script files exist on disk.

**Deploy cron silently overwrites ALL manual GCS edits — CRITICAL (v22.15).** The deploy cron (`f9a24ed64aa5`) runs `gazzetta_deploy_to_gcs.sh` every 15min, syncing `site/` → GCS with `gsutil -m rsync -d -r`. ANY file you upload directly to GCS via `gsutil cp` gets wiped within 15 minutes when the cron syncs the stale `site/` copy over it. This is the #1 reason translations, HTML fixes, and JS patches appear to "revert" — they were never saved to the canonical `site/` directory. **Deploy cron silently overwrites ALL manual GCS edits — CRITICAL (v22.15, upgraded v22.44).** The deploy cron (`f9a24ed64aa5`) now runs `shipit.sh` every 60min (was every 15min raw gsutil rsync before v22.44). The cron runs the FULL pipeline: intel_to_stories → local sync → build_site → build_hashed_assets → GCS deploy → deploy_report → git push. This means ANY uncommitted changes in the project root get committed and pushed automatically. Keep the working tree clean — commit or stash before the cron fires. The old rsync-only cron was the #1 reason manual GCS uploads appeared to "revert.": `gsutil cp site/FILE gs://www.lagazzettadikyiv.com/FILE && gsutil setmeta -h 'Cache-Control:max-age=0,must-revalidate' gs://www.lagazzettadikyiv.com/FILE`. After every deploy, verify the GCS copy matches the source: `diff <(gsutil cat gs://www.lagazzettadikyiv.com/index.html) site/index.html`. If they differ, the cron hasn't run yet or the deploy script has a stale path.

### Safety Branch Drift — Regression Recovery (v22.42+, June 2026)

**The disaster:** Features developed across multiple commits (v22.21–v22.27) on a parallel branch (`infra-upgrade-2026-06`) were never merged back to `main`. When the working tree was rebuilt from `main`, 98 files and 9,226 lines of production code vanished: `flow-nodes.html` (1,178 lines), `sector.js`, nav indicators, WCAG color fixes, frameless design enforcement, product-nav, i18n attributes, content-hashed assets, and more. The live site regressed silently — hero indicators blank, buttons non-functional, containers empty.

**Root cause:** Branch switch without merge-back. The infrastructure work created a divergence that grew to 5,145 deletions on `main` relative to the infra-upgrade branch.

**Recovery procedure (learned from this disaster):**
1. `git diff main..<safety-branch> --stat` — identify all missing files
2. `git checkout <safety-branch> -- <critical-files>` — restore specific files (don't merge entire branch if it has diverged config)
3. Update `config.yaml` pages/assets/data_files for any new files (flow-nodes.html, sector.js, flow_nodes.json, etc.)
4. Update `shipit.sh` SYNC_FILES array for any new pages
5. Run `refresh_context.py` — §4.5 pre-deploy check verifies structural integrity AND HTTP 200 on all product pages
6. `bash shipit.sh` — full deploy

**Prevention guardrails (implemented June 2026):**
- **`refresh_context.py` §4.5 PRE-DEPLOY CHECK**: Regex-verifies critical HTML elements exist in `site/` (hero section, product-nav, container collapsibles, onboarding overlay, storyFreshness, flowFreshness). **§4.5c:** Verifies HTTP 200 on all 7 product pages (flow-nodes.html, event-horizon.html, stories.html, flows.html, signal.html, track.html, trades.html). Blocks deploy (exit code 1) if any element missing or any page returns non-200.
- **`scripts/safe_git.py`**: Pre-commit auto-backup — copies all uncommitted files to `.backup/<timestamp>/` before destructive git operations (checkout, reset, revert). `.backup/` is gitignored.
- **Pre-deploy working-tree check**: `refresh_context.py` §4.5a warns if uncommitted files exist.
- **Config.yaml**: Central configuration — pages, assets, data files, GCS, cache policies. shipit.sh SYNC_FILES reads from here. When adding new pages or assets, update config.yaml FIRST.
- **`prd.md`**: Product Requirements Document — 3 personas (Quant, C-Suite, Degen), feature matrix, data pipeline architecture, design contract, quality gates. Update when adding features or changing UX.

**Never again:**
- Don't create parallel branches without an explicit merge-back plan
- Don't rebuild working trees from a single branch when parallel work exists
- Always run `refresh_context.py` after any git operation that could change files
- If `refresh_context.py` shows PRE-DEPLOY BLOCKED, investigate before deploying\n\n**Force-overwrite i18n keys when fixing translations.** Code like `if k not in ru: ru[k] = v` silently skips existing keys with WRONG values. If `buy` exists as `"BUY"` (untranslated), the guard skips it — translation stays broken. Always use unconditional assignment: `ru[k] = v`. Verify with `python3 -c "import json; d=json.load(open('site/i18n_ru.json')); print({k:d[k] for k in ['buy','sell','watch']})"` after updating.\n\n**CDN caching causes focus groups to evaluate stale pages.** GCS CDN revalidates every request (max-age=0, must-revalidate — v22.12). Changes are instant — but verify the origin first: `gsutil cp gs://www.lagazzettadikyiv.com/index.html - | grep '<new-element>'`. Only spawn the focus group after confirming the origin has the updated content.

**All containers collapsed by default since v20.1.** The front page is a lobby — hero section + 3 descriptive sentences + footer. Users choose what to open based on orientation. The v19 pattern of expanding THE ANCHOR by default was retired after the user said it confused new visitors who don't understand PDR/asset projections. Descriptive sentences (`.container-desc`, visible when collapsed, hidden when expanded) guide first-time visitors.

### Two Story Types — Field Set Differences (v22.38)

Stories come from TWO different pipelines with different field sets:

| Field | Intel Pipeline (`intel_to_stories.py`) | Editorial Writer (cron `011c8be0b17c`) |
|-------|--------------------------------------|----------------------------------------|
| `generated_at` | ✓ Present (per-story) | ✗ Missing |
| `timestamp` | ✗ | ✗ |
| `date` | ✗ | ✗ |
| `capital_flow` dict | ✓ With amount_b, direction, etc. | ⚠ Simplified or absent |
| `story_id` | 100+ chars (from Telegram intel) | Shorter, editorial-format |

**Impact:** The story detail page's time badge depends on `story.timestamp || story.date || story.generated_at`. Editorial writer stories have NONE of these fields → time badge renders empty. Fix: ensure ALL stories get `generated_at` from the document-level timestamp during pipeline processing.

**Story ID URL constraint:** Intel pipeline story IDs can exceed 100 characters (e.g., `n21_multi_pillar__eu_21st_sanctions_package_90_banks_11_crypto_platforms_banned...`). URLs exceeding ~80 chars cause browser truncation and 404s on story pages. Fix: `intel_to_stories.py` must cap story IDs at 80 chars: `story_id[:80]`.

### Data Contract — Every Story MUST Have `generated_at` (v22.38)

Before deploy, verify:
```bash
python3 -c "import json; d=json.load(open('site/data/stories.json')); missing=[s['story_id'][:40] for s in d['stories'] if 'generated_at' not in s]; print(f'Missing: {len(missing)}') if missing else print('All stories have generated_at ✓')"
```

Auto-fix in pipeline: add `generated_at` from document-level timestamp to any story missing it.

**`ui_contract_check.py` must match current labels.** After renaming hero stats or masthead classes, grep the check script and update it. After v22.7 (Directional alignment → Flow conviction): check updated. After v22.8 (Flow conviction → Confidence): `if 'Confidence' not in html: issues.append(...)`. After v22.7 (masthead-fox → masthead-caduceus): update any CSS selector or HTML check referencing the old class name.

**Precision/numerical changes require professional review BEFORE deploy.** Any change to ATR values, confidence model weights, stop multipliers, track record logic, or data formulas must be audited by 3 professional personas (CFA charter holder, portfolio manager, fintech data engineer) through a gambler's lens BEFORE shipping. Use `delegate_task` with 3 parallel subagents. This is NOT optional — v20.16 shipped with 4 bugs that professional review caught (settlement loop missing, ADA target inverted, stake unit label wrong, WATCH assets getting BUY stops). The workflow: implement → spawn CFA+PM+Fintech auditors → fix all bugs found → deploy. See `gazzetta-precision-pipeline` skill for audit dimensions and scoring.

**YouTube Shorts without subtitles — derive from context.** When a user sends a YouTube Short with disabled captions (youtube-transcript-api returns TranscriptsDisabled), don't get stuck trying to extract audio. Use title, comments, channel context, and historical knowledge to derive the relevant insight. The user is sending the Short for its thesis connection, not for verbatim transcription. Persepolis 1971 celebration → capital destination analysis (vanity spend vs. productive investment as regime stability signal).

**Flow positioning all "hedging" → generate_flows.py defaults.** Fixed in v22.8: `positioning = cf.get("positioning", "hedging")` defaulted every flow to "hedging" because story capital_flow dicts lacked a positioning key. Fix: derive from direction + magnitude at line 263 of generate_flows.py. If reverting or rewriting flow generation, NEVER default to a single positioning value — always derive from actual flow data.

- **Python execution:** ALWAYS use `.venv/bin/python` for all Python scripts in this project. The venv is at the project root with requests, bs4, and pyyaml installed. Never use bare `python3` — it may resolve to a different Python with missing dependencies. The existing `pipeline_chain.sh` still uses bare `python3` (legacy) but `shipit.sh` and `refresh_context.py` enforce `.venv/bin/python`.
- Image placement techniques: see `references/image-slot-integration.md` — background fill, ornament strips, legibility overlays, gradient replacement
- Image/screenshot review via vision API: see `references/vision-and-screenshots.md` — current vision provider status
- Capital flow methodology: see `gazzetta-capital-flows` skill
- Mobile progressive disclosure: see `references/mobile-progressive-disclosure.md` — TL;DR+Hook formula, industry patterns (FT/Bloomberg/Robinhood)
- Asset icon system: see `references/asset-icon-system.md` — ASSET_ICONS map, institutional color tokens, teaser card integration, pitfalls
- Orphan auto-linking: see `references/orphan-auto-link-v23.6.md` — asset_class matching recipe, 24→0 fix
- Sidebar pre-population: see `references/sidebar-pre-population-v23.6.md` — injecting live data at build time
- Infrastructure scripts (v23.0): see `references/infrastructure-scripts-v23.md` — gcp_monitor.py, marketing_bot.py, SEO pages, font-size floor
- Three-column Golden Ratio Grid (v23.5): see `references/three-column-golden-ratio-grid.md` — layout spec, responsive breakpoints, side-column populator
- Market data & Asymmetry Score (v23.12): see `references/market-data-asymmetry-v23.9.md` — yfinance integration, signal.json injection, formula v2.0 mathematical delta
- Math Sanity Check (v23.12): see `references/math-sanity-check-v23.12.md` — formula derivation, test vectors, diagnostic traces
- SEO strategy: see `references/seo-strategy.md` — multi-page static GCS site, artefacts, pipeline integration
- Capital hinting strategy: see `references/capital-hinting-strategy.md` — information scent research, hint implementation, competitor patterns
- Product management guardrails: see `gazzetta-product-management` skill
- i18n implementation: see `references/i18n-implementation.md` — full recipe for adding multi-language support to static GCS site

**Triangulation container empty after page load → boot race condition.** `renderTriangulation()` called synchronously after `appendStoryCard()` in `boot()` may run before the DOM is ready because `insertAdjacentHTML` isn't always instant. Fix (v22.8): `scheduleTriangulation()` retries up to 10× at 300ms intervals via `setTimeout`, checking `document.querySelectorAll('.card[data-story-id]').length > 0`. Also, `updateMasthead()` is now called at the START of `boot()` — before any async `await` — so the masthead timestamp never shows `—`. Both fixes in `app.js`.

## Institutional Positioning Labels (v22.12+)

The raw positioning codes (`accumulating`, `distributing`, `hedging`) are institutional jargon — meaningless to retail users. The `positionLabel()` function in `app.js` (line 283) translates them into VARIED self-explanatory labels using a cycling variants system:

### Variant system (v22.15+ — i18n-aware)

Instead of one static label per positioning type, the `POSITION_VARIANTS` const contains **3 variants per positioning type**, each stored as a `{key, fallback}` object for i18n. The `positionLabel()` function cycles deterministically AND translates at render time via `i18n.t(v.key, v.fallback)`:

| Positioning | i18n keys | English fallback |
|------------|----------|-----------------|
| `accumulating` | `pos_accumulating_1`, `_2`, `_3` | "Institutions buying — net inflow", "Capital flowing in — accumulation detected", "Positioning long — institutional demand" |
| `distributing` | `pos_distributing_1`, `_2`, `_3` | "Institutions selling — net outflow", "Capital flowing out — distribution detected", "Reducing positions — institutional selling" |
| `hedging` | `pos_hedging_1`, `_2`, `_3` | "Mixed signals — hedging both sides", "Direction unclear — capital in standby", "Balanced flows — no clear direction" |

The old pattern of 7+ variants per type was rolled back to 3 in v22.15 — the i18n complexity of maintaining 19 translated strings outweighed the variation benefit. The `{key, fallback}` object pattern (instead of calling `i18n.t()` at definition time) ensures labels update on language switch.

Used in two places: flow items (Container 2) and expanded story card CAPITAL FLOW blocks. The `generate_flows.py` script stores the raw codes in `flows.json`; the JS presentation layer handles translation and variation. Never show raw `accumulating`/`distributing`/`hedging` to users — always run through `positionLabel()`.

### Flow aggregation (v22.12+)

Duplicate flows (same headline + direction + amount, different story_ids) are aggregated into single rows with a `catalyst-badge` showing the count. The `aggregateFlows()` function in `app.js` runs before `renderCapitalFlows()`. CSS: `.catalyst-badge` — 8px gold uppercase pill with 1px border, `margin-left: 6px`. Example: 3 identical "$1.0B flowing into defense" flows → 1 row with `3 CATALYSTS` badge. This fixed a credibility problem flagged by the financial journalist focus group persona: "Duplicate rows destroy credibility."

Standard label before v22.12: `"Institutional positioning: accumulating"` — removed. "Institutional" was jargon; the new labels tell the user WHAT the money is doing.

The five containers MUST hold only their designated content. Cross-contamination is a logical leak that destroys the site's premise→conclusion chain:

| Container | Holds ONLY | NEVER contains |
|-----------|-----------|----------------|
| 1. What the capital is saying | Story cards with They Say/Reality/THE PLAY | Flow data, anchor positions, triangulation scores |
| 2. Where the smart money is going | Clean `$XB flowing into/out of asset` flow items | Story headlines, narrative text, "stories in play" |
| 3. Your trades this week | Anchor assets with entry/target/stop | Story summaries, flow projections |
| 4. The Signal | Triangulation scores cross-referencing C1+C2+C3 | New stories or flows not derived from C1-C3 |
| 5. Track Record | Settled bet P&L, win rate | Unresolved predictions, editorial commentary |

**Common violation:** Flow headlines using story claims as display text (e.g., "SpaceX IPO oversubscription at $300B+ valuation triggers..." appearing in Container 2 instead of "$300.0B flowing into tech"). This happens when `generate_flows.py` uses the story's `claim` field verbatim instead of extracting clean flow data. The Logic Professor persona in `focus-group-review` catches this — spawn it when container boundaries are suspect.
