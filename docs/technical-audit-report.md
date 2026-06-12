# Gazzetta di Kyiv — Technical Systems Architecture Audit
**Reviewer:** Systems Architect (Refinitiv/Bloomberg)  
**Date:** 2026-06-12  
**Context:** Phase 1 findings — 245 stories, 199 flows, static GCS hosting

---

## Architecture Overview (Current State)

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRODUCTION (live)                        │
│                                                                 │
│  GCS Bucket (lagazzettadikyiv.com)                              │
│  ├── index.html          (22.5KB — SSR shell, no content)       │
│  ├── app.1683dea1.js     (129KB — all rendering logic)          │
│  ├── styles.6e5321ba.css (74KB — full design system)            │
│  ├── i18n.7dcc40be.js    (3.4KB — i18n runtime)                │
│  ├── data/                                                      │
│  │   ├── stories.json    (1.5MB — 245 stories, $0B total)       │
│  │   ├── flows.json     (215KB — 199 flows, $3,074B tracked)   │
│  │   ├── market_prices.json (57KB)                              │
│  │   ├── market_regime.json                                     │
│  │   └── living_stories.json                                    │
│  ├── stories.html, flows.html, signal.html, trades.html,        │
│  │   track.html, event_horizon.html, flow-nodes.html            │
│  └── ru/ → 404                                                  │
│                                                                 │
│  CDN: Google Cloud CDN (max-age=3600 for assets, 0 for HTML)   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       PIPELINE (local macOS)                     │
│                                                                 │
│  SQLite DB (gazzetta.db) ← 3 ingestion paths:                   │
│  ├── Telegram Monitor → intel_to_stories.py                     │
│  ├── OSINT Collector → fetch_intel.py → approve_draft.py        │
│  └── Manual drafts                                              │
│                                                                 │
│  └── db_to_json.py → stories.json + flows.json                  │
│                        (appends to site/data/)                  │
│                          ↓                                      │
│  build_site.py → site/ (static HTML/JS/CSS)                     │
│        ↓                                                        │
│  shipit.sh → gsutil rsync → GCS                                 │
│        ↓                                                        │
│  verify_reality.py → post-deploy audit                          │
│                                                                 │
│  Cron schedule: every 60min (pipeline) + every 30min (health)   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (vanilla JS, no framework)           │
│                                                                 │
│  Boot sequence:                                                  │
│  1. <body> rendered (empty containers, loading skeletons)        │
│  2. i18n.js loads (inline <script> at end of <body>)            │
│  3. app.js loads (regular <script>, NOT async/defer)             │
│  4. boot() runs:                                                  │
│     a. Wait for i18nReady event (5s timeout)                     │
│     b. renderAnchor(), renderTrackRecord()                       │
│     c. updateMasthead()                                         │
│     d. await fetchFlows() (AJAX)                                 │
│     e. await market_prices.json (AJAX)                           │
│     f. await living_stories.json → stories.json (AJAX chain)     │
│     g. appendStoryCard() for each story                          │
│     h. populateSidebar() → more AJAX fetches                     │
│     i. setTimeout → populateTeasers() → even more AJAX          │
│     j. setInterval(fetchFlows, 5min)                             │
│     k. setInterval(pollLivingStories, interval)                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Technical SWOT

### Strengths

| # | Strength | Impact |
|---|----------|--------|
| S1 | **Pure JAMstack on GCS** — zero server operational burden. No VMs, no containers, no autoscaling. $0-5/mo hosting. | Cost efficiency |
| S2 | **Sophisticated data pipeline** — SQLite-backed with 3 ingestion paths (Telegram, OSINT RSS, manual). DB-to-JSON compilation with entity extraction, paradigm tagging, multi-persona enrichment. | Data architecture |
| S3 | **Semantic triangulation engine** — stories → flows → assets → positions → trades linked in a unified graph. Cross-entity references maintained. | Differentiation |
| S4 | **Computed confidence + ATR stops** — 4-factor confidence model (flow magnitude, pace, positioning, contradiction) with volatility-adjusted stops. Institutional-grade analytics. | Core product value |
| S5 | **Comprehensive cron ecosystem** — 5 active jobs covering pipeline, health check, CEO oversight, market data, session review. Self-monitoring infrastructure. | Operational maturity |
| S6 | **Post-deploy verification protocol** — `verify_reality.py` with 3-lens check (retrospective, introspective, extrapolative). Reality gap detection on every deploy. | Quality assurance |
| S7 | **Good HTTP performance** — DNS 2ms, TCP 29ms, SSL 95ms, TTFB 259ms, total 269ms. GCS edge delivers fast responses globally. | Latency |
| S8 | **CORS + retry logic in fetch** — AbortController for stale fetch cancellation, exponential backoff (1s-2s-4s-8s), 2 retries per fetch. Network resilience. | Frontend robustness |

