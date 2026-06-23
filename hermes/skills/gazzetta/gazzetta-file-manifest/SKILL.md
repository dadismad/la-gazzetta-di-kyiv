---
name: gazzetta-file-manifest
description: Strict file manifest protocol for La Gazzetta di Kyiv. Map-before-modify, no ghost files, clear division of labor between /public (deploy), /data (working files), /scripts (logic). Load this before ANY file operation on the Gazzetta project.
version: 2.0.0
category: gazzetta
---

# Gazzetta di Kyiv — Strict File Manifest Protocol v2.0

## Architecture change (June 2026)

The project was restructured from a 21-page multi-HTML site to a single-page application compiled by `build_frontend.py`. `public/data/` is now the CANONICAL data store (contradiction_synthesizer writes directly to it). The old `site/` directory, `public/api/`, `public/dashboard/`, and 40+ dead scripts have been archived or deleted. Scripts remain flat (no subdirectories) because governor.py hardcodes `SCRIPTS/"filename.py"` paths.

## S1 — Map Before Modifying

Before touching ANY file, verify it exists:

```bash
ls ~/lagazzettadikyiv/scripts/   # 13 active scripts
ls ~/lagazzettadikyiv/public/    # index.html, styles.css, robots.txt, sitemap.xml, data/
ls ~/lagazzettadikyiv/data/      # market_prices.json, market_regime.json, editorial_state.json, narratives.json
```

## S2 — Division of Labor

