# Multi-Persona Enrichment Pipeline

## Purpose

Generates C-Suite, Quantitative, and Degen/Execution persona blocks for stories
lacking them, using the DeepSeek API. Ensures 100% of stories have multi-persona coverage.

## Persona Blocks

Each story's `multi_persona` field contains three blocks:

- **c_suite**: `{headline, body, implication}` — Macro context for capital allocators
- **quant**: `{headline, body, metrics}` — Flow telemetry: signal ("WATCH"/"BUY"/"SELL"), confidence_pct (50-85), pace (1.0-3.0), correlation
- **degen**: `{headline, body, signal, entry, stop}` — Action triggers with emoji + ticker

## Script

`scripts/enrich_multi_persona.py`

### API Key Extraction

Does NOT use `DEEPSEEK_API_KEY` env var directly. Parses `custom_providers` JSON
from the environment, finds the provider with "deepseek" in its name, and extracts
the `api_key` field:

```python
providers = json.loads(os.environ.get("custom_providers", "[]"))
for p in providers:
    if "deepseek" in p.get("name", "").lower():
        API_KEY = p.get("api_key", "")
        break
```

### Database Schema

Uses `gazzetta.db` with table `stories`:
- Column `id` (TEXT PRIMARY KEY) — NOT `story_id`
- Column `full_json` (TEXT) — the complete story JSON
- Column `multi_persona_raw` (TEXT) — stores JSON of the 3 persona blocks

### Query

```sql
SELECT id, full_json FROM stories 
WHERE multi_persona_raw IS NULL OR multi_persona_raw = ''
```

### Update

```sql
UPDATE stories SET full_json = ?, multi_persona_raw = ? WHERE id = ?
```

### API Call

Endpoint: `https://api.deepseek.com/v1/chat/completions`
Model: `deepseek-chat`
Parameters: `temperature=0.4, max_tokens=600, response_format={"type": "json_object"}`

### Generation Prompt

The system prompt instructs the model to generate three persona perspectives
with specific fields. The model outputs valid JSON only. Rate limit: 0.5s between calls.

### Idempotency

Skips stories that already have `multi_persona_raw` set. Safe to run repeatedly —
only processes new/orphaned stories.

## Pipeline Integration

Stage 1.02 in `shipit.sh` — runs after `db_to_json.py`, before `fetch_live_prices.py`.

```bash
$PYTHON "$PROJECT/scripts/enrich_multi_persona.py" || echo "  ⚠ Multi-persona skipped (API unavailable)"
```

Output: "Found 0 orphan stories (no multi_persona)" when all stories are enriched.

## Session Reference

June 10, 2026: Built and ran `enrich_multi_persona.py` to process 22 orphan stories.
100% coverage achieved (59/59 stories). Integrated as Stage 1.02 in shipit.sh.
