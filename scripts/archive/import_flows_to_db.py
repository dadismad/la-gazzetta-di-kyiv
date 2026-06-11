#!/usr/bin/env python3
"""Import regenerated flows.json into gazzetta.db, replacing old flows."""
import json, sqlite3, sys

new_flows = json.load(open('site/data/flows.json'))
print(f'New flows: {len(new_flows["flows"])} entries')

conn = sqlite3.connect('gazzetta.db')

cur = conn.execute('SELECT COUNT(*) FROM flows')
old_count = cur.fetchone()[0]
print(f'Old flows in DB: {old_count}')

conn.execute('DELETE FROM flows')
print(f'Deleted {old_count} old flows')

for f in new_flows['flows']:
    fid = f.get('id', '')
    story_id = f.get('story_id', None)
    name = f.get('headline', f.get('name', ''))
    category = f.get('category', '')
    net_direction = f.get('direction', f.get('net_direction', ''))
    amount_b = f.get('amount_b', 0)
    velocity = f.get('velocity', 0)
    last_updated = f.get('generated_at', f.get('last_updated', ''))
    full_json = json.dumps(f)
    
    conn.execute('''INSERT INTO flows (id, story_id, name, category, net_direction, amount_b, velocity, last_updated, full_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (fid, story_id, name, category, net_direction, amount_b, velocity, last_updated, full_json))

conn.commit()

cur = conn.execute('SELECT COUNT(*) FROM flows')
new_count = cur.fetchone()[0]
print(f'New flows in DB: {new_count}')

cur = conn.execute('SELECT amount_b FROM flows')
generic = sum(1 for (ab,) in cur if ab <= 1.5)
print(f'Generic flows: {generic}')

conn.close()
print('DB UPDATE COMPLETE')
