# HERMES CORE DIRECTIVES — La Gazzetta di Kyiv
## Architecture & Operating Protocol v1.0
### Author: Hermes Agent (Lead Architect / CTO)
### Date: June 12, 2026

> **Read this file before executing ANY task on the Gazzetta di Kyiv project.**
> These directives encode every lesson learned from deployment regressions,
> data pipeline failures, and design drift. Violating any rule below has
> caused a production incident in the past.

---

## §0 — ARCHITECTURE PHILOSOPHY

This is a **Dynamic, Data-Driven Application**, not a static website.

### The Three-Layer Architecture

```
┌─────────────────────────────────────────┐
│  LAYER 3: PRESENTATION (HTML + CSS)     │
│  Pure structure. Zero content inside.   │
│  index.html, stories.html, styles.css   │
│  All content comes from JS injection.   │
├─────────────────────────────────────────┤
│  LAYER 2: APPLICATION (Vanilla JS)      │
│  Fetches JSON → builds DOM → renders.   │
│  app.js, story-app.js, sector.js        │
│  State: window.STORIES_DATA, Gazzetta.* │
├─────────────────────────────────────────┤
│  LAYER 1: DATA (JSON + SQLite)          │
│  Single source of truth for content.    │
│  gazzetta.db → db_to_json.py → JSON     │
│  stories.json, flows.json, signal.json  │
└─────────────────────────────────────────┘
```

### Core Principle: Content Never Lives in HTML

HTML files contain **semantic structure only**: `<div>` containers, `<header>`, `<nav>`, `<main>`, `<footer>`. All story headlines, amounts, flow data, trade ideas, and signal information are **injected at runtime by JavaScript** reading from JSON data files.

**Why:** A single JSON update can refresh every page simultaneously. Editing HTML to change a headline would require finding every occurrence, risking drift, and breaking the separation of concerns.

---

## §1 — DATA PIPELINE (Layer 1)

### §1.1 — Source of Truth

```
gazzetta.db (SQLite) ──AUTHORITATIVE──► db_to_json.py ──► data/stories.json
                                                         ──► data/flows.json
```

**Never edit JSON files directly to change content.** The JSON is a compiled artifact. Changes must originate in the database (via `intel_to_stories.py`, `approve_draft.py`, or direct SQL), then be compiled by `db_to_json.py`.

### §1.2 — Pipeline Chain Order (CRITICAL)

The order of pipeline scripts matters. Running them out of order causes regressions:

```
1. fetch_intel.py          — OSINT RSS feeds → drafts table
2. intel_to_stories.py     — Telegram intel → stories table
3. enrich_editorial_stories.py — Add capital_flow to bare stories
4. ensure_generated_at.py  — Backfill timestamps
5. fetch_live_prices.py    — CoinGecko price feed
6. build_related_links.py  — Story→story cross-linking
7. analyze_narratives_v2.py — Market narrative detection
8. generate_signal_api.py  — Signal API endpoint
9. generate_trades_api.py  — Trades API endpoint
10. build_track_record.py  — Track record compilation
11. generate_flows.py      — Flow analysis (writes to site/data/)
12. db_to_json.py          — MUST RUN LAST — overwrites all with DB truth
13. build_site.py          — Sync data/ → site/data/
14. build_hashed_assets.py — Hash CSS/JS for cache-busting
15. gsutil rsync           — Deploy to GCS
```

**Rule: `db_to_json.py` is always the LAST data generator.** Any script that writes to `data/*.json` must run before it. The database is authoritative — `db_to_json.py` overwrites generator output with DB-sourced truth.

### §1.3 — JSON Data Contract

The frontend JavaScript expects specific field names. Never rename these without updating all consumers:

