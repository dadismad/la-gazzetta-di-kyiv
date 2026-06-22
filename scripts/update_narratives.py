#!/usr/bin/env python3
"""
La Gazzetta di Kyiv — Phase 3
Module: update_narratives.py
Purpose: Compute dynamic narrative metrics from stories.json and refresh narratives.json.
Reads: data/stories.json, data/narratives.json
Writes: data/narratives.json (atomic)
"""

import os, sys, json, math
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("/opt/gazzetta-di-kyiv/data")
STORIES_FILE = DATA_DIR / "stories.json"
NARRATIVES_FILE = DATA_DIR / "narratives.json"

STATUS_THRESHOLDS = {
    "story_count_emergent": 3,
    "strength_stable": 0.5,
    "strength_waning": 0.1,
    "velocity_growing": 0.01,
    "velocity_waning": -0.03,
}


def fix_ownership(path_str: str):
    if sys.platform != "linux":
        return
    try:
        import pwd, grp
        uid = pwd.getpwnam("gazzetta").pw_uid
        gid = grp.getgrnam("gazzetta").gr_gid
        os.chown(path_str, uid, gid)
    except (KeyError, OSError):
        pass


def load_json(path: Path) -> dict:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def compute_narrative_metrics(stories: list, narratives: dict) -> dict:
    """Aggregate stories per narrative and compute strength/velocity/status."""
    now = datetime.now(timezone.utc)

    # Group stories by narrative_id
    groups = defaultdict(list)
    for s in stories:
        nid = s.get("narrative_id", "unassigned")
        groups[nid].append(s)

    updated = {}
    for nid, meta in narratives.items():
        group = groups.get(nid, [])

        # Count
        story_count = len(group)

        # Capital total
        capital_total = sum(
            s.get("capital_at_stake_usd", 0) for s in group
        )

        # Materiality ratio
        material_count = sum(1 for s in group if s.get("materiality_pass"))
        materiality_ratio = material_count / story_count if story_count > 0 else 0.0

        # Average contradiction gap
        avg_gap = (
            sum(s.get("contradiction_gap", 0) for s in group) / story_count
            if story_count > 0
            else 0.0
        )

        # Strength score (0-1): composite of capital volume + gap + materiality
        # Log-scale capital: $1B → 0.3, $10B → 0.6, $100B → 0.9
        capital_log = (
            math.log10(max(capital_total, 1_000_000)) / 12
        )  # normalizes ~$1T → 1.0
        gap_norm = avg_gap / 100.0
        strength = round(
            capital_log * 0.4 + gap_norm * 0.3 + materiality_ratio * 0.3, 3
        )

        # Velocity placeholder (requires previous-cycle state for true derivative)
        # For now: gap × materiality_ratio as a proxy for "signal intensity"
        velocity = round(gap_norm * materiality_ratio * 0.1, 4)

        # Lifecycle status
        status = _compute_status(
            story_count, strength, velocity, meta.get("status", "emergent")
        )

        updated[nid] = {
            **meta,
            "status": status,
            "strength_score": strength,
            "velocity": velocity,
            "story_count": story_count,
            "capital_total_usd": capital_total,
            "materiality_ratio": materiality_ratio,
            "avg_contradiction_gap": round(avg_gap, 1),
            "last_updated": now.isoformat(),
        }

    return updated


def _compute_status(count, strength, velocity, current_status):
    """Heuristic lifecycle transition logic."""
    if count < STATUS_THRESHOLDS["story_count_emergent"]:
        return "emergent"
    if velocity < STATUS_THRESHOLDS["velocity_waning"] and strength < STATUS_THRESHOLDS["strength_stable"]:
        return "waning"
    if strength < STATUS_THRESHOLDS["strength_waning"] and count < 5:
        return "waning"
    if velocity > STATUS_THRESHOLDS["velocity_growing"]:
        return "growing"
    if strength >= STATUS_THRESHOLDS["strength_stable"]:
        return "stable"
    return current_status or "emergent"


def main():
    print("[update_narratives] Computing narrative metrics...")

    stories_data = load_json(STORIES_FILE)
    narratives_data = load_json(NARRATIVES_FILE)

    all_stories = stories_data.get("all_stories", [])
    narratives = narratives_data.get("narratives", {})

    if not narratives:
        print("[-] No narratives seed found. Aborting.")
        sys.exit(1)

    updated = compute_narrative_metrics(all_stories, narratives)

    output = {
        "metadata": {
            "version": "1.0",
            "updated": datetime.now(timezone.utc).isoformat(),
        },
        "narratives": updated,
    }

    tmp_path = NARRATIVES_FILE.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, NARRATIVES_FILE)

    fix_ownership(str(NARRATIVES_FILE))

    # Report
    for nid, m in sorted(updated.items()):
        print(
            f"  {nid:25s} stories={m['story_count']:3d}  "
            f"capital=${m['capital_total_usd']/1e9:6.1f}B  "
            f"strength={m['strength_score']:.2f}  "
            f"status={m['status']}"
        )

    print(f"[+] Narratives updated: {len(updated)} total")


if __name__ == "__main__":
    main()
