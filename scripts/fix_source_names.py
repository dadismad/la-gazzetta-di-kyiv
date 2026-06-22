#!/usr/bin/env python3
"""fix_source_names.py — Replace 'RSS' with real domain names."""
import os, sys, json, shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from contradiction_synthesizer import extract_domain

def main():
    data_path = Path(__file__).parent.parent / "data" / "stories.json"
    backup_path = data_path.with_suffix('.json.bak')
    shutil.copy(data_path, backup_path)
    print(f"[*] Backup saved to {backup_path}")

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_stories = data.get("all_stories", [])
    fixed_count = 0

    for story in all_stories:
        url = story.get("source_url", "")
        extracted = extract_domain(url)

        # Enforce synthesizer's single source of truth unconditionally
        story["source_name"] = extracted
        story["feed_source"] = extracted
        fixed_count += 1

    data["all_stories"] = all_stories

    tmp_path = data_path.with_suffix('.json.tmp')
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, data_path)

    print(f"[+] Step 5b Complete: Cleaned {fixed_count} source strings.")

if __name__ == "__main__":
    main()