| Field | Consumer | Must Be |
|-------|----------|---------|
| `capital_flow.amount_b` | app.js line ~2052 | Float, not string. Null → rendered as "—" |
| `capital_flow.pace_multiplier` | app.js, flow cards | Float ≥ 0.5. Null → rendered as 1.0 |
| `capital_flow.direction` | app.js | "inflow" or "outflow" |
| `capital_flow.asset_class` | app.js, sector bars | Lowercase string (tech, crypto, defense...) |
| `generated_at` | Time badges | ISO 8601. Missing → "Unknown time" |
| `story_id` | Card linking | Unique string. Duplicates → duplicate cards |
| `contradiction_score` | Tier badge | Integer 0-100 |
| `headline` | Card display | String, max 200 chars for card view |

### §1.4 — Amount Extraction Rules

Every story MUST have a unique, context-derived `amount_b`. The `$5B uniformity bug` (where 75% of stories showed the same amount) was caused by a hardcoded default.

**Rules:**
1. Extract explicit amounts from text (`$3.2B`, `€500M`) — never guess
2. If no explicit amount: use entity-based sizing (Fed ≥ $10B, mutual fund ≤ $500M)
3. If no entity match: use asset-class ranges with MD5 hash for deterministic variety
4. **Never** hardcode a single default value (like 5.0)
5. Distribution test in `test_platform.py` enforces: no single amount > 80% of flows

### §1.5 — Pace Derivation Rules

Same as amounts — every flow needs a unique, content-derived `pace_multiplier`:

```
pace = (horizon_base + urgency_bonus) × contradiction_multiplier × asset_velocity
```

| Horizon | Base Pace |
|---------|-----------|
| 1-6h | 3.0 |
| 6-24h | 2.2 |
| 24-72h | 1.5 |
| 1w+ | 1.1 |
| structural | 0.8 |

---

## §2 — APPLICATION LAYER (Layer 2)

### §2.1 — State Management (Vanilla JS)

No frameworks. The app uses a simple global namespace:

```javascript
window.Gazzetta = {
    State: {},    // Runtime state
    UI: {},       // DOM helpers (byId, etc.)
    Data: {}      // Data accessors (getJSON, getDataPath, etc.)
};

window.STORIES_DATA = [];  // Full story array — populated by boot()
window.i18n = {};           // Internationalization (EN-only post June 2026)
```

**Rules:**
1. `STORIES_DATA` is populated ONCE at boot() and reused — never fetch stories.json twice per page
2. `teaserStoryCount` reads from `STORIES_DATA.length`, not a separate count
3. All interactive elements use `data-action` attributes with event delegation — no `onclick` in HTML
4. `byId()` is page-aware: checks `.product-page` scope first, then `document.getElementById()`. Returns null safely on missing elements — never throws

### §2.2 — DOM Injection Pattern

Content is injected, not hardcoded. The pattern:

```javascript
// 1. Fetch data
const data = await getJSON('./data/stories.json');

// 2. Build HTML string from data
const html = data.stories.map(story => storyCardHTML(story)).join('');

// 3. Inject into container
document.getElementById('newsCol').innerHTML = html;

// 4. Wire interactions
wireCardDelegation();
```

**Never** write story content, headlines, amounts, or trade ideas directly into HTML files. The only things that live in HTML are:
- Container `<div>` elements with IDs
- Navigation structure
- Masthead/SVG emblems
- Footer links
- Meta tags and SEO structured data

### §2.3 — Teaser Architecture (Index Page)

The index page shows **previews**, not full content. Each INTEL/ALPHA product gets a teaser card:

```
┌─────────────────────────────────────────┐
│ Stories                                  │
│ 20 stories                               │
│ Narrative intelligence decoded...        │
│ $50M Medicare Advantage plans denied...  │
│ $2.1B U.S. yield surge...               │
│                    [ALL STORIES →]       │
└─────────────────────────────────────────┘
```

- Teasers show `.slice(0, 20)` stories — NOT all 245
- Each teaser links to the full product page (stories.html, flows.html, etc.)
- "20 stories" count is dynamic: `teaserStoryCount.textContent = items.length + ' stories'`
- Full rendering happens on the dedicated product pages