### Weaknesses *(ranked by severity)*

| # | Severity | Weakness | Evidence |
|---|----------|----------|----------|
| W1 | **CRITICAL** | **No server-side rendering — JS-dependent blank page.** Without JavaScript, the site shows 0 story cards, 0 flows, 0 content. The 22.5KB HTML is 19.4% inline SVG masthead art, not content. | HTML body content = 18.9KB of structure, ~4.3KB masthead SVGs, 0 story cards. Everything populated via `appendStoryCard()` in JS. |
| W2 | **CRITICAL** | **Data quality collapse — 245 stories have $0 amount_b, 0% confidence.** The entire capital flow tracking system reports zero dollars and zero confidence. All stories have defaulted to null/zero values. | `total amount_b: $0`, `confidence values: [0]`. 490 data quality issues flagged (245 stories × 2 fields). |
| W3 | **HIGH** | **Flows DRY — flows separated from stories.json.** The `stories.json` has no `flows` key despite having 245 stories. Flows live in a separate `flows.json` requiring a 2nd HTTP fetch. Story ↔ flow cross-linking happens client-side via `refreshFlowStoryLinks()`. | `stories.json`: `Has flows key: False`. Separate `flows.json` (215KB) fetched asynchronously. |
| W4 | **HIGH** | **/ru/ is completely broken (404).** The Russian-language version returns 404 for all pages. The sitemap indexes `/ru/` URLs that don't resolve. SEO and accessibility to Russian-speaking audience is zero. | `curl -sI https://www.lagazzettadikyiv.com/ru/` → `HTTP/2 404`. |
| W5 | **HIGH** | **No build-time static rendering — 6 fetches required for first meaningful paint.** The critical path: HTML → CSS → i18n.js → app.js → fetchFlows → fetchMarketPrices → fetchLivingStories → fetchStoriesJSON → DOM rendering. Minimum 4 network round-trips before ANY story content appears. | `boot()` has await chain: fetchFlows() → fetch prices → living_stories.json → stories.json → appendStoryCard(). |
| W6 | **HIGH** | **Cron job history of silent wipe — no persistence guarantee.** All 12 cron jobs were wiped by a scheduler restart on June 11 2026. Site froze for 12+ hours. No automatic recovery. | KB documented: "Gateway PID survived, jobs.json cleared. 0 jobs. Site froze for 12+ hours." |
| W7 | **MEDIUM** | **Root/site file duplication causes silent drift.** 17 HTML/JS/CSS files exist in both project root AND `site/`. Edits to root don't auto-propagate to `site/`. Only `index.html` currently differs. | KB documented: "Root = edit target, site/ = deploy target. Any edit to root without copying to site/ won't deploy." |
| W8 | **MEDIUM** | **Triple script locations — canonical source unclear.** Scripts live in: `scripts/` (39 files, 5821 LOC), `ops/` (34 files, 1212 LOC), `~/.hermes/scripts/gazzetta_*` (20 files). No single source of truth. | KB documented, confirmed by inspection. |
| W9 | **MEDIUM** | **129KB monolithic JS bundle — no code splitting.** All functionality (masthead, cards, sidebar, flows, trades, track record, event horizon, i18n, analytics, share buttons) lives in one file. Any change requires full re-download. | `app.1683dea1.js` = 129,000 bytes. CSS = 74KB. Total frontend payload = 206KB. |
| W10 | **LOW** | **Horizon page returns 404.** `https://www.lagazzettadikyiv.com/horizon.html` → 404. Navigation links to it exist on all other pages. | curl confirmed. |
| W11 | **LOW** | **No structured SEO metadata per page.** All pages share the same `<title>` and `<meta description>` — no per-story/per-flow meta tags. OpenGraph tags are generic site-level. | Single `<title>` across all 6 pages. No structured data for stories/flows. |
| W12 | **LOW** | **9 hardcoded masthead SVGs = 4.3KB (19.4% of HTML).** Replaced every deploy, never cached independently. Inline SVGs cannot be cached by the browser across page loads. | Every HTML page inline-contains identical 4.3KB of SVG markup. |

### Opportunities

