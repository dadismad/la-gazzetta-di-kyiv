# Pipeline Diagram — Gazzetta di Kyiv

> Data flow architecture: collection -> processing -> publishing -> governance.

## High-Level Flow

[Telegram Monitor] (30m) -+-> [Pipeline Chain] (60m) -> [Deploy] (15m) -> GCS
                          |
[Source Monitor] (60m) ---+   (writes stories.json directly, conflict risk)

## Pipeline Chain (scripts/pipeline_chain.sh)

Step 1: intel_to_stories.py
  Input: data/telegram_intel/latest.json
  Output: data/stories.json (appends new stories)
  Logic: Reads intel['stories'], deduplicates on story_id

Step 2: decay_stories.py
  Input: data/stories.json
  Output: data/stories.json, data/stories_archive.json
  Logic: breaking -> new -> active -> developing -> background, archives >7d

Step 2.5: validate_stories.py
  Input: data/stories.json
  Output: data/stories.json (repaired)
  Logic: Ensures every story has capital_flow dict with required fields

Step 3: generate_flows.py
  Input: data/stories.json
  Output: data/flows.json
  Logic: 3-tier extraction: capital_flow dict -> implication -> portfolio

Step 3.5: translate_content.py
  Input: data/stories.json, site/data/stories_ru.json
  Output: data/stories_ru.json, data/flows_ru.json
  Logic: Russian translation via DeepSeek API

Step 4: build_site.py
  Input: data/*.json (13 files)
  Output: site/data/*.json, site/api/v1/home/*.json
  Logic: Smart merge for stories.json (preserves site-only stories)

## Data File Sync (build_site.py SYNC_FILES)

narratives.json, stories.json, stories_in_play.json, living_stories.json,
story_registry.json, intelligence_objects.json, asset_claims_latest.json,
representation_techniques.json, source_registry_ranked.json, ops_status.json,
publish_manifest.json, flows.json, website_stories_latest.json

## Independent Pipelines

Living Stories Enrich (2h):
  Input: data/stories.json, data/living_stories.json
  Output: data/living_stories.json (enriched sub-threads, stale tagging)

Phase3 Daily Brief (24h, 09:00):
  Input: data/phase2_scores.json (or fallback)
  Output: data/phase3_daily_brief.md
  Runs: phase2_scoring.py || generate_candidates_fallback.py

## Deployment

gazzetta-deploy-to-gcs (15m):
  gsutil rsync site/ -> gs://www.lagazzettadikyiv.com
  42 objects synced, gcloud auth via pureciclismo@gmail.com

## Known Issues

1. Source Monitor writes stories.json directly (conflict with pipeline chain)
2. P8/P10 directories (data/publish, data/quality_gates) were missing
3. No retry, no alerting on any step (see process-registry.md failure table)
