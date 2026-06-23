# Deduplication Pattern (v23.0)

Implemented June 2026. Two-layer deduplication for OSINT draft ingestion.

## Layer 1: Exact Match (SQL)

```sql
SELECT 1 FROM drafts WHERE suggested_headline = ? AND source = ?
```

Simple, fast, catches exact duplicates.

## Layer 2: Fuzzy Word-Overlap (Python)

When exact match fails, check recent drafts (last 20 from same source) for >85% word overlap:

```python
words_a = set(headline.lower().split())
words_b = set(existing_headline.lower().split())
overlap = len(words_a & words_b) / max(len(words_a | words_b), 1)
if overlap >= 0.85:  # 85% word overlap = duplicate
    return True
```

## Schema Constraints

```sql
CREATE UNIQUE INDEX IF NOT EXISTS idx_stories_slug ON stories(slug);
CREATE UNIQUE INDEX IF NOT EXISTS idx_stories_id ON stories(id);
CREATE INDEX IF NOT EXISTS idx_stories_headline ON stories(headline);
```

## Where Implemented

- `scripts/fetch_intel.py` — `draft_exists()` function
- `gazzetta.db` — schema constraints via `init_db.py --migrate`
