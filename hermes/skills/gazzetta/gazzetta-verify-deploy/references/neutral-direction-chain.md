# "Neutral" Direction Chain — Full Bug Reproduction

## Summary

When stories in `gazzetta.db` have capital_flow direction `"neutral"` (from `fetch_intel.py`'s
`detect_direction()` which defaults to `"neutral"` when no keywords match), this cascades
through multiple pipelines unless normalized at EVERY stage.

## The Chain

```
DB stories: direction="neutral"
  │
  ├─▶ db_to_json.py → stories.json
  │   └─ capital_flow.direction still "neutral"
  │       │
  │       ├─▶ db_to_json.py → flows.json
  │       │   └─ compile_flows() normalizes via _normalize_direction() ✓
  │       │
  │       └─▶ asymmetry loop (db_to_json.py line 371)
  │           └─ `if direction == "neutral": continue` → SKIPS story
  │           └─ Result: null asymmetry_score for that story
  │
  └─▶ Browser rendering
      └─ Shows direction label from capital_flow.direction
```

## Fixes Required (All 4)

### 1. compile_flows() in db_to_json.py (flows.json output)
```python
# Line ~258 — normalize after loading from DB
flow["direction"] = _normalize_direction(flow.get("direction", ""))
```
This was added — flows.json now has 0 "neutral" values.

### 2. compile_stories() in db_to_json.py (stories.json output)
```python
# Line ~140 — when primary_flow exists
if not cf.get("direction") or cf.get("direction") == "neutral":
    pd = primary_flow.get("direction", "")
    cf["direction"] = pd if pd and pd != "neutral" else "inflow"
```
This covers stories WITH a linked primary_flow. But stories without one escape.

### 3. Post-loop cleanup pass (v24.3)
```python
# After the story loop completes, before writing stories.json:
for s in stories:
    cf = s.get("capital_flow", {})
    if isinstance(cf, dict) and cf.get("direction", "") == "neutral":
        cf["direction"] = "inflow"
        s["capital_flow"] = cf
```
This catches ALL remaining "neutral" values regardless of primary_flow presence.

### 4. Asymmetry loop skip removal
```python
# Line ~377 — REMOVE the "neutral" skip
# OLD: if not ac or not direction or direction == "neutral": continue
# NEW: if not ac or not direction: continue
```
Even after normalizing, keep this removed as defense-in-depth.

## Verification

```bash
# Check stories.json for "neutral"
curl -sk $SITE/data/stories.json | python3 -c "
import json,sys;d=json.load(sys.stdin)
all_s=([d.get('lead')] if d.get('lead') else [])+d.get('stories',[])
dirs={}
for s in all_s:
    cf=s.get('capital_flow',{})
    if isinstance(cf,dict): dirs[cf.get('direction','')]=dirs.get(cf.get('direction',''),0)+1
print(f'Neutral: {dirs.get(\"neutral\",0)}')"

# Check asymmetry
curl -sk $SITE/data/stories.json | python3 -c "
import json,sys;d=json.load(sys.stdin)
all_s=([d.get('lead')] if d.get('lead') else [])+d.get('stories',[])
nulls=sum(1 for s in all_s if s and s.get('asymmetry_score') is None)
print(f'Asymmetry nulls: {nulls}')"
```

## Root Fix (Long-Term)

Fix `detect_direction()` in `fetch_intel.py` to never return "neutral":
```python
def detect_direction(text):
    # ... existing keyword matching ...
    return "inflow"  # capital-first bias — never "neutral"
```

## Session Reference

Discovered June 11, 2026 across 3 debug sprints:
- Sprint 1: Fixed flows.json — 40 "neutral" → 0
- Sprint 2: Fixed asymmetry nulls — 57 null → 0
- Sprint 3: Fixed stories.json — 17 cap_flow "neutral" → 0
