#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('/Users/alexstocchi/projects/gazzetta-di-kyiv/gazzetta.db')
conn.row_factory = sqlite3.Row

for draft_id in [320, 319, 317, 314, 316, 312]:
    cursor = conn.execute("SELECT id, source, raw_content, suggested_headline, created_at FROM drafts WHERE id = ?", (draft_id,))
    row = cursor.fetchone()
    if row:
        content = row['raw_content'][:800] if row['raw_content'] else '(no content)'
        print(f"=== Draft #{row['id']} [{row['source']}] ===")
        print(f"Headline: {row['suggested_headline'][:150]}")
        print(f"Created: {row['created_at']}")
        print(f"Content: {content}")
        print()

conn.close()
