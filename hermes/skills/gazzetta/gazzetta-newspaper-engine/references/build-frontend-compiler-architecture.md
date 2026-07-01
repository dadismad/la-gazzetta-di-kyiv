# build_frontend.py — Multi-View SPA Compiler (v3.1, June 2026)

> **ARCHITECTURE NOTE — Phase 4 (June 2026):** The hardcoded `PILL_ORDER`/`TICKER_MAP`/`ICON_MAP`/`invalidation_threshold()` system described below is SUPERSEDED. As of v3.1, all narrative configuration reads dynamically from `narratives.json` via `load_narratives_config()`. Story grouping uses `narrative_id` (not `_container_id`). See `references/phase-4-frontend-migration.md` for the full migration detail. The sections below documenting the compiler's rendering logic, design tokens, Tailwind config, and tab navigation remain accurate for the current architecture.

Replaces the old `build_site.py` + `dashboard.js` + hashed JS architecture. Runs on the VM every 10 minutes as pipeline step 4. Generates a single responsive `index.html` with 4 analytical views, progressive disclosure accordions, and Shiller 7-stage lifecycle taxonomy.

## Architecture: Multi-View SPA

A single HTML file with tab-based navigation. All data embedded at build time as `<script>` constants. No fetch() calls, no CDN cache issues for data, no loading spinners. File size: ~640KB for 600+ stories.

### Four views

1. **Stream** (default) — Chronological contradiction story feed. Cards show: headline, capital exposure bar, gap score, tier badge. Consensus/Reality text hidden behind "Read Dispatch" `<details>` accordion for progressive disclosure.

2. **Capital Flows** — Macro ledger table (8 narratives × 9 columns: Narrative, Ticker, Inflow, Outflow, Net, Total, Stories, Discrepancies, Gap). Discrepancy markers: crimson left border + warning icon on rows with >3 discrepancies. System health badges. Collapsible "Macro Regime" and "Cross-Asset Snapshot" panels. Table wrapped in `overflow-x-auto` for mobile.

3. **Contradictions** — Sortable matrix (Highest Gap / Largest Capital / Most Recent). Filterable by narrative. Each row is a `<details>` element — tap to expand full Consensus/Reality text. REFLEXIVITY ALERT flag on gap ≥ 80.

4. **About / Macro Perspective** — Three collapsible sections (The Lefevre Filter, Narrative Lifecycle Phases, Reflexivity Alert). Phase table now shows Shiller 7-stage taxonomy + current market price + threshold delta percentage. Invalidation Threshold Tracker with proximity monitoring.

### Tab navigation
- Desktop: horizontal tab bar (Stream | Capital | Matrix | About)
- Mobile: bottom nav bar with Material Symbols icons
- Hash-based routing: `#stream`, `#capital`, `#contradictions`, `#about`
- Delegated click listener on `#tab-nav` using `e.target.closest('[data-tab]')`
- Active tab indicated by gold bottom border

## Progressive Disclosure (Native `<details>` + `<summary>`)

Zero JavaScript accordions. All expandable sections use HTML5 `<details>` elements:
- Browser disclosure triangles hidden via `summary::-webkit-details-marker { display: none }` + `list-style: none`
- Material Symbols `expand_more` icon with 180° rotation on `details[open]`
- Fade-in animation on expand: `@keyframes fadeIn { from { opacity: 0; transform: translateY(-4px) } }`
- 48px minimum tap target on all `<summary>` elements

## Data Computation (Python side)

The Python `build()` function computes all analytics from `data/stories.json` and `data/market_prices.json`:

- **Narratives**: per-container title, ticker, capital_b, count, gap, direction split, Shiller 7-stage phase, invalidation threshold, current market price, threshold delta pct
- **Capital Flows**: inflow_b, outflow_b, net_b, total_b, discrepancy count per narrative
- **Contradictions**: sorted by gap, with headline, container, tier, time_ago, they_say, reality
- **Cross-asset**: from public/data/flows.json (VIX, DXY, EURUSD, Brent, Gold, etc.)
- **Regime**: from flows.json or stories_raw
- **Market prices**: from data/market_prices.json (nested under `prices` key)

### Shiller 7-Stage Narrative Lifecycle Taxonomy

```python
def narrative_phase(gap, count, prev_phase=None):
    """Shiller 7-stage narrative lifecycle model."""
    if count < 2: return "STEALTH", "Early innovators — narrative invisible to public"
    if count < 5: return "AWARENESS", "Institutional attention, first capital allocation"
    if gap >= 80: return "MANIA", "Euphoric divergence — price completely detached from fundamentals"
    if gap >= 60: return "BLOW-OFF", "Parabolic narrative acceleration, maximum contradiction"
    if gap >= 40: return "FEAR", "Narrative fragility exposed — capital begins questioning thesis"
    if gap >= 20: return "CAPITULATION", "Mass abandonment of narrative — positioning unwinds"
    if prev_phase and prev_phase == "CAPITULATION":
        return "DESPAIR", "Narrative fully priced out — bottom formation"
    return "DESPAIR", "Narrative dormant — awaiting new catalyst"
```

Phase color coding: MANIA/BLOW-OFF = crimson badge, FEAR/CAPITULATION = gold badge, STEALTH/AWARENESS/DESPAIR = neutral badge.

