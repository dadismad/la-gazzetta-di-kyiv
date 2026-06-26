# CTO State Persistence Protocol — La Gazzetta di Kyiv
# Updated: 2026-06-26 19:50 Kyiv
# Read this at the START of every session.

## Architecture State

### Infrastructure
- **VM**: gazzetta-prod (e2-micro, us-central1-a, 3.8GB RAM, 30GB disk, 4.2GB used)
- **Project root**: /opt/gazzetta-di-kyiv/
- **User**: gazzetta (all pipeline processes)
- **Python venv**: /opt/gazzetta-di-kyiv/venv/bin/python
- **Deploy**: deploy_to_gcs.py → gs://www.lagazzettadikyiv.com/ → CDN
- **Scheduler**: systemd timer gazzetta-governor.timer (10-min cycle)
- **SSH alias**: gazzetta-prod
- **Local repo**: ~/lagazzettadikyiv/
- **Git remote**: https://github.com/pureciclismo/gazzetta-di-kyiv (HTTPS, pureciclismo token)
- **gsutil**: /opt/gazzetta-di-kyiv/devvit/google-cloud-sdk/bin/gsutil (symlink → /usr/bin/gsutil)
- **DB**: /opt/gazzetta-di-kyiv/data/gazzetta.db (must use `sudo -u gazzetta sqlite3`)

### Pipeline (16 steps)
youtube → arxiv → ingestion → market_data → cftc_data → fred_data → derivatives
→ synthesis → classify → calc_capital → gen_flows → build_frontend → test_platform
→ pulse → telegram_post → deploy

### Active Scripts (25)
build_frontend.py (1720L), contradiction_synthesizer.py (1069L), governor.py,
calculate_capital.py, classify_stories.py, db_to_json.py, deploy_to_gcs.py,
fetch_arxiv.py, fetch_cftc.py, fetch_derivatives.py, fetch_fred.py,
fetch_narrative_cap.py, fetch_patents.py, fetch_youtube.py, generate_flows.py,
health_check.py, ingestion_triage.py, market_reality.py, narrative_pulse.py,
purge_cache.py, telegram_broadcast.py, telegram_stats.py, test_platform.py,
traffic_cop.py, build_dossiers.py

### Data Files
- stories.json: public/data/stories.json (600 stories, 6.8MB)
- flows.json: public/data/flows.json (12 narratives, 4.7KB)
- narratives.json: data/narratives.json (12 narratives with tickers + invalidation thresholds)
- narrative_graph.json: data/narrative_graph.json (67 assets across 12 narratives)
- narrative_cap.json: data/narrative_cap.json ($18.28T total NMC pool)
- market_prices.json: data/market_prices.json (42 tickers)
- cftc_positions.json: data/cftc_positions.json
- fred_series.json: data/fred_series.json (27 series, regime always NEUTRAL)
- derivatives.json: public/data/derivatives.json
- gazzetta.db: 2,593 ingested, 376 DB stories

### Key Configurations
- BATCH_SIZE=10 (synthesis processes 10 items per cycle)
- MAX_CAPITAL_PER_STORY=10_000_000_000 ($10B hard cap)
- MATERIALITY_THRESHOLD_USD=50_000_000
- 12 narratives with destination-framing display names
- 5 tabs: Flow, Tactical Bets, Capital Flows, Contradictions, About
- Capital bridge: capital_at_stake_usd → capital_volume_usd in build_frontend.py line 228-230

### API Keys
- DEEPSEEK_API_KEY: in GCP Secret Manager (gazzetta-deepseek-key) + VM .env
- FRED_API_KEY: in GCP Secret Manager (gazzetta-fred-key v2) + VM .env
- TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID: in VM .env
- CFTC: public SODA API, no key needed

## Active Bugs & Known Issues

### P2 — Deferred
- FRED macro regime classifier stuck at "NEUTRAL" (27/27 series fetched, thresholds need review)
- NMC data 26h stale (fetch_narrative_cap.py not in 10-min governor pipeline)
- Light-mode design refactor (~50 color changes in build_frontend.py, approved not executed)

### P3 — Cosmetic
- GAP Leaderboard ticker labels use story-affected tickers (not narrative canonical) — line 1224 JS
- "No threshold defined" text was removed (Jun 26 fix), but About tab Lifecycle Phases table still shows "No threshold defined" appended to some entries — likely cached HTML. Verify after next governor cycle.
- Trophy Asset CFT block had empty CATALYST/FLOW — .strip() guard added (Jun 26 fix). Verify after next synthesis cycle.

### Fixed Today (Jun 26)
- ✅ Capital computation: FRED normalization + per-story division + $10B hard cap (f1070ec2)
- ✅ Capital field bridge: capital_at_stake_usd → capital_volume_usd in build_frontend (f1070ec2)
- ✅ Source attribution: extract_domain() replaces source_type.upper(), 13 named sources (fffddf14)
- ✅ VM script audit: 77→25 active scripts (47692d37)
- ✅ NMC asset expansion: 57→67 assets, $9.31T→$18.28T (4ea6a446)
- ✅ 5 P2/P3 UI fixes: threshold text, sidebar tickers, CFT guards, N/A display, radar dynamics (fb870680)

## Strategic Direction (Jun 26)

### In Progress
- CTO_STATE.md persistence protocol (THIS FILE) — read at session start, update at session end
- GAP terminology deprecation — research retail-friendly alternatives
- Telegram 2.0 redesign — transform broadcasts from AI summaries to trading desk signals
- NMC continuous reassessment

### Deferred Strategic
- Thematic Portfolios (v2.0): narrative cards → mini-portfolios with ticker grids
- Allocation Detail Pages (v3.0): click-through to full allocation screens
- Cloud migration (Phase 2+): Docker, Cloud Run, GitHub Actions — documented, not urgent
- Monetisation: freemium with Clerk+Stripe — spec written, no code

## Next Session Priorities
1. Read this file first
2. GAP terminology proposal for Alex approval
3. Telegram 2.0 redesign proposal
4. FRED classifier fix
5. Move fetch_narrative_cap.py into governor for live NMC

## Deployment Pattern (do NOT deviate)
1. Edit locally in ~/lagazzettadikyiv/
2. scp to gazzetta-prod:/tmp/
3. sudo mv to /opt/gazzetta-di-kyiv/scripts/
4. sudo find /opt/gazzetta-di-kyiv/scripts/__pycache__ -delete
5. Run modified script via sudo -u gazzetta /opt/gazzetta-di-kyiv/venv/bin/python
6. Verify output
7. git add + commit + push IMMEDIATELY (do not wait for auto-commit watchdog)
8. For full deploy: run build_frontend.py then deploy_to_gcs.py

## Critical Pitfalls (do NOT repeat)
- Google edge caching on storage.googleapis.com: requires cache-busting query params for verification
- Governor timer overwrites manual repairs: stop timer (sudo systemctl stop gazzetta-governor.timer) before manual JSON repairs, restart after
- SQLite on VM: must use `sudo -u gazzetta sqlite3` — bare sqlite3 fails with readonly error
- Deploy race: build → deploy must be atomic or governor will overwrite between steps
- API keys with shell-special chars: write to /tmp/file first, source via $(cat /tmp/file)
- Never pipe Python through SSH heredoc — bash interprets $ and {} in f-strings
- Use temp files (scp .py → /tmp/) for all VM Python execution