---

## §3 — PRESENTATION LAYER (Layer 3)

### §3.1 — Design System (Immutable)

| Property | Value | Never Change To |
|----------|-------|-----------------|
| Background | `#FFFFFF` | Any off-white, #F8FAFE, #FAFAFA |
| Card bg | `#FFFFFF` | Any tint |
| Gold accent | `#D4AF37` | #B8860B, #C8A44E (use only where specified) |
| Masthead border | `2px solid #D4AF37` | 1px, any other color |
| Card left border | `2px solid #D4AF37` | Gray, no border |
| Ink (body text) | `#111827` | #333, #000 |
| Divider | `1px solid #E5E7EB` | Thicker, colored |
| Display font | Playfair Display | Any serif substitution |
| Body font | Source Serif 4 | Georgia, Times |
| Sans font | Inter | System sans-serif |
| Border radius | `0` everywhere | Rounded cards |
| Box shadow | None on cards | Material shadows |

### §3.2 — Masthead Rules

- Caduceus (☤) LEFT of name
- Crossed bulavas (⚔) RIGHT of name
- Both must be present on EVERY page (index + all sub-pages)
- Masthead name: Playfair Display, shimmering Tyrian purple gradient
- Gold 2px border-bottom below masthead
- Mobile: symbols scale to 14×22px @ 600px, 12×18px @ 400px

### §3.3 — Two-World Split (INTEL / ALPHA)

