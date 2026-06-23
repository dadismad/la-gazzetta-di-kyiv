# Coalescence Alerts & Cross-Narrative Hint Badges
>
> June 2026 — Phase B2/B3 frontend visualization layer in build_frontend.py

## Architecture Overview

Two visualization systems that surface the `cross_narrative_impact` data from `contradiction_synthesizer.py` to the reader:

### B2: Cross-Narrative Hint Badges

Renders on individual story cards when `s.cross_narrative_impact` has entries. Compact badges show the direction and target narrative:

```
[PARALLEL STACK]  >> REINFORCES [SUPPLY CHAIN BALKANIZATION]
```

**Implementation:**
- JS template injection in the STREAM CARDS render loop (build_frontend.py ~line 691)
- Checks `(s.cross_narrative_impact||[]).length`
- Maps each impact entry to a `<span>` badge with:
  - Icon: `trending_up` (reinforces) or `call_split` (complicates)
  - Color: `text-gold` (reinforces), `text-crimson` (complicates)
  - Title attribute: mechanism text (tooltip on hover)
  - Font: `text-[10px]` with uppercase tracking
- Badges wrap below the narrative tag line, full-width in card header

**Data flow:**
```
stories.json → all_stories → __STORIES_JSON__ → STORIES constant → card render
```
`cross_narrative_impact` field is in the story dict from `assemble_story()` → serialized in `stories_json` → available as `s.cross_narrative_impact` in JS.

**Verification:**
```js
// In browser console on live site:
document.querySelectorAll('[class*="text-10px"]').length  // hint badge count
STORIES.find(s => (s.cross_narrative_impact||[]).length > 0)  // find story with XNI
```

### B3: Coalescence Alerts

Computational aggregation in the Python compiler that detects when 3+ independent stories within a 6-hour window signal the same cross-narrative vector.

**Implementation:**

**Python computation (before HTML generation):**
```python
from datetime import datetime, timezone, timedelta  # must add timedelta

coalescence_alerts = []
now = datetime.now(timezone.utc)
cutoff = now - timedelta(hours=6)
xni_signals = {}  # key: (target_narrative, direction) -> [story_headlines]

for s in all_stories:
    xni = s.get("cross_narrative_impact") or []
    if not xni: continue
    # time filter
    gen_ts = datetime.fromisoformat(...)
    if gen_ts < cutoff: continue
    # group by (target, direction)
    for impact in xni:
        target = impact.get("narrative", "")
        direction = impact.get("direction", "neutral")
        if not target or direction == "neutral": continue
        key = (target, direction)
        if key not in xni_signals: xni_signals[key] = []
        xni_signals[key].append({...})

# Generate alerts for signals with 3+ stories
for (target, direction), hits in xni_signals.items():
    if len(hits) >= 3:
        target_display = NARRATIVE_DISPLAY.get(target, ...)
        coalescence_alerts.append({...})

coalescence_json = json.dumps(coalescence_alerts, ensure_ascii=False)
html = html.replace("__COALESCENCE_ALERTS__", coalescence_json)
```

**HTML placeholder (Live Ledger view):**
```html
<div id="coalescence-alerts" class="mb-stack-space-md"></div>
```

**JS renderer (before tab switching logic):**
```javascript
const COALESCENCE_ALERTS = __COALESCENCE_ALERTS__;  // in data injection block

(function(){
  var alertsEl = document.getElementById('coalescence-alerts');
  if (alertsEl && COALESCENCE_ALERTS && COALESCENCE_ALERTS.length) {
    alertsEl.innerHTML = COALESCENCE_ALERTS.map(function(a){
      // Gold-bordered panel with CAPITAL CONVERGENCE header
      // Lists source stories with arrow_forward icons
      // Shows: "{count} independent signals are {VERBING} {TARGET}"
      ...
    }).join('');
  }
})();
```

**Alert rendering:**
- Gold left-border (`border-l-2 border-gold`)
- Gold-tinted background (`bg-gold/5`)
- Header: "CAPITAL CONVERGENCE" in gold uppercase
- Body: "{N} independent signals are REINFORCING/COMPLICATING {TARGET_NARRATIVE} in the past 6 hours. The narratives are coalescing."
- Source stories listed below with arrow icons

**Test gate:** 107 PASS / 0 FAIL as of June 2026 (increased from 101 due to new cross_narrative_impact tags detected in stories.json).

## Requirements

- `from datetime import timedelta` must be added to `build_frontend.py` imports
- `NARRATIVE_DISPLAY` dict must exist for target narrative name resolution
- `__COALESCENCE_ALERTS__` placeholder must be in the HTML template AND in the replace() chain
- `const COALESCENCE_ALERTS = __COALESCENCE_ALERTS__;` must be in the data injection `<script>` block
- JS renderer must run before the main tab switching IIFE
