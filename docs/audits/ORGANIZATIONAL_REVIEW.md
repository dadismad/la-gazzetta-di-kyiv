# Gazzetta di Kyiv — Great Organizational Review

**Date:** 2026-06-11  
**Scope:** Full audit of files, processes, protocols, Hermes management, website architecture, gaps, and redundancies  
**Author:** Hermes Agent (Great Organizational Review)

---

## Executive Summary

Gazzetta di Kyiv is a sophisticated narrative intelligence media platform with a rich knowledge base of 22+ Hermes skills, 7 cron jobs, 63+ Python scripts, and 45+ HTML pages across dual directory trees. It has evolved rapidly through iterative focus group feedback and user direction. However, this organic growth has created significant organizational debt:

- **Root/site split is undefined** — duplicate files with divergent content across two directories
- **Cron scripts live outside the repo** — 4 of 7 cron scripts exist only in `~/.hermes/scripts/` with no version control
- **Pipeline has a known broken stage** — `gazzetta-market-data` cron exits with `generate_flows.py` TypeError
- **Skills overlap 40%** — many reference files/skills cross-reference each other in hard-to-maintain ways
- **No automated deploy verification actually works** — verification skills reference `browser_snapshot`/`browser_vision` tools unavailable in this Hermes installation
- **.gitignore contains malformed entries** — embedded `\\n` literals instead of newlines
- **Data flows duplicate across files** — `stories.json` exists in 4 locations with no definitive source-of-truth protocol

---

## 1. FILE INVENTORY

### 1.1 Project Root — All Tracked Files

| Category | Count | Path | Status |
|----------|-------|------|--------|
| HTML (root) | 23 | `~/gazzetta-di-kyiv/*.html` | SOURCE templates — diverged from site/ |
| HTML (site/) | 20 | `~/gazzetta-di-kyiv/site/*.html` | DEPLOYED versions (post-hashing) |
| JS (root) | 5 | app.js, story-app.js, sector.js, i18n.js | SOURCE (unhashed) |
| JS (site/) | 3 | app.js, story-app.js, sector.js | DEPLOYED (post-hashing, NO i18n.js) |
| CSS (root) | 1 | styles.css | SOURCE |
| CSS (site/) | 2 | styles.css, styles-modern.css | DEPLOYED |
| Python scripts | 63 | `scripts/*.py`, `ops/*.py`, `data/telegram_intel/*.py` | Active |
| Shell scripts | 3 | shipit.sh, `scripts/pipeline_chain.sh`, `scripts/fetch_all_market_data.sh` | Active |
| Data files (JSON) | ~20 | `data/*.json`, `data/publish/*.json`, `site/data/*.json`, `site/api/*.json` | Generated |
| Config | 1 | config.yaml | See recommendations |
| Database | 1 | gazzetta.db | Source of truth (in .gitignore) |
| Other | 1 | .gitignore | Malformed entries |

### 1.2 Active vs. Stale vs. Missing Files

**Active:** shipit.sh, `scripts/db_to_json.py`, `scripts/intel_to_stories.py`, `scripts/build_site.py`, `scripts/build_hashed_assets.py`, `scripts/generate_flows.py`, `scripts/generate_signal_api.py`, all 6 main SKILL.md files

**Stale/Purged-but-present:** `site/contacts.html`, `site/cooperation.html`, `site/ops.html`, `site/privacy.html`, `site/research.html`, `site/variant-modern.html` — these are listed in .gitignore (via broken `\\n` entries) but still on disk

**Weakly ignored:** The `.gitignore` has malformed escaped-newline entries (`\\n` literals) meaning files like `site/contacts.html` are NOT actually ignored. This is a security/inventory risk.

### 1.3 Files Referenced in Crons/Skills That Don't Exist

| File Referenced | Where | Exists Instead |
|-----------------|-------|----------------|
| `gazzetta_product_factory.sh` | cron `gazzetta-product-factory` | Only in `~/.hermes/scripts/` (not in repo) |
| `gazzetta_health_check.sh` | cron `gazzetta-health-check` | Only in `~/.hermes/scripts/` (not in repo) |
| `gazzetta_enrich_stories.py` | cron `gazzetta-living-stories` | Only in `~/.hermes/scripts/` (not in repo) |
| `gazzetta_pipeline_chain.sh` | cron `gazzetta-market-data` | Only in `~/.hermes/scripts/` (not in repo) |
| `data/quality_gates/latest.json` | CEO overseer freshness check | May not exist — flagged in SKILL.md |
| `data/telegram_intel/latest.json` | editorial-writer Step 1 | May not exist — no regeneration pipeline |
| `ops/` or `~/.hermes/scripts/` telegram pipeline scripts | CEO overseer freshness | Confirmed none exist |

