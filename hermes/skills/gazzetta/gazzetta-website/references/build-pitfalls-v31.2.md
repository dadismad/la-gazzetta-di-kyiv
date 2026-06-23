# Build & Rendering Pitfalls (v31.2 — June 2026)

## Material Symbols Font URL

**The bug:** The Material Symbols font URL was missing the `opsz` (optical size) axis:
```
MALFORMED: family=Material+Symbols+Outlined:wght,FILL@100..700,0..1
```
This caused all 371 icon elements to render at 0x0 pixels. Their `textContent` (e.g., `auto_stories`, `sync_alt`, `account_tree`, `arrow_forward`) appeared as visible text across navigation, alerts, cards, and mobile nav — 343 instances of raw icon-name gibberish.

**Detection:** `document.querySelector('.material-symbols-outlined')?.offsetWidth === 0` on elements that should be visible.

**Correct URL:**
```
family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200
```

**Required CSS rule (add before `</style>`):**
```css
.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  display: inline-block;
  line-height: 1;
}
```

**File to edit:** `build_frontend.py` (or `build_frontend_staging.py`), in the `<head>` template section where stylesheet links are injected.

## Cross-Current Coalescence Aggregation

**The problem:** When the same narrative target receives both `reinforces` and `complicates` signals (3+ each within 6 hours), the old code rendered two identical-looking CAPITAL CONVERGENCE cards — both with the same gold header, same narrative name, just opposite directions. Users perceived this as a duplicate/bug.

**The insight:** A narrative being pulled in opposite directions simultaneously is NOT a rendering bug — it's the ultimate manifestation of market reflexivity. It's the most valuable analytical signal the platform produces.

**Solution:** Merge bidirectional alerts into a single CROSS-CURRENT CONVERGENCE card.

### Backend change (`build_frontend.py`, coalescence computation section):

Group signals by target narrative FIRST (not by `(target, direction)` pair):

```python
target_signals = {}  # key: target -> {"reinforces": [...], "complicates": [...]}
for s in all_stories:
    for impact in s.get("cross_narrative_impact", []):
        target = impact.get("narrative", "")
        direction = impact.get("direction", "neutral")
        if not target or direction == "neutral":
            continue
        if target not in target_signals:
            target_signals[target] = {"reinforces": [], "complicates": []}
        target_signals[target][direction].append({...})

# Generate alerts
for target, directions in target_signals.items():
    reinforcing = directions["reinforces"]
    complicating = directions["complicates"]
    if len(reinforcing) >= 3 and len(complicating) >= 3:
        # Cross-current: both directions
        coalescence_alerts.append({
            "type": "cross_current",
            "target": target_display,
            "reinforcing": {"count": len(reinforcing), "top_stories": reinforcing[:4]},
            "complicating": {"count": len(complicating), "top_stories": complicating[:4]},
        })
    elif len(reinforcing) >= 3:
        # Single-direction classic
        coalescence_alerts.append({"type": "single", ...})
    elif len(complicating) >= 3:
        coalescence_alerts.append({"type": "single", ...})
```

### Frontend change (JS renderer):

Detect `type: "cross_current"` and render a unified card:
- Icon: `swap_horiz` (bidirectional)
- Header: "CROSS-CURRENT CONVERGENCE" (gold uppercase)
- Body: "[Narrative] is being pulled in opposite directions simultaneously — X signals reinforcing, Y signals complicating within the past 6 hours."
- Layout: `grid grid-cols-1 md:grid-cols-2 gap-stack-space-md`
  - Left column: gold-tinted panel with `trending_up` icon + "Reinforcing (N)" header + evidence list
  - Right column: crimson-tinted panel with `trending_down` icon + "Complicating (N)" header + evidence list

Single-direction alerts (`type: "single"`) still render as classic CAPITAL CONVERGENCE cards with directional icon and verb.

## Headline Truncation

**The bug:** `contradiction_synthesizer.py` line 409 had:
```python
"headline": llm_story.get("headline", title)[:120],
```
This hard character cut produced truncated headlines like "BATRK liquidation signals decou" and "decoupling fro". No word-boundary check.

**Fix:**
```python
"headline": (lambda h: h if len(h) <= 120 else h[:120].rsplit(" ", 1)[0] + "...")(llm_story.get("headline", title)),
```

This truncates at the last space before position 120, appending "..." only when truncation occurs.

## Narrative Filter Wiring

**The bug:** Template strings generating onclick handlers produced unquoted variable references:
```javascript
onclick="setNarrativeFilter('+n.id+')"  // produces: setNarrativeFilter(dollar_decline)
```
The argument `dollar_decline` is an undefined JS variable, not a string. The function receives `undefined`.

**Fix:** Wrap in escaped quotes:
```javascript
onclick="setNarrativeFilter(\''+n.id+'\')"  // produces: setNarrativeFilter('dollar_decline')
```

**The `setNarrativeFilter()` function** must:
1. Accept a narrative ID string
2. Build a lookup from NARRATIVES (id -> title)
3. Filter STORIES by `_container_title` matching the narrative title
4. Re-render `#story-cards` using the same card template as initial load
5. Highlight the active pill in `#sidebar-nav` (add `text-gold`, remove from others)
6. Switch to the stream tab via `window.switchTab('stream')`
7. Support `'__all'` to clear the filter

Also add `cursor-pointer` class to narrative filter pills.
