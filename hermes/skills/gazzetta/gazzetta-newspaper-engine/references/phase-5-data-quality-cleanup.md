# Phase 5 — Data Quality Cleanup (June 21, 2026)

## Context

Phase 3 (Narrative Architecture) introduced `classify_stories.py` as stage 4 in the governor pipeline. Phase 4 made `build_frontend.py` fully data-driven with dynamic `load_narratives_config()`. But two data quality bugs persisted:

1. Legacy narrative tags (`china_ascendancy`, `eu_fragmentation`) kept appearing in stories.json every cycle
2. 36 stories remained `unassigned` because keyword coverage was incomplete
3. 5 test failures from orphaned story IDs in the old tags_index

## Root Cause Analysis

### Bug 1: Synthesis → Classify Ping-Pong

**Chain**: DB `narrative_tag` column (legacy values like `china_ascendancy`) → synthesis `assemble_story()` → `narrative_id = narrative_tag` → stories.json gets infected → classify fixes it → next synthesis cycle creates new stories with same legacy tags.

**Fix (contradiction_synthesizer.py line 400)**: Always set `narrative_id = "unassigned"` in `assemble_story()`. The DB's `narrative_tag` is still used for internal processing (container mapping, ticker selection, asset class resolution) but NEVER propagated to the `narrative_id` output field. Only `classify_stories.py` (stage 4) assigns `narrative_id`.

### Bug 2: Classify Fallback Self-Infection

**Chain**: `classify_story()` had a tier-3 fallback: when no keyword matched, it returned `story.get("pillar")` or `story.get("container")`. On legacy-tagged stories, the pillar field WAS the legacy tag. So the fallback "fixed" the story by assigning the same legacy tag — a silent no-op that preserved bad data indefinitely.

**Fix (classify_stories.py)**: Fallback now checks a `CANONICAL` whitelist (12 narrative IDs) before returning any legacy value. Non-canonical pillars return `"unassigned"`. This eliminated all 22 legacy-tagged stories in one cycle.

### Bug 3: Incomplete Keyword Coverage

35 stories were `unassigned` because the SEED_KEYWORDS dict was missing critical terms for energy/geopolitical stories (Iran, OPEC, Hormuz, Russia/Ukraine), tech company names (OpenAI, Anthropic, AWS, Rivian), and macro terms (inflation, World Bank, wholesale price).

**Fix**: Added 40+ keywords across all 12 narratives. Coverage went from 278/314 (88%) to 293/314 (93%). Remaining 21 unassigned are genuine non-financial content (Powerball numbers, coffee maker recalls, Social Security announcements).

### Bug 4: Orphaned tags_index

The `tags_index` in stories.json still referenced story IDs from the old 8-container system. After container rebuild, stored story IDs no longer matched — 5 test failures.

**Fix**: One-shot rebuild of `tags_index` from `narrative_id` + `entity_tags`. Containers rebuilt to include all 12 narrative IDs. Test suite patched for 12 containers.

## Files Modified

| File | Change |
|------|--------|
| `contradiction_synthesizer.py` L400 | `narrative_id` always `"unassigned"` |
| `classify_stories.py` | 40+ keywords, canonical whitelist fallback |
| `test_platform.py` | 12 containers, 153 tests, margin for unassigned |
| `stories.json` | Tags index + containers rebuilt |

## Results

```
Before:  106/111 tests, 5 failures (orphans + 8-container expectations)
After:   153/153 tests, 0 failures
Before:  22 legacy-tagged stories (china_ascendancy + eu_fragmentation)
After:   0 legacy-tagged stories
Before:  36 unassigned stories
After:   21 unassigned (genuinely non-financial)
Before:  8 containers
After:   12 containers (all canonical narratives)
```

## Critical Rule

**Synthesis must never set `narrative_id`.** The DB's `narrative_tag` is a legacy ingestion hint used only for internal processing (container mapping, ticker selection). The single source of truth for `narrative_id` is `classify_stories.py`. If a future pipeline change adds a new narrative_id source, it WILL create classification ping-pong with classify.