### 1.4 Duplicate Data Files (Split-Brain Risk)

| File | Locations | Risk |
|------|-----------|------|
| `stories.json` | `data/`, `site/data/`, `data/publish/`, `site/api/v1/home/` | Multiple copies, different pipelines generate different subsets |
| `flows.json` | `data/`, `site/data/` | `db_to_json.py` generates 80+ flows, `generate_flows.py` generates 12-20. Which is authoritative? |
| `narratives.json` | `data/`, `site/data/`, `data/publish/` | Triple copy with no clear sync direction |

---

## 2. PROCESS MAP

### 2.1 Cron Job → Script → File → Deploy Chain

| Cron | Frequency | Type | What Runs | Produces | Status |
|------|-----------|------|-----------|----------|--------|
| `gazzetta-product-factory` | Every 60m | Script | `gazzetta_product_factory.sh` → fetch_intel → intel_to_stories → approve_drafts → generate_flows → db_to_json → shipit | Full site deploy | OK (12 runs) |
| `gazzetta-health-check` | Every 30m | Script | `gazzetta_health_check.sh` | Health report to Telegram | OK (21 runs) |
| `gazzetta-ceo-overseer` | Every 15m | Agent | Loads gazzetta-ceo-overseer skill | Surveillance report | OK (34 runs) |
| `gazzetta-market-data` | Every 360m | Script | `gazzetta_pipeline_chain.sh` → intel_to_stories → decay → validate → generate_flows → translate → build_site | Data refresh | **ERROR** (generate_flows.py TypeError) |
| `gazzetta-quality-gate` | 07:00, 19:00 | Agent | Loads gazzetta-interpret-review-execute skill | Quality report | OK (1 run) |
| `gazzetta-editorial-writer` | 06:30, 18:30 | Agent | Loads gazzetta-editorial-writer skill | Editorial cycle | OK (1 run) |
| `gazzetta-living-stories` | Every 120m | Script | `gazzetta_enrich_stories.py` | Story enrichment | OK (5 runs) |
| `daily-session-review` | 22:00 daily | Agent | Loads daily-session-review skill | Memory extraction | Never run (0 completed) |

### 2.2 shipit.sh Full Pipeline

```
Stage 0: nuclear_clean → rm -rf site/{data,api,ru,media} + hashed assets
Stage 1: db_to_json → data/stories.json + data/flows.json from gazzetta.db
Stage 1.02: enrich_multi_persona → multi-persona blocks
Stage 1.05: fetch_live_prices → CoinGecko prices
Stage 1.1: build_related_links → story→story & story→flow links
Stage 1.2: analyze_narratives → 3 Core Market Narratives
Stage 1.5: enrich → editorial enrichment + signal/trades APIs
Stage 2: build_site → sync data/ → site/data/
Stage 2.2: generate_broadcasts → distribution content
Stage 2.5: TEST GATE → test_platform.py (blocking — aborts on failure)
Stage 3: build_hashed_assets → SHA256 hash CSS/JS, rewrite HTML
Stage 3.1: ru_sync_gate → SKIPPED (Russian removed)
Stage 4: GCS deploy → rsync -d to bucket, set cache headers
Stage 5: external_verify → curl homepage + stories.json
Stage 6: deploy report → deploy_report.txt
Stage 7: git sync → add → commit → push
```

**Gap:** Stage 5 verifies only via curl (static HTML only) — cannot detect JS rendering failures. Skills reference `browser_snapshot`/`browser_vision` tools that don't exist in this Hermes installation.

### 2.3 Editorial Pipeline

```
Telegram Intel Monitor (30m) → intel_to_stories.py → gazzetta.db (SQLite)
    → db_to_json.py → data/stories.json + data/flows.json
        → enrich_editorial_stories.py (capital_flow + generated_at)
        → ensure_generated_at.py (backfill timestamps)
        → generate_signal_api.py → api/v1/signal.json
        → generate_trades_api.py → api/v1/trades.json
        → build_track_record.py → track_record.json
        → translate_content.py → stories_ru.json + flows_ru.json
            → build_site.py → site/data/
                → shipit.sh → GCS → LIVE
```

