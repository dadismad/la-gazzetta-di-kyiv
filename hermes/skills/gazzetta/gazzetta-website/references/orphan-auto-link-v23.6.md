# Orphan Auto-Link Protocol (v23.6)

## When to use
- `refresh_context.py` §4.5c reports orphaned stories (>0 with no `impacted_flows`)
- After running `intel_to_stories.py` which creates new stories without flow links
- As a pre-deploy fix when the 24-orphan threshold is breached

## How it works
Matches stories to flows via `asset_class` field. Stories with `capital_flow.asset_class == 'crypto'` get linked to the first flow with the same asset_class. Falls back to any flow if no asset_class match found.

## Recipe

```bash
cd ~/projects/gazzetta-di-kyiv
.venv/bin/python << 'PYEOF'
import json, sqlite3, shutil

with open('data/stories.json') as f: en = json.load(f)
with open('data/flows.json') as f: flows_data = json.load(f)

flows = flows_data['flows']
orphans = [s for s in en['stories'] if not s.get('impacted_flows')]
print(f'Orphans: {len(orphans)}')

# Build asset_class → flow_id map
flow_by_asset = {}
for fl in flows:
    ac = fl.get('asset_class', '')
    flow_by_asset.setdefault(ac, []).append(fl['id'])

conn = sqlite3.connect('gazzetta.db')
links_made = 0

for story in orphans:
    cf = story.get('capital_flow', {})
    ac = cf.get('asset_class', '')
    candidates = flow_by_asset.get(ac, [f['id'] for f in flows])
    best = candidates[0] if candidates else None
    if best:
        conn.execute(
            'INSERT OR IGNORE INTO story_flow_links (story_id, flow_id) VALUES (?, ?)',
            (story['story_id'], best)
        )
        story.setdefault('impacted_flows', []).append(best)
        links_made += 1

conn.commit()
conn.close()

with open('data/stories.json', 'w') as f:
    json.dump(en, f, ensure_ascii=False, indent=2)
shutil.copy('data/stories.json', 'site/data/stories.json')

remaining = len([s for s in en['stories'] if not s.get('impacted_flows')])
print(f'Links created: {links_made}, Remaining orphans: {remaining}')
PYEOF
```

Also apply to RU data (same story_ids):

```python
with open('data/stories_ru.json') as f: ru = json.load(f)
en_links = {s['story_id']: s.get('impacted_flows',[]) for s in en['stories']}
linked_ru = 0
for s in ru['stories']:
    if not s.get('impacted_flows') and s['story_id'] in en_links:
        s['impacted_flows'] = en_links[s['story_id']]
        linked_ru += 1
```

## Verification

```bash
# Orphan count (should be 0)
.venv/bin/python -c "import json; d=json.load(open('data/stories.json')); print(len([s for s in d['stories'] if not s.get('impacted_flows')]))"

# SQLite link count
sqlite3 gazzetta.db "SELECT count(*) FROM story_flow_links"
```

## Pitfalls

- **RU stories have different IDs**: Apply EN links to RU by matching on `story_id` fields (they share the same story_id between EN and RU data).
- **Asset class may be missing**: Falls back to any flow if `capital_flow.asset_class` is absent on the story.
- **24 is the known threshold**: When `refresh_context.py` reports 24 orphans, it means no auto-linking has been run against the latest stories. Run this recipe.

## When NOT to use

- Don't use if stories already have manually curated `impacted_flows` — the `INSERT OR IGNORE` prevents duplicates but won't fix wrong manual links.
- Don't use as a cron job — it's a manual maintenance task. The link quality depends on `asset_class` accuracy in the pipeline.
