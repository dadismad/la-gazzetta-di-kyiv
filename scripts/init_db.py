#!/usr/bin/env python3
"""init_db.py — Initialize gazzetta.db SQLite database.

Creates relational schema for stories, flows, and story-flow links.
Establishes proper types, primary keys, and foreign key constraints.

Schema:
  stories
    id                   TEXT PRIMARY KEY  — story_id
    slug                 TEXT              — URL-friendly identifier
    headline             TEXT              — display headline
    sector               TEXT              — sector classification
    pillar               TEXT              — paradigm pillar
    tier                 TEXT              — freshness tier
    confidence           TEXT              — confidence level
    contradiction_score  INTEGER           — 0-100
    generated_at         TEXT              — ISO timestamp
    time_decay_raw       TEXT              — JSON: decay metadata
    entity_tags_raw      TEXT              — JSON: extracted entities
    multi_persona_raw    TEXT              — JSON: persona-specific content
    capital_flow_raw     TEXT              — JSON: inline capital flow dict
    full_json            TEXT              — complete story JSON blob

  flows
    id                   TEXT PRIMARY KEY  — flow_id
    story_id             TEXT              — FK → stories.id
    name                 TEXT              — display name (from headline)
    category             TEXT              — asset class / flow category
    net_direction        TEXT              — inflow | outflow
    amount_b             REAL              — amount in billions
    velocity             REAL              — pace_multiplier
    last_updated         TEXT              — ISO timestamp
    full_json            TEXT              — complete flow JSON blob

  story_flow_links
    story_id             TEXT              — FK → stories.id
    flow_id              TEXT              — FK → flows.id
    PRIMARY KEY (story_id, flow_id)

Usage:
  python3 scripts/init_db.py          # creates gazzetta.db (fails if exists)
  python3 scripts/init_db.py --force  # drops and recreates
"""

import os
import sys
import sqlite3
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT / "gazzetta.db"


def create_schema(conn):
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

    -- Indexes for common query patterns
    CREATE INDEX idx_stories_generated_at ON stories(generated_at);
    CREATE INDEX idx_stories_sector ON stories(sector);
    CREATE INDEX idx_stories_tier ON stories(tier);
    CREATE INDEX idx_flows_category ON flows(category);
    CREATE INDEX idx_flows_net_direction ON flows(net_direction);
    CREATE INDEX idx_flows_story_id ON flows(story_id);
    """)

    conn.commit()
    print(f"✓ Schema created in {DB_PATH}")


def main():
    force = "--force" in sys.argv

    if DB_PATH.exists() and not force:
        print(f"ERROR: {DB_PATH} already exists.")
        print("  Use --force to drop and recreate (data will be lost).")
        print("  Or run import_json_to_db.py to seed existing DB.")
        sys.exit(1)

    if DB_PATH.exists() and force:
        DB_PATH.unlink()
        print(f"✓ Existing {DB_PATH} removed.")

    conn = sqlite3.connect(str(DB_PATH))
    try:
        create_schema(conn)
        print(f"✓ Database initialized: {DB_PATH}")
        print(f"  Tables: stories, flows, story_flow_links")

        # Show schema summary
        for table in ["stories", "flows", "story_flow_links"]:
            cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
            print(f"\n  {table} ({len(cols)} columns):")
            for col in cols:
                print(f"    {col[1]:22s} {col[2]:10s} {'PK' if col[5] else '':5s} {'NOT NULL' if col[3] else ''}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
