# safeCF() Pattern — Null-Safe Capital Flow Rendering

**Problem:** Stories in `stories.json` can have `capital_flow` dicts with null fields:
- `claim: null` — renders as `undefined — projected ...` 
- `amount_b: null` — renders as `undefined` in amount positions
- `confidence: null` — renders as `change at undefined confidence`
- `projected: "{...raw JSON...}"` — renders raw JSON objects into DOM

**Root cause:** `db_to_json.py` writes `capital_flow` dicts directly from DB without filling defaults. The JS card renderer (`cfClaim`, `cfHint`, `capitalFlowHTML`) accesses these fields without null guards — template literals like `${cf.claim}` produce the string `"undefined"` when `cf.claim` is `null`.

**Impact:** 37/189 stories affected (June 2026). 287 instances of `undefined` in a single page load. Users see literal "undefined" in story cards.

## Solution: safeCF() Normalizer

Insert this function before `capitalFlowHTML()` in `app.js`:

```javascript
function safeCF(raw) {
  if (!raw || typeof raw !== 'object') return { 
    claim: '', direction: 'inflow', amount_b: 0, 
    asset_class: '', projected: '', confidence: '65%', 
    positioning: '' 
  };
  const proj = raw.projected;
  return {
    claim: raw.claim || (raw.direction || 'inflow') + ' ' + (raw.asset_class || ''),
    direction: raw.direction || 'inflow',
    amount_b: raw.amount_b || 0,
    asset_class: raw.asset_class || '',
    projected: (typeof proj === 'string' && proj.startsWith('{')) 
      ? 'Capital flow tracked' 
      : (proj || 'Capital flow tracked'),
    confidence: raw.confidence || '65%',
    positioning: raw.positioning || '',
    anchor_symbol: raw.anchor_symbol || '',
    pace_multiplier: raw.pace_multiplier || 1
  };
}
```

Then replace ALL occurrences of:
- `const cf = s.capital_flow || {};` → `const cf = safeCF(s.capital_flow);`
- `const cf = story.capital_flow;` → `const cf = safeCF(story.capital_flow);`
- `let cf = story.capital_flow;` → `let cf = safeCF(story.capital_flow);`

Key locations in app.js (4 call sites):
1. Flow direction bias computation (~line 1072)
2. Card severity determination (~line 1229)
3. Contradiction score calculation (~line 1252)
4. Card rendering template (~line 1304)
5. Homepage teaser populator (~line 2303)

Also fix `data-update-count="${story.update_count}"` → `data-update-count="${story.update_count || 0}"` (~line 1383) — `update_count` is always undefined on stories from gazzetta.db.

## DB Backfill

After adding safeCF(), backfill the database to prevent recurrence:

```python
import sqlite3, json
db = sqlite3.connect('gazzetta.db')
cur = db.execute('SELECT id, capital_flow_raw FROM stories WHERE capital_flow_raw IS NOT NULL')
for story_id, cf_raw in cur.fetchall():
    cf = json.loads(cf_raw)
    changed = False
    if cf.get('claim') is None:
        cf['claim'] = (cf.get('direction','inflow') + ' ' + cf.get('asset_class','')).strip()
        changed = True
    if cf.get('amount_b') is None:
        cf['amount_b'] = 0; changed = True
    if cf.get('confidence') is None:
        cf['confidence'] = '65%'; changed = True
    if cf.get('projected') and isinstance(cf['projected'], str) and cf['projected'].startswith('{'):
        cf['projected'] = 'Capital flow tracked'; changed = True
    if changed:
        db.execute('UPDATE stories SET capital_flow_raw = ? WHERE id = ?', (json.dumps(cf), story_id))
db.commit()
```

Then regenerate: `python3 scripts/db_to_json.py` → deploy `site/data/stories.json` → GCS.

## Verification

```js
// After deploy — must return 0, 0, 190
JSON.stringify({
  undefined: (document.body.innerHTML.match(/undefined/g)||[]).length,
  nullText: (document.body.innerHTML.match(/>null</g)||[]).length, 
  cards: document.querySelectorAll('.card').length
})
```

PASS: `undefined = 0`, `nullText = 0`, `cards > 0`.
FAIL if `undefined > 0` → safeCF() not covering all access sites.
