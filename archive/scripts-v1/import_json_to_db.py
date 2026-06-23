#!/usr/bin/env python3
"""import_json_to_db.py — Seed gazzetta.db from existing JSON files.

Reads data/stories.json and data/flows.json, inserts into SQLite tables,
and creates story_flow_links from:
  - flow.story_id → maps flow back to its source story
  - story.impacted_flows[] → maps story to flows it impacts

Usage:
  python3 scripts/import_json_to_db.py           # normal import
  python3 scripts/import_json_to_db.py --dry-run  # validate only
"""

import json
import os
import sys
import sqlite3
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT / "gazzetta.db"
DATA = PROJECT / "data"
STORIES_PATH = DATA / "stories.json"
FLOWS_PATH = DATA / "flows.json"


def slugify(text):
    """Generate URL-friendly slug from text."""
    if not text:
        return "untitled"
    import re
    slug = text.lower()[:80]
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug or "untitled"


def import_stories(conn, stories_list):
    """Insert stories into stories table."""
    count = 0
    for s in stories_list:
        sid = s.get("story_id", "")
        if not sid:
            print(f"  SKIP: story has no story_id")
            continue

        conn.execute("""
            INSERT OR REPLACE INTO stories (
                id, slug, headline, sector, pillar, tier, confidence,
                contradiction_score, generated_at,
                time_decay_raw, entity_tags_raw, multi_persona_raw,
                capital_flow_raw, full_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sid,
            slugify(s.get("headline", sid)),
            s.get("headline", ""),
            s.get("sector", ""),
            s.get("pillar", s.get("paradigm_pillar", "")),
            s.get("tier", "active"),
            s.get("confidence", "medium"),
            s.get("contradiction_score", 0),
            s.get("generated_at", ""),
            json.dumps(s.get("time_decay", {})) if s.get("time_decay") else None,
            json.dumps(s.get("entity_tags", {})) if s.get("entity_tags") else None,
            json.dumps(s.get("multi_persona", {})) if s.get("multi_persona") else None,
            json.dumps(s.get("capital_flow", {})) if s.get("capital_flow") else None,
            json.dumps(s, ensure_ascii=False),
        ))
        count += 1
    return count


def import_flows(conn, flows_list):
    """Insert flows into flows table."""
    count = 0
    for f in flows_list:
        fid = f.get("id", "")
        if not fid:
            print(f"  SKIP: flow has no id")
            continue

        name = f.get("headline", "") or f"{f.get('amount_b', 0)}B {f.get('direction', '')} {f.get('asset_class', '')}".strip()
        if not name:
            name = fid[:60]

        conn.execute("""
            INSERT OR REPLACE INTO flows (
                id, story_id, name, category, net_direction,
                amount_b, velocity, last_updated, full_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fid,
            f.get("story_id", ""),
            name,
            f.get("asset_class", f.get("category", "")),
            f.get("direction", f.get("net_direction", "inflow")),
            f.get("amount_b", 0.0),
            f.get("pace_multiplier", f.get("velocity", 1.0)),
            f.get("generated_at", f.get("last_updated", "")),
            json.dumps(f, ensure_ascii=False),
        ))
        count += 1
    return count


def create_links(conn, stories_list, flows_list):
    """Create story_flow_links from bidirectional relationships."""
    link_count = 0

    # Map flow_id → story_id from flows data
    flow_to_story = {f.get("id"): f.get("story_id") for f in flows_list if f.get("id") and f.get("story_id")}

    # 1) flows → stories (flow.story_id)
    for flow_id, story_id in flow_to_story.items():
        try:
            conn.execute(
                "INSERT OR IGNORE INTO story_flow_links (story_id, flow_id) VALUES (?, ?)",
                (story_id, flow_id)
            )
            link_count += 1
        except sqlite3.IntegrityError:
            pass  # FK violation — story doesn't exist (shouldn't happen)

    # 2) stories → flows (story.impacted_flows)
    for s in stories_list:
        sid = s.get("story_id", "")
        impacted = s.get("impacted_flows", [])
        for ifid in impacted:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO story_flow_links (story_id, flow_id) VALUES (?, ?)",
                    (sid, ifid)
                )
                link_count += 1
            except sqlite3.IntegrityError:
                pass

    return link_count


def main():
    dry_run = "--dry-run" in sys.argv

    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found. Run init_db.py first.")
        sys.exit(1)

    if not STORIES_PATH.exists():
        print(f"ERROR: {STORIES_PATH} not found.")
        sys.exit(1)

    # Load JSON data
    with open(STORIES_PATH) as sf:
        stories_data = json.load(sf)
    stories_list = stories_data.get("stories", [])

    # Merge lead story (stored separately) into stories list
    lead_story = stories_data.get("lead")
    if lead_story and lead_story.get("story_id"):
        lead_id = lead_story["story_id"]
        existing_ids = {s.get("story_id") for s in stories_list}
        if lead_id not in existing_ids:
            stories_list.insert(0, lead_story)
            print(f"  + merged lead story: {lead_id[:60]}...")

    flows_list = []
    if FLOWS_PATH.exists():
        with open(FLOWS_PATH) as ff:
            flows_data = json.load(ff)
        flows_list = flows_data.get("flows", [])

    print(f"Loaded: {len(stories_list)} stories, {len(flows_list)} flows")

    if dry_run:
        # Validate without writing
        print("\n--- DRY RUN (validation only) ---")
        issues = 0
        for s in stories_list:
            if not s.get("story_id"):
                print(f"  WARN: story missing story_id: {s.get('headline', '?')[:60]}")
                issues += 1
        for f in flows_list:
            if not f.get("id"):
                print(f"  WARN: flow missing id: {f.get('headline', '?')[:60]}")
                issues += 1
            if not f.get("story_id"):
                print(f"  WARN: flow missing story_id: {f.get('id', '?')[:60]}")
                issues += 1
        print(f"Validation complete: {issues} issues")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys=ON")

    try:
        # Import stories
        story_count = import_stories(conn, stories_list)
        print(f"✓ Imported {story_count} stories")

        # Import flows
        flow_count = import_flows(conn, flows_list)
        print(f"✓ Imported {flow_count} flows")

        # Create links
        link_count = create_links(conn, stories_list, flows_list)
        print(f"✓ Created {link_count} story_flow_links")

        conn.commit()

        # Verify
        s_count = conn.execute("SELECT COUNT(*) FROM stories").fetchone()[0]
        f_count = conn.execute("SELECT COUNT(*) FROM flows").fetchone()[0]
        l_count = conn.execute("SELECT COUNT(*) FROM story_flow_links").fetchone()[0]
        print(f"\n  DB state: {s_count} stories · {f_count} flows · {l_count} links")

    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
