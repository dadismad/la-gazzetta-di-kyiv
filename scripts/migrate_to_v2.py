#!/usr/bin/env python3
"""
migrate_to_v2.py — Schema migration for 6-container architecture.

Idempotent — safe to re-run. Adds:
  1. container TEXT column to stories (nullable, CHECK constraint added later)
  2. thesis TEXT column to stories
  3. story_tags table (story_id, tag) with FK to stories

Usage: python3 scripts/migrate_to_v2.py [--rollback]
"""

import sqlite3, sys, os, shutil
from datetime import datetime

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT, "gazzetta.db")
BACKUP_PATH = os.path.join(PROJECT, "gazzetta_v1_backup.db")

ROLLBACK = "--rollback" in sys.argv


def migrate():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: {DB_PATH} not found")
        sys.exit(1)
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    
    print(f"[{datetime.utcnow().isoformat()}] Migration starting...")
    
    # ── Step 1: Add container column ──
    try:
        conn.execute("ALTER TABLE stories ADD COLUMN container TEXT")
        print("  ✓ Added container column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("  → container column already exists (skipping)")
        else:
            raise
    
    # ── Step 2: Add thesis column ──
    try:
        conn.execute("ALTER TABLE stories ADD COLUMN thesis TEXT")
        print("  ✓ Added thesis column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("  → thesis column already exists (skipping)")
        else:
            raise
    
    # ── Step 3: Create story_tags table ──
    conn.execute("""
        CREATE TABLE IF NOT EXISTS story_tags (
            story_id TEXT NOT NULL,
            tag TEXT NOT NULL,
            PRIMARY KEY (story_id, tag),
            FOREIGN KEY (story_id) REFERENCES stories(id)
        )
    """)
    print("  ✓ story_tags table ready")
    
    # ── Step 4: Create indexes ──
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_stories_container ON stories(container)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_story_tags_tag ON story_tags(tag)
    """)
    print("  ✓ Indexes created")
    
    # ── Step 5: Verify ──
    columns = conn.execute("PRAGMA table_info(stories)").fetchall()
    col_names = [c[1] for c in columns]
    print(f"  Stories columns: {col_names}")
    
    tag_count = conn.execute("SELECT COUNT(*) FROM story_tags").fetchone()[0]
    story_count = conn.execute("SELECT COUNT(*) FROM stories").fetchone()[0]
    print(f"  Stories: {story_count}, Tags: {tag_count}")
    
    conn.commit()
    conn.close()
    print(f"[{datetime.utcnow().isoformat()}] Migration complete.")


def rollback():
    """Restore from v1 backup."""
    if not os.path.exists(BACKUP_PATH):
        print(f"ERROR: No backup found at {BACKUP_PATH}")
        sys.exit(1)
    
    shutil.copy2(BACKUP_PATH, DB_PATH)
    print(f"[{datetime.utcnow().isoformat()}] Rollback complete — restored from {BACKUP_PATH}")


if __name__ == "__main__":
    if ROLLBACK:
        rollback()
    else:
        migrate()