### Threshold Proximity Delta Tracking

`market_prices.json` is read at build time. For each narrative, the current spot price is compared to the invalidation threshold:

| Narrative | Ticker | Threshold | Current Price | Delta |
|---|---|---|---|---|
| Dollar Decline | DXY | > 106 | 102.1 | -3.7% |
| China's Ascent | FXI | -15% quarterly | — | — |

Deltas displayed in About phase table with color coding: negative delta < -10% = crimson warning.

### Invalidation Thresholds (hardcoded per narrative)

- Dollar Decline: DXY > 106 (USD strengthening reverses thesis)
- Energy Sovereignty: Brent < $65 (Energy independence narrative breaks)
- Deglobalization: XLI +8% MoM (Industrial re-globalization invalidates)
- China Ascent: FXI -15% quarterly (Capital flight contradicts ascent)
- Space Economy: ROKT -25% (Space investment thesis invalidated)
- Gene Editing: ARKG -30% (Biotech funding freeze contradicts)
- Tech Convergence: QQQ -20% (Tech selloff invalidates convergence)
- Wealthy Sports: BATRK -25% (Sports asset bubble pops)

## Mobile Viewport Calibration (v2.2)

### Masthead
- Responsive font: `text-lg sm:text-xl md:text-2xl` (18px → 20px → 24px)
- `whitespace-nowrap` enforced — single-line guarantee
- `md:gold-outline` — text-stroke disabled on mobile (blurry on small text)
- Tracking: `tracking-tight` on mobile, `tracking-widest` on desktop
- Flanking icons scale: `text-base sm:text-lg md:text-xl`

### Tab Navigation
- Mobile: `px-2 py-2 text-xs`, icon-only labels (text hidden with `hidden sm:inline`)
- `whitespace-nowrap` on all tab buttons
- Container: `max-w-full min-w-full overflow-x-auto hide-scrollbar`

### Typography Downscale
- Body: `text-sm sm:text-body-md` (14px → 16px)
- Metadata: `text-xs sm:text-metadata-sm` (12px → 13px)
- Labels: `text-[10px] sm:text-label-xs` (10px → 12px)
- Headlines: `text-base sm:text-lg md:text-headline-md` (16px → 18px → 22px)

### Viewport Containment
- All articles: `overflow-x-hidden`
- Capital table: `<div class="overflow-x-auto hide-scrollbar">` with `min-w-[600px]`
- Phase table: `<div class="overflow-x-auto hide-scrollbar">` with `min-w-[500px]`
- Cross-asset grid: `grid-cols-1 sm:grid-cols-2 md:grid-cols-4`
- All four views: `pb-20 sm:pb-stack-space-lg` for bottom nav clearance
- Horizontal padding: `px-2 sm:px-margin-horizontal`

## Staging Isolation Protocol

Before touching production `build_frontend.py` or `index.html`:

1. Copy compiler: `cp scripts/build_frontend.py scripts/build_frontend_staging.py`
2. Apply changes to staging only
3. Compile to `public/index_staging.html` (NOT `index.html`)
4. Deploy staging: `gsutil cp public/index_staging.html gs://BUCKET/staging/index_staging.html`
5. Review at `https://www.lagazzettadikyiv.com/staging/index_staging.html`
6. Only after review approval: `cp build_frontend_staging.py build_frontend.py` on VM
7. Next governor cycle picks it up automatically

Production `index.html` and `build_frontend.py` are NEVER touched until review sign-off.

## Design Token Compliance

All Stitch DESIGN.md rules encoded in Tailwind config:
- `borderRadius: "0px"` everywhere
- `boxShadow: none` via global CSS `* { box-shadow: none !important; }`
- Colors: surface #FAF9F6, gold #D4AF37, crimson #8B0000, roman-purple #66023C
- Fonts: Playfair Display (headlines), Inter (body/metadata)
- Gold 1px structural rules via `border-gold` class
- Gold strikethrough masthead via `::after` pseudo-element
- Dark navy sidebar (#000000) on desktop (md: breakpoint)
- Discrepancy row: `border-left: 4px solid #BA1A1A` + `rgba(255,218,214,0.2)` background

## Pipeline Position

Step 4 of 8 in the governor pipeline:
```
ingestion → market_data → synthesis → build_frontend → gen_flows → test_platform → telegram_post → deploy
```

The deploy step:
```bash
gsutil -m rsync -r -d public/ gs://www.lagazzettadikyiv.com/
```

## Cache-Control

The compiler does NOT set cache headers. The deploy step uses `gsutil -h 'Cache-Control:no-cache,no-store,max-age=0' cp`. Without this, the GCS load balancer serves stale versions for up to 1 hour — even with CDN disabled on the backend bucket (`enableCdn: false`). The load balancer has its own caching layer independent of Cloud CDN.

**CDN invalidation (when load balancer cache is stale):**
```bash
gcloud compute url-maps invalidate-cdn-cache gazzetta-url-map --path "/*"
```

**Detection**: compare `curl -sI https://www.lagazzettadikyiv.com/ | grep content-length` with direct GCS: `curl -sI https://storage.googleapis.com/www.lagazzettadikyiv.com/index.html | grep content-length`. If they differ, the load balancer cache is stale.
