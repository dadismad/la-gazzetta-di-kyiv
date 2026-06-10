#!/usr/bin/env python3
"""Clean orphan flow references from stories in gazzetta.db."""
import json, sqlite3

conn = sqlite3.connect('gazzetta.db')

# Get valid flow IDs
cur = conn.execute('SELECT id FROM flows')
valid_ids = set(row[0] for row in cur)

# Find and fix stories with orphan flow refs
cur = conn.execute('SELECT id, full_json FROM stories')
fixed = 0
for story_id, full_json in cur:
    story = json.loads(full_json)
    impacted = story.get('impacted_flows', [])
    if not impacted:
        continue
    cleaned = [fid for fid in impacted if fid in valid_ids]
    if len(cleaned) != len(impacted):
        story['impacted_flows'] = cleaned
        conn.execute('UPDATE stories SET full_json = ? WHERE id = ?',
                     (json.dumps(story), story_id))
        fixed += 1
        print(f'Fixed: {story_id} ({len(impacted)} → {len(cleaned)} flows)')

conn.commit()
print(f'\nFixed {fixed} stories')
conn.close()
