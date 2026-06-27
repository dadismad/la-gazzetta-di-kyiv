# 🌐 LA GAZZETTA DI KYIV: MASTER ARCHITECTURE & CTO ONBOARDING

**Date of Record:** June 27, 2026
**System Status:** V2 "Sovereign Terminal" (Autonomous / Live)
**Founders:** Alexander Solianin (CEO/Chief Editor), Alessio Stocchi (CTO)

---

## 1. Executive Summary & Core Business Logic

La Gazzetta di Kyiv is not a news aggregator; it is an **Asymmetric Intelligence Terminal**. It measures the mathematical divergence between mainstream media narratives and institutional capital reality, outputting highly actionable, directional trade setups.

The system operates fully autonomously via a **10-minute cloud-native pipeline**. It ingests Tier-1 data, synthesizes it using advanced LLMs trained on the CEO's specific editorial voice, calculates proprietary "Contrarian Edge" (Δ Edge) metrics, and deploys a static HTML/JS frontend to Google Cloud Storage alongside automated Telegram broadcasts.

---

## 2. Infrastructure & Hosting (The "Zero-Cost" Sovereign Cloud)

| Component | Detail |
|-----------|--------|
| **Compute** | GCP e2-micro VM (us-central1-a). Fits entirely within the GCP Always Free tier. |
| **Orchestration** | `governor.py` invoked by systemd timer `gazzetta-governor.timer` (10-minute cycle). Replaces legacy cron for maximum reliability. |
| **Database** | Serverless relational SQLite (`gazzetta.db`). Acts as the absolute local source of truth. |
| **Frontend Deployment** | SPA pushed to GCS bucket via `shipit.sh` shell script. |
| **Caching Policy** | HTML: `Cache-Control: public, max-age=0, must-revalidate`. JSON endpoints: `private, no-store` — guarantees real-time data fidelity for traders. |

---

## 3. The Data & AI Pipeline (The "Truth Engine")

The platform relies on a heavily vetted, multi-tiered data ingestion system to prevent hallucinations and retail noise.

### A. Ingestion Layers

| Tier | Source | Data | Method |
|:----:|--------|------|--------|
| **1 — Macro Reality** | FRED API, CFTC SODA API | Macro-regime classification, institutional futures positioning | REST API + ZIP download (financial futures) |
| **2 — Market Reality** | yfinance → AlphaVantage fallback | Live ticker pricing, 24h deltas, VIX | Python SDK with HA cascade |
| **3 — Intelligence** | 12 curated RSS feeds + Telegram bridges | ECB Press, Financial Times, Geopolitical Futures, Bloomberg, SCMP, Al-Monitor | RSS polling + Telegram message bridging |

### B. The AI Synthesis Engine

| Role | Provider | Model | Notes |
|------|----------|-------|-------|
| **Primary** | Zhipu AI (GLM) | `glm-5.2` | Prompt-engineered with the Solianin Doctrine (S.T.I.R. Protocol). Full editorial voice. |
| **Fallback (HA)** | DeepSeek | `deepseek-chat` | Auto-triggers on rate limit, timeout, or empty response. Zero-downtime guarantee. |

**Anti-Hallucination Guards:**
- Template Rot detection: post-processing strips banned phrases ("fails to," "market unmoved," "markets shrug")
- JSON schema validation: every LLM output validated against strict schema before storage
- Narrative scoring sanity: scores outside 0.0-1.0 range rejected and re-requested
- Source anchoring: `they_say` must begin with exact source name from provided SOURCE field

### C. The Contrarian Edge (Δ Edge) — Numeric Anchoring Table

The Δ Edge score is computed by the LLM using a numeric anchoring system, not a simple formula. The LLM identifies which specific tickers moved, by what magnitude, and in which direction relative to the media narrative.

| Score Range | Criteria | Example |
|:-----------:|----------|---------|
| **0–15** | No tracked ticker moved >0.5%, OR no material connection between event and tracked assets | Cultural news with zero financial instruments at stake |
| **16–30** | Minor tension — ticker moved 0.5–1.5% against narrative direction | Oil +0.8% on OPEC cut rumor that media dismisses |
| **31–50** | Moderate contradiction — ticker moved 1.5–3% against narrative | Defense ETF -2.1% while media reports "geopolitical escalation" |
| **51–75** | Significant contradiction — ticker moved 3–5% OR 2+ tickers moved 2%+ against narrative | Gold -2.2%, Silver -4.2% on Iran deal media calls "stalled" |
| **76–100** | Extreme contradiction — broad index moved 2%+ OR sector ETF moved 5%+ opposing narrative | SMH -7.01% while media runs "AI boom accelerating" headlines |