| # | Opportunity | Potential Impact |
|---|-------------|-----------------|
| O1 | **Migrate to SSG (Astro/Next.js SSG)** — pre-render all 245 stories as static HTML at build time. Zero JS needed for initial content visibility. | Time-to-content: 3s→300ms. SEO: indexed story content. Core Web Vitals pass. |
| O2 | **Server-side rendering for hero stats** — inject computed hero values (stories tracked, capital tracked, model confidence) into HTML at build time. No JS fetch needed for above-fold stats. | First meaningful paint: 5 fetches → 0 fetches. |
| O3 | **Code-split JS by page** — index.js (10KB for homepage), story-card.js (20KB shared), flows-page.js (30KB), trades-page.js (15KB). Defer non-critical JS. | JS payload per page: 129KB → ~30KB. |
| O4 | **Implement ISR or serverless API** — use Cloudflare Workers or Vercel Edge for dynamic data fetching without full-page reload. Live price data without client-side polling. | Real-time data with 0ms client-side latency. No 5-min poll interval. |
| O5 | **Automate /ru/ deployment** — fix the ru_sync_gate ordering issue and make /ru/ part of the normal deploy pipeline, not a post-hoc copy step. | Bilingual reach. SEO in Russian. 50%+ addressable audience expansion. |
| O6 | **CI/CD pipeline with preview deployments** — deploy PR previews to GCS subdirectories. Rollback via `gsutil rsync` from git tags. | Deploy confidence: manual shipit.sh → push-button rollback. |
| O7 | **Convert to PWA** — service worker for offline reading, push notifications for new flows, add-to-homescreen. | User retention + notification channel independent of Telegram. |
| O8 | **API layer** — expose stories/flows/assets via REST/GraphQL API. Enable programmatic access, embed widgets, feed financial terminals. | New distribution channel + product surface area. |

### Threats

| # | Threat | Severity | Mitigation Potential |
|---|--------|----------|---------------------|
| T1 | **JS hard failure = complete site blackout.** Any JS error in boot sequence (i18n race, null DOM element, fetch failure) leaves users with empty masthead + loading skeletons. | **CRITICAL** | SSR or noscript fallback |
| T2 | **GCS single-bucket dependency.** All assets, data, and HTML live in one GCS bucket. No multi-region failover configured. Bucket deletion/access-revocation = total site loss. | **HIGH** | Multi-region bucket, IaC backup |
| T3 | **Scheduler restart wipes cron jobs silently.** Known issue — no persistence for cron job definitions. Gateway restart = pipeline death with no alert. | **HIGH** | Cron job definition as code (declarative config) |
| T4 | **CDN serving stale data due to max-age=0 on HTML, 1hr on assets.** HTML is not cached, but assets are cached 1hr. If HTML references old hashed assets after a rollback, 404 errors for 1hr. | **MEDIUM** | Inline critical CSS/JS |
| T5 | **Content distribution risk from 6 separate HTML files with independently-maintained nav.** Navigation fragmentation caused dead links in the past (horizon.html vs event_horizon.html). | **MEDIUM** | SSG with shared nav component |
| T6 | **`amount_b` data pipeline failure breaks core value prop.** If the amount computation pipeline produces $0, every story card shows "capital flow" with no dollar amount — product is non-functional. | **CRITICAL** | Data validation gate before deploy |
| T7 | **macOS → Linux env mismatch in shell scripts.** `date -Iseconds` works on GNU but not BSD. Cron runs on macOS, would break on Linux migration. | **LOW** | Shellcheck in CI |

---

## 2. TOP 5 Technical Bottlenecks

### #1: Zero Server-Side Rendering (CRITICAL)
**What:** The site is 100% JS-dependent. The HTML sent to the browser is a shell with empty `<div>` containers. All 245 story cards, 199 flows, sidebar data, and hero stats are populated by JS after 4-6 sequential AJAX fetches totaling ~2MB of JSON.
**Why it's a blocker:** 
- First contentful paint shows only masthead + loading skeletons
- First meaningful paint requires 2-5 seconds on 4G (6 sequential fetches)
- SEO = zero. Googlebot won't wait for JS. Every story is invisible to search.
- No graceful degradation: JS error = completely empty page
- Core Web Vitals (LCP, CLS, INP) all fail

### #2: Data Quality Pipeline Collapse (CRITICAL)
**What:** 245 stories all report `amount_b: $0` and `confidence_pct: 0`. The entire capital-flow tracking product is reporting zero dollars with zero confidence.
**Root cause:** The `db_to_json.py` pipeline or the SQLite DB has lost or nulled the amount and confidence fields. Stories are being generated/exported without the financial data that makes the product valuable.
**Why it's a blocker:**
- Core value prop ("track capital flows") is broken
- Every story card shows "—" where a dollar amount should be
- The entire product is a shell without financial data
- Users see 245 stories with no dollar amounts → no credibility

