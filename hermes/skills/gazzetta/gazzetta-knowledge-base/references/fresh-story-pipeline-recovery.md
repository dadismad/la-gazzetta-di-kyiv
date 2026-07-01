# Fresh-Story Pipeline Recovery (v27.1 June 2026)

Full recovery playbook when front-page stories are stale (>24h old) despite the pipeline running.

## Symptoms

- Front page teasers all show "1d ago" freshness
- `stories.json` on GCS has 0 stories from today
- `gazzetta.db` has drafts but no new stories
- Hero indicators show `—` (cascaded failure from missing data/)

## Root Cause Chain

1. **fetch_intel.py not in pipeline** — the cron runs `db_to_json.py` which reads from the `stories` table, but nothing collects NEW stories from RSS feeds. The OSINT collector (`fetch_intel.py`) was a manual step.

2. **No bulk draft approval** — `fetch_intel.py` writes to the `drafts` table as `pending_review`. `approve_draft.py` only handles individual IDs via `--id`. Without bulk approval, drafts never become stories.

3. **`db_to_json.py` sorts by `contradiction_score DESC` before `generated_at DESC`** — new stories created with `contradiction_score=50` (default) sort AFTER old stories with score=75, regardless of how fresh they are. The frontend teaser only shows the first 20 stories, so fresh content is invisible.

4. **SQLite `json_extract()` crashes on invalid JSON** — the SQL query uses `json_extract(full_json, '$.capital_flow.contradiction_flag')` in the ORDER BY. If ANY row has `json_valid(full_json)=0`, the entire query fails with "malformed JSON". Python's `json.loads('')` succeeds, but SQLite's `json_valid('')` returns 0. Empty strings and NULL ids cause this.

5. **`full_json` must be valid, rich JSON** — `db_to_json.py` reads ONLY the `full_json` column from the `stories` table — it ignores all other columns (`headline`, `sector`, `pillar`, etc.). If `full_json='{}'`, the story is invisible. The `full_json` must contain `story_id`, `headline`, `capital_flow`, `tier`, `sector`, `pillar`, `contradiction_score`, `generated_at`, and other fields.

## Recovery Procedure (Step by Step)

### 1. Collect fresh intel
```bash
cd ~/lagazzettadikyiv
python3 scripts/fetch_intel.py
```
RSS feeds → `drafts` table as `pending_review`.

### 2. Bulk-approve all pending drafts
Run the embedded Python bulk-approver in the unified pipeline or standalone:
```bash
cd ~/lagazzettadikyiv
python3 -c "
import sqlite3, json, re
from datetime import datetime, timezone

db = sqlite3.connect('gazzetta.db')
now = datetime.now(timezone.utc).isoformat()
draft_cols = ['id', 'source', 'raw_content', 'suggested_headline', 'suggested_multi_persona', 'suggested_flows', 'created_at', 'status']

pending = db.execute(\"SELECT * FROM drafts WHERE status='pending_review'\").fetchall()
approved = skipped = 0

for draft in pending:
    d = dict(zip(draft_cols, draft))
    did = d['id']
    
    # Skip if story already exists
    if db.execute('SELECT id FROM stories WHERE id=?', (did,)).fetchone():
        db.execute(\"UPDATE drafts SET status='approved' WHERE id=?\", (did,))
        skipped += 1
        continue
    
    headline = d.get('suggested_headline', '') or ''
    cf = {}
    try: cf = json.loads(d.get('suggested_flows', '{}'))
    except: pass
    mp = {}
    try: mp = json.loads(d.get('suggested_multi_persona', '{}'))
    except: pass
    
    sector = cf.get('asset_class', 'general') if isinstance(cf, dict) else 'general'
    pillar = cf.get('direction', '') if isinstance(cf, dict) else ''
    slug = re.sub(r'[^a-z0-9]+', '-', headline.lower())[:80].strip('-') if headline else did
    
    amt = cf.get('amount_b', 0) if isinstance(cf, dict) else 0
    amt = amt or 0
    conf = 'high' if amt > 50 else 'medium' if amt > 10 else 'low'
    
    # Build FULL rich JSON (NOT empty object!)
    full = {
        'story_id': did,
        'headline': headline,
        'slug': slug,
        'sector': sector,
        'pillar': pillar,
        'tier': 'DEVELOPING',
        'confidence': conf,
        'confidence_pct': 50,
        'contradiction_score': 75,     # Must be 75+ to sort alongside existing stories
        'generated_at': d.get('created_at') or now,
        'capital_flow': cf if cf else {
            'direction': 'inflow',
            'amount_b': 1.0,
            'asset_class': sector,
            'pace_multiplier': 1.0,
        },
        'they_say': headline,
        'reality': '',
        'thesis': '',
        'actors': [],
        'horizon': 'medium',
        'multi_persona': mp,
        'impacted_flows': [],
        'entity_tags': [],
        'time_decay': {},
    }
    
    db.execute(\"\"\"
        INSERT INTO stories 
        (id, slug, headline, sector, pillar, tier, confidence, 
         contradiction_score, generated_at, time_decay_raw, entity_tags_raw,
         multi_persona_raw, capital_flow_raw, full_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    \"\"\", (
        did, slug, headline, sector, pillar, 'DEVELOPING', conf, 75,
        d.get('created_at') or now, '{}', '[]',
        json.dumps(mp), json.dumps(cf), json.dumps(full)
    ))
    
    db.execute(\"UPDATE drafts SET status='approved' WHERE id=?\", (did,))
    approved += 1

db.commit()
rem = db.execute(\"SELECT COUNT(*) FROM drafts WHERE status='pending_review'\").fetchone()[0]
print(f'Approved {approved} new stories, {skipped} duplicates, {rem} remaining')
db.close()
"
```

