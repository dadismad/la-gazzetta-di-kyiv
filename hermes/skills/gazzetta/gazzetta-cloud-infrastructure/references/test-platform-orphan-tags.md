# Test Platform — Tags Index Integrity

## Status: FIXED (June 21, 2026)

153/153 tests passing. Zero orphan tags.

## Previous State

Before June 21, `test_platform.py` reported 5-9 failures per cycle — orphaned story_ids in the `tags_index` referencing deleted/capped stories. The synthesis `merge_stories` function only APPENDED new story IDs to the tags_index, never removed old ones. After 100+ cycles, the index accumulated hundreds of dead references.

## Root Cause

Two contributors:

1. **Synthesis `merge_stories`** only added new story IDs to `tags_index`, never pruned orphans. Old code:
   ```python
   tags_index = existing.get("tags_index", {})
   for s in new_stories:
       for tag in s.get("tags", []):
           sid = str(s.get("story_id", ""))
           if sid and sid not in tags_index[tag]:
               tags_index[tag].append(sid)
   ```

2. **Story capping** (`MAX_PER_NARRATIVE = 50`) removed older stories from `all_stories` but their IDs remained in `tags_index`.

## Fix — Two Parts

### Part 1: classify_stories.py rebuilds tags_index every cycle

```python
# In classify_stories.py main(), after updating all_stories:
tags_index = {}
for s in all_stories:
    sid = str(s.get("story_id", ""))
    nid = s.get("narrative_id", "")
    if nid and nid != "unassigned":
        tags_index.setdefault(nid, [])
        if sid and sid not in tags_index[nid]:
            tags_index[nid].append(sid)
    for tag in (s.get("entity_tags") or []):
        tags_index.setdefault(tag, [])
        if sid and sid not in tags_index[tag]:
            tags_index[tag].append(sid)
stories_data["tags_index"] = tags_index
```

### Part 2: synthesis `merge_stories` also rebuilds (not preserves)

Changed from append-only to full rebuild from current `all_stories` after capping. This ensures the tags_index never accumulates orphans even when classify doesn't run.

### Part 3: Test reads from `data/stories.json`

The test initially pointed at `public/data/stories.json` (synthesis output) while classify wrote to `data/stories.json` — two different files, two different tags_index states. Fixed by keeping test on `data/stories.json` where classify + calc_capital write.

## Detection

If orphan failures reappear, check:
1. Did a governor cycle skip classify? (classify runs `critical=True`)
2. Is someone writing directly to `public/data/stories.json` bypassing the pipeline?
3. Did synthesis merge run without classify following?