### #3: Sequential Fetch Waterfall in Boot Sequence (HIGH)
**What:** `boot()` executes this sequential chain:
1. Wait for i18nReady event (up to 5s)
2. `await fetchFlows()` — HTTP round-trip for `data/flows.json`
3. `await fetch('./data/market_prices.json')` — HTTP round-trip
4. `await getJSON(LIVING_DATA, null)` — HTTP round-trip for `living_stories.json`
5. `await getJSON(getDataPath(), null)` — HTTP round-trip for `data/stories.json` (1.5MB)
6. Then `appendStoryCard()` for each of 245 stories (DOM manipulation)
7. Then `populateTeasers()` via setTimeout (more fetches)
8. Then `updateCumulativeStats()` (computation over fetched data)
**Impact:** ~4-6 sequential network fetches before any story content renders. On a cold cache with moderate latency, this is 3-6 seconds of blank page.

### #4: 1.5MB Unoptimized JSON Payload (HIGH)
**What:** `stories.json` is 1.5MB (compressed ~350KB) containing 245 full story objects with nested entity_tags, multi_persona objects, capital_flow dicts, paradigm_implications, etc. The client downloads the ENTIRE dataset even if the user only sees the first 10 stories.
**Impact:**
- Mobile data: 1.5MB download + 215KB for flows.json + 57KB market prices + other files = ~2MB total
- Parse time: `JSON.parse()` of 1.5MB on low-end mobile CPU = 200-500ms
- 245 DOM nodes created via `appendStoryCard()` triggers layout thrashing
- No pagination, no virtual scrolling, no lazy loading

### #5: Monolithic Deploy Pipeline with No Rollback (MEDIUM)
**What:** The deploy pipeline (`shipit.sh`) is a single script with 8 sequential stages. If stage 4 (GCS rsync) partially fails, the site is in an inconsistent state. There is no rollback mechanism — no tagged releases, no golden image, no blue-green deployment.
**Confirmed issues:**
- Stale hashed script references deployed to GCS (old hashes → 404s)
- Redirect stubs deployed instead of full pages (372 bytes → empty pages)
- `ru_sync_gate` runs at wrong stage (pre-hash instead of post-hash)
- Git merge conflict on generated artifacts (`site/data/stories.json` has `UU` status)
- No automated rollback — recovery requires manual `gsutil cp` from git history

---

## 3. Choke Points / Single Points of Failure

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  SQLite DB   │───→│ db_to_json.py│───→│ stories.json  │
│ (gazzetta.db)│    │              │    │ (data pipeline)│
└──────────────┘    └──────────────┘    └──────────────┘
       │                    │                   │
       │ SPOF #1            │ SPOF #2            │ SPOF #3
       ▼                    ▼                    ▼
  DB corruption →      Script crash →      Empty/missing
  no stories ever      pipeline stalls      JSON → blank
  exported              silently            frontend