**Gap:** No automated RU translation pipeline running. No `translate_content.py` in any cron. The RU `index.html` at `site/ru/` doesn't exist in the repo.

### 2.4 Missing Processes

- **No automatic Telegram content publishing** — editorial-writer generates `telegram_latest.md` but no cron publishes it
- **No Devvit auto-deploy** — editorial-writer generates `reddit_latest.md` but the Devvit bake → upload → install cycle is manual
- **No quality_gates persistence** — `latest.json` has no regeneration pipeline per SKILL.md
- **No telegram_intel regeneration** — stale >12h with no fix path
- **No .gitignore repair** — malformed `\\n` entries silently fail to ignore purged pages

---

## 3. PROTOCOL AUDIT

### 3.1 SKILL.md Accuracy Assessment

| Skill | Version | Status | Issues |
|-------|---------|--------|--------|
| `gazzetta-website` | 23.22.0 | **Overgrown** | 1084 lines — tries to cover design, deployment, verification, i18n, flow-nodes, triangulation. Needs splitting. |
| `gazzetta-ceo-overseer` | 2.4.3 | **Partial** | References browser/vision tools unavailable in this env. Auto-fix commands reference `~/.hermes/scripts/` that may not exist. |
| `gazzetta-verify-deploy` | 2.1.0 | **Cannot execute** | Mandates browser console checks, snapshots, vision tools — all unavailable. |
| `gazzetta-editorial-writer` | 1.5.0 | **Active** | Well-maintained with quality gate notes. References pipeline-gotchas.md. |
| `gazzetta-sqlite-pipeline` | 1.0.0 | **Accurate** | Clean architecture diagram. |
| `gazzetta-knowledge-base` | 1.9.0 | **Reference-only** | Pure reference — no actionable commands. |
| `gazzetta-knowledge-index` | 1.2.0 | **Useful but stale** | Pipeline map references outdated cron IDs. |
| `gazzetta-capital-flow-monitor` | 1.0.1 | **Contradicts others** | Says run `generate_flows.py` but gazzetta-website says NEVER run it standalone (truncates flows). |
| `gazzetta-generate-flows` | 1.0.0 | **Contradicts others** | Same issue — recommends `generate_flows.py` standalone. |
| `gazzetta-living-stories` | 1.0.0 | **Lightweight** | References scripts that don't match current architecture. |
| `gazzetta-integrity-check` | 1.0.1 | **Stale** | References old cron IDs. |
| `gazzetta-russian-translation` | - | **Partially stale** | RU pipeline removed June 2026 — skill references scripts/paths that may not exist. |
| `gazzetta-devvit-posting` | 1.0.0 | **Active** | Well-maintained with clear bake→upload→install workflow. |
| `gazzetta-reddit-devvit-pipeline` | 2.0.0 | **Overlaps devvit-posting** | ~30% overlap with gazzetta-devvit-posting. Should merge. |
| `gazzetta-paradigm-and-strategy` | 1.0.0 | **Reference** | Broad strategy — no stale commands. |
| `gazzetta-precision-pipeline` | 1.5.0 | **Pure reference** | No actionable commands. |
| `gazzetta-marketing-playbook` | 1.0.0 | **Pure reference** | No stale commands. |
| `gazzetta-interpretation-framework` | 1.0.0 | **Active** | Well-scoped. |
| `gazzetta-event-driven-trading` | 1.0.0 | **Pure reference** | No stale commands. |
| `gazzetta-prediction-market-trading` | 1.0.0 | **Pure reference** | No stale commands. |
| `asymmetric-positioning-framework` | 1.0.0 | **Pure reference** | No stale commands. |
| `focus-group-review` | 3.0.0 | **Cannot fully execute** | References browser_snapshot/browser_vision tools unavailable. |
| `content-analysis-loop` | 1.0.0 | **Pure reference** | No stale commands. |

### 3.2 Cross-Skill Contradictions

**HIGH PRIORITY — Contradictory flow generation instructions:**

