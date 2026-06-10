# Gazzetta di Kyiv — Development Goals

> Updated: 2026-06-09 · Refresh context: `python3 refresh_context.py`

## Phase 1: Infrastructure and State Stabilization ✅

- [x] Virtual environment (`.venv/`, Python 3.13.7)
- [x] `.gitignore` (venv, build artifacts, OS files)
- [x] `shipit.sh` — 6-stage build → hash → deploy → verify → git pipeline
- [x] `refresh_context.py` — Grounding Protocol (git/data/live drift detection)
- [x] Content-hashed assets (`build_hashed_assets.py`) with immutable caching
- [x] Canonical source → `site/` sync
- [x] Build manifest (`build-manifest.json`)
- [x] WCAG AA contrast (green #047857, gold #B8860B)
- [x] Frameless design enforcement (no shadows, borders, radius)
- [x] Error visibility (empty catch blocks logged)
- [x] Story timestamps (relative time indicators)
- [x] Duplicate-ID rendering bugs fixed (`byId()` page-aware resolution)

## Phase 2: Configuration Decoupling

- [x] Central `config.yaml` — site metadata, paths, feature flags
- [x] `scripts/intel_to_stories.py` — dynamic config import via PyYAML
- [x] `shipit.sh` — reads paths from config
- [ ] `scripts/generate_flows.py` — migrate to config
- [ ] `scripts/build_site.py` — migrate to config
- [ ] `scripts/build_hashed_assets.py` — migrate to config
- [ ] `refresh_context.py` — migrate to config

## Phase 3: Script Modernization (Python 3.13)

- [x] All scripts run via `.venv/bin/python` (3.13.7)
- [x] `requests`, `bs4` (BeautifulSoup), `pyyaml` installed
- [ ] Type hints throughout (PEP 484)
- [ ] Replace string paths with `pathlib.Path`
- [ ] Replace `os.path` with `pathlib` where practical
- [ ] Add `__main__` guard blocks to all scripts
- [ ] Remove dead code / unused imports
- [ ] Add docstrings to all public functions

## Phase 4: Automated Deployment Reports

- [x] `deploy_report.txt` generated on each deploy
- [x] Report includes: timestamp, commit hash, story count, live headers
- [x] Report synced to GCS (`lagazzettadikyiv.com/deploy_report.txt`)
- [ ] Weekly digest report (stories/week, top flows, drift incidents)
- [ ] Slack/Telegram notification on deploy
- [ ] Dashboard page on site showing deploy history

## Future Phases

- [ ] Phase 5: Data Pipeline Hardening (validate, retry, alert on stale data)
- [ ] Phase 6: Multi-language (Russian, Italian, Ukrainian)
- [ ] Phase 7: API v2 (structured feeds, RSS, JSON API)
- [ ] Phase 8: Performance (lazy loading, image optimization, CDN edge caching)
- [ ] Phase 9: User Accounts (saved filters, alerts, watchlists)
- [ ] Phase 10: Mobile App (React Native / PWA)

## Strategic Audit — Bloomberg (2026-06-10)
- [ ] Live Ticker Tape [HIGH IMPACT] [MEDIUM]
  _Real-time scrolling price ticker at page top with last-trade prices, % change, and volume for key assets._
  → Establishes 'terminal-grade' data authority — signals the site is alive and institutional.
- [ ] Dark Terminal Mode [MEDIUM IMPACT] [MEDIUM]
  _Professional dark background with high-contrast amber/green mono text mimicking Bloomberg Terminal._
  → Reduces eye strain for professional users who keep the site open all day.
- [ ] Asset Class Color System [HIGH IMPACT] [LOW]
  _Consistent color coding per asset class (FX=Blue, Equities=Green, Commodities=Gold, Crypto=Purple) across all charts and data._
  → Reduces cognitive load — users instantly recognize asset context without reading labels.

## Strategic Audit — Zerohedge (2026-06-10)
- [ ] Firehose Feed [HIGH IMPACT] [LOW]
  _Continuous scrolling feed of headlines with timestamps, no pagination — infinite scroll._
  → Captures scanning behavior — traders refreshing for new signals get immediate value.
- [ ] Comment Section Velocity [MEDIUM IMPACT] [MEDIUM]
  _Active comment section with upvote/downvote that surfaces crowd sentiment on each story._
  → Adds community validation layer — crowd wisdom can complement systematic analysis.
- [ ] Zero-Click Headline Expansion [HIGH IMPACT] [LOW]
  _Hovering over a headline shows the first 3 paragraphs without navigating away._
  → Increases scan speed — traders can assess 3x more stories per minute.

## Strategic Audit — Reuters (2026-06-10)
- [ ] Fact-Checked Source Attribution [HIGH IMPACT] [LOW]
  _Every data point carries a visible source citation with timestamp and verification status._
  → Builds institutional trust — readers can trace every claim to its origin.
- [ ] Photo-Led Story Cards [HIGH IMPACT] [MEDIUM]
  _Every story card has a high-quality lead image with overlay headline and category tag._
  → Increases engagement — visual processing is 60,000x faster than text.
- [ ] Section-Specific RSS Feeds [MEDIUM IMPACT] [LOW]
  _Granular RSS feeds per topic, region, and asset class for programmatic consumption._
  → Enables API-like distribution without building a full API — reaches power users and bots.

## Strategic Audit — Kobeissi (2026-06-10)
- [ ] Chart-Anchored Analysis [HIGH IMPACT] [MEDIUM]
  _Every macro thesis paired with an annotated chart showing key levels, signals, and historical patterns._
  → Visual conviction — readers trust analysis more when they can see the data themselves.
- [ ] Newsletter-First Publishing [HIGH IMPACT] [LOW]
  _Content optimized for email delivery with digest format, TLDR summaries, and mobile-friendly sizing._
  → Email is the highest-conversion distribution channel for financial content.
- [ ] Twitter Thread Expansion [MEDIUM IMPACT] [LOW]
  _Long-form analysis broken into numbered tweet-sized chunks for native social distribution._
  → Maximizes reach — Twitter is where financial professionals discover new sources.

## Strategic Audit — Polymarket (2026-06-10)
- [ ] Probability-Anchored Headlines [HIGH IMPACT] [MEDIUM]
  _Every story shows real-time prediction market odds for the event outcome._
  → Adds quantitative conviction layer — 'market says 67% chance' is more compelling than opinion.
- [ ] Event Resolution Timeline [HIGH IMPACT] [HIGH]
  _Visual countdown to event resolution with historical odds chart showing probability shifts over time._
  → Creates urgency and narrative arc — users return to see how odds evolved.
- [ ] Volume-Weighted Consensus [MEDIUM IMPACT] [MEDIUM]
  _Market odds weighted by trading volume and unique traders, not just raw probability._
  → Prevents manipulation — thin markets with 1-2 traders shouldn't show the same confidence as deep ones.