### /public/ — Deploy Directory (synced to GCS)
- **index.html** — The single production HTML file (compiled by build_frontend.py, ~290 KB)
- **styles.css** — CSS (NO content hash — hashed filenames are DEPRECATED)
- **robots.txt**, **sitemap.xml** — SEO files
- **public/data/** — CANONICAL data store:
  - `stories.json` — written by contradiction_synthesizer.py, read by build_frontend.py and telegram_broadcast.py
  - `flows.json` — written by generate_flows.py, read by build_frontend.py
  - `posted_stories.jsonl` — Telegram idempotency log, written by telegram_broadcast.py
- **What does NOT live here**: Nothing else. All old multi-page HTML files, JS duplicates, API endpoints, and dashboard files have been deleted.

### /data/ — Working Files (NOT deployed)
- `market_prices.json` — written by market_reality.py, read by contradiction_synthesizer.py
- `market_regime.json`, `editorial_state.json`, `narratives.json` — configuration/reference
- **Do NOT edit data/stories.json or data/flows.json** — canonical versions are in public/data/

### /scripts/ — Pipeline Logic (13 active scripts, flat structure)
- **Active pipeline**: governor.py, ingestion_triage.py, market_reality.py, contradiction_synthesizer.py, build_frontend.py, build_frontend_staging.py, generate_flows.py, telegram_broadcast.py, test_platform.py
- **Shared**: traffic_cop.py
- **Utilities**: health_check.py, gcf_governor_bridge.py
- **Dead scripts**: Archived to `scripts/archive/` (48 files)
- **Do NOT create subdirectories** — governor.py hardcodes `SCRIPTS/"filename.py"` in its STEPS list

### /docs/ — Documentation
- All architecture docs, runbooks, audits
- `/docs/archive/` — Old root-level .md files moved here during June 2026 cleanup

### /templates/ — Shared Components
- `header.html`, `footer.html`
- `locales/` — i18n files

### /ops/ — Operations
- `gazzetta-governor.service`, `gazzetta-governor.timer` — systemd unit files

## S3 — No Ghost Files

**Deleted and never coming back:**
- `site/` — Dead (replaced by public/)
- `public/api/` — Dead (SPA has no API endpoints)
- `public/dashboard/` — Dead (dashboard.js architecture replaced by build_frontend.py compiler)
- `agents_build/` — Dead (duplicate of scripts, deleted June 2026)
- `staging/` — Dead (old mockup screenshots)
- Root-level Docker, package.json, cloud_entrypoint.py — Deleted June 2026
- `db_to_json.py` — REMOVED from pipeline (overwrites contradiction data with flat baselines)
- `shipit.sh`, `deploy_routine.sh`, `shipit_cloud.sh` — Deleted (governor handles deploy)
- `pipeline_chain.sh` — Dead (references scripts that no longer exist)
- Hashed CSS/JS files — DEPRECATED (use styles.css and inline JS in build_frontend.py)

## S4 — Content vs UI Strict Separation

| If the user asks to... | Edit THIS | NOT this |
|------------------------|-----------|----------|
| Fix content quality (headlines, sources, scoring) | contradiction_synthesizer.py SYSTEM_PROMPT | Any HTML file |
| Add source attribution to cards | build_frontend.py template JS | public/data/stories.json |
| Change capital volume data | market_reality.py (AUM fetch) + contradiction_synthesizer.py (assemble_story) | public/data/stories.json |
| Change CSS styling | public/styles.css | — |
| Fix pipeline order | governor.py STEPS list | systemd unit files |
| Fix Telegram formatting | telegram_broadcast.py format_story_for_telegram() | cco_telegram.py (archived) |
| Deploy | governor deploy step or manual gsutil cp | shipit.sh (deleted) |

## S5 — Pre-Modification Checklist

1. Is this a content change or a UI change? (See S4 table)
2. Does the target file exist on the VM at the same path? (Local and VM must stay in sync)
3. Will this edit be overwritten by the next pipeline cycle? (public/data/ IS overwritten — it's the output, not the input)
4. If editing contradiction_synthesizer.py SYSTEM_PROMPT: test with --dry-run first

## S6 — Post-Modification Verification

1. Push to VM: `gcloud compute scp ... gazzetta-prod:/opt/gazzetta-di-kyiv/scripts/`
2. Restore ownership: `sudo chown -R gazzetta:gazzetta /opt/gazzetta-di-kyiv/scripts/`
3. Run tests: `python3 scripts/test_platform.py` (must pass 106+/107)
4. Build: `python3 scripts/build_frontend.py` (must succeed, ~290 KB output)
5. Check governor logs: `journalctl -u gazzetta-governor | grep -E 'deploy|FAIL'`
6. Verify on live site with browser_console

## S7 — Pipeline Data Flow

```
ingestion_triage.py → gazzetta.db (ingestion_hashes table)
       ↓
market_reality.py → data/market_prices.json (AUM + prices)
       ↓
contradiction_synthesizer.py → public/data/stories.json (DeepSeek output)
       ↓
generate_flows.py → public/data/flows.json
       ↓
build_frontend.py → public/index.html (compiled SPA)
       ↓
test_platform.py → 107 tests
       ↓
telegram_broadcast.py → Telegram channel
       ↓
deploy → gsutil rsync public/ → GCS + CDN invalidation
```

## S9 — Local macOS Directory Structure (June 2026)

The local project root is `~/lagazzettadikyiv/`. The empty shell `~/gazzetta-di-kyiv/` (1 file: `scripts/health_check.py`) is a dead duplicate — ignore or delete it.

```
~/lagazzettadikyiv/           ← Single source of truth (local)
├── scripts/                  ← Active pipeline scripts (~20 files, flat)
├── data/                     ← Canonical data + archive/
│   ├── archive/              ← Stale/backup data files
│   ├── config/               ← data_sources_v2.json
│   ├── market_data/          ← FRED, COT, signals, ICI flows
│   ├── quality_gates/
│   ├── telegram_intel/
│   └── reddit_ingest/
├── design/                   ← Design artifacts (Stitch exports, briefs, patches)
│   ├── master-design-brief.md
│   ├── stitch-exports/
│   └── patches/
├── hermes/                   ← Hermes operational mirror (skills copy, cron inventory, memory snapshot)
├── archive/                  ← Historical reference
│   ├── scripts-v1/           ← ~50 archived scripts from v1–v2
│   └── old-pages/            ← contacts.html, ops.html, etc.
├── docs/                     ← Architecture docs, audits
├── ops/                      ← Systemd unit files, watchdog scripts
├── devvit/                   ← Reddit integration (node_modules, dist)
├── templates/                ← HTML header/footer, i18n locales
├── .backup/                  ← Pre-migration CSS/JS backups
├── .git/                     ← Git history (tags v17–v31+)
├── .venv/                    ← Python 3.13 virtualenv
├── gazzetta.db               ← SQLite database (local mirror)
└── .env.example
```

**Key rules**:
- Do NOT create subdirectories in `scripts/` — `governor.py` hardcodes `SCRIPTS/"filename.py"` paths
- `data/archive/` holds stale files (old watchdogs, backups, deprecated JSON). Active data stays in `data/` root.
- `design/` is NOT deployed. It's local design collateral only.
- `hermes/` is a mirror of `~/.hermes/` state — not the canonical source. Hermes's live state is in `~/.hermes/skills/`, `~/.hermes/memory/`, `~/.hermes/cron/`.
- The `gazzetta.db` locally is a mirror/snapshot. The live DB is on the VM at `/opt/gazzetta-di-kyiv/data/gazzetta.db`.

Files on the VM at `/opt/gazzetta-di-kyiv/` are owned by `gazzetta:gazzetta`. The systemd service runs as `gazzetta`. After any scp push as `alexstocchi`, run: `sudo chown -R gazzetta:gazzetta /opt/gazzetta-di-kyiv/scripts/`. The SSH user is `alexstocchi` (not `gazzetta`).

**CRITICAL — Two copies of stories.json must stay in sync (June 2026):**
- `data/stories.json` — working copy used by contradiction_synthesizer.py
- `public/data/stories.json` — deployed copy synced to GCS by governor deploy step
- After any data migration, BOTH copies must be updated AND chown'd to gazzetta:gazzetta
- Failing to sync public/data/ means GCS serves stale data until the next governor cycle
- Failing to chown means the governor crashes with `Permission denied` on next cycle
- Full protocol: see `gazzetta-cloud-infrastructure` → Data Migration Protocol