| Skill | Says |
|-------|------|
| `gazzetta-website` | `db_to_json.py` is authoritative (80+ flows). **Never run `generate_flows.py` standalone** — it truncates 84→12 flows |
| `gazzetta-capital-flow-monitor` | Runs `generate_flows.py` as step 1 of its pipeline |
| `gazzetta-generate-flows` | `generate_flows.py` is the tool to use — outputs 12 flows |
| cron `gazzetta-market-data` | Calls `gazzetta_pipeline_chain.sh` which runs `generate_flows.py` |

This contradiction means the pipeline chain called by `gazzetta-market-data` may be overwriting rich flow data with minimal flows.

### 3.3 CEO Overseer Auto-Fix Verification

The CEO overseer's auto-fix commands reference:
- `~/.hermes/scripts/` paths for recovery scripts
- `gsutil` from `~/lagazzettadikyiv/google-cloud-sdk/bin/`
- `browser_snapshot` / `browser_vision` for visual verification

**Status:** The GSDK `gsutil` exists and works. The browser tools do NOT exist in this Hermes installation. The CEO overseer can check HTTP endpoints but cannot verify JS rendering. Auto-fix claims may be based on incomplete data.

### 3.4 Deploy Verification Protocol

The protocol defined in `gazzetta-verify-deploy` mandates:
1. Reversion check (curl) — **works**
2. flows.json quality check (curl) — **works**
3. Browser console checks — **DOES NOT WORK — no browser tools**
4. ALL-PAGE VISUAL SWEEP — **DOES NOT WORK — no browser_vision**
5. Corrupted file detection (bash grep) — **works**
6. RU page verification — **partially works** (RU removed June 2026)

**Verdict:** The deploy verification protocol cannot be fully executed in this environment. Critical gaps exist around JS interactivity checks.

---

## 4. HERMES MANAGEMENT

### 4.1 Skill Inventory — 22 Skills Total

**Active (production-facing, used in crons):** 6
- gazzetta-website, gazzetta-ceo-overseer, gazzetta-verify-deploy, gazzetta-editorial-writer, gazzetta-interpret-review-execute, gazzetta-knowledge-index

**Pipeline/Infrastructure:** 4
- gazzetta-sqlite-pipeline, gazzetta-capital-flow-monitor, gazzetta-generate-flows, gazzetta-living-stories

**Quality/Process:** 3
- gazzetta-integrity-check, gazzetta-precision-pipeline, focus-group-review

**Content Production:** 3
- gazzetta-russian-translation, gazzetta-devvit-posting, gazzetta-reddit-devvit-pipeline

**Reference Only (no executable commands):** 6
- gazzetta-knowledge-base, gazzetta-paradigm-and-strategy, gazzetta-marketing-playbook, gazzetta-interpretation-framework, gazzetta-event-driven-trading, gazzetta-prediction-market-trading, asymmetric-positioning-framework, content-analysis-loop

**Stale/Candidates for merge:**
- `gazzetta-devvit-posting` and `gazzetta-reddit-devvit-pipeline` overlap ~30%
- `gazzetta-generate-flows` contradicts `gazzetta-website` on flow authority
- `gazzetta-capital-flow-monitor` overlaps with `gazzetta-generate-flows`

### 4.2 Cron Jobs — Agent vs Script Split

| Cron | Type | Est. Token Cost | Notes |
|------|------|----------------|-------|
| gazzetta-product-factory | Script ($0) | 0 | 1h cycle |
| gazzetta-health-check | Script ($0) | 0 | 30min cycle |
| gazzetta-ceo-overseer | Agent (~2K tokens) | ~2K × 96/day = ~192K/day | Every 15min — HIGH cost |
| gazzetta-market-data | Script ($0) | 0 | Every 360min — **broken** |
| gazzetta-quality-gate | Agent (~5K tokens) | ~5K × 2/day = ~10K/day | Twice daily |
| gazzetta-editorial-writer | Agent (~15K tokens) | ~15K × 2/day = ~30K/day | Twice daily |
| gazzetta-living-stories | Script ($0) | 0 | Every 120min |
| daily-session-review | Agent (~8K tokens) | ~8K/day | Every 22:00 — never run |

**Total agent token cost:** ~232K tokens/day (~$1-2/day depending on model)

### 4.3 Profile Structure

- **Active profile:** `default` (this session)
- **Other profiles:** None detected in `~/.hermes/profiles/`
- **Cross-profile issues:** None

### 4.4 Memory Persistence

