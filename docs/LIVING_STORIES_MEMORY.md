# Living Stories Architecture — Canonical Reference

## Overview
The living stories system provides continuous story evolution for Gazzetta di Kyiv using a 3-tier update cadence, persistent story registry, and evolution scoring — all without LLM calls in Tier 2.

## 3-Tier Cadence
| Tier | Name | Schedule | LLM? | Cost |
|------|------|----------|------|------|
| T1 | `gazzetta-telegram-monitor` | Every 30m | Yes | $0.015 |
| T2 | `gazzetta-living-stories-enrich` | Every 2h (:15) | **No** | $0.00 |
| T3a | `gazzetta-editorial-writer` | 06:45 / 18:45 | Yes | $0.03 |

## Core Files

### `data/story_registry.json` — Persistent Story Registry
- `stories.{story_id}`: Each story tracked from first appearance through resolution
- Fields: `story_id`, `first_seen`, `last_updated`, `status` (evolving|resolved|stale), `update_count`, `original_setup_id`, `original_headline`, `current_headline`, `sector`, `paradigm_pillar`, `actors`, `geography`, `thread_ids`, `evolution_score_peak`, `evolution_score_current`, `invalidation_triggers`, `last_asset_projection`, `image_url`

### `data/stories/{story_id}/timeline.json` — Thread Timeline
- `threads[].type`: "main" or "sub_thread"
- `threads[].evolution[]`: Each evidence update with `update_id`, `timestamp`, `type` (initial_broadcast|evidence_update|frame_shift|thread_creation), `evidence_titles`, `source_count`, `reality_delta`, `evolution_score`, `asset_projection`

### `data/publish/living_stories.json` — Frontend Payload
- Compressed, render-optimized view with `lead`, `stories[]`, `archived_stories[]`
- Each entry: `story_id`, `headline`, `status`, `update_count`, `last_updated`, `updated_ago`, `they_say`, `reality`, `thesis`, `actors`, `sector`, `has_live_updates`, `latest_evolution_type`, `thread_count`, `thread_previews[]`, `asset_claim`, `image_url`

### `scripts/enrich_stories.py` — Tier 2 Runner
- No LLM calls. Uses Jaccard similarity + keyword extraction
- Evolution score = `actor_match * 0.4 + geography_match * 0.3 + pillar_match * 0.2 + recency * 0.1`
- Thresholds: 0.6 for update, 0.85 for sub-thread spawn
- Stale after 48h below 0.6

## Guardrails
- **Skip condition:** If T1 detects zero novel entities in 2h, T2 skips (`micro_update_skips` increments). After 3 consecutive skips, suppressed until T1 finds new evidence.
- **Status transitions:** new→evolving→resolved (7d no updates, or invalidation trigger, or manual archive)
- **Stale:** score < 0.6 for 48h → tagged stale (editorial decision to resolve)
- **Frontend:** Story cards keyed by `story_id` from `stories.json`, DOM stateful patching via polling

## Cron Job
- Name: `gazzetta-living-stories-enrich`
- Schedule: `15 */2 * * *` (every 2 hours on the :15)
- no_agent: true (script-only, no LLM)
- Script: `~/.hermes/scripts/gazzetta_enrich_stories.py` (wrapper)
- Workdir: `~/.hermes/hermes-agent/gazzetta-di-kyiv`

## Editorial Writer Integration
- Skill `gazzetta-editorial-writer` loads `story_registry.json` and `living_stories.json` in Step 1
- Lead story selection (Step 3) prefers evolving stories with 3+ updates unless overridden
- `stories.json` output (Step 8.5) includes `story_id` for frontend keying