```

### SPOF #1: gazzetta.db (SQLite single-file database)
**What breaks if it fails:** The entire data pipeline. All 3 ingestion paths write to it. `db_to_json.py` reads from it. If corrupted: zero stories, zero flows deployed.
**Risk:** No replication. No backup automated. Single file on a macOS workstation.
**Compounding factor:** The `gazzetta.lock` file suggests concurrent write access but no WAL-mode journaling observed.

### SPOF #2: db_to_json.py (single compilation script)
**What breaks if it fails:** `build_site.py` and `shipit.sh` depend on its output (`stories.json` + `flows.json`). Script crash at any stage produces incomplete JSON → deploy publishes broken data.
**Past incidents:**
- OSINT exclusion filter silently blocked all osint-source stories (170 drafts stuck)
- Draft status mismatch (`pending_review` vs `pending`) blocked 224 drafts
- Amount parsing bugs (PROCUREMENT matched as "M" → million)
- Confidence stuck at flat defaults (50/65/75)

### SPOF #3: GCS bucket (single storage backend)
**What breaks if it fails:** The entire site. Every asset, every HTML page, every data file. No replica, no CDN origin fallback.
**Failure modes:**
- Bucket deleted → site gone
- Access revoked → 403 for all visitors
- Regional outage → site down globally (GCS is multi-region, but single storage class)
- Accidental overwrite by `gsutil rsync` → no automatic recovery

### SPOF #4: Cron scheduler (single process on macOS)
**What breaks if it fails:** The entire pipeline stops. No new stories, no updated flows, no deploy. The 12-hour silent outage on June 11 2026 is the canonical example.
**Risk:** `jobs.json` is in-memory, not persisted. Scheduler restart = total wipe. No alert when jobs go missing.

### SPOF #5: boot() function (single JS entry point)
**What breaks if it fails:** The entire frontend. A single `TypeError` for a null DOM element (as happened with Flow Nodes) blocks ALL content rendering. No partial degradation — it's all-or-nothing.

### SPOF #6: Hermes Agent (single automation orchestrator)
**What breaks if it fails:** The entire automation stack — cron, pipeline scripts, CEO overseer, health checks. Hermes Agent on macOS is the linchpin that creates stories, runs the pipeline, and deploys. If it goes down, nothing runs.

---

## 4. Error Resilience Audit

### (a) GCS bucket goes down

| Aspect | Assessment |
|--------|------------|
| **User experience** | Complete blackout. All HTML, CSS, JS, data files are on GCS. No fallback CDN, no backup origin. Users see browser error page. |
| **Detection** | `gazzetta-health-check` cron (every 30m, curl homepage) would detect this on the next tick. No real-time alerting. |
| **Recovery time** | 30 min minimum (next cron tick) + manual intervention. No automated failover. |
| **Data safety** | Stories and flows exist in local SQLite DB and git history. Source data is safe — only serving is affected. |
| **Mitigation** | None currently. Recommended: Cloudflare as CDN failover, multi-region GCS bucket, or static backup to S3. |

### (b) stories.json is corrupt

| Aspect | Assessment |
|--------|------------|
| **User experience** | Blank story section — "Intelligence update in progress" placeholder shown. Sidebar may still render from `flows.json`. |
| **Detection** | `getJSON()` returns `null` → boots falls to fallback rendering path. `gazzetta-ceo-overseer` cron (every 15m) would detect via page quality check. |
| **Recovery** | `db_to_json.py` re-runs from SQLite DB. Worst case: `git checkout` previous good `stories.json` + `gsutil cp`. Past incidents show this recovery takes hours. |
| **Partial failure** | `getJSON()` has AbortController + retry (2 retries, exponential backoff). If retries exhaust, returns `fallback`. Content degrades gracefully to placeholder. |
| **Assessment** | **ADEQUATE.** The frontend has a fallback ("Intelligence update in progress") but no data validation gate before deploy. |

### (c) A JS fetch fails

| Aspect | Assessment |
|--------|------------|
| **Flows fetch failure** | `fetchFlows()` is awaited → boot blocks here. If `getJSON` returns `null` after retries, flows data is empty. Hero stats that depend on flows (confidence, contradictions) show dashes. |
| **Stories fetch failure** | `getJSON(getDataPath(), null)` returns `null` → `"Intelligence update in progress"` shown. No story cards. Sidebar may still work. |
| **Market prices failure** | Try/catch wrapped with `/* prices optional */` — graceful degradation. Trade hooks fall back to non-divergent display. |
| **Living stories failure** | Falls through to `stories.json` fallback path. Graceful. |
| **Styling/asset failure** | If `styles.css` fails to load, page renders as unstyled HTML (readable but broken layout). Font failure is cross-origin — `font-display: swap` would prevent invisible text but isn't configured. |
| **Assessment** | **GOOD for data fetches** (retry + graceful fallback). **POOR for CSS/JS** (no integrity checks, no SRI hashes, no inline critical path). |

### (d) CDN serves stale cache

| Aspect | Assessment |
|--------|------------|
| **Current cache policy** | HTML: `max-age=0,must-revalidate` (always fresh). JS/CSS: `public, max-age=3600` (1hr cache). JSON: `private, no-store` (never cached). SVGs (inline): never cached individually. |
| **Stale JS scenario** | If `app.1683dea1.js` is updated but CDN still has hash-based URLs pointing to old content, the cache-busting works correctly (hash in filename). However, if HTML references an OLD hash, the old JS is served for up to 1hr. |
| **Stale CSS scenario** | Same as JS — hash-based filenames prevent serving old CSS with new HTML, UNLESS the deploy mixed up hash references (past incident). |
| **Stale data scenario** | JSON has `no-store` — always fresh from GCS origin. Good. |
| **Detection** | No stale-content alerting. Past incidents: stale hashed refs caused 404s, not stale rendering. |
| **Assessment** | **ADEQUATE for data, MEDIUM-RISK for assets.** Hash-based cache busting works correctly when deploy is clean. The real risk is mismatched hash references during deploy (past incident). |

---

## 5. Performance Audit

### Critical Rendering Path

```
┌──────────────────────────────────────────────────────────────────┐
│               CRITICAL RENDERING PATH (CRP)                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  STEP 1: DNS lookup (2ms)                                        │
│  STEP 2: TCP connection (29ms)                                   │
│  STEP 3: TLS handshake (95ms)                                    │
│  STEP 4: ⚡ HTML download (269ms TTFB, 22.5KB)                    │
│           ↓                                                      │
│  STEP 5: Parse HTML → DOM tree                                  │
│           - 9 inline SVGs parsed (4.3KB, 19.4% of HTML)         │
│           - Masthead rendered (visible to user)                  │
│           - Empty containers created (newsCol, sidebar)          │
│           - Loading skeletons visible                            │
│           ↓                                                      │
│  STEP 6: ⚡ BLOCKING: Google Fonts CSS                           │
│           <link href="fonts.googleapis.com/css2?family=..."      │
│           → External cross-origin font CSS blocks rendering       │
│           → 2 preconnects resolve early, but still external      │
│           ↓                                                      │
│  STEP 7: ⚡ BLOCKING: styles.6e5321ba.css (74KB)                  │
│           → CSSOM construction (blocks render)                    │
│           → Large CSS file → 50-200ms parse time on mobile        │
│           → 1hr CDN cache (good after first visit)                │
│           ↓                                                      │
│  STEP 8: Parse <body> inline script (nav dropdown)               │
│           → Small (635 chars), fast                              │
│           ↓                                                      │
│  STEP 9: ⚡ BLOCKING: i18n.7dcc40be.js (3.4KB)                    │
│           ↓                                                      │
│  STEP 10: ⚡ BLOCKING: app.1683dea1.js (129KB)                    │
│            → Parse + compile 129KB JS (500-1500ms on mobile)     │
│            → boot() starts execution                              │
│            ↓                                                      │
│  STEP 11: await i18n._ready (poll every 50ms, timeout 5s)        │
│            ↓                                                      │
│  STEP 12: await fetchFlows() (HTTP round-trip)                   │
│            ↓                                                      │
│  STEP 13: await market_prices.json (HTTP round-trip)             │
│            ↓                                                      │
│  STEP 14: await living_stories.json → stories.json (HTTP chain)  │
│            ↓                                                      │
│  STEP 15: appendStoryCard() × 245 (DOM manipulation)             │
│            → Layout thrashing on every card addition              │
│            ↓                                                      │
│  STEP 16: First Meaningful Paint (estimated: 2-5s on 4G)         │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│  FIRST CONTENTFUL PAINT: ~300ms (masthead only)                  │
│  FIRST MEANINGFUL PAINT: ~2-5s (story cards visible)              │
│  TIME TO INTERACTIVE: ~5-8s (all JS parsed + executed)            │
│  LARGEST CONTENTFUL PAINT: ~3-6s (last story card rendered)       │
└──────────────────────────────────────────────────────────────────┘
```

### What Blocks First Paint

| # | Blocker | Impact | Fix Priority |
|---|---------|--------|-------------|
| 1 | **Google Fonts CSS** (external, blocking) | Blocks CSSOM construction while font CSS downloads. ~200-500ms delay on first visit. | **HIGH** — self-host fonts or use `font-display: swap` |
| 2 | **74KB styles.css** (render-blocking) | Must be fully downloaded and parsed before first paint. ~300-800ms on 4G. | **HIGH** — inline critical CSS, defer non-critical |
| 3 | **129KB app.js** (render-blocking, not async/defer) | Blocks HTML parsing entirely. Must download, parse, compile before boot() starts. ~500-1500ms on mobile. | **HIGH** — add `defer`, code-split |
| 4 | **Sequential await chain in boot()** | 3-4 sequential HTTP fetches before DOM rendering starts. ~1000-3000ms latency. | **MEDIUM** — parallelize fetches, use Promise.all() |
| 5 | **1.5MB JSON parse** | `JSON.parse()` of 1.5MB on low-end mobile = 200-500ms. | **MEDIUM** — paginate, use streaming JSON parser |
| 6 | **No SSR for above-fold content** | Hero stats, story count, and first story card all require JS. | **HIGH** — inject hero stats + first 5 stories into HTML at build time |

---

## 6. 3-Month Technical Roadmap

### Phase 1: Stop the Bleeding (Weeks 1-2)

**Goal:** Fix data quality, restore /ru/, stabilize pipeline.

| Week | Action | Tools | Success Criteria |
|------|--------|-------|------------------|
| 1 | **Fix amount_b and confidence pipeline** — trace data flow from SQLite → `db_to_json.py` → `stories.json`. Find why 245 stories have $0 amount_b and 0% confidence. Fix the SQL query or `compute_confidence()` import. | `sqlite3`, `db_to_json.py`, `gazzetta_audit_report.json` | `stories.json` has >50 unique amount_b values, >10 unique confidence values |
| 1 | **Restore /ru/ pages** — fix `detectLang()` URL path detection, fix `ru_sync_gate` ordering (post-hash stage), deploy JS/CSS to GCS `/ru/` directory. | `i18n.js`, `shipit.sh`, `gsutil cp` | `curl -sI https://lagazzettadikyiv.com/ru/` → 200 |
| 2 | **Persist cron job definitions** — move cron job configuration from `jobs.json` (volatile) to a YAML config file that auto-restores on scheduler restart. Add startup hook to verify all jobs are registered. | `hermes cron`, YAML config, startup health check | Scheduler restart → all jobs auto-recreated |
| 2 | **Add deploy validation gate** — `verify_reality.py` runs BEFORE `gsutil rsync`, not after. Block deploy if: story count < 50% of expected, any amount_b is 0, confidence values are flat. | `verify_reality.py`, `shipit.sh` | Deploy blocked 100% of times when data is corrupt |