Memory entries are stored in `~/.hermes/hermes-agent/` (the default profile path). The CEO overseer's `ghost detection` check confirms `~/.hermes/hermes-agent/gazzetta-di-kyiv/` does NOT exist — good, no ghost copies.

---

## 5. WEBSITE ARCHITECTURE

### 5.1 HTML Templates — Active vs Purged

**Active (20 pages in site/):**
`index.html` (homepage), `stories.html`, `flows.html`, `signal.html`, `trades.html`, `track.html`, `event_horizon.html`, `flow-nodes.html`, `story.html`, `capital.html`, `markets.html`, `geopolitics.html`, `wealth.html`, `pleasure.html`, `about.html`, `data.html`, `methodology.html`, `sources.html`, `terms.html`, `dashboard/index.html`

**Purged but still on disk (in root only):**
`contacts.html`, `cooperation.html`, `ops.html`, `privacy.html`, `research.html`, `variant-modern.html`

**GCS verification:** Contents of `site/` are what gets synced. Purged root HTML files are NOT deployed to GCS. They exist as local artifacts only.

### 5.2 CSS Architecture

- **One primary file:** `styles.css` (~8,000+ lines)
- **Secondary file:** `styles-modern.css` (experimental variant)
- **Hashing:** SHA256 first 8 hex chars → `styles.354543bb.css`
- **Version tracking:** None beyond content hashing
- **Root vs site/ divergence:** Root has unhashed `styles.css`, site/ has hashed `styles.354543bb.css`. If both are edited independently, they will diverge silently.

### 5.3 JavaScript Architecture

| File | Purpose | Dependencies | Size |
|------|---------|-------------|------|
| `app.js` | Main app — collapsible containers, hero indicators, story cards, flow rendering, anchor positions, signal triangulation, track record, i18n integration, share buttons, polling | i18n.js, styles.css | ~3,500+ lines |
| `story-app.js` | Story detail page (`story.html?id=X`) — intel report renderer, prev/next navigation | app.js (Gazzetta namespace), i18n.js | ~1,000+ lines |
| `sector.js` | Sector pages (geopolitics, markets, wealth, pleasure) — keyword-filtered story display | app.js (shared Gazzetta namespace) | ~500+ lines |
| `i18n.js` | Internationalization — loads `i18n_ru.json`, `applyTranslations()`, `i18n.t()` | None | ~200+ lines |

**Critical:** `i18n.js` exists at root level but NOT in `site/`. After `build_hashed_assets.py` runs, it should produce `i18n.[hash].js` in `site/`. If it doesn't, RU translations on the live site are broken.

### 5.4 Data Flow

```
gazzetta.db (SQLite) → db_to_json.py
    → data/stories.json     (canonical, ~200+ stories)
    → data/flows.json       (canonical, ~80+ flows)
    → site/data/stories.json (deploy copy)
    → site/data/flows.json   (deploy copy)

data/ → build_site.py → site/data/ (syncs 13+ files)

Site JS bootstrap:
1. index.html loads → app.js + i18n.js
2. fetchFlows() → site/data/flows.json → render flows + hero confidence
3. fetch stories.json → site/data/stories.json → render story cards
4. Triangulation → signal.json + trades.json
5. Start polling loops

Product pages (stories.html, flows.html, etc.):
- Same data files (site/data/stories.json)
- Different JS rendering paths
- share app.js for masthead/nav/i18n
```

**Same data path for homepage and product pages:** YES — all read from `site/data/stories.json` and `site/data/flows.json`. The difference is in the JS renderer, not the data source.

### 5.5 Hashed Asset System

`build_hashed_assets.py` handles:
1. SHA256 hash of CSS/JS → 8-char hex prefix
2. Create hashed copy in site/
3. Rewrite ALL HTML references in site/ to use hashed filenames
4. Generate `build-manifest.json`

**Hashed assets are NOT in the repo** — they're in `.gitignore` and generated at build time.

---

## 6. GAPS & REDUNDANCIES

### 6.1 What Should Exist But Doesn't

