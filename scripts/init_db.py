#!/usr/bin/env python3
"""init_db.py — Initialize gazzetta.db SQLite database.

Creates relational schema for stories, flows, story-flow links, and drafts.
Establishes proper types, primary keys, and foreign key constraints.

Schema:
  stories, flows, story_flow_links — as documented in v3.0

  drafts
    id                   INTEGER PRIMARY KEY AUTOINCREMENT
    source               TEXT              — origin of the draft (rss_feed, telegram, manual)
    raw_content          TEXT              — full raw text from source
    suggested_headline   TEXT              — AI-suggested or extracted headline
    suggested_multi_persona TEXT           — JSON: persona-specific content blocks
    suggested_flows      TEXT              — JSON: capital flow suggestions
    created_at           TEXT              — ISO timestamp
    status               TEXT DEFAULT 'pending_review'

Usage:
  python3 scripts/init_db.py            # creates gazzetta.db (fails if exists)
  python3 scripts/init_db.py --force    # drops and recreates
  python3 scripts/init_db.py --migrate  # add new tables to existing DB (safe)
"""

import os
import sys
import sqlite3
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT / "gazzetta.db"


def create_all_tables(conn):
    """Create all tables (full schema)."""
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    conn.executescript("""
    CREATE TABLE stories (
        id                  TEXT PRIMARY KEY,
        slug                TEXT,
        headline            TEXT,
        sector              TEXT,
        pillar              TEXT,
        tier                TEXT,
        confidence          TEXT,
        contradiction_score INTEGER,
        generated_at        TEXT,
        time_decay_raw      TEXT,
        entity_tags_raw     TEXT,
        multi_persona_raw   TEXT,
        capital_flow_raw    TEXT,
        full_json           TEXT
    );

    CREATE TABLE flows (
        id                  TEXT PRIMARY KEY,
        story_id            TEXT,
        name                TEXT,
        category            TEXT,
        net_direction       TEXT,
        amount_b            REAL,
        velocity            REAL,
        last_updated        TEXT,
        full_json           TEXT,
        FOREIGN KEY (story_id) REFERENCES stories(id)
    );

    CREATE TABLE story_flow_links (
        story_id            TEXT,
        flow_id             TEXT,
        PRIMARY KEY (story_id, flow_id),
        FOREIGN KEY (story_id) REFERENCES stories(id),
        FOREIGN KEY (flow_id) REFERENCES flows(id)
    );

    CREATE TABLE drafts (
        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
        source               TEXT,
        raw_content          TEXT,
        suggested_headline   TEXT,
        suggested_multi_persona TEXT,
        suggested_flows      TEXT,
        created_at           TEXT,
        status               TEXT DEFAULT 'pending_review'
    );

    -- Indexes for common query patterns
    CREATE UNIQUE INDEX idx_stories_slug ON stories(slug);
    CREATE INDEX idx_stories_generated_at ON stories(generated_at);
    CREATE INDEX idx_stories_sector ON stories(sector);
    CREATE INDEX idx_stories_tier ON stories(tier);
    CREATE INDEX idx_flows_category ON flows(category);
    CREATE INDEX idx_flows_net_direction ON flows(net_direction);
    CREATE INDEX idx_flows_story_id ON flows(story_id);
    CREATE INDEX idx_drafts_status ON drafts(status);
    CREATE INDEX idx_drafts_source ON drafts(source);
    """)


def migrate_add_drafts(conn):
    """Add drafts table to existing DB — safe, no data loss."""
    existing = {row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}

    if "drafts" in existing:
        print("  drafts table already exists — skipping")
        return False

    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript("""
    CREATE TABLE drafts (
        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
        source               TEXT,
        raw_content          TEXT,
        suggested_headline   TEXT,
        suggested_multi_persona TEXT,
        suggested_flows      TEXT,
        created_at           TEXT,
        status               TEXT DEFAULT 'pending_review'
    );
    CREATE INDEX idx_drafts_status ON drafts(status);
    CREATE INDEX idx_drafts_source ON drafts(source);
    """)
    conn.commit()
    print("✓ drafts table added to existing database")
    return True


def show_tables(conn):
    """Display all tables and their columns."""
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    print(f"\n  Tables: {', '.join(t[0] for t in tables)}")
    for (table_name,) in tables:
        cols = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        print(f"\n  {table_name} ({len(cols)} columns):")
        for col in cols:
            pk = "PK" if col[5] else ""
            nn = "NOT NULL" if col[3] else ""
            print(f"    {col[1]:24s} {col[2]:10s} {pk:4s} {nn}")


def run_all_migrations(conn):
    """Apply all pending migrations to existing DB."""
    existing = {row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' OR type='index'"
    ).fetchall()}

    # Migration 1: drafts table
    if "drafts" not in existing:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.executescript("""
            CREATE TABLE drafts (
                id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                source               TEXT,
                raw_content          TEXT,
                suggested_headline   TEXT,
                suggested_multi_persona TEXT,
                suggested_flows      TEXT,
                created_at           TEXT,
                status               TEXT DEFAULT 'pending_review'
            );
            CREATE INDEX idx_drafts_status ON drafts(status);
            CREATE INDEX idx_drafts_source ON drafts(source);
        """)
        conn.commit()
        print("  ✓ drafts table added")

    # Migration 2: unique slug index
    if "idx_stories_slug" not in existing:
        # First check for duplicate slugs and warn
        dupes = conn.execute("""
            SELECT slug, COUNT(*) FROM stories GROUP BY slug HAVING COUNT(*) > 1
        """).fetchall()
        if dupes:
            print(f"  ⚠ {len(dupes)} duplicate slug(s) found — cannot create UNIQUE index")
            for slug, cnt in dupes:
                print(f"    slug='{slug[:50]}' appears {cnt} times")
            return False
        conn.execute("CREATE UNIQUE INDEX idx_stories_slug ON stories(slug)")
        conn.commit()
        print("  ✓ UNIQUE index on stories.slug created")
    
    return True


def main():
    force = "--force" in sys.argv
    migrate = "--migrate" in sys.argv

    # ── Migration mode: add tables to existing DB ──
    if migrate:
        if not DB_PATH.exists():
            print(f"ERROR: {DB_PATH} not found. Run without --migrate to create.")
            sys.exit(1)
        conn = sqlite3.connect(str(DB_PATH))
        try:
            run_all_migrations(conn)
            show_tables(conn)
        finally:
            conn.close()
        return

    # ── Fresh creation ──
    if DB_PATH.exists() and not force:
        print(f"ERROR: {DB_PATH} already exists.")
        print("  Use --force to drop and recreate (data will be lost).")
        print("  Use --migrate to add new tables safely.")
        sys.exit(1)

    if DB_PATH.exists() and force:
        DB_PATH.unlink()
        print(f"✓ Existing {DB_PATH} removed.")

    conn = sqlite3.connect(str(DB_PATH))
    try:
        create_all_tables(conn)
        print(f"✓ Database initialized: {DB_PATH}")
        show_tables(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
