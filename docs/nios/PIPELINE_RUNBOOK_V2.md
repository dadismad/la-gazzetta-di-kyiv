# Pipeline Runbook V2

## End-to-end run
```bash
cd /Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv
./scripts/run_pipeline_v2.sh
```

## Stages
1. `collect_multisource.py`
2. `analyze_narratives_v2.py`
3. `publish_quality_gate_v21.py` (hard stop if confidence/invalidation quality fails)
4. `prepare_publish_payloads_v2.py`
5. `pipeline_audit.py`

## Key outputs
- Canonical events: `data/normalized/events_latest.json`
- Canonical intelligence: `data/processed/narrative_intelligence_latest.json`
- Site payloads: `site/api/v1/home/{regime,setups,contradictions}.json`
- Channel payloads: `data/publish/{telegram_latest.md,reddit_latest.md}`
- Audit: `data/audit/pipeline_audit_latest.{json,md}`

## Integration with legacy autopost
`agentic_research_publish_cycle.sh` runs v2 first, then syncs `data/publish/reddit_latest.md` -> `data/reddit_post_payload.md` for compatibility with existing NLP audit + post routines.

## Failure policy
- If collection yields zero events, pipeline marks stale and audit reports blocker.
- If mandatory site payloads are missing/stale, audit returns degraded status.
- Publishing should be blocked when blocker findings exist.