### 3. Fix SQLite JSON validity (malformed JSON error)
```bash
cd ~/lagazzettadikyiv
python3 -c "
import sqlite3, json
db = sqlite3.connect('gazzetta.db')
# Find stories where SQLite json_valid fails (stricter than Python json.loads)
bad = db.execute(\"SELECT rowid, id, full_json FROM stories WHERE json_valid(full_json)=0\").fetchall()
for row in bad:
    print(f'  Fixing rowid={row[0]}, id={row[1]}')
    db.execute(\"UPDATE stories SET full_json='{}' WHERE rowid=?\", (row[0],))
db.commit()
remaining = db.execute('SELECT COUNT(*) FROM stories WHERE json_valid(full_json)=0').fetchone()[0]
print(f'Fixed {len(bad)} rows, {remaining} remaining invalid')
db.close()
"
```

### 4. Rebuild JSON + deploy
```bash
cd ~/lagazzettadikyiv
python3 scripts/db_to_json.py        # DB → data/stories.json + data/flows.json
python3 scripts/build_site.py        # Sync data/ → public/data/ + inject components
python3 scripts/build_hashed_assets.py  # Hash assets + rewrite HTML refs

GSDK=~/lagazzettadikyiv/devvit/google-cloud-sdk/bin
$GSDK/gsutil -m rsync -r public/ gs://www.lagazzettadikyiv.com/
```

### 5. Verify
```bash
# Check GCS has fresh stories
curl -s "https://www.lagazzettadikyiv.com/data/stories.json?t=$(date +%s)" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); s=d['stories']; today=[x for x in s if x.get('generated_at','').startswith('2026-06-')]; print(f'{len(s)} total, {len(today)} from today, first: {(s[0].get(\"headline\",\"\"))[:60]}')"

# Verify data/ exists on GCS (not 404)
curl -sI https://www.lagazzettadikyiv.com/data/stories.json | head -1
# MUST be HTTP/2 200
```

## Prevention: Pipeline Script Update

The unified pipeline script (`gazzetta_pipeline_unified.sh`) now includes:

```
Stage 0 (clean) → Stage 0.5 (fetch_intel.py) → Stage 0.6 (bulk_approve drafts) → Stage 1 (db_to_json.py) → ...
```

This ensures fresh stories are collected and approved BEFORE JSON compilation on every cron tick.

## Key Numbers from Recovery

| Metric | Before | After |
|--------|--------|-------|
| Stories total | 246 | 317 |
| Stories from today | 0 | 57 |
| Freshness on teasers | "1d ago" | "<1h ago" |
| First story headline | Medicare Advantage... | Iran denies Trump's claims... |
| Pending drafts | 270 | 0 |

## Pitfalls

- **`full_json='{}'` is invisible to db_to_json.py** — the script reads ONLY `full_json`, ignoring the `headline`, `sector`, `pillar`, `tier` columns. If `full_json` is an empty object, the story won't appear in `stories.json`.
- **`contradiction_score` must be 75+, not 50** — otherwise fresh stories sort after old ones regardless of `generated_at DESC`.
- **SQLite `json_valid()` is stricter than Python `json.loads()`** — empty strings and NULLs are invalid to SQLite but OK in Python.
- **`json_extract()` throws on invalid JSON** — not a graceful NULL, it crashes the entire query with "malformed JSON".