**Reference calculation** (approximation, not the full LLM method):
```
GAP ≈ floor(10 × Σ|percentage_moves_of_contradictory_tickers|)
```
Example: URA +2.31% and NLR +2.44% both contradict → GAP ≈ floor(10 × 4.75) = 47.

**The full scoring is a weighted LLM assessment** incorporating: ticker movement magnitude, narrative-vector alignment across 12 dimensions, capital volume at stake, source credibility, and narrative saturation (existing story count). The numeric anchor provides a floor; editorial judgment provides precision. This is documented in `contradiction_synthesizer.py` lines 342–353 (scoring guide) and 296–435 (full system prompt).

---

## 4. Frontend Architecture & Design Paradigms

The frontend is a vanilla JS and HTML SPA styled with CDN-injected Tailwind CSS (`cdn.tailwindcss.com`) plus an inline `<style>` block generated by `build_frontend.py`.

### Design Tokens (v34.0 Dark Terminal)

```css
:root {
  --bg-primary:    #0A0A0F;    /* Terminal black — body */
  --bg-secondary:  #12121A;    /* Card surface */
  --bg-tertiary:   #1A1A24;    /* Expanded card / hover */
  --text-primary:  #E6E4E0;    /* Warm off-white — body text */
  --text-secondary:#9B97B0;    /* Labels, metadata */
  --gold:          #D4AF37;    /* Signal accent — tradable edge */
  --crimson:       #8B0000;    /* BREAKING alerts */
  --green:         #27AE60;    /* LONG / inflow */
  --red:           #E74C3C;    /* SHORT / outflow */
}
```

### Mobile Progressive Disclosure

Viewports <768px use CSS-hidden `<details>` tags. The default mobile card shows:
- Asset Icon + Ticker
- Δ Edge score badge (color-coded: orange ≥80, gold 60–79, grey <60)
- 1-Sentence Hook (single-line, text-overflow: ellipsis)

User must tap to expand the full trade thesis, entry/stop/target levels, and alpha trigger.

```html
<details class="story-card-hint">
  <summary class="card-hook">
    <span class="asset-icon">🏭</span>
    <span class="ticker">CAT</span>
    <span class="edge-badge edge-80">Δ 81</span>
    <span class="one-liner">Dealer glut signals 22% downside media hasn't priced</span>
  </summary>
  <div class="card-expanded"><!-- Full thesis --></div>
</details>
```

### Horizontal Navigation

Top menu uses `display: flex; overflow-x: auto; scroll-snap-type: x mandatory` for native app-like swipe on mobile. Scrollbar hidden via `scrollbar-width: none`.

### Design Constraints (Non-Negotiable)

