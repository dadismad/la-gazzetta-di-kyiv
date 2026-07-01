# Content Dedup — Jaccard Similarity in contradiction_synthesizer.py

Added June 2026 to prevent near-duplicate story headlines bloating the feed.

## Problem

The contradiction_synthesizer produces multiple stories per narrative/asset pair. When news clusters around a topic (e.g., multiple Taiwan sovereignty reports), the synthesizer generates headlines that are near-identical. At peak: 12 duplicate headlines in 597 total stories.

## Fix: `_dedup_new_stories()` in `merge_stories()`

### Algorithm

```python
def _headline_similarity(h1: str, h2: str) -> float:
    """Jaccard similarity between tokenized headlines. 0.0-1.0."""
    STOP = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at",
            "to", "for", "of", "and", "or", "but", "with", "from", "by", "as",
            "its", "it", "has", "have", "had", "not", "no", "that", "this",
            "be", "will", "can", "could", "would", "should", "may", "might",
            "just", "only", "also", "still", "now", "then", "after", "before",
            "fails", "failed", "markets", "market", "amid", "new", "us", "s"}
    import re
    def tokens(h):
        return set(w for w in re.split(r"[^a-z0-9]+", h.lower().strip())
                   if len(w) > 2 and w not in STOP)
    t1, t2 = tokens(h1), tokens(h2)
    if not t1 or not t2:
        return 0.0
    return len(t1 & t2) / len(t1 | t2)
```

### Threshold

`0.65` — after testing, catches "[Subject] fails to [verb] [ticker]" pattern duplications while allowing legitimately distinct stories about the same asset.

### Placement

In `merge_stories()`, BEFORE prepending to `all_stories`:

```python
existing_headlines = [s.get("headline", "") for s in existing.get("all_stories", [])]
deduped = _dedup_new_stories(new_stories, existing_headlines)
skipped = len(new_stories) - len(deduped)
if skipped > 0:
    print(f"  WARN dedup: {skipped} near-duplicate story(s) filtered")
all_stories = deduped + existing.get("all_stories", [])
```

Two checks: against existing headlines AND within the new batch (first story in batch is kept, near-duplicate subsequent ones are dropped).

## Deployment

File: `/opt/gazzetta-di-kyiv/scripts/contradiction_synthesizer.py` (VM)
The `_headline_similarity` and `_dedup_new_stories` functions were added directly above `merge_stories()`.
Tests confirmed: 101 PASS / 0 FAIL after deploy.
