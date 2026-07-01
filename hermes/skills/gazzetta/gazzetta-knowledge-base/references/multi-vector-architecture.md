# Multi-Vector Narrative Architecture (v1.0, June 2026)

## Overview

Replaced single-tag 1:1 story-to-narrative classification with proportional 12-vector scoring via DeepSeek.
One article can populate 1-5 narrative containers simultaneously based on weighted relevance.

## System Prompt Engineering

The DeepSeek `SYSTEM_PROMPT` in `contradiction_synthesizer.py` (line ~226) outputs:

```json
{
  "narrative_scores": {
    "dollar_decline": 0.0, "energy_sovereignty": 0.0, ...
  },
  "affected_tickers": ["TSM", "NVDA"],
  "affected_asset_classes": ["tech", "semiconductors"]
}
```

**Critical constraints:**
- Must include the word "json" in prompt text (DeepSeek `response_format={"type":"json_object"}` requirement)
- Proportionality rule: "This is an asset-allocation weighting, not a binary tag. Use FULL 0.0-1.0 range PROPORTIONALLY."
- 0.40 threshold for container inclusion
- 0.30 threshold for Domino spillover display
- `max_tokens: 1200` (was 800 — 12 floats + arrays need more space)

## Pipeline Integration

### Files Modified
- `contradiction_synthesizer.py` — SYSTEM_PROMPT, `pick_market_context()`, `assemble_story()`, `merge_stories()`, `build_user_prompt()`, `call_deepseek()`, `run()`
- `classify_stories.py` — multi-vector bypass (stories with `narrative_weights` skip keyword matching), `tags_index` multi-container indexing, `GAZZETTA_HOME` env var support
- `build_frontend.py` — `build_cft_block()` helper, Alpha Board view, CFT rendering JS, mobile masthead fix

### Key Functions

**`assemble_story()`** — extracts `narrative_scores` from LLM response, computes `primary` (max score), `containers_list` (scores >= 0.40), populates `narrative_weights`, `containers`, `narrative_confidence`

**`merge_stories()`** — replaces single `container` append with `containers` list iteration; capping by primary only (avoids capital inflation); tags_index rebuilt from containers list

**`classify_stories.py`** — stories with `narrative_weights` bypass keyword matching entirely; legacy "unassigned" stories still keyword-matched as safety net

**`build_cft_block(nid, stories, config)`** — uses `containers` list for multi-vector routing; finds top-gap story per narrative; builds Domino ripples from `narrative_weights` at 0.30 threshold

## Data Model

New story fields:
- `narrative_weights`: dict of 12 float scores (0.0-1.0)
- `containers`: list of narrative_ids where score >= 0.40
- `container`: primary narrative_id (backward compat)
- `narrative_confidence`: primary score as float
- `affected_tickers`: LLM-suggested ticker symbols
- `affected_asset_classes`: LLM-suggested asset classes

## Governor Integration

- `os.environ["DEEPSEEK_API_KEY"] = DEEPSEEK_KEY` must be set in governor.py after `_secret()` call (line 51)
- Subprocess inherits env via `env={**os.environ, "PYTHONUNBUFFERED":"1"}`
- Without this, synthesis stage fails with "DEEPSEEK_API_KEY not set"

## Frontend: Alpha Board

5-tab SPA: Stream | Alpha | Capital Flows | Contradictions | About

CFT cards render per narrative with:
- Catalyst headline + gap meter bar
- Flow: capital_fmt + direction
- Trade: ticker pills + asset class tags
- Domino: clickable spillover pills (scroll to target narrative card)

Empty narratives (cft=null) hidden entirely.

## CDN Deployment Pattern

Two GCS buckets: `lagazzettadikyiv.com` and `www.lagazzettadikyiv.com`
Upload to BOTH. Then invalidate: `gcloud compute url-maps invalidate-cdn-cache gazzetta-url-map --path='/*'`
CDN has independent cache from GCS — curl may show new content while browser still serves stale.
