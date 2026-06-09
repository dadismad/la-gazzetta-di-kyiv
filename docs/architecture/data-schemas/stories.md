# Data Schema: stories.json

> Canonical source for all narrative intelligence stories.

## Top-Level Structure

{
  "generated_at": "string (ISO 8601)",
  "lead": "object (lead story, same schema as story below)",
  "stories": "array[Story]"
}

## Story Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| story_id | string | yes | Unique ID: n{number}_{pillar}__{slug} |
| headline | string | yes | Display headline |
| sector | string | yes | geopolitics/markets/tech/wealth/pleasure |
| pillar | string | yes | Six paradigm pillar |
| paradigm_pillar | string | yes | Same as pillar (unified schema) |
| paradigm_implications | string[] | yes | Actionable implications |
| they_say | string | yes | Consensus narrative |
| reality | string | yes | Contradictory reality |
| thesis | string | yes | Trade thesis |
| actors | array | yes | Named entities |
| horizon | string | yes | 24-72h, 1-2w, 1-3m, structural |
| confidence | string | yes | high/medium/low |
| actionable_trade | string | yes | Specific trade idea |
| capital_flow | object | yes | See below |
| capital_flow_implication | string | yes | Directional implication |
| portfolio_implication | string | yes | Portfolio-level implication |
| freshness_tier | string | if decayed | breaking/new/active/developing/background |
| contradiction_score | number | if scored | 0-100 contradiction depth |
| story_status | string | if decayed | Same as freshness_tier |

## capital_flow Object

| Field | Type | Description |
|-------|------|-------------|
| projected | string | Projected flow direction |
| confidence_pct | number | 0-100 confidence |
| pace_multiplier | number | Speed factor |
| direction | string | inflow/outflow |
| amount_b | number | Amount in billions |

## Current State (2026-06-06)

- 19 stories active
- 6 paradigm pillars covered
- 82% aggregate flow confidence
