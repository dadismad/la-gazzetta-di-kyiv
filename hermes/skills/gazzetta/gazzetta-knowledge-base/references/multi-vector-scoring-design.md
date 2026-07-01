# Multi-Vector Narrative Scoring — Design Decision (June 2026)

## Problem

Current pipeline forces 1:1 story-to-narrative tagging. The DeepSeek prompt emits a single
`narrative_tag` string. A TSMC Arizona fab delay tagged `ai_chips` is invisible to the
`deglobalization` and `china_ascent` dashboards. Capital-at-stake math undercounts
spillover because the same event moves 3-5 vectors but is credited to only one.

## Design

Replace single `narrative_tag` output with a `narrative_scores` dict — the LLM scores
the story against ALL 12 vectors simultaneously (0.0-1.0 float each). This is an
asset-allocation weighting, not a binary tag.

### Schema (DeepSeek response_format: json_object)

```
{
  "headline": "...",
  "they_say": "...",
  "reality": "...",
  "contradiction_gap": "integer (0-100)",
  "capital_volume_usd": "integer",
  "narrative_scores": {
    "dollar_decline": "float (0.0-1.0)",
    "energy_sovereignty": "float (0.0-1.0)",
    "deglobalization": "float (0.0-1.0)",
    "china_ascent": "float (0.0-1.0)",
    "space_economy": "float (0.0-1.0)",
    "gene_editing": "float (0.0-1.0)",
    "tech_convergence": "float (0.0-1.0)",
    "wealthy_sports": "float (0.0-1.0)",
    "ai_chips": "float (0.0-1.0)",
    "crypto_reserve": "float (0.0-1.0)",
    "rate_cycle": "float (0.0-1.0)",
    "commodity_supercycle": "float (0.0-1.0)"
  },
  "affected_tickers": ["string"],
  "affected_asset_classes": ["string"]
}
```

### Proportionality Constraint

The matrix is NOT binary. A 0.9 on the primary vector might ripple at 0.3-0.4 into
adjacent vectors. Set 0.0 only for genuinely unrelated vectors. Do not assign 1.0
to multiple vectors — this is a weighting distribution.

### Multi-Container Assignment

Stories appear in any container where `score >= 0.40`. A story typically populates
3-5 containers simultaneously. The downstream `merge_stories()` function appends
the story to each qualifying container bucket. Capital-at-stake math counts the
story in each pool — correct for spillover modeling.

### DeepSeek API Requirement

The system prompt MUST contain the word "json" for `response_format={"type": "json_object"}`
to be honored by DeepSeek's API. The lead-in "Respond with ONLY valid json."
satisfies this constraint.

## Files Affected (Executed & Verified — June 21 2026)

| File | Change | Status |
|------|--------|--------|
| `contradiction_synthesizer.py` SYSTEM_PROMPT | Replace single-tag schema with 12-vector matrix + proportionality constraint | EXECUTED |
| `contradiction_synthesizer.py` pick_market_context() | Expand to all 12 vectors with demarcated blocks | EXECUTED |
| `contradiction_synthesizer.py` build_user_prompt() | Drop narrative_tag param, add multi-vector instruction | EXECUTED |
| `contradiction_synthesizer.py` assemble_story() | Parse scores, set narrative_weights, containers list, fallback to legacy | EXECUTED |
| `contradiction_synthesizer.py` merge_stories() | Multi-container append (primary-only cap) | EXECUTED |
| `classify_stories.py` | DeepSeek bypass for weighted stories; tags_index multi-vector; GAZZETTA_HOME support | EXECUTED |

## Verification Results

Dry-run #1 (lunar economy article): `narrative_scores` dict with 12 keys returned correctly.
Live run #1 (Iran $300B reconstruction): 3 containers populated (energy_sovereignty, tech_convergence, ai_chips).
Live run #2 (classify): 191 stories checked, 41 unassigned re-classified, 2 weighted stories bypassed intact.

## Pre-Assigned Tag (Ingestion)

The ingestion layer pre-assigns a `narrative_tag` in the DB. Post-refactor, this
becomes a hint only — the LLM scores ALL vectors regardless. The pre-assigned tag
is still used as fallback if the LLM returns no scores.
