# Data Schema: intelligence_object.schema.json

> JSON Schema for intelligence objects (signals).

## Schema Reference

- **File**: api/v1/intelligence_object.schema.json
- **Format**: JSON Schema draft 2020-12
- **Title**: IntelligenceObject

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier |
| event | string | Event description |
| narrative_primary | string | Primary narrative |
| scenarios | array | Scenario array |
| retail_setups | array | Setup descriptions |
| invalidations | array | Invalidation conditions |
| confidence | number | 0-100 confidence |
| citations | array | Source citations |
| updated_at | string | ISO 8601 timestamp |

## Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| narrative_hidden | string | Hidden/subtext narrative |
| beneficiaries | string[] | Who benefits |
| losers | string[] | Who loses |
