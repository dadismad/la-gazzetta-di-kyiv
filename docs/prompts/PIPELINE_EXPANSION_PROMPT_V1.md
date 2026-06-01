# PIPELINE EXPANSION PROMPT — NEW SOURCES TO PUBLISHING (V1)

Expand the pipeline with additional high-signal sources and deterministic processing.

## Expansion goals
1. Add multi-source collection beyond single-subreddit fallback.
2. Introduce explicit retrieval adapters per source class.
3. Normalize into one canonical events dataset.
4. Improve narrative analysis with actor/incentive/contradiction extraction.
5. Generate channel-specific payloads from canonical interpretation object.

## Required source classes
- RSS major macro/geopolitical outlets
- Reddit macro + geopolitics communities
- Optional platform snapshots (feature-flagged if auth blocked)

## Required processing stages
1. `collect_multisource` -> writes `data/raw/*` and `data/normalized/events_latest.json`
2. `analyze_narratives_v2` -> writes `data/processed/narrative_intelligence_latest.json`
3. `prepare_publish_payloads_v2` -> writes site/reddit/telegram payload artifacts
4. `validate_article_contract` + style lint gates before publish

## Architecture constraints
- Deterministic outputs for same input snapshot.
- Explicit stale markers if any source fetch fails.
- No hidden dependency on external home-directory DB without fallback.
- Each stage emits compact run metadata (counts, durations, status).

## Verification
- Run pipeline end-to-end once.
- Validate generated JSON schema shape and mandatory fields.
- Confirm website endpoint files updated and readable.
- Produce a short remediation list for remaining blockers.