### Phase 2: Architecture Stabilization (Weeks 3-5)

**Goal:** Eliminate SPOFs, add SSR for critical content, improve frontend resilience.

| Week | Action | Tools | Success Criteria |
|------|--------|-------|------------------|
| 3 | **SSR for hero + first 5 stories** — modify `build_site.py` to inject hero stats (story count, capital tracked, confidence) and first 5 story cards directly into `index.html` as static HTML. Stories loaded via JS are subsequent. | `build_site.py`, Python string templating | `curl` returns HTML with 5 story cards visible. JS disabled → above-fold content readable. |
| 3 | **Inline critical CSS** — extract above-fold styles (masthead, hero, first card, layout grid) and inline them in `<head>`. Defer full `styles.css` to render-blocking. | Critical CSS extraction (Penthouse/Critical), `build_site.py` | Lighthouse: Eliminate render-blocking resources. FCP < 1.0s. |
| 4 | **Self-host Google Fonts** — download Playfair Display + Source Serif 4 + Inter, serve from GCS with cache headers. Eliminate cross-origin font request. Use `font-display: swap`. | Google Fonts download, GCS upload, CSS update | No external font requests in DevTools network tab |
| 4 | **Add SRI hashes + integrity checks** — `build_hashed_assets.py` generates `integrity="sha256-..."` attributes for all external scripts and stylesheets. Fail deploy if SRI mismatch. | `build_hashed_assets.py` | Console: no SRI errors. Subresource Integrity passes. |
| 5 | **Implement rollback mechanism** — tag deployments in git (`deploy-YYYYMMDD-HHMM`). `shipit.sh` saves pre-deploy state. Rollback script: `gsutil rsync` from previous deployed hash. | Git tags, `shipit.sh --rollback` | `bash shipit.sh --rollback` restores previous state in <60s |