- **No third-party JS chart libraries.** No D3.js, Chart.js, Recharts. All visualizations use vanilla SVG or Canvas.
- **Frameless.** No border-radius on containers. No box-shadows. Structure expressed through borders and color.
- **Mobile-native.** Design for 390px first. Desktop is the expanded view.
- **Gold is signal.** Gold (#D4AF37) appears ONLY where there is a tradable edge. Never decorative.

### i18n — English / Russian

- **Static UI:** English and Russian HTML pages compiled and deployed simultaneously. Russian pages served at `/ru/` routes with proper `hreflang` alternates in sitemap.xml.
- **Dynamic Content (Data Pipeline):** English stories flow through the full pipeline automatically. Russian story translation pipeline is the **next milestone** — currently English-only for dynamic trade_thesis and narrative content. See §7 for execution plan.

---

## 5. Methodological Moats (Defensibility)

### 1. Representational Proxy Portfolios (RPP)

We do not claim to track "Total Narrative Market Cap." We track **highly liquid, canonical asset pools** selected for causal relevance to each narrative. For example:

- **Tech Convergence:** QQQ, SMH, MSFT, AMZN, GOOGL — cloud + enterprise tech
- **Rate Cycle:** TLT, SHY, IEF, ZN=F, ZB=F — duration-sensitive instruments

Each proxy asset must satisfy: (a) demonstrable causal link to narrative, (b) average daily volume ≥$50M, (c) institutional accessibility, (d) statistically significant narrative beta.

This is mathematically defensible for VC due diligence. Full methodology: `docs/NMC_METHODOLOGY_PITCH.md`.

### 2. CTO State Persistence Protocol

No AI agent or engineer operates without reading and writing to `CTO_STATE.md` at the repository root. This file serves as permanent short-term memory for active bugs, architectural shifts, pipeline integrity, and session context. All 16 pipeline steps, all 26 active scripts, all VM specs, and all deployment patterns are documented here.

---

## 6. Key Scripts & File Map

| Script | Lines | Role |
|--------|:-----:|------|
| `governor.py` | — | Pipeline orchestrator (systemd timer, 10-min cycle) |
| `contradiction_synthesizer.py` | 1,104 | LLM-powered contradiction analysis (GLM 5.2 → DeepSeek) |
| `build_frontend.py` | 1,730 | SPA compiler: stories → HTML/CSS/JS |
| `telegram_broadcast.py` | 752 | 4-format Telegram dispatch (DESK WIRE, SETUP, FLOW, PULSE) |
| `calculate_capital.py` | 402 | NMC computation via RPP methodology |
| `fetch_cftc.py` | 272 | CFTC COT physical commodity positioning |
| `fetch_fred.py` | — | FRED macro series + regime classification |
| `market_reality.py` | — | Live pricing: yfinance → AlphaVantage cascade |
| `shipit.sh` | 79 | Unified build + deploy with cache header injection |

| Data File | Location | Content |
|-----------|----------|---------|
| `stories.json` | `public/data/` | 600+ stories, 6.8MB |
| `flows.json` | `public/data/` | 12 narratives with capital flow data |
| `cftc_positions.json` | `data/` | CFTC institutional positioning |
| `fred_series.json` | `data/` | FRED macro regime data |
| `gazzetta.db` | `data/` | SQLite — source of truth (4.2GB) |

---

## 7. Incoming CTO: Immediate Action Roadmap

The pipeline executes autonomously. The terminal is live. The next technical priorities:

### P0 — Operational Integrity
- [ ] **Resolve Test 156:** 155/156 assertions passing. Investigate the `energy_sovereignty` container name mismatch (typo in test or data). Clear the board to 100%.
- [ ] **Automate DB backup:** Daily `gsutil cp` of `gazzetta.db` to GCS coldline.

### P1 — Product Completeness
- [ ] **C6 Crosshair Component:** Build a 4-quadrant scatter plot (Narrative Intensity vs. Capital Flow Velocity) using **vanilla SVG** — consistent with existing node-link diagram architecture. No D3.js, no Chart.js. Reference implementation: `public/flow-nodes.html` (pure SVG node-link diagram, 13 nodes, 23 edges, Bezier routing).
- [ ] **Russian Dynamic Data Pipeline:** Auto-translate trade_thesis and narrative strings via GLM 5.2 batch translation. See execution plan below.
- [ ] **CFTC Financial Futures:** Complete integration of CFTC financial futures data (Treasuries, currencies, equity indices) via ZIP download parser — eliminates ETF AUM reliance for rate_cycle and dollar_decline narratives.

### P2 — Monetization
- [ ] **Stripe Paywall Gate:** Hide Entry/Stop/Invalidation behind premium authentication. Keep Context/Hook free for SEO and lead generation.
- [ ] **Thematic Narrative Portfolios:** Productize the 12 proxy portfolios as investable baskets.

### P3 — Scaling
- [ ] **VM Upgrade:** e2-micro → e2-medium ($25/month) for memory headroom.
- [ ] **Dockerization:** Containerize each pipeline step for reproducibility and parallel scaling.
- [ ] **Monitoring:** Add `pipeline_health` endpoint returning step-level status.

---

## 8. Russian Dynamic Data Pipeline — Technical Execution Plan

### Current State
- Static UI fully bilingual (`/ru/` routes, sitemap hreflang tags)
- Russian HTML pages exist at `ru/index.html` with proper language alternates
- Dynamic content (stories, trade theses, narrative strings) is **English-only**
- `docs/strategy.md` confirms: "Russian translation HTML done, data pipeline pending"

### Target State
Every story published in English is automatically translated to Russian within the same 10-minute governor cycle. Russian-speaking users at `/ru/` see the same content freshness as English users.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│               contradiction_synthesizer.py               │
│                                                          │
│  English story generated (GLM 5.2 / DeepSeek)           │
│         │                                                │
│         ▼                                                │
│  ┌──────────────────┐                                   │
│  │  Story written    │                                   │
│  │  to stories.json  │                                   │
│  └──────┬───────────┘                                   │
│         │                                                │
│         ▼                                                │
│  ┌──────────────────────────────────────┐               │
│  │  RU_TRANSLATION_BATCH (async queue)   │               │
│  │                                       │               │
│  │  Fields to translate:                 │               │
│  │  • headline (≤100 chars)              │               │
│  │  • they_say (≤500 chars)              │               │
│  │  • reality (≤500 chars)               │               │
│  │  • alpha_trigger (≤300 chars)         │               │
│  │  • entry_rationale (≤200 chars)       │               │
│  │  • trade_thesis.invalidation (≤200)   │               │
│  │                                       │               │
│  │  Total per story: ~1,800 chars        │               │
│  │  Estimated tokens: ~500 input + 400   │               │
│  │  output per story                     │               │
│  │                                       │               │
│  │  Provider: GLM 5.2 (batch mode)       │               │
│  │  Fallback: DeepSeek                   │               │
│  │  Max stories per batch: 5             │               │
│  │  Concurrency: 3 parallel calls        │               │
│  │  Time per batch: ~8 seconds            │               │
│  └──────────────────┬───────────────────┘               │
│                     │                                    │
│                     ▼                                    │
│  ┌──────────────────────────────────────┐               │
│  │  stories_ru.json written              │               │
│  │  (Russian language variant)           │               │
│  └──────────────────┬───────────────────┘               │
│                     │                                    │
│                     ▼                                    │
│  ┌──────────────────────────────────────┐               │
│  │  build_frontend.py — RU mode          │               │
│  │  Reads stories_ru.json               │               │
│  │  Writes ru/index.html                │               │
│  │  Writes ru/dossier/*.html            │               │
│  └──────────────────┬───────────────────┘               │
│                     │                                    │
│                     ▼                                    │
│  ┌──────────────────────────────────────┐               │
│  │  shipit.sh deploys ru/ to GCS         │               │
│  │  (same cache policy as EN)            │               │
│  └──────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
```

### Implementation Plan

| Step | File | Change | Time |
|:----:|------|--------|:----:|
| 1 | `scripts/translate_ru.py` (NEW) | Batch translation script. Reads `stories.json`, translates fields listed above via GLM 5.2, writes `stories_ru.json`. Tracks translated story IDs to avoid re-translation. | 2h |
| 2 | `scripts/build_frontend.py` | Add `--lang ru` mode. Reads `stories_ru.json` instead of `stories.json`. Outputs to `ru/` subdirectory. Same CSS, same JS, Russian text. | 1h |
| 3 | `governor.py` | Add `translate_ru` step after `synthesis` in STEPS array. Add `build_frontend --lang ru` step after main build. | 30m |
| 4 | `scripts/test_platform.py` | Add RU assertions: verify `stories_ru.json` exists, same story count as EN, no untranslated English strings in Russian fields. | 30m |
| 5 | Dry-run + deploy | Translate 5 stories, build RU frontend, verify `/ru/` pages render correctly. | 30m |

### GLM 5.2 Translation Prompt Design

```
System: You are a professional financial translator. Translate the following 
trading-desk content from English to Russian. Preserve:
- All ticker symbols (NVDA, GLD, TLT) — never translate
- All numbers, percentages, prices ($221.14, 1.35%, $87.36)
- All narrative names as proper nouns
- Trading terminology: use professional Russian trading-desk nomenclature
  (стоп-лосс, тейк-профит, лонг, шорт, волатильность, дивергенция)
- The author's first-person voice: "Я ожидаю", "Данные показывают"
- No hedging, no softening of conviction

User: Translate these fields to Russian. Return JSON with same keys, Russian values.
{field_name: "original English text", ...}
```

### Performance Guarantee

- **Max stories per 10-minute cycle:** 10 (BATCH_SIZE in synthesizer)
- **Translation time per story:** ~1.5 seconds (GLM 5.2)
- **Total translation overhead:** ~15 seconds for a full batch
- **Pipeline impact:** Negligible — governor has 10-minute cycle; translation adds <3% to cycle time
- **Fallback:** If GLM 5.2 translation fails, story publishes in English only (no blocking)

### Cost

- GLM 5.2 API: ~¥0.01 per story (~$0.0014)
- At 10 stories/cycle × 144 cycles/day = ~$2/day at full load
- Realistic: ~$0.50/day (average 3-5 new stories per cycle)

---

## A. Appendix: Solianin Editorial Voice (S.T.I.R. Protocol)

Deployed in `contradiction_synthesizer.py` system prompt. Full specification: `docs/EDITORIAL_DOCTRINE.md`.

**S — Structure:** 3 declarative thesis bullets. Directional, falsifiable claims.
**T — Tension:** Quote media consensus → undermine with market data → causal chain X→Y→Z.
**I — Instrument:** Exact ticker + LONG/SHORT/STRADDLE + entry/stop/target/invalidation levels.
**R — Risk:** One sentence on what breaks the thesis.

Voice rules: first-person authority, zero infrastructure mentions, 15–25 word sentences, no hedging.

---

*This document is the single source of truth for La Gazzetta di Kyiv's technical architecture. All incoming engineers, VC technical auditors, and AI agents must read this before operating on the codebase.*
