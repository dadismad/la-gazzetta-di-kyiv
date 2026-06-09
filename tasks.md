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