### Phase 3: Performance Optimization (Weeks 5-7)

**Goal:** Sub-second first meaningful paint. 90+ Lighthouse score.

| Week | Action | Tools | Success Criteria |
|------|--------|-------|------------------|
| 5 | **Code-split app.js** — split into: `index.js` (homepage rendering, 15KB), `cards.js` (story card component, 20KB), `anchor.js` (sidebar, 25KB), `analytics.js` (track record, 15KB), `shared.js` (data fetching, utils, 10KB). Each page loads only what it needs. | ES modules, Rollup/Vite | Per-page JS payload < 50KB |
| 6 | **Implement JSON pagination** — split `stories.json` into `stories-page-1.json` (20 stories), `stories-page-2.json`, etc. On scroll to bottom, fetch next page. Client-side virtual scrolling for 245 cards. | `db_to_json.py`, app.js IntersectionObserver | Initial JSON payload: 1.5MB → 150KB. Lazy load remaining. |
| 6 | **Parallelize boot() fetches** — replace sequential `await` chain with `Promise.all()`. Fire `fetchFlows()`, market prices, and stories in parallel. i18n check is non-blocking with fallback. | `app.js` boot() | All data fetches complete in 1 RTT instead of 4. |
| 6 | **Add `defer` to all scripts** — move `<script>` tags to `<head>` with `defer` attribute. Content renders before JS executes. No parser blocking. | `index.html` + all pages | Lighthouse reports 0 render-blocking scripts |
| 7 | **Add service worker for offline mode** — cache stories.json and flows.json for offline reading. Background sync for updated stories. | Service Worker API | Offline: cached stories readable. Online: updates sync. |

