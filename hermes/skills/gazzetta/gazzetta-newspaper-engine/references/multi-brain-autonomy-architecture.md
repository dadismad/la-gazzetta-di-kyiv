# Multi-Brain Autonomy Architecture

## Principle

A single agent (Hermes) is a single point of failure. When the agent's session ends or is interrupted, all dependent work halts. The solution: split responsibilities across independent "brains" that run autonomously on infrastructure that doesn't depend on any single human session.

Each brain owns one function. Each brain runs on its own schedule. If one brain dies, the others don't notice.

## Brain 1: The Governor (VM, systemd)

**What**: Data pipeline — ingestion, market prices, contradiction synthesis
**Where**: GCP VM (gazzetta-prod, e2-micro, Debian 12)
**Schedule**: Every 10 minutes via systemd timer
**Produces**: stories-v4.json, flows.json, market_prices.json
**Deploys to**: GCS data/
**Runtime**: systemd oneshot service as `gazzetta` user
**Independence**: Zero dependency on Hermes. Runs on Google Cloud infrastructure.
**Status**: Already operational. Zero changes needed.

## Brain 2: The Designer (Hermes cron)

**What**: Frontend regeneration — reads data from GCS, rebuilds index.html, deploys to GCS
**Where**: Hermes cron job (runs as independent agent session)
**Schedule**: Every 30 minutes
**Input**: stories-v4.json, flows.json (from Brain 1), Stitch design tokens
**Output**: index.html (single responsive file)
**Deploys to**: GCS root
**Independence**: Hermes cron fires regardless of whether a human conversation is active. If the agent running the job fails, the next cron tick spawns a fresh agent session.
**Status**: Needs to be built (implementation Step 3)

## Brain 3: The Publisher (VM, same systemd service)

**What**: Content distribution — posts top stories to Telegram, Reddit
**Where**: VM as part of governor pipeline
**Schedule**: Each governor cycle (every 10 min)
**Produces**: Telegram posts via cco_telegram.py
**Independence**: Same infrastructure as Brain 1. Zero dependency on Hermes.
**Status**: Already operational.

## Why This Fixes The Halt Problem

```
BEFORE (single point of failure):
  Hermes conversation → does everything → if session ends, everything stops

AFTER (multi-brain):
  Brain 1 (VM)      → never stops (systemd)
  Brain 2 (cron)     → never stops (Hermes scheduler)
  Brain 3 (VM)       → never stops (systemd)
  Hermes (human)     → Architect only — sets up system, then brains run themselves
```

## Frontend Architecture (Single Responsive File)

The old approach (build_site.py + hashed JS + multiple HTML files + dashboard.js) is replaced by:

- **Single index.html** at GCS root
- CSS via Tailwind CDN with Stitch DESIGN.md tokens injected into tailwind.config
- Fonts via Google Fonts (Inter, Playfair Display, Material Symbols)
- Data loaded via fetch() from data/stories-v4.json and data/flows.json
- Responsive: mobile single-column (Stitch layout), desktop adds dark sidebar (Banani layout)
- Zero build step. Zero npm. Zero hashed filenames.

### Design Token Sources

| Source | Provides |
|--------|----------|
| Stitch DESIGN.md | Colors (#FAF9F6, #D4AF37, #8B0000, #1A1F2E), typography (Playfair+Inter), 0px radius, no shadows, gold rules, masthead design, card anatomy |
| Banani desktop | Dark sidebar (#000000, 320px), narrative nav with Material Symbol icons, vulnerability map widget, capital flows table |

### What Gets Deleted

- build_site.py — replaced by Brain 2's direct HTML generation
- styles.css — replaced by Tailwind CDN + inline tokens
- dashboard.js — replaced by inline JS in index.html
- All hashed JS files (app.*.js, i18n.*.js, sector.*.js, story-app.*.js)
- Old HTML pages (about.html, archive.html, etc.) — replaced by clean new pages
- Heat map bubbles — violate 0px radius spec
