# Pipeline Expansion Execution Report (V1)

## Objective
Expand from a mostly Reddit-centric executable path into a multi-source, canonical, auditable data pipeline:
collection -> normalization -> analysis -> content prep -> publishing artifacts -> audit.

## New components shipped

### Source configuration
- `data/config/data_sources_v2.json`
  - RSS: BBC World, Bloomberg Markets, FT World, Guardian World
  - Reddit: worldnews, economics, stocks, geopolitics

### Collection and normalization
- `scripts/collect_multisource.py`
  - Fetches RSS/Reddit inputs
  - Stores raw snapshots in `data/raw/`
  - Writes canonical normalized events: `data/normalized/events_latest.json`

### Analysis and interpretation
- `scripts/analyze_narratives_v2.py`
  - Aggregates tags/topics
  - Produces setups + contradictions + regime
  - Writes `data/processed/narrative_intelligence_latest.json`

### Content preparation and publishing artifacts
- `scripts/prepare_publish_payloads_v2.py`
  - Updates:
    - `site/api/v1/home/setups.json`
    - `site/api/v1/home/contradictions.json`
    - `site/api/v1/home/regime.json`
  - Generates:
    - `data/publish/telegram_latest.md`
    - `data/publish/reddit_latest.md`

### Audit and reliability
- `scripts/pipeline_audit.py`
  - Verifies artifact presence/freshness and semantic integrity
  - Outputs:
    - `data/audit/pipeline_audit_latest.json`
    - `data/audit/pipeline_audit_latest.md`

### Orchestration
- `scripts/run_pipeline_v2.sh`
- Integrated into main autopost loop:
  - `scripts/agentic_research_publish_cycle.sh` now runs v2 first and syncs Reddit payload for backward compatibility.

## Execution proof
- `./scripts/run_pipeline_v2.sh`
  - events: 200
  - failures: 0
  - setups: 3
  - audit status: ok

## Why this matters
- Moves execution from implicit, scattered source handling to explicit, config-driven ingestion.
- Produces one canonical processed object for all downstream channels.
- Adds first-class audit artifacts each cycle.
- Preserves compatibility with existing posting mechanism while improving data quality path.