| Gap | Impact | Effort |
|-----|--------|--------|
| **No cron scripts in repo** — gazzetta_product_factory.sh, gazzetta_health_check.sh, gazzetta_enrich_stories.py, gazzetta_pipeline_chain.sh exist only in `~/.hermes/scripts/` | Version control blind spot. Repo fork = cron scripts lost. | Low — copy to repo |
| **No .gitignore repair** — malformed `\\n` entries don't actually ignore files | Purged HTML files may leak into commits. New developers confused. | **Trivial** — 1-line fix |
| **No RU deployment** — stage 3.1 is `echo SKIPPED` | Russian audience has no live site | High effort (separate concern) |
| **No quality_gates persistence** — `latest.json` has no regeneration pipeline | CEO overseer can't verify quality gate freshness | Low — remove the check or create a stub |
| **No Telegram auto-publish** — editorial-writer generates content but no cron distributes it | Content produced but not distributed | Medium |
| **No Devvit auto-deploy** — reddit_latest.md generated but Devvit bake/upload/install is manual | Reddit content not auto-published | Medium |
| **No i18n.js in site/** — root has it but site/ may not after build | RU translations broken if i18n.js isn't deployed | Medium — verify build chain |
| **No browserless verification** — deploy verification protocol mandates unavailable tools | False "all clear" reports | Low — add curl+console alternatives |

### 6.2 What Exists Twice (Redundancies)

| Redundancy | Locations | Consolidation |
|------------|-----------|---------------|
| gazzetta_product_factory.sh | `~/.hermes/scripts/`, `gazzetta-sqlite-pipeline/scripts/`, `gazzetta-website/scripts/` | 3 copies, 2 skill versions (v23.22 vs v23.24) |
| verify_reality.py | `gazzetta-sqlite-pipeline/scripts/`, `gazzetta-knowledge-base/scripts/`, `scripts/` | 3 copies |
| gazzetta-devvit-posting + gazzetta-reddit-devvit-pipeline | Different skills, ~30% overlap | Merge into one |
| stories.json | `data/`, `site/data/`, `data/publish/` | 3 copies with no clear write authority |
| flows.json | `data/`, `site/data/` | 2 copies, 2 different generators |
| narratives.json | `data/`, `site/data/`, `data/publish/` | 3 copies |
| HTML files | `root/*.html` + `site/*.html` | Diverged copies |

### 6.3 What's Broken Silently

| Issue | Symptom | Detection Method |
|-------|---------|-----------------|
| `generate_flows.py` TypeError on float | `gazzetta-market-data` cron exits with code 1 | jobs.json shows `last_status: error` |
| RU page not deployed | Stage 3.1 is echo SKIPPED | Manual check — no health check catches it |
| i18n.js may be absent from site/ | RU users see only English | Check `site/` for i18n files |
| quality_gates/latest.json stale | CEO overseer flags stale data | SKILL.md confirms no regeneration exists |
| telegram_latest.md stale >12h | Telegram content not fresh | SKILL.md confirms no regeneration pipeline |
| Duplicate flow generators | db_to_json.py (80+ flows) vs generate_flows.py (12-20) | Pipeline chain runs generate_flows AFTER db_to_json, overwriting |

### 6.4 Manual Steps That Should Be Automated

| Step | Current | Target |
|------|---------|--------|
| Reddit posting | Manual Devvit bake→upload→install | Cron script |
| Telegram content distribution | Editorial-writer produces content, no cron publishes | Telegram bot cron |
| RU language deploy | Stage 3.1 is echo SKIPPED | Re-enable or remove cleanly |
| Quality gate persistence | quality_gates/latest.json has no writer | Add minimal writer script |
| Cron script syncing | Scripts exist in ~/.hermes/scripts/ but not in repo | Copy to repo `scripts/cron/` |

---

## 7. RECOMMENDATIONS

### PRIORITY 1 — CRITICAL (Fix now)

| # | Recommendation | Impact | Effort | Risk |
|---|---------------|--------|--------|------|
| 1.1 | **Fix .gitignore escaped newlines** — Replace `\\n` literals with real newlines | Prevents purge-page leakage into git | **Trivial** (1 edit) | Very low |
| 1.2 | **Fix generate_flows.py TypeError** — Add `isinstance(amt_str, (str, bytes))` guard in `parse_amount()` (line 48) | Unblocks gazzetta-market-data cron | **Trivial** (1 line) | Very low |
| 1.3 | **Fix flow generation authority** — Ensure pipeline_chain.sh calls db_to_json.py (not generate_flows.py) as authoritative source. OR: Remove generate_flows.py from pipeline if db_to_json is canonical. | Prevents 80+→12 flow truncation | Low | Medium (need to pick authority) |
| 1.4 | **Copy cron scripts to repo** — `cp ~/.hermes/scripts/gazzetta_*.{sh,py} ~/projects/gazzetta-di-kyiv/scripts/cron/` | Version control for all scripts | Low | Very low |
| 1.5 | **Fix root/site divergence** — Decide: root=SOURCE or site=SOURCE? If root is source, build_site.py must copy root→site before hashing. If site is source, delete root duplicates. | Prevents silent divergence | Medium | Medium |

### PRIORITY 2 — HIGH (Fix this week)

| # | Recommendation | Impact | Effort | Risk |
|---|---------------|--------|--------|------|
| 2.1 | **Merge gazzetta-devvit-posting + gazzetta-reddit-devvit-pipeline** — 30% overlap causes confusion | Cleaner Reddit pipeline | Low | Very low |
| 2.2 | **Add browserless deploy verification** — Create `scripts/deploy_verify.py` that checks HTTP endpoints, JSON integrity, mtime freshness without browser | Real verification instead of "can't check" | Medium | Low |
| 2.3 | **Normalize data file locations** — Pick ONE authoritative copy per data file. Update build_site.py accordingly. | Eliminate split-brain | Medium | Medium |
| 2.4 | **Check i18n.js presence in site/** — Verify build_hashed_assets.py processes i18n.js. If missing, add to ASSETS list. | RU translation fixes | Low | Very low |
| 2.5 | **Remove quality_gates staleness check or add stub** — Either create `scripts/touch_quality_gate.py` or remove the check from CEO overseer | Silent false "FAIL" alerts | Low | Very low |

### PRIORITY 3 — MEDIUM (Fix this sprint)

| # | Recommendation | Impact | Effort | Risk |
|---|---------------|--------|--------|------|
| 3.1 | **Purge root HTML duplicates** — Remove `contacts.html`, `cooperation.html`, `ops.html`, `privacy.html`, `research.html`, `variant-modern.html` from disk (already in gitignore intent) | Cleaner repo | Low | Low |
| 3.2 | **Consolidate flow generation skills** — Merge gazzetta-capital-flow-monitor, gazzetta-generate-flows, and the contradictory flow sections in gazzetta-website into one skill | Eliminate contradictions | Medium | Low |
| 3.3 | **Add `scripts/cron/` directory** — Copy all cron scripts into repo with README explaining they're symlinked/copied to ~/.hermes/scripts/ | Traceability | Low | Low |
| 3.4 | **Audit SKILL.md version drift** — 22 skills with no unified version system. Add version cross-reference table to gazzetta-knowledge-index. | Better maintainability | Medium | Low |
| 3.5 | **Fix daily-session-review cron** — Has never run (0 completed). Either configure or remove. | Resource cleanup | Low | Very low |

### PRIORITY 4 — LOW (Nice to have)

| # | Recommendation | Impact | Effort | Risk |
|---|---------------|--------|--------|------|
| 4.1 | **Automate Telegram content distribution** — Add cron that reads `data/publish/telegram_latest.md` and sends via Bot API | Full auto-publishing | High | Medium |
| 4.2 | **Add RU deploy back or remove cleanly** — Stage 3.1 echo SKIPPED is untidy. Either implement RU pipeline or add architectural note | Cleaner codebase | High | Low |
| 4.3 | **Split gazzetta-website SKILL.md** — 1084 lines covering design, deploy, verification, i18n, flow-nodes, triangulation. Split into 3-4 focused skills. | Maintainability | High | Low |
| 4.4 | **Add version tracking to CSS** — Comment header with date and change summary | Debuggability | Trivial | Very low |

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Python scripts | 63 |
| Total HTML pages | 23 (root) + 20 (site/) |
| Total JS files | 5 (root) + 3 (site/) |
| Total Hermes skills | 22 |
| Active cron jobs | 8 (7 gazzetta + 1 daily-session) |
| Broken cron jobs | 1 (gazzetta-market-data) |
| Files outside repo referenced | 4 cron scripts |
| Skills with verifiable contradictions | 3 (flow generation authority) |
| Tools referenced but unavailable | 2 (browser_snapshot, browser_vision) |
| Data files with duplicate locations | 3 (stories.json, flows.json, narratives.json) |
| Purged-but-on-disk HTML files | 6 |
| .gitignore formatting bugs | 1 (malformed escaped newlines) |
