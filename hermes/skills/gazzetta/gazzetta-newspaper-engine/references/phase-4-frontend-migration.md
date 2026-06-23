# Phase 4 — Frontend Data Model Migration (June 2026)

## Summary

Migrated `build_frontend.py` from a hardcoded 8-narrative system with legacy `containers`-based story grouping to a fully dynamic 12-narrative system driven by `narratives.json` and `narrative_id`-based grouping.

## What Was Removed

| Before | After |
|---|---|
| `TICKER_MAP` dict — 8 hardcoded ticker symbols | `narrative_config[id]["tickers"][0]` from `narratives.json` |
| `PILL_ORDER` list — 8 hardcoded narrative IDs | `load_narratives_config()` — sorted by capital_total_usd |
| `ICON_MAP` dict — 8 hardcoded Material Symbol names | `ICON_FALLBACK_MAP` — 12 entries, `"public"` fallback |
| `invalidation_threshold()` function — 8 hardcoded thresholds | `narrative_config[id]["invalidation_threshold"]` |
| Container expansion (`for cid, cdata in containers.items()`) | Top-level `all_stories` array from `stories.json` |
| `_container_id` story grouping | `narrative_id` story grouping |
| `cdata.get("title", ...)` fallback for display names | `narrative_config[id].get("display_name", ...)` |

## What Was Added

### `load_narratives_config()`

```python
def load_narratives_config():
    path = DATA / "narratives.json"
    if not path.exists():
        return {}, list(LEGACY_ORDER)
    data = load_json(path)
    narratives = data.get("narratives", {})
    ordered = sorted(narratives.keys(),
                    key=lambda nid: (narratives[nid].get("capital_total_usd", 0),
                                    narratives[nid].get("story_count", 0)),
                    reverse=True)
    return narratives, ordered
```

Fallback to `LEGACY_ORDER` (8-narrative list) if `narratives.json` doesn't exist. Wired into `build()` as the single source of truth for narrative taxonomy.

### `ICON_FALLBACK_MAP`

12 entries covering all current narratives. Missing narratives get `"public"` Material Symbol. Extend this map when adding new narratives — keep `narratives.json` as the authoritative taxonomy, `ICON_FALLBACK_MAP` as the visual mapping.

### `_container_title` Injection from `narrative_id`

```python
for s in all_stories:
    nid = s.get("narrative_id", "")
    if nid and nid in narrative_config:
        s["_container_id"] = nid
        s["_container_title"] = narrative_config[nid].get("display_name", nid)
```

This preserves JS rendering compatibility — all frontend JS still uses `_container_id` and `_container_title` for display. The injection bridges the new `narrative_id` field to the old JS variable names without changing any JS code.

### Story Source: `all_stories` Top-Level

```python
all_stories = stories_raw.get("all_stories", [])
if not all_stories:
    # Legacy fallback: expand containers
    containers = stories_raw.get("containers", {})
    for cid, cdata in containers.items():
        for s in cdata.get("stories", []):
            s["_container_id"] = cid
            all_stories.append(s)
```

The `stories.json` top-level `all_stories` array contains ALL stories with `narrative_id` set by `classify_stories.py`. The legacy container expansion is a fallback only. This means stories classified as `crypto_reserve`, `ai_chips`, `rate_cycle`, or `commodity_supercycle` appear in the frontend even though they have no entry in the old `containers` dict.

## Grouping Change

**All grouping calls changed from `_container_id` to `narrative_id`:**

1. Narrative summaries: `s.get("narrative_id") == cid`
2. Capital flows: `s.get("narrative_id") == n["id"]`
3. Contradiction discrepancies: unchanged (uses `contradiction_gap >= 40` filter)
4. JS-side rendering: unchanged (uses `_container_title` injected above)

## Pipeline Position

`build_frontend.py` runs as stage 7 of 10. It comes AFTER `classify_stories.py` (stage 4) which stamps `narrative_id` on every story, so the `narrative_id` field is always populated at build time.

## Verification

```bash
# Check all 12 narratives in output
grep -o '"id": "[a-z_]*"' public/index.html | sort -u

# Check narrative distribution
python3 -c "
import json, re
with open('public/index.html') as f:
    html = f.read()
m = re.search(r'const NARRATIVES = (\[.+?\]);', html, re.DOTALL)
for n in json.loads(m.group(1)):
    print(f'{n[\"id\"]:25s} | {n[\"count\"]:3d} stories | {n[\"capital_b\"]:>6.1f}B')
"
```

## Key Architecture Principle

**Zero hardcoded narrative logic remains in `build_frontend.py`.** Add a 13th narrative to `narratives.json`, and the frontend picks it up on the next governor cycle with zero code changes. The pipeline is fully data-driven:

1. `narratives.json` — authoritative taxonomy (which narratives exist, display names, tickers, thresholds)
2. `classify_stories.py` — stamps `narrative_id` on every story
3. `build_frontend.py` — reads both, groups by `narrative_id`, renders all matching stories
