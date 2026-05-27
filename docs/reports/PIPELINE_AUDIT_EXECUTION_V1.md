# Pipeline Audit Execution Report (V1)

## Scope audited
- Repository architecture and doctrine files
- Scripted ingestion/scoring/drafting/publishing chain
- Site API payload generation
- Cron scheduling and runtime status
- Data contract and style-gate coverage

## Evidence snapshot
- Script inventory: `scripts/*.py` (18 scripts)
- Cron state checked (7 jobs):
  - active + OK: `011c8be0b17c`, `a8c20991c60a`
  - paused intentionally: `12051ebe2746`, `67609e89de17`
  - degraded secondary lane: `feef56da90cb` (last_status error)
- Current pipeline audit artifact:
  - `data/audit/pipeline_audit_latest.json`
  - `data/audit/pipeline_audit_latest.md`

## Findings (before remediation)
1. **High operational coupling to legacy Reddit-only pipeline**
   - Existing autopost path depended heavily on `devvit_only_pipeline.py` + legacy payload path.
2. **Source fragility and hidden dependency risk**
   - Legacy site builder used external home-directory DB path (`~/.hermes/data/social_umbrella/events.db`) as implicit dependency.
3. **Incomplete source diversification in executable chain**
   - Repo had source registries/docs, but core execution path was not enforcing multi-source collection each cycle.
4. **Audit visibility existed but lacked deterministic fresh-cycle audit script in main chain**
   - No consolidated executable audit stage guaranteed on each run.

## Remediations executed
- Added deterministic multi-source collection stage (`scripts/collect_multisource.py`) using config-driven source list.
- Added analysis stage (`scripts/analyze_narratives_v2.py`) producing canonical intelligence object.
- Added publish-prep stage (`scripts/prepare_publish_payloads_v2.py`) updating site + channel payload files from one source-of-truth.
- Added executable audit stage (`scripts/pipeline_audit.py`) producing JSON + markdown audit artifacts.
- Added orchestrator (`scripts/run_pipeline_v2.sh`) and integrated it into primary autopost cycle via `scripts/agentic_research_publish_cycle.sh`.
- Replaced failing Reuters feed in v2 config with BBC world RSS (observed zero failures post-fix).

## Current status after remediation
- `run_pipeline_v2.sh` executes end-to-end successfully.
- Latest normalized events: 200 items, 0 source failures.
- Site payloads refreshed from canonical processed file.
- Audit status: `ok` with 0 findings.

## Remaining watchpoints
- Improve semantic tag extraction quality (many RSS items have empty keyword tags; currently topic fallback is used).
- Extend actor/incentive extraction beyond topic-level defaults.
- Decide whether to retire or fully refactor legacy `phase2/phase3/reddit_*` chain to avoid duplicate logic.
