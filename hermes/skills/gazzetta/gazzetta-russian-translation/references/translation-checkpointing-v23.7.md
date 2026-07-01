# Translation Checkpointing (v23.7)

## Problem
`translate_content.py` batched 20 stories per API call. DeepSeek API routinely times out at 180s, losing all progress. Each retry started from zero.

## Solution: SQLite Checkpointing

Story-level checkpoints in `gazzetta.db` table `translation_checkpoint`:

```sql
CREATE TABLE IF NOT EXISTS translation_checkpoint (
    story_id TEXT PRIMARY KEY,
    translated_at TEXT,
    status TEXT DEFAULT 'done'
);
```

## Workflow

1. **First run**: `DEEPSEEK_API_KEY=*** .venv/bin/python scripts/translate_content.py`
   - Processes stories in batches of 3
   - Saves checkpoint after EACH story
   - Saves RU JSON after each batch
   - On timeout: next run resumes from last checkpoint

2. **Resume**: `.venv/bin/python scripts/translate_content.py --resume`
   - Skips stories already in `translation_checkpoint`
   - Only processes untranslated stories

3. **Dry-run**: `.venv/bin/python scripts/translate_content.py --dry-run`
   - Shows count of untranslated stories without API calls

## Key Design Decisions

- **Batch size: 3** (not 20) — avoids timeout, each story ~8-15s
- **Checkpoint per story** (not per batch) — granular resume
- **Cyrillic verification** — if a story is checkpointed but lacks Cyrillic characters, the checkpoint is invalid and gets reset
- **Reset dead checkpoints**: `DELETE FROM translation_checkpoint WHERE story_id IN (SELECT story_id FROM ... WHERE headline has no Cyrillic)`

## Verification

```python
import json
with open('data/stories.json') as f: en = json.load(f)
with open('data/stories_ru.json') as f: ru = json.load(f)
en_ids = {s['story_id'] for s in en['stories']}
en_ids.add(en.get('lead',{}).get('story_id',''))
ru_map = {s['story_id']: s for s in ru['stories']}
cyr = sum(1 for sid in en_ids if sid in ru_map 
          and any(0x0400 <= ord(c) <= 0x04FF for c in str(ru_map[sid].get('headline',''))))
print(f'EN with Cyrillic RU: {cyr}/{len(en_ids)}')
```