### Phase 4: Platform Migration (Weeks 7-10)

**Goal:** Move from build-on-deploy model to a proper static site generator.

| Week | Action | Tools | Success Criteria |
|------|--------|-------|------------------|
| 7-8 | **Evaluate SSG options** — PoC Astro vs 11ty vs Hugo for this use case. Key requirement: build-time data compilation from JSON files, not CMS dependency. | Astro, 11ty, Hugo | Working prototype with 245 pre-rendered story pages |
| 8 | **Implement SSG prototype** — story pages generate at build time (`/stories/slug.html`). Index page pre-renders with 10 stories. Dynamic content (flows, prices) still fetched client-side. | Astro/11ty | `build` command produces deployable `dist/` directory with static HTML |
| 9 | **Port pipeline to SSG** — `db_to_json.py` → SSG build step. `shipit.sh` → SSG `deploy` command. Remove `build_site.py` in favor of SSG framework build. | Astro build pipeline | `npm run build && npm run deploy` replaces 8-stage shipit.sh |
| 9 | **Add preview deployments** — branch `deploy-preview/*` deploys to `gs://lagazzettadikyiv.com/preview/*` for stakeholder review before production. | GCS subdirectories, GitHub Actions | `https://lagazzettadikyiv.com/preview/pr-123/` renders correctly |
| 10 | **Add visual regression testing** — Percy/Chromatic-style screenshot comparison on every deploy. Catch CSS regressions before they hit production. | Playwright/Screenshot CI | 0 visual regressions slipped to production in 2-week trial |

### Phase 5: Production Hardening (Weeks 10-12)

**Goal:** Enterprise-grade reliability, monitoring, and recovery.

| Week | Action | Tools | Success Criteria |
|------|--------|-------|------------------|
| 10 | **Multi-region GCS bucket** — configure GCS dual-region or add Cloudflare as CDN origin. Failover tested with manual bucket takedown. | GCS multi-region, Cloudflare | GCS region failure → Cloudflare serves cached content |
| 10 | **Add uptime monitoring** — UptimeRobot/Checkly ping every 5 minutes. SMS + Telegram alert on down detection. SLA: 99.9% uptime. | UptimeRobot, Checkly, PagerDuty | 3 consecutive failed checks → Telegram alert in <60s |
| 11 | **Implement data backup** — automated daily `sqlite3 gazzetta.db ".backup backups/gazzetta-YYYY-MM-DD.db"` + upload to separate GCS bucket. Retention: 30 days. | `sqlite3 .backup`, `gsutil cp` | `gs://lagazzettadikyiv-backups/db/` has daily snapshots |
| 11 | **Add feature flags** — simple server-side feature flags via `config.json`. Toggle dark mode, new layout, i18n beta without redeploy. | Config JSON, JS flag consumer | Toggle `features.new_layout = true` → new layout active in <5min |
| 12 | **Final hardening pass** — Lighthouse audit (target: 90+ perf, 90+ accessibility, 100 SEO), bundle analysis, a11y audit (axe-core), security headers audit (HSTS, CSP). | Lighthouse CLI, axe-core, securityheaders.com | All targets met. CSP deployed without violations. |

---

## Summary: What We'd Fix Today

If I had 48 hours to make this production-grade, in order:

1. **Fix the data pipeline** — 245 stories at $0B/null confidence makes the entire product non-functional
2. **SSR masthead + hero stats** — inject generated_at, story count, capital tracked into HTML at build time
3. **Add `defer` to all scripts** — instant win, 0 code change, eliminates render blocking
4. **Fix /ru/** — known playbook exists, just execute it
5. **Parallelize boot() data fetches** — change `await a(); await b()` → `Promise.all([a(), b()])`
6. **Persist cron jobs** — prevent another 12-hour silent outage
7. **Add deploy validation gate** — never deploy broken data again

**Status: PRE-PRODUCTION.** The conceptual architecture (semantic graph, computed confidence, ATR stops, pipeline orchestration) is impressive and differentiated. The execution (data quality collapse, JS-only rendering, monolithic bundle, /ru/ dead, cron volatility) needs hardening before this is production-grade for active users.