- **INTEL** (Reality): Stories, Flows, Horizon, Flow Nodes — what's happening
- **ALPHA** (Execution): Signal, Trades, Track Record — where to act
- INTEL header: black badge (#111827), white text
- ALPHA header: gold badge (#D4AF37), white text
- Nav grouped by layer with `.nav-group-label`

---

## §4 — CONTINUOUS DEPLOYMENT

### §4.1 — Deploy Script: shipit.sh

Location: `~/lagazzettadikyiv/shipit.sh`

**9 stages, sequential:**
```
0. nuclear_clean    — Purge generated dirs, recreate api/v1/home (NOT data/en/)
1. db_to_json       — SQLite → JSON compilation
1.x enrich          — Multi-persona, live prices, related links, narratives, editorial
2. build_site       — data/ → site/data/ sync
2.5 TEST GATE       — test_platform.py (142 assertions, BLOCKING — abort on fail)
3. hash_assets      — SHA256 CSS/JS, rewrite HTML references
4. GCS deploy       — gsutil rsync -d, set cache headers
5. live_verify      — curl public URL, compare with local
6. deploy_report    — Write deploy_report.txt
7. git_sync         — add → commit → push
```

### §4.2 — Test Gate (BLOCKING)

`test_platform.py` runs 5 rounds, 142 assertions. **If it fails, deploy is ABORTED.** Never bypass the test gate for CSS-only changes — test class names may have drifted from CSS refactors.

### §4.3 — GCS Cache Strategy

| File Type | Cache Header | Reason |
|-----------|-------------|--------|
| Hashed CSS/JS (`styles.*.css`) | `max-age=31536000, immutable` | Content hash = unique URL |
| HTML (`*.html`) | `max-age=0, must-revalidate` | Must always fetch fresh |
| JSON (`data/*.json`) | `no-store` | Dynamic content, never cache |

### §4.4 — Post-Deploy Verification

**Always verify after deploy using the browser, not curl/snapshot/git log:**

1. `browser_navigate` to `https://www.lagazzettadikyiv.com/?cb=<timestamp>`
2. `browser_console` check: `window.STORIES_DATA.length`, `document.body.innerHTML.length`
3. `browser_vision` screenshot — confirm gold borders, masthead, card rendering
4. Check console for errors: `browser_console()` (no expression)

**Why:** curl returns pre-JS static HTML with `—` placeholders. browser_snapshot shows accessibility tree pre-JS-population. git log shows source control, not GCS deploy state. Only `browser_vision` (screenshot) + `browser_console` (post-JS DOM query) confirm live render.

### §4.5 — Cron Pipeline

The `gazzetta-product-factory` cron runs hourly via `gazzetta_pipeline_unified.sh`:

- **Type:** `no_agent=true` (script-only, no LLM tokens)
- **Schedule:** `0 */1 * * *` (every hour at :00)
- **Script:** `~/.hermes/scripts/gazzetta_pipeline_unified.sh`
- **Per-stage timeout:** 60s per Python stage, 120s for GCS rsync
- **Failure handling:** Non-critical stages continue on failure; test gate is BLOCKING

---

## §5 — FILE MANAGEMENT RULES

### §5.1 — Edit the Repo, Not GCS

**Never upload files directly to GCS with gsutil cp.** The cron deploy runs hourly and will overwrite any manual GCS changes. Always edit files in `~/lagazzettadikyiv/site/` and deploy via `shipit.sh` or wait for the next cron cycle.

### §5.2 — Nuclear Clean Safety

`shipit.sh` Stage 0 deletes `site/data/` and `site/api/` before every build. HTML/CSS/JS source files in `site/` root are preserved. Hashed assets are cleaned. After nuclear clean, only `site/api/v1/home` is recreated — **NOT `site/data/en/`** (removed June 2026, RU scorched-earth).

### §5.3 — Root-vs-Site JS Sync

When editing `app.js`, `story-app.js`, `sector.js`, or `styles.css` at the repo root, you MUST copy to `site/` before `build_hashed_assets.py` runs:

```bash
cp app.js story-app.js sector.js i18n.js styles.css site/
```

`build_hashed_assets.py` reads from `site/`, not the repo root. Changes to root JS/CSS without the `cp` are silently ignored — the old hash is used, HTML references the old file, nothing changes.

### §5.4 — Multi-Block CSS Drift

When CSS changes span multiple tool calls, `site/styles.css` can fall behind `styles.css`. After ANY CSS edit, verify:

```bash
echo "Root: $(wc -c < styles.css)  Site: $(wc -c < site/styles.css)"
```

If sizes differ, re-copy before deploy.

---

## §6 — VERIFICATION PROTOCOL

### §6.1 — The Hierarchy of Truth

```
browser_vision (screenshot)     ← GOLD STANDARD — visual confirmation
         ↑
browser_console (JS query)      ← Confirms JS-populated state
         ↑
browser_snapshot (full=true)    ← Post-JS DOM structure
         ↑
curl (HTTP response)            ← Pre-JS static HTML
         ↑
git log (source control)        ← What was committed, not what's deployed
```

### §6.2 — Snapshot Compact-Mode False Positive

`browser_snapshot` in default compact mode shows ~17 elements for a page with 246 stories and 2.1MB body. **NEVER claim a page is empty/broken based on snapshot alone.** Always verify with:

```javascript
// Minimum verification before reporting any issue:
browser_console("document.body.innerHTML.length")     // Should be > 50000
browser_console("window.STORIES_DATA?.length")         // Should be > 0
browser_console("document.querySelectorAll('.card').length")  // Should be > 10
```

### §6.3 — CSS Verification

When verifying CSS changes, use `getComputedStyle()`, not source grep:

```javascript
// Confirms gold border is actually rendering:
getComputedStyle(document.querySelector('.card')).borderLeftWidth  // Should be "2px"
getComputedStyle(document.querySelector('.card')).borderLeftColor  // Should be rgb(212, 175, 55)
```

Source grep can show the rule exists but CDN edge cache can serve old CSS.

---

## §7 — ANTI-PATTERN CATALOG

### These actions have caused production incidents. Never repeat them.

| # | Anti-Pattern | What Happened | Correct Approach |
|---|-------------|---------------|-----------------|
| 1 | Hardcoding content in HTML | Stories couldn't update without HTML edits | All content via JS injection from JSON |
| 2 | Editing GCS directly | Overwritten by next cron deploy | Edit repo, deploy via shipit.sh |
| 3 | `cp *.html site/` without JS files | `i18n is not defined` on all pages | Always `cp *.html *.js *.css site/` together |
| 4 | Changing CSS class names without updating test_platform.py | Test gate falsely aborts deploy | Update tests in same commit |
| 5 | Hardcoded `amount_b=5.0` default | 75% of stories showed identical $5B | Context-derived amounts with entity sizing |
| 6 | Hardcoded `pace_multiplier=1.0` | All flows showed identical velocity | 4-factor pace derivation from content |
| 7 | Running `generate_flows.py` after `db_to_json.py` | 199 DB flows overwritten by 12 LLM flows | db_to_json.py ALWAYS runs last |
| 8 | Updating only `capital_flow_raw` column, not `full_json` | Inconsistent data served to frontend | Always update both columns in one transaction |
| 9 | Verifying deploy with curl | Saw `—` placeholders, reported site broken | Verify with browser_console + browser_vision |
| 10 | Verifying deploy with browser_snapshot compact mode | Saw 17 elements, reported skeletal page | Verify with console body length + card count |
| 11 | Deleting `site/` without recreating `api/v1/home` | API endpoints 404 | shipit.sh nuclear_clean now recreates dirs |
| 12 | Using `patch()` on hashed HTML | Line-number artifacts rendered as visible text | Use `write_file` for large HTML changes, or restore from git + re-patch |
| 13 | `osint%` source filter in db_to_json.py | 170 drafts excluded for 48+ hours | No source prefix filtering — all approved stories export |
| 14 | `data/en/` vestige recreated by shipit.sh | EN-only copy persisted after RU removal | Removed `mkdir -p site/data/en` from nuclear_clean |
| 15 | Forgetting to `cp` root JS/CSS to `site/` | Deploy used old hashed files, changes invisible | Add explicit cp step before build_hashed_assets.py |
| 16 | CDN edge cache serving old CSS at bumped `?v=` URL | `getComputedStyle` showed old values despite new CSS on GCS | Deploy CSS BEFORE HTML, verify with timestamp `?cb=` breaker |
| 17 | Running generators in wrong order | `db_to_json.py` overwritten by later generators | Enforce pipeline chain order (see §1.2) |

---

## §8 — SESSION OPERATING RULES

### Before ANY Task on Gazzetta:

1. **Load the skill:** `skill_view("gazzetta-website")` or `skill_view("gazzetta-knowledge-index")`
2. **Read these directives:** This file is your constitution — if a proposed action contradicts it, the action is wrong
3. **Check live state first:** `browser_navigate` + `browser_console` before assuming anything is broken
4. **Verify file paths:** Repo is at `~/lagazzettadikyiv`, not `~/projects/gazzetta-di-kyiv`

### During ANY Task:

1. **Edit source files in the repo** — never GCS directly
2. **Use `browser_vision` for visual verification** — never claim success from curl/snapshot
3. **Run the test gate** after any code change: `python3 scripts/test_platform.py`
4. **Update this file** if you discover a new anti-pattern or learn a new rule

### After ANY Deploy:

1. `browser_navigate` with `?cb=<timestamp>` cache breaker
2. `browser_console` — check for errors, verify STORIES_DATA loaded
3. `browser_vision` — visual confirmation of rendering
4. If anything looks wrong: diagnose with console queries BEFORE declaring broken

---

## §9 — MEMORY SYNCHRONIZATION

This file is the **canonical operating manual**. When session memory and this file conflict, this file wins.

**Update triggers:**
- New anti-pattern discovered → add to §7
- Design system changed → update §3
- Pipeline order changed → update §1.2
- New verification requirement → add to §6

**Do NOT store operational rules in session memory alone.** Memory is compact and ephemeral. This file is durable and read before every task.
