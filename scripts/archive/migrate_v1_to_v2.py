#!/usr/bin/env python3
"""
migrate_v1_to_v2.py — Legacy data retrofit for v3.0 8-narrative dashboard.

Reads every story row from gazzetta.db, maps old 6-container names to
new 8-narrative tags, sets baseline capital_volume_usd and contradiction_gap,
and writes the updated full_json back to the DB.

IDEMPOTENT: safe to run multiple times. Only modifies rows that lack
capital_volume_usd or contradiction_gap in their full_json payload.

Usage:
  python3 scripts/migrate_v1_to_v2.py
  python3 scripts/migrate_v1_to_v2.py --dry-run
"""

import json
import os
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DB_PATH = os.environ.get("GAZZETTA_DB_PATH", str(PROJECT / "gazzetta.db"))

# Old 6-container names → new 8-narrative tags
# Stories are distributed across the 8 narratives based on their container:
CONTAINER_TO_NARRATIVE = {
    "monetary_order":        "dollar_decline",
    "energy_resources":      "energy_sovereignty",
    "technology_ai":         "tech_convergence",       # broader umbrella
    "information_narrative": "wealthy_sports",         # closest analog
    "biosecurity_health":    "gene_editing",
    "flashpoints":           "deglobalization",
    # Already-migrated narrative tags (passthrough)
    "energy_sovereignty":    "energy_sovereignty",
    "dollar_decline":        "dollar_decline",
    "deglobalization":       "deglobalization",
    "china_ascent":          "china_ascent",
    "space_economy":         "space_economy",
    "gene_editing":          "gene_editing",
    "tech_convergence":      "tech_convergence",
    "wealthy_sports":        "wealthy_sports",
}

BASELINE_CAPITAL = 100_000_000   # $100M floor
BASELINE_GAP = 15                # low contradiction default


def main():
    import sqlite3

    dry_run = "--dry-run" in sys.argv

    if not DB_PATH.endswith(".db") or not Path(DB_PATH).exists():
        print(f"ERROR: DB not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")

    # 1. Check schema — need container, full_json, id
    cols = [r[1] for r in conn.execute("PRAGMA table_info(stories)")]
    needed = {"id", "container", "full_json"}
    missing = needed - set(cols)
    if missing:
        print(f"ERROR: Missing columns in stories table: {missing}")
        print(f"       Available: {sorted(cols)}")
        conn.close()
        sys.exit(1)

    # 2. Fetch all stories
    rows = conn.execute(
        "SELECT id, container, full_json FROM stories"
    ).fetchall()

    updated = 0
    already_ok = 0
    errors = 0

    for story_id, container, fj_str in rows:
        if not fj_str or fj_str == "{}":
            errors += 1
            continue

        try:
            story = json.loads(fj_str)
        except json.JSONDecodeError:
            errors += 1
            continue

        old_container = container or ""
        new_container = CONTAINER_TO_NARRATIVE.get(old_container)

        if new_container is None:
            print(f"  [{story_id}] unknown container '{old_container}' — skipping")
            errors += 1
            continue

        modified = False

        # Apply container mapping to both column and JSON
        if old_container != new_container:
            story["container"] = new_container
            modified = True

        # Apply baseline capital_volume_usd
        if story.get("capital_volume_usd") is None:
            story["capital_volume_usd"] = BASELINE_CAPITAL
            # Also set capital_flow if missing
            if "capital_flow" not in story or not story["capital_flow"]:
                story["capital_flow"] = {
                    "direction": "neutral",
                    "amount_b": BASELINE_CAPITAL / 1e9,
                    "asset_class": "mixed",
                    "projected": "",
                }
            else:
                story["capital_flow"]["amount_b"] = BASELINE_CAPITAL / 1e9
            modified = True

        # Apply baseline contradiction_gap
        if story.get("contradiction_gap") is None:
            story["contradiction_gap"] = BASELINE_GAP
            # Also set contradiction_score for frontend compatibility
            story["contradiction_score"] = BASELINE_GAP
            modified = True

        if modified:
            if not dry_run:
                conn.execute(
                    "UPDATE stories SET container = ?, full_json = ? WHERE id = ?",
                    (new_container, json.dumps(story, ensure_ascii=False), story_id),
                )
            updated += 1
            print(
                f"  [{story_id}] {old_container:25s} → {new_container:25s}"
                f"  cap=$100M  gap=15"
            )
        else:
            already_ok += 1

    if not dry_run:
        conn.commit()

        # Regenerate stories.json via db_to_json
        print("\nRegenerating stories.json...")

    conn.close()

    print(f"\n{'DRY RUN — ' if dry_run else ''}Migration complete.")
    print(f"  Updated:    {updated}")
    print(f"  Already ok: {already_ok}")
    if errors:
        print(f"  Errors:     {errors}")

    # If not dry run, regenerate stories.json and deploy JSON
    if not dry_run and updated > 0:
        # Write updated stories.json to both locations
        import subprocess
        result = subprocess.run(
            [sys.executable, str(PROJECT / "scripts" / "db_to_json.py")],
            capture_output=True, text=True, cwd=str(PROJECT),
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"WARNING: db_to_json.py failed: {result.stderr}")
            sys.exit(1)

        # Sync to public/data/
        src = PROJECT / "data" / "stories.json"
        dst = PROJECT / "public" / "data"
        dst.mkdir(parents=True, exist_ok=True)
        if src.exists():
            (dst / "stories.json").write_text(src.read_text())
            print("  stories.json synced to public/data/")

    elif dry_run:
        print("\nRun without --dry-run to apply changes and regenerate stories.json.")

    sys.exit(0 if errors == 0 else 1)


if __name__ == "__main__":
    main()
