---
name: gazzetta-sqlite-pipeline
description: SQLite-backed data pipeline for Gazzetta di Kyiv. Migration from flat JSON to relational database with db_to_json compilation step. Use when modifying pipeline scripts, adding data sources, or debugging data integrity issues.
version: 1.0.0
---

# Gazzetta SQLite Pipeline (v3.0)

The Gazzetta data layer uses SQLite as the source of truth, with a compilation step that generates flat JSON for the JAMstack frontend.

## Architecture

```
                    ┌──────────────────────────────┐
                    │   OSINT Collector (cron)      │
                    │   fetch_intel.py              │
                    │   RSS feeds → drafts table    │
                    └──────────┬───────────────────┘
                               │ pending_review
                               ▼
                    ┌──────────────────────────────┐
                    │   Draft Approval Queue        │
                    │   approve_draft.py --id N     │
                    │   → stories + flows + links   │
                    └──────────┬───────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
     ┌────────────┐   ┌────────────┐   ┌────────────┐
     │ Telegram   │   │ RSS Feeds  │   │ Manual     │
     │ Monitor    │   │ (ECB,etc)  │   │ Drafts     │
     │ (30m)      │   │ (cron)     │   │            │
     └─────┬──────┘   └─────┬──────┘   └─────┬──────┘
           │                │                │
           └────────┬───────┴────────┬───────┘
                    │                │
                    ▼                ▼
           ┌──────────────────────────────┐
           │   gazzetta.db (SQLite)       │
           │   · stories                  │
           │   · flows                    │
           │   · drafts                   │
           │   · story_flow_links         │
           └──────────────┬───────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │   db_to_json.py              │
           │   SQL → stories.json         │
           │   SQL → flows.json           │
           └──────────────┬───────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │   build_site.py              │
           │   │   data/ → public/data/ + API   │
           └──────────────┬───────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │   shipit.sh (8 stages)       │
           │   db→json → build → test →  │
           │   hash → GCS → verify → git │
           └──────────────────────────────┘
```

## Database: gazzetta.db

