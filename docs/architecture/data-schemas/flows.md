# Data Schema: flows.json

> Canonical source for capital flow visualization.

## Top-Level Structure

{
  "generated_at": "string (ISO 8601)",
  "generated_by": "string",
  "next_update": "string (ISO 8601)",
  "update_frequency": "string",
  "summary": "string",
  "aggregate_confidence": "number (0-100)",
  "aggregate_confidence_label": "string",
  "aggregate_direction": "string (inflow/outflow)",
  "total_flows_tracked": "number",
  "flows": "array[Flow]",
  "methodology": "string",
  "glossary": "object"
}

## Flow Object

| Field | Type | Description |
|-------|------|-------------|
| id | string | flow_{story_id} |
| headline | string | Display headline with amount and direction |
| amount_b | number | Amount in billions |
| projected | string | Projected flow narrative |
| pace_multiplier | number | Speed factor (1.0 = normal) |
| direction | string | inflow/outflow |
| positioning | string | accumulating/distributing/hedging |
| asset_class | string | equities/fixed_income/commodities/crypto/real_estate |
| anchor_symbol | string | Ticker or index symbol |
| story_id | string | Links to parent story by story_id |
| confidence_pct | number | 0-100 |
| confidence_level | string | high/medium/low |
| confidence_trace | string | Explanation of confidence calculation |
| flow_sources | string[] | government/corporate/retail/institutional/central_bank |

## Current State (2026-06-06)

- 12 flows tracked
- 82% aggregate confidence
- 11:1 inflow/outflow ratio
