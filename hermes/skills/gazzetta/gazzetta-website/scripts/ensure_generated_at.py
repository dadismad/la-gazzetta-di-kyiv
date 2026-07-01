#!/usr/bin/env python3
"""Ensure every story in stories.json has a generated_at field.

Reads document-level generated_at and copies it to any story missing the field.
Run before story-app.js rendering to prevent empty time badges.
"""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent if '__file__' in dir() else Path.cwd()
DATA_FILE = PROJECT_ROOT / "site" / "data" / "stories.json"

def main():
    if not DATA_FILE.exists():
        print(json.dumps({"ok": False, "error": "stories.json not found"}))
        sys.exit(1)

    with open(DATA_FILE) as f:
        d = json.load(f)

    doc_ts = d.get("generated_at", datetime.now(timezone.utc).isoformat())
    count = 0
    for s in d.get("stories", []):
        if "generated_at" not in s:
            s["generated_at"] = doc_ts
            count += 1

    d["generated_at"] = datetime.now(timezone.utc).isoformat()

    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

    # Also update data/ copy
    data_copy = PROJECT_ROOT / "data" / "stories.json"
    if data_copy.exists():
        with open(data_copy, "w") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)

    print(json.dumps({
        "ok": True,
        "stories_total": len(d["stories"]),
        "generated_at_added": count,
        "doc_timestamp": doc_ts[:19]
    }))

if __name__ == "__main__":
    main()
