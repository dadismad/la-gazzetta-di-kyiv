# CTO State Persistence Protocol — La Gazzetta di Kyiv
# Updated: 2026-06-27 01:20 Kyiv (Phase C Complete)
# Read this at the START of every session.

## Architecture State

### Infrastructure
- **VM**: gazzetta-prod (e2-micro, us-central1-a, 3.8GB RAM, 30GB disk, 4.2GB used)
- **Project root**: /opt/gazzetta-di-kyiv/
- **User**: gazzetta (all pipeline processes)
- **Python venv**: /opt/gazzetta-di-kyiv/venv/bin/python
- **Deploy**: gsutil rsync/cp → gs://www.lagazzettadikyiv.com/ → CDN (5-15min cache)
- **Scheduler**: systemd timer gazzetta-governor.timer (10-min cycle)
- **SSH alias**: gazzetta-prod
- **Local repo**: ~/lagazzettadikyiv/
- **Git remote**: https://github.com/pureciclismo/gazzetta-di-kyiv (HTTPS, pureciclismo token)
- **gsutil**: /opt/gazzetta-di-kyiv/devvit/google-cloud-sdk/bin/gsutil
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

### Key Data Files
- stories.json: public/data/stories.json (600 stories, 6.8MB)
- flows.json: public/data/flows.json (12 narratives)
- narratives.json: data/narratives.json (12 narratives with tickers)
- narrative_graph.json: data/narrative_graph.json (67 assets)
- narrative_cap.json: data/narrative_cap.json ($18.28T total NMC)
- derivatives.json: public/data/derivatives.json
- gazzetta.db: SQLite database

## Phase C — Completed Today (Jun 26–27)

### C1: GAP → Δ Edge (Contrarian Edge) Semantic Transition
- 31 patches to build_frontend.py: all user-facing "GAP" replaced with "Δ Edge"
- 16 patches to telegram_broadcast.py: gap_to_tag→edge_tag, hashtags, format strings
- Crosshair axis: "Δ Edge (Contrarian Edge) →"
- Leaderboard: "Δ EDGE LEADERBOARD" with "Δ 94", "Δ 81" etc.
- Story cards: "Δ EDGE 63" instead of "GAP 63"
- Capital Flows, About, Contradictions tabs: all Δ Edge
- Meta tags updated
- Backend field names (contradiction_gap, gap field in JSON) preserved — no DB migration

### C2: Telegram 2.0 Three-Format System
- Refactored telegram_broadcast.py format_story_for_telegram()
- **THE SETUP**: High-conviction trades (direction + entry/stop/target + alpha trigger)
  - Header: 🔥/📈 THE SETUP: DIRECTION TICKER R:R | Δ EDGE score | NMC
  - Alpha trigger sentence, Media vs Capital, === TRADE PARAMETERS ===
  - Stop, Target, Invalidation, Horizon, Conviction, Narrative context
- **THE FLOW**: Structural capital migration (macro/commodity/crypto shifts)
  - Header: 💹 THE FLOW: ACCUMULATION/DISTRIBUTION/ROTATION
  - === MEDIA vs CAPITAL ===, capital metrics, institutional bias
- **THE PULSE**: Rapid-response radar (unchanged from main() heartbeat)
- Box-drawing chars replaced with ASCII === separators
- FALLBACK_FORMAT simplified to SETUP↔FLOW rotation
- All hashtags: #EDGE_ALERT, #EDGE_ACTIVE, #EDGE_MONITOR

### Verified
- 146/146 tests passing
- Live CDN: lagazzettadikyiv.com renders Δ Edge throughout
- Sample THE SETUP dispatch: clean, actionable, professional
- All 5 P2/P3 bug fixes (from earlier) still active

## Remaining Known Issues

### P2 — Deferred
- FRED macro regime classifier stuck at "NEUTRAL"
- NMC data 26h stale (fetch_narrative_cap.py not in governor)
- Light-mode design refactor (~50 color changes)

### P3 — Minor
- broadcast_state.json permission issue on rsync (lock file)
- Some story-level tickers still use affected_tickers[0] (not narrative canonical)

## Strategic Direction

### Completed ✅
- CTO_STATE.md persistence protocol (this file)
- GAP → Δ Edge semantic transition
- Telegram 2.0 three-format system
- 5 P2/P3 UI fixes (threshold text, sidebar tickers, CFT guards, N/A display, radar dynamics)
- NMC expansion 57→67 assets

### Next Priorities
1. FRED classifier fix (unstick from NEUTRAL)
2. Move fetch_narrative_cap.py into governor for live NMC
3. Weekly NMC reassessment cadence
4. Light-mode design refactor
5. Thematic Portfolios (v2.0) — narrative cards → mini-portfolios

## Deployment Pattern (do NOT deviate)
1. Edit locally in ~/lagazzettadikyiv/
2. scp to gazzetta-prod:/tmp/
3. sudo mv to /opt/gazzetta-di-kyiv/scripts/
4. sudo find /opt/gazzetta-di-kyiv/scripts/__pycache__ -delete
5. Run modified script via sudo -u gazzetta /opt/gazzetta-di-kyiv/venv/bin/python
6. Verify output
7. git add + commit + push IMMEDIATELY
8. For full deploy: run build_frontend.py then gsutil cp/rsync to GCS
9. Verify via raw storage.googleapis.com URL first; CDN caches 5-15min

## Critical Pitfalls (do NOT repeat)
- GCS index.html may NOT update via rsync — use direct `gsutil cp` if needed
- Google edge caching on storage.googleapis.com: requires cache-busting query params
- Governor timer overwrites manual repairs: stop timer before manual JSON repairs
- SQLite on VM: must use `sudo -u gazzetta sqlite3`
- API keys with shell-special chars: write to /tmp/file first
- Never pipe Python through SSH heredoc — bash interprets $ and {} in f-strings
- Use temp files (scp .py → /tmp/) for all VM Python execution