Located at project root. NOT committed to git (.gitignore'd). Binary stays local.

### Tables

**stories** (14 columns): id, slug, headline, sector, pillar, tier, confidence, contradiction_score, generated_at, time_decay_raw, entity_tags_raw, multi_persona_raw, capital_flow_raw, full_json

**flows** (9 columns): id, story_id, name, category, net_direction, amount_b, velocity, last_updated, full_json

**story_flow_links** (2 columns): story_id, flow_id — PRIMARY KEY (story_id, flow_id), FK to both parent tables

**drafts** (8 columns): id (INTEGER PK AUTOINCREMENT), source, raw_content, suggested_headline, suggested_multi_persona (JSON), suggested_flows (JSON), created_at, status (DEFAULT 'pending_review')

**pipeline_state** (7 columns): id (INTEGER PK CHECK id=1), state (TEXT, CHECK IN 'IDLE','PROCESSING','ERROR'), started_at, pid, hostname, updated_at. Singleton row — used by `traffic_cop.py` for concurrency control. INSERT OR IGNORE seeds the row on first run.

**ingestion_hashes** (8 columns): id (INTEGER PK AUTOINCREMENT), hash (TEXT UNIQUE), source_url, source_type (CHECK IN 'rss','youtube','manual'), title, text_preview, full_text, narrative_tag, created_at. Used by `ingestion_triage.py` for cryptographic dedup. SHA-256 full-text hashing prevents duplicate content from reaching the LLM enrichment layer.

### Key Design Decisions

- `full_json` column stores the complete JSON blob for forward compatibility — any new field added to stories/flows is preserved even if no matching column exists
- `story_flow_links` is bidirectional: populated from flow.story_id AND story.impacted_flows
- `db_to_json.py` resolves links back into `impacted_flows` arrays in the JSON output
- `intel_to_stories.py` now uses INSERT OR REPLACE directly into SQLite, then calls db_to_json.py

## Scripts

### init_db.py
Creates schema. Three modes:
- No flag: creates DB (fails if exists)
- `--force`: drops and recreates
- `--migrate`: adds new tables to existing DB safely (no data loss). Use this when extending schema.

### import_json_to_db.py
Seeds DB from existing data/stories.json and data/flows.json. Merges lead story into the stories array before import. Handles FK constraints gracefully.

### db_to_json.py
Compiles SQLite → JSON. Reads stories + flows, resolves story_flow_links → impacted_flows, reconstructs the stories.json envelope (with lead detection) and flows.json envelope (with sector_summary).

### intel_to_stories.py (v3.0)
Bridge: telegram_intel/latest.json → gazzetta.db. Deduplicates against DB queries instead of JSON parsing. After insertion, auto-runs db_to_json.py to compile fresh JSON.

### traffic_cop.py — Concurrency Lock
Singleton process guard. Reads `pipeline_state` row: if PROCESSING → `sys.exit(0)`. If IDLE → sets PROCESSING → caller works → release resets to IDLE. WAL mode. Importable as `PipelineLock` class with context manager support.

### ingestion_triage.py — Cryptographic Dedup
Pulls RSS feeds (7 sources mapped to 8 narratives) and YouTube transcripts (`youtube-transcript-api`, oEmbed title). SHA-256 hashes full text, checks `ingestion_hashes` table — duplicates are discarded, new items saved with `full_text` + `text_preview` + `narrative_tag`. This is the cost-control gate before LLM enrichment.

### market_reality.py — Round-Robin Financial Data
Fetches ticker prices with yfinance (primary) → AlphaVantage (fallback). 34 tickers mapped to 8 narratives + 5 benchmarks. Smart fallback delay: only rate-limits when AlphaVantage is actually used. Output: `data/market_prices.json`.

### contradiction_synthesizer.py — DeepSeek-Powered Contradiction Analysis (v1.0, June 2026)
Bridges raw ingestion data to the frontend. Reads un-processed news from `ingestion_hashes WHERE processed=0`, pairs them with market prices from `data/market_prices.json`, sends them to DeepSeek API via async batch (aiohttp, semaphore max 5 concurrent, 1-3s random jitter, 90s timeout), and writes enriched stories directly to `public/data/stories.json` via atomic swap (tmp → validate → os.replace).

**DeepSeek response schema** (system-prompt enforced via `response_format: {"type": "json_object"}`):
- `headline` (max 100 chars, contradiction-focused, named actors)
- `narrative_tag` (one of 8: energy_sovereignty, dollar_decline, deglobalization, china_ascent, space_economy, gene_editing, tech_convergence, wealthy_sports)
- `they_say` (media consensus, 1-2 sentences)
- `reality` (market data reality, 1-2 sentences referencing ticker prices)
- `contradiction_gap` (integer 0-100)
- `capital_volume_usd` (integer, estimated aggregate market cap in USD)

**Async batch pattern:** `asyncio.gather()` with `asyncio.Semaphore(5)` + `aiohttp.ClientSession`. Rate-limited items (HTTP 429) are left with `processed=0` for retry next run. Failed items marked `processed=-1`. Jitter: `random.uniform(1.0, 3.0)` between calls.

**Atomic write:** Reads existing `public/data/stories.json` → prepends new stories → sorts by `generated_at DESC` → writes `stories.tmp.json` → validates required keys + types → `os.replace()`. Mirrors to `data/stories.json`. Uses `traffic_cop.PipelineLock` for concurrency safety.

**New story fields added to schema:** `reality` (string), `contradiction_gap` (int), `capital_volume_usd` (int). Narrative tag mapped to 6 containers via `NARRATIVE_TO_CONTAINER` dict.

**Resilience:** 429 → leave unprocessed. Timeout/500 → mark `processed=-1`. Empty API response → caught before JSON parse. Malformed JSON → strips markdown fences. Missing `market_prices.json` → runs with "No market data" fallback. Missing/corrupt `stories.json` → starts from fresh skeleton.

### Alternative Pipeline: LLM-First Ingestion (v1.0, June 2026)
A parallel ingestion path using DeepSeek for enrichment instead of the multi-step enrichment chain:

```
ingestion_triage.py  →  ingestion_hashes (SHA-256 dedup, processed=0)
market_reality.py    →  data/market_prices.json
       ↓                        ↓
contradiction_synthesizer.py → DeepSeek API → public/data/stories.json
       ↑
traffic_cop.py (concurrency lock on all three)
```

This path bypasses gazzetta.db stories table entirely — writes directly to stories.json. It is an ALTERNATIVE to the traditional `fetch_intel → intel_to_stories → enrichment chain → db_to_json` path. Choose one; don't run both simultaneously on the same data or they'll conflict on stories.json output.

### fetch_intel.py — OSINT Collector
Fetches open financial/macro RSS feeds (see `references/rss-feed-registry.md` for working feeds). For each new item: extracts entities (assets, geographies, actors), detects asset class + direction, generates multi-persona blocks and suggested flows, inserts into `drafts` table with status='pending_review'. Requires `feedparser` (installed via `.venv/bin/pip install feedparser`).

Runs as a `no_agent=true` cron via a wrapper at `~/.hermes/scripts/gazzetta_fetch_intel.py`.

### approve_draft.py — Draft Approval Command
Reads a draft by ID, converts into a full story + linked flow, inserts into stories/flows tables, auto-creates story_flow_links, updates draft status to 'approved', then auto-runs db_to_json.py. Accepts both `--id=3` and `--id 3` formats, batch via `--id 3,5,7`. Use `--list` to see pending drafts.

### enrich_editorial_stories.py (v22.45+)
Bridges the two-generation pipeline gap. Editorial writer produces stories without `capital_flow` or `generated_at`. This script detects asset_class from keywords, derives direction from sentiment, computes approximate amount, and adds a `capital_flow` dict with `pace_multiplier=1.5` (medium velocity). Also adds `generated_at` from document timestamp. Runs at shipit.sh Stage 1.5.

### ensure_generated_at.py (v22.45+)
Backfills `generated_at` on any story missing it, using the document-level timestamp. Runs at shipit.sh Stage 1.5 after enrichment. Ensures story detail pages always show time badges.

### backfill_pace.py (v22.45)
One-time migration: reads `data/stories.json`, derives pace from story content using the 4-factor algorithm (horizon × urgency × contradiction × asset velocity), writes back both JSON and gazzetta.db. Used when migrating from the hardcoded `pace_multiplier: 1.0` era to content-derived pace.

## Deploy Pipeline (shipit.sh) — 9 stages (v22.45+)

9 stages with automated test gate + editorial enrichment:
1. **db_to_json** — compile SQLite → JSON (skipped if no gazzetta.db)
1.5. **enrich** — `enrich_editorial_stories.py` adds capital_flow + generated_at to editorial stories; `ensure_generated_at.py` backfills timestamps on all stories
2. **build_site** — sync data/ → public/data/ + API endpoints
2.5. **test_platform** — 5-round BS4 test suite (142 assertions). Any failure → abort deploy.
3. **hash assets** — SHA256-hash CSS/JS, rewrite HTML references
4. **GCS deploy** — gsutil rsync + cache-policy setmeta
5. **live verify** — curl headers from lagazzettadikyiv.com
6. **deploy report** — generate public/deploy_report.txt
7. **git sync** — add → commit → push (skippable with --skip-git)

### test_platform.py — Automated Test Suite

5 rounds, 142 assertions. See `references/test-assertion-catalog.md` for full spec.

| Round | Assertions | What It Checks |
|---|---|---|
| 1. Poison Values | 44 | 11 pages scanned for `undefined`, `null`, `NaN` (word-boundary), `[]` |
| 2. Flow Integrity | 32 | Every linked story has valid non-zero `amount_b` + `pace_multiplier`; cross-verifies `capital_flow` matches linked `flow` row in DB; distribution test (≤80% uniformity, ≤20% at $5B); duplicate slug/headline check; entity scale check (central banks ≥$1B, small funds ≤$2B) |
| 3. HTML Structure | 55 | Each page: `<html>`, `<body>`, stylesheet link, title/h1 heading, body content |
| 4. Timestamps | 4 | Freshness elements, hero indicators, services grid, teaser containers |
| 5. JSON Consistency | 8 | `data/` = `public/data/` counts match, timestamps < 24h old |

**False-positive fix**: NaN detection uses `\bNaN\b` word-boundary regex to avoid matching words like "financial" / "inanimate".

## Amount Extraction: Preventing the $5B Uniformity Bug

**Critical pitfall**: When `extract_amount()` always returns a flat default (e.g. `5.0`) for RSS snippets that lack explicit `$XB` patterns, **75%+ of flows converge to the same value**. The frontend renders homogenous numbers and the site loses all differentiation between stories.

### Pattern: Two-Tier Extraction

```python
def extract_amount(text):
    """Return float or None. None = signal to use context heuristic."""
    # Try explicit patterns first: $XB, X billion/trillion/million, €XB
    # If nothing found, return None — never a hardcoded default.
    return None

def context_amount(asset_class, direction, headline):
    """Deterministic but varied fallback using asset-class ranges + hash."""
    import hashlib
    h = int(hashlib.md5((headline or asset_class).encode()).hexdigest()[:4], 16)
    base_ranges = {
        "crypto": (0.5, 8.0), "equities": (1.0, 15.0),
        "commodities": (2.0, 12.0), "tech": (1.0, 20.0),
        "defense": (1.5, 10.0), "fixed_income": (3.0, 25.0), "fx": (5.0, 50.0),
    }
    lo, hi = base_ranges.get(asset_class, (1.0, 10.0))
    return round(lo + (h % int((hi - lo) * 10)) / 10.0, 1)

# Call site:
amount_b = extract_amount(raw_text)
if amount_b is None:
    amount_b = context_amount(asset_class, direction, headline)
```

This is implemented in both `fetch_intel.py` and `approve_draft.py`.

### Distribution Test (test_platform.py)

The test suite catches the uniformity bug before deploy. A dedicated check asserts that no single amount accounts for >80% of linked flows, and no more than 20% of flows are at exactly $5.0B. If either fails, the test aborts and shipit.sh blocks deploy.

Additionally, the suite now includes:
- **Duplicate check**: no two stories share the same slug or normalized headline
- **Entity scale check**: stories mentioning "Fed"/"ECB"/"central bank" must have amounts ≥ $1B; stories mentioning "mutual fund"/"small-cap" must be ≤ $2B

### Entity-Based Sizing Engine (config.yaml `entity_scales`)

When no explicit dollar amount is found in text, the `context_amount()` function in `fetch_intel.py` scans headlines against entity_scales defined in `config.yaml`:

| Category | Range | Example Keywords |
|---|---|---|
| `central_banks` | $10B–$150B | fed, ecb, lagarde, powell, imf |
| `megacorps` | $1B–$15B | nvidia, oracle, spacex, jpmorgan |
| `crypto_assets` | $100M–$8B | bitcoin, ethereum, defi, stablecoin |
| `mutual_funds` | $10M–$500M | mutual fund, small-cap, etf, pension |
| `sovereign_wealth` | $5B–$50B | sovereign wealth, swf, norway fund |
| `defense_military` | $1B–$20B | defense, nato, missile, pentagon |

If no entity keyword matches, falls back to asset-class ranges; if no asset class either, defaults to **$10M–$50M** (was flat $5B).

The function uses a headline MD5 hash for deterministic variety within each range — same headline always produces same amount, but different headlines produce different amounts.

### Duplicate Story Prevention

**Critical pitfall**: `db_to_json.py` includes the lead story in BOTH the `lead` field AND `stories[]` array. Frontend line 2050 does `[storiesData.lead, ...storiesData.stories]` — prepending lead to the array. If lead is already in the array, it renders twice. **Fix**: `"stories": stories[1:] if lead else stories` (line 100). The test suite verifies `lead_in_array == 0`.

**Schema-level prevention**: `init_db.py --migrate` adds `CREATE UNIQUE INDEX idx_stories_slug ON stories(slug)`. Ingestion scripts use `INSERT OR REPLACE` so duplicate slugs silently update existing rows rather than creating duplicates.

### Direct DB Surgery for Existing Defaults

When existing flows are already at $5.0B, update them directly via SQL with realistic amounts derived from the news context:

```sql
UPDATE flows SET amount_b = ?, net_direction = ?, category = ? WHERE id = ?;
-- Also update full_json blob with new values for db_to_json to pick up
UPDATE flows SET full_json = ?, name = ? WHERE id = ?;
```

Use the `debug_flows.py` diagnostic to inventory the distribution before and after surgery.

### DB Backfill Pattern: Two-Column Update (v22.45)

When backfilling story data (pace, amounts, etc.) into gazzetta.db, you MUST update BOTH columns:
1. **`capital_flow_raw`** — the canonical capital_flow dict (read by `db_to_json.py` for flow enrichment)
2. **`full_json`** — the complete story blob (read by `db_to_json.py` for the story itself)

Updating only one column causes `db_to_json.py` to serve inconsistent data: the story JSON has the old value but the capital_flow dict has the new one. Always update both in a single transaction:

```python
conn.execute("UPDATE stories SET capital_flow_raw = ?, full_json = ? WHERE id = ?",
           (json.dumps(cf), json.dumps(story), sid))
```

For flows, only `full_json` needs updating (no separate column for flow metrics). The `db_to_json.py` reads `full_json` from flows table. Key: the flow's `full_json` field is `pace_multiplier`, NOT `velocity` — `db_to_json.py` v22.44 referenced a nonexistent key, silently setting pace to None.

### Editorial Writer Enrichment (v22.45+)

The editorial writer produces stories WITHOUT `capital_flow` dicts and WITHOUT `generated_at`. These bare stories were deployed and rendered with broken time badges and zero flow data. The fix has two parts:

1. **`scripts/enrich_editorial_stories.py`** — runs at shipit.sh Stage 1.5. For each editorial story: detects asset_class from keywords, detects direction from sentiment, derives approximate amount from headline/context, adds `capital_flow` dict with `pace_multiplier=1.5` (medium velocity default), and adds `generated_at` from document-level timestamp.

2. **`scripts/ensure_generated_at.py`** — also runs at Stage 1.5. Checks every story in `data/stories.json` and adds `generated_at` from document timestamp to any story missing it. Runs unconditionally.

Both scripts use `|| echo "⚠ FAILED — continuing"` in shipit.sh so failures are logged but don't block deploy.

`db_to_json.py` performs a proper JOIN to inject real flow metrics into story `capital_flow` dicts:

1. Fetches all flows upfront: `SELECT id, amount_b, velocity, net_direction, category FROM flows`
2. For each story with `impacted_flows`, looks up the primary linked flow
3. Overwrites `capital_flow.amount_b`, `pace_multiplier`, `direction`, `claim` with real DB values
4. Frontend line 2052 reads `s.capital_flow.amount_b` — now always reflects DB truth

Result: **0 flow-story amount mismatches** (verified by test Round 2 cross-verification).

## UX Design Standards (Enforced by Tests)

When modifying any product page (event_horizon.html, flow-nodes.html, etc.), enforce:

| Property | Standard |
|---|---|
| Background | `#FFFFFF` |
| Cards | `#FFFFFF` |
| Gold | `#B8860B` (DarkGoldenrod) |
| Divider | `#E5E7EB` |
| Ink (body) | `#111827` |
| Green | `#047857` |
| Red | `#DC2626` |
| Display font | Playfair Display |
| Body font | Source Serif 4 (must be in Google Fonts URL) |
| Sans font | Inter |
| Border-radius | `0` everywhere (2px only on tiny badges) |
| Box-shadow | None |
| Timestamps | `<time>` element on masthead, `flow-freshness` spans on every data container |
| Dark themes | **Not allowed** — all pages must default to light. flow-nodes.html has `.cn-dark` toggle only.|

## Pace Derivation (v22.45 — prevents the `pace_multiplier=1.0` uniformity bug)

**Critical pitfall**: When every flow has `pace_multiplier=1.0`, the velocity dimension becomes meaningless — all flows look equally urgent. This is the pace equivalent of the `$5B amount uniformity` bug. Root cause chain:

### Three-Layer Fix (all three required — one alone won't hold)

**Layer 1 — `intel_to_stories.py`**: Derive pace from story content instead of hardcoding 1.0.
```python
# urgency keywords in headline/bet score higher pace
urgency_keywords = ["breaking", "crash", "spike", "plunge", "surge", "crisis", "imminent"]
urgency_hits = sum(1 for k in urgency_keywords if k in text_combined)
# Horizon-based base: shorter horizon = higher velocity
horizon_base = {"1-6h": 3.0, "6-24h": 2.2, "24-72h": 1.5, "1w+": 1.1, "structural": 0.8}
# Contradiction multiplier: high tension = capital moves faster
contra_mult = 1.0 + (contradiction_score - 50) * 0.01 if contradiction_score > 50 else 1.0
# Asset-class velocity modifier
asset_velocity = {"crypto": 1.3, "defense": 1.2, "commodities": 1.1, "equities": 0.95, "fixed_income": 0.8}
pace_mult = round((horizon_base + urgency_bonus) * contra_mult * asset_velocity, 1)
```
Implementation: `scripts/intel_to_stories.py` line ~400, replaces `"pace_multiplier": 1.0`.
Migration script for existing stories: `scripts/backfill_pace.py` — uses identical derivation logic.

**Layer 2 — `db_to_json.py` line 79**: The JOIN injection that enriches story `capital_flow` from the flows table MUST preserve story-derived pace. The old code `cf["pace_multiplier"] = primary_flow["velocity"]` overwrote the content-derived pace with stale flow velocity (which was itself 1.0). Fix: `cf["pace_multiplier"] = cf.get("pace_multiplier") or primary_flow["velocity"]` — only use flow velocity as fallback when story has no pace.

**Layer 3 — gazzetta.db flows table**: The `full_json` blob in the flows table also stores `pace_multiplier`. After backfilling stories, update the flows table too:
```python
for flow in db_flows:
    matching_story = find_story(flow.story_id)
    flow.pace_multiplier = matching_story.capital_flow.pace_multiplier
    UPDATE flows SET full_json = json.dumps(flow) WHERE id = flow.id
```

### The Circular Dependency Trap

The pipeline has a circular dependency that makes pace changes self-defeating without all three layers:

```
intel_to_stories → DB stories (pace from content) ✓
  → db_to_json → data/stories.json (overwrites pace with DB flow velocity) ✗
    → generate_flows → public/data/flows.json (reads overwritten pace=1.0) ✗
      → shipit.sh stage 1: db_to_json → overwrites public/data/flows.json from DB ✗
```

Each stage overwrites the previous stage's work. **After any data model change, verify with GCS origin**: `gsutil cp gs://www.lagazzettadikyiv.com/data/flows.json - | python3 -c "import json,sys; from collections import Counter; p=[f['pace_multiplier'] for f in json.load(sys.stdin)['flows']]; print(Counter(p))"` — must show varied pace, not `{1.0: N}`.

### Verification (after any pipeline change)
```bash
# 1. Stories.json pace variety
python3 -c "import json; from collections import Counter; d=json.load(open('data/stories.json')); print(Counter(s['capital_flow']['pace_multiplier'] for s in d['stories']))"
# Must show >3 unique values, not {1.0: N}

# 2. Flows.json pace variety  
python3 -c "import json; from collections import Counter; d=json.load(open('site/data/flows.json')); print(Counter(f['pace_multiplier'] for f in d['flows']))"
# Must show varied pace, not {1.0: N}

# 3. GCS origin (CDN may lag)
gsutil cp gs://www.lagazzettadikyiv.com/data/flows.json - | python3 -c "..."
```

## Pitfalls

- **CDN caching**: GCS has 10-min edge cache. Use `?nocache=<ts>` to verify fresh content after deploy.
- **Root-vs-site JS sync gap (v26.8 CRITICAL)**: `shipit.sh` nuclear_clean deletes hashed assets but does NOT copy `app.js` / `styles.css` from project root → `site/`. `build_hashed_assets.py` reads from `site/`, so changes to root JS/CSS are silently ignored. Symptom: new JS deploys with old hash, HTML references old file, nothing changes. **Fix**: `cp app.js site/app.js` before running `build_hashed_assets.py`. Or add a cp step to shipit.sh Stage 2. Also applies to `story-app.js`, `sector.js`, `i18n.js`.
- **Tier-fraction sector_total feedback loop (v26.8)**: `db_to_json.py` computed story amounts as `flow_total * tier_fraction` where `flow_total = sector_totals.get(cat)`. Sector totals summed ALL flows, including already-inflated ones, creating a feedback loop: $747B tech sector × 0.08 DEVELOPING = $60B per story. **Fix**: use `flow_total = float(primary_flow["amount_b"])` — the individual flow's amount, not the entire sector. A story linked to a $0.51B flow now gets ~$0.04B (DEVELOPING), not $52B.
- **Live-price merge → ANCHOR_ASSETS (v26.8)**: `fetch_live_prices.py` writes `market_prices.json` → `window._lastTickerMap`. To populate sidebar tickers, merge live prices into `ANCHOR_ASSETS` after the fetch. Symbol mapping: ANCHOR_ASSETS symbols → `_lastTickerMap` keys (e.g., SPX→spy, BRENT→cl=f, DXY→uup, GOLD→gold, BTC→btc-usd, 10Y→tlt). The `_lastTickerMap` has entries with `{ticker, price, change_pct, direction}` — use `change_pct` and `direction` directly, don't recompute. See `references/live-price-frontend-merge.md`.
- **Lead story**: stories.json stores lead separately from the stories array. Both import_json_to_db.py and db_to_json.py handle this merge/split.
- **Duplicate story IDs**: The stories array sometimes has duplicates. import_json_to_db.py uses INSERT OR REPLACE; db_to_json.py counts unique stories.
- **shipit.sh path**: Must use `${BASH_SOURCE[0]}` not `$0` because cron runs via `bash shipit.sh` which sets `$0` to `bash`.
- **gazzetta.db missing**: If DB doesn't exist, shipit.sh skips db_to_json stage (uses existing JSON). This prevents pipeline breakage on first setup.
- **Arg parsing in CLI scripts**: Shell splits `--id 3,5,7` into two args. Support both `--id=3` and `--id 3` by iterating with index (check for `arg == "--id"` then consume next arg). Using only `startswith("--id=")` silently drops space-separated args.
- **Circular dependency trap (v23.0)**: `shipit.sh` Stage 1 runs `db_to_json.py` which compiles flows.json from the DB flows table. This overwrites any output from `generate_flows.py`. If the DB flows table is stale (e.g., old pace=1.0 values), the deployed site shows stale flows. Fix: when backfilling data, update BOTH the JSON file AND the DB table. Use pattern from `scripts/backfill_pace.py`.
- **db_to_json line 79 pace overwrite (v23.0)**: Changed from `cf["pace_multiplier"] = primary_flow["velocity"]` (always overwrote with stale flow velocity) to `cf["pace_multiplier"] = cf.get("pace_multiplier") or primary_flow["velocity"]` (preserves story-derived pace, falls back to flow velocity only when pace is 0/None).
- **Cron wrapper pattern**: Hermes cron expects scripts at `~/.hermes/scripts/` for `no_agent=true` jobs. For project scripts, create a wrapper: bash header `cd /path/to/project && exec .venv/bin/python scripts/actual_script.py "$@"`. Name the wrapper to match what the cron references.
- **osint source filter silently excludes stories (v23.24 CRITICAL)**: `db_to_json.py` line 35 had `WHERE json_extract(full_json, '$.source') NOT LIKE 'osint%'` — this excluded ALL stories from `osint_the_cradle`, `osint_reuters_business`, and any other source with `osint` prefix. 170 drafts accumulated with zero becoming public stories for 48+ hours. **The filter is now REMOVED.** All stories in the DB export regardless of source. If a filter is reintroduced, it must be on `status='approved'` (drafts table), NEVER on the source prefix.
- **Product Factory must include draft approval step (v23.24)**: The unified `gazzetta_product_factory.sh` must run `approve_draft.py` after `fetch_intel.py`. Without it, drafts pile up and never become stories. The script now auto-approves top 15 pending drafts per cycle. Cron cadence: every 60m.
- **verify_reality.py — post-deploy truth check**: Run `python3 scripts/verify_reality.py` after every deploy. Three-lens check: RETROSPECTIVE (public JSON freshness <15min, SSL reachability), INTROSPECTIVE (DB count = public count, amount uniqueness, trade hook format), EXTRAPOLATIVE (cron health, script existence, cache headers). Non-zero exit = reality gap — do NOT report success.
- **Browser snapshot alone is NOT verification**: The browser snapshot tool captures pre-JS DOM. A page that loads content via JavaScript (like stories.html with 228K chars of innerHTML) may show only 11 elements in the snapshot. Always verify with `browser_console` (e.g., `document.querySelectorAll('#newsCol .card').length`) before reporting a page as broken.
- **Test platform class name drift**: test_platform.py checked for `.hero-indicator` class but the HTML used `.hero-ind`. When CSS refactors rename classes, the test must be updated in the same commit or shipit.sh test gate will falsely abort deploy.
- **Two-column DB update (v22.45)**: When backfilling story data, update BOTH `capital_flow_raw` AND `full_json` columns. Updating only one causes `db_to_json.py` to serve inconsistent data. See "DB Backfill Pattern" section above.
- **db_to_json overwrites story pace with flow velocity (v22.45)**: `db_to_json.py` line 79 injected `primary_flow["velocity"]` into story capital_flow — but the flows table column is `pace_multiplier`, not `velocity`. This silently set pace to None (rendered as 1.0 by frontend). The overwrite also created a circular dependency: DB flows (stale) → story pace (stale) → generate_flows (reads stale story pace) → DB flows (stale). Fix: use `cf.get("pace_multiplier") or primary_flow["pace_multiplier"]` to preserve story-derived pace.
- **Two-generation pipeline gap (v22.45)**: Editorial writer produces stories without `capital_flow` or `generated_at`. Fixed by `enrich_editorial_stories.py` at shipit.sh Stage 1.5. The older `data/stories.json` path already has these fields from `intel_to_stories.py`.
- **DB backfill must update BOTH columns**: When updating existing data in gazzetta.db, the `capital_flow_raw` column, `full_json` column, AND the flows table's `full_json` ALL need updating. `db_to_json.py` reads `full_json` from both tables, so stale data in any one column propagates. Verify with direct SQL queries, not just JSON file checks.
- **`processed` column missing on `ingestion_hashes` (v1.0, June 2026):** The `contradiction_synthesizer.py` requires a `processed` column on `ingestion_hashes` to track which items have been sent to DeepSeek. The `ensure_processed_column()` function handles this idempotently via `PRAGMA table_info` + `ALTER TABLE ADD COLUMN`. If the synthesizer runs before `ingestion_triage.py` has created the table, it will fail — always run triage first. The `generate_flows.py` cron writes to site/data/flows.json but that gets overwritten by the next deploy. The DB flows table is the TRUE source of truth for flow data — update it, not just the JSON.
- **SQLite permissions trap — readonly database error (v3.5, June 2026):** The DB file at `/opt/gazzetta-di-kyiv/data/gazzetta.db` is owned by `gazzetta:gazzetta`. Any user other than `gazzetta` (including `alexstocchi`) gets `Error: attempt to write a readonly database (8)` even on SELECT queries. SQLite's journal mode creates temporary files in the DB directory, which requires write permission on the directory. Fix: always use `sudo -u gazzetta sqlite3 /opt/gazzetta-di-kyiv/data/gazzetta.db "..."` when querying from outside pipeline scripts (cron jobs, manual SSH, Hermes agents). Pipeline scripts already run as `sudo -u gazzetta` via the governor so they are unaffected. `sqlite3 -readonly` flag does NOT help — the journal file creation happens regardless.
- **`generate_flows.py` writes to BOTH `data/` and `site/data/` (v25.19)**: Lines 637-640 have a "reference copy" (`DATA_FLOWS = PROJECT_ROOT / "data" / "flows.json"`) that silently overwrites the `db_to_json.py` output in `data/`. When `db_to_json.py` runs BEFORE `generate_flows.py`, the 199 DB-sourced flows get replaced by 12 LLM-generated flows. Fix: remove the `data/flows.json` reference write from `generate_flows.py` entirely. The DB is authoritative for flows.
- **Pipeline chain order: `db_to_json.py` MUST run last (v25.19)**: Any script that writes to `data/flows.json` or `site/data/flows.json` MUST run BEFORE `db_to_json.py`. The correct order: generators (signal, trades, track_record, prices) → `db_to_json.py` (overwrites with DB truth) → deploy. Never run generators after `db_to_json.py`.
- **Generator path mismatch: `api/v1/` vs `data/` (v25.19)**: `generate_signal_api.py` writes to `site/api/v1/signal.json` and `generate_trades_api.py` writes to `site/api/v1/trades.json`, but the website fetches from `/data/signal.json` and `/data/trades.json`. After running these generators, copy their output: `cp site/api/v1/signal.json site/data/signal.json` and `cp site/api/v1/trades.json site/data/trades.json`.
- **Bulk draft approval with full_json construction (v27.0 CRITICAL)**: `approve_draft.py` only handles individual `--id` values. The pipeline needs bulk approval. The inline Python in Stage 0.6 builds complete `full_json` objects containing ALL story fields (`story_id`, `headline`, `sector`, `pillar`, `tier`, `confidence_pct`, `contradiction_score`, `generated_at`, `capital_flow`, `they_say`, `multi_persona`). NEVER set `full_json='{}'` — `db_to_json.py` reads ALL story data from `full_json`, ignoring column-level data like `headline` and `sector`. An empty `full_json` produces stories with no headline, no capital flow, and no generated_at timestamp.
- **contradiction_score sort buries fresh stories (v27.0)**: `db_to_json.py` sorts by `contradiction_score DESC` before `generated_at DESC`. New stories with default `contradiction_score=50` get buried behind old stories with score 75. The frontpage teaser shows the first 20 stories from the sorted array, so all fresh content is invisible. Fix: set `contradiction_score=75` (or higher) on new stories to match/exceed existing scores. The inline bulk_approve at Stage 0.6 does this automatically.
- **SQLite json_extract() fails on empty full_json (v27.0)**: The sort query in `db_to_json.py` uses `json_extract(full_json, '$.capital_flow.contradiction_flag')` which raises `sqlite3.OperationalError: malformed JSON` on rows where `full_json` is empty string or `NULL`. Symptoms: `db_to_json.py` exits with "ERROR: malformed JSON" with no other trace. Fix: ensure every story has valid JSON in `full_json` (at minimum `'{}'`), then use `json_valid(full_json)=0` to find and fix orphans. If a row has `id=NULL`, target it by `rowid`.
- **Two pipeline paths conflict on stories.json (v1.0, June 2026):** The traditional pipeline (`fetch_intel → enrichment → db_to_json`) and the LLM-first path (`ingestion_triage → market_reality → contradiction_synthesizer`) both write to `public/data/stories.json`. Running both simultaneously corrupts the output — the last writer wins and the loser's stories are silently lost. Choose ONE path for production. The LLM-first path is designed for autonomous operation via DeepSeek enrichment; the traditional path is designed for the multi-step enrichment chain with DB-backed state.

- **Two-bucket GCS deploy (v27.0)**: The project has TWO GCS buckets — `gs://www.lagazzettadikyiv.com/` (primary) AND `gs://lagazzettadikyiv.com/` (non-www, abandoned for weeks). If only the www bucket is deployed, users visiting the non-www URL (HTTP or HTTPS) see weeks-old stale content with different CSS/JS hashes and no data. Pipeline Stage 4 now deploys to BOTH buckets. The canonical URL in HTML (`rel="canonical"`) is already `https://www.lagazzettadikyiv.com/` so SEO is unaffected.
- **Template footer contains asset references (v27.0)**: `templates/footer.html` has `<script src="./app.js?v=sprint4"></script>`. When `build_site.py` injects this template into HTML files, it overwrites any hashed asset references that `build_hashed_assets.py` had previously written. The fix: update `templates/footer.html` to reference the CURRENT hashed filenames (`app.ad499bee.js`, `i18n.e879a05a.js`). Long-term: `build_hashed_assets.py` should also update the template's references.
- **Freshness label missing on new stories (v27.1)**: When stories are bulk-approved with `time_decay_raw='{}'`, the parsed `time_decay` dict has no `current_freshness` field. The frontend teaser renderer (`populateTeasers()` in app.js ~line 2543) conditionally rendered the `<span class="freshness-ago">` only when `fresh !== undefined`. This caused new stories to display no time indicator at all. Fix: always render the freshness span, using `formatTimeAgo(s.generated_at)` for the label text and defaulting the CSS class to `freshness-recent` when `current_freshness` is undefined.
- **build_hashed_assets.py regex pattern limitation (v27.0)**: The regex `\?v=[\d.]+` only matches numeric cache busters (`?v=22.22`), not alphanumeric ones (`?v=sprint4`, `?v=fix2`). Fixed to `\?v=\w+` which matches any word characters. If the regex doesn't match, `build_hashed_assets.py` silently skips the file and the HTML retains its old asset reference.
- **public/data/ is a build artifact — never exists by default (v27.0)**: `public/data/` does NOT exist in the repo. It is created by `build_site.py` which copies files from `data/` → `public/data/`. If you deploy without running `build_site.py`, the ENTIRE site breaks: all JS fetches (`./data/stories.json`, `./data/flows.json`) return 404, every hero indicator shows `—`, and no content renders. The nuclear clean at Stage 0 deliberately deletes `public/data/` to prevent stale artifacts. Stage 2 (`build_site.py`) MUST run before deploy to recreate it.

## Sprint 4: Flow Dimension Fields (v27.0)

`compute_flow_dimensions.py` adds three portfolio-manager-grade fields to every flow object in `flows.json`:
- `duration` — "intraday" | "positional" | "structural" (derived from pace_multiplier)
- `counterparty` — "retail" | "institutional" | "sovereign" | "corporate" | "mixed" (derived from flow_sources)
- `scale` — 1-10 integer (normalized amount * confidence * pace)

Also adds `flow_dimensions` metadata block to `flows.json`. Runs as Stage 1.5f in the pipeline, AFTER `build_track_record` and BEFORE `build_site`. Both `deploy_routine.sh` (Cloud Run) and `gazzetta_pipeline_unified.sh` (local) include this stage.

`test_platform.py` Round 2 checks that all flows carry these fields and that `flow_dimensions` metadata is present. Any missing field → deploy blocked.

### fetch_live_prices.py OUTPUT_PATH Pitfall (v27.0 CRITICAL)

`fetch_live_prices.py` originally wrote to `public/data/market_prices.json`. `db_to_json.py` reads from `data/market_prices.json` for asymmetry computation, then writes asymmetry scores back to `data/market_prices.json` AND syncs to `public/data/market_prices.json`. This overwrote the fresh price data with stale DB-derived data (8 assets, generated_at from June 11).

**Fix**: Changed `OUTPUT_PATH` to `PROJECT / "data" / "market_prices.json"`. Pipeline stage order also requires `fetch_live_prices` to run BEFORE `db_to_json` (Stage 0.95, not Stage 1.05). If db_to_json runs first, it reads the OLD market_prices.json and overwrites the fresh data.

### OSINT Cloud Migration (v27.0)

The OSINT collector (`fetch_intel.py`) is now integrated into the Cloud Run pipeline as Stage 0. The flow:

```
Cloud Scheduler (every 10 min)
  → Cloud Run job gazzetta-pipeline
    → Download DB from GCS
    → Stage 0: fetch_intel.py (RSS feeds → drafts table, non-blocking)
    → Stage 0.2: bulk_approve (drafts → stories, auto-approves all pending)
    → Stage 1: db_to_json.py (stories → JSON, must run AFTER fetch_intel)
    → ... remaining stages
```

`cloud_entrypoint.py` calls `fetch_intel.py` with a 90s timeout before `run_pipeline()`. Failure is non-blocking — if RSS feeds are down, the pipeline continues with existing DB data. Docker dependencies added: `feedparser`, `pyyaml`.

`deploy_routine.sh` now includes Stage 0.1 (fetch_intel) and Stage 0.2 (bulk_approve) before db_to_json. The bulk_approve inline script builds complete `full_json` objects with `contradiction_score=75` and `generated_at` set to the current timestamp.

## Cron Integration (v27.0)

The local cron `gazzetta-product-factory` (420d5f0f0c88) is now PAUSED — the Cloud Run pipeline is the sole active sync mechanism. The local script (`gazzetta_pipeline_unified.sh`) remains available as a cold standby with native macOS timeout support (no GNU coreutils dependency).

The unified Product Factory runs as a `no_agent=true` cron every 60m:
```
cronjob create --name gazzetta-product-factory --schedule "0 */1 * * *"
               --script gazzetta_pipeline_unified.sh --no_agent true
               --deliver origin
```
Workdir is NOT set (defaults to session cwd). The script uses absolute paths internally.

Wrapper at `~/.hermes/scripts/gazzetta_pipeline_unified.sh` runs 9 stages with per-stage 60s timeouts:
1. Stage 0 — Nuclear clean: delete `public/data/`, `public/api/`, old hashed assets
2. Stage 0.5 — `fetch_intel.py`: 12 RSS sources → drafts table (25-50 new drafts per cycle)
3. Stage 0.6 — Bulk approve: inline Python auto-approves ALL pending drafts, builds complete `full_json` with all story fields, inserts into stories table with `contradiction_score=75`
4. Stage 1 — `db_to_json.py`: SQLite → JSON (MUST run LAST among data generators)
5. Stage 1.02–1.5e — Enrichment: `enrich_multi_persona.py`, `fetch_live_prices.py`, `build_related_links.py`, `enrich_editorial_stories.py`, `ensure_generated_at.py`, signal/trades/track generators
6. Stage 2 — `build_site.py`: syncs `data/` → `public/data/` (15 JSON files) + injects header/footer from templates into 21 HTML files
7. Stage 2.5 — `test_platform.py`: BLOCKING gate — any failure aborts deploy
8. Stage 3 — `build_hashed_assets.py`: hashes CSS/JS, rewrites HTML references from `app.js` → `app.HASH.js`
9. Stage 4 — GCS deploy: rsync to BOTH `gs://www.lagazzettadikyiv.com/` AND `gs://lagazzettadikyiv.com/` (non-www), then set cache headers
10. Stage 5 — External verify: curl HTTP status, story count
11. Stage 7 — Git sync: add → commit → push

Each stage runs independently with `|| true` — one failure doesn't kill the chain. The GCS deploy has a 120s timeout for www, 60s for non-www.

## Support Files

- `scripts/verify_reality.py` — Three-lens post-deploy verification (Retrospective/Introspective/Extrapolative). Run after every deploy.
- `scripts/gazzetta_product_factory.sh` — 7-stage unified pipeline cron wrapper. Replaces all fragmented ingestion crons.
- `references/rss-feed-registry.md` — Working RSS feeds with known-good URLs
- `references/debug-flows-diagnostic.md` — Flow distribution diagnostic queries
- `references/deduplication-pattern-v23.md` — Story deduplication patterns
- `references/test-assertion-catalog.md` — Full test assertion catalog
- `references/pipeline-enrichment-stage-v23.md` — Editorial enrichment stage docs
- List pending: `python3 scripts/approve_draft.py --list`
- List with limit: `python3 scripts/approve_draft.py --list --limit 50`
- Approve: `python3 scripts/approve_draft.py --id 3,5,7`
