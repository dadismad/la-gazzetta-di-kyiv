#!/usr/bin/env python3
"""align_tiers.py — Recompute tiers from contradiction_gap."""
import os, sys, json, shutil
from pathlib import Path

def compute_tier(story):
    gap = story.get("contradiction_gap", 0)
    if gap >= 65: return "BREAKING"
    if gap >= 40: return "ACTIVE"
    return "SETTLING"

def main():
    data_path = Path(__file__).parent.parent / "data" / "stories.json"
    backup_path = data_path.with_suffix('.json.bak')
    shutil.copy(data_path, backup_path)
    print(f"[*] Backup saved to {backup_path}")

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_stories = data.get("all_stories", [])
    for story in all_stories:
        story["tier"] = compute_tier(story)

    data["all_stories"] = all_stories

    tmp_path = data_path.with_suffix('.json.tmp')
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, data_path)

    print("[+] Step 5c Complete: Re-aligned all tiers based on contradiction_gap.")

if __name__ == "__main__":
    main()
