# Pipeline Audit (Latest)

Status: **ok**
Generated: 2026-05-31T12:00:20.316838+00:00

## Artifact checks
- normalized_events: exists=True age_seconds=0 path=`data/normalized/events_latest.json`
- processed_intelligence: exists=True age_seconds=0 path=`data/processed/narrative_intelligence_latest.json`
- site_regime: exists=True age_seconds=0 path=`site/api/v1/home/regime.json`
- site_setups: exists=True age_seconds=0 path=`site/api/v1/home/setups.json`
- site_contradictions: exists=True age_seconds=0 path=`site/api/v1/home/contradictions.json`
- telegram_payload: exists=True age_seconds=0 path=`data/publish/telegram_latest.md`
- reddit_payload: exists=True age_seconds=0 path=`data/publish/reddit_latest.md`

## Findings
- [MEDIUM] Source retrieval failures detected | evidence: failures=4 in data/normalized/events_latest.json | fix: Add alternate mirror/feed and retry policy for failed sources