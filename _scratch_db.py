#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('/Users/alexstocchi/projects/gazzetta-di-kyiv/gazzetta.db')
conn.row_factory = sqlite3.Row

# Check drafts table schema
cursor = conn.execute("PRAGMA table_info(drafts)")
print("=== Drafts Schema ===")
for col in cursor:
    print(f"  {col['name']} ({col['type']})")

# Check stories table schema 
cursor = conn.execute("PRAGMA table_info(stories)")
print("\n=== Stories Schema ===")
for col in cursor:
    print(f"  {col['name']} ({col['type']})")

# Get recent approved drafts
try:
    cursor = conn.execute("""
        SELECT id, source, suggested_headline, status, created_at
        FROM drafts WHERE status = 'approved'
        ORDER BY created_at DESC LIMIT 10
    """)
    print("\n=== Recent Approved Drafts ===")
    for row in cursor:
        print(f"#{row['id']} [{row['source']}] {row['suggested_headline'][:120]}")
except Exception as e:
    print(f"Drafts query error: {e}")

# Get high-tier stories
try:
    cursor = conn.execute("""
        SELECT story_id, headline, tier, created_at
        FROM stories WHERE tier NOT IN ('DEVELOPING', 'BACKGROUND', '')
        ORDER BY created_at DESC LIMIT 10
    """)
    print("\n=== Non-DEVELOPING Stories ===")
    for row in cursor:
        print(f"{row['story_id']}: [{row['tier']}] {row['headline'][:120]}")
        print(f"  created: {row['created_at']}")
except Exception as e:
    print(f"Stories query error: {e}")

# Count by tier
try:
    cursor = conn.execute("""
        SELECT tier, COUNT(*) as cnt FROM stories GROUP BY tier ORDER BY cnt DESC
    """)
    print("\n=== Stories by Tier ===")
    for row in cursor:
        print(f"  {row['tier']}: {row['cnt']}")
except Exception as e:
    print(f"Tier count error: {e}")
