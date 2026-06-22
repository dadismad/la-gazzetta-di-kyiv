#!/usr/bin/env python3
"""
Ensure every story in stories.json has a generated_at field.
Reads stories.json, adds generated_at from document-level timestamp
to any story missing it. Runs before deploy (Stage 2.5 pre-check).
"""

import json, sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "stories.json"


def main():
    if not DATA_FILE.exists():
        print("no stories.json, skipping")
        return 0

    d = json.loads(DATA_FILE.read_text())
    stories = d.get("stories", [])
    if not stories:
        print("no stories to check")
        return 0

    now = datetime.now(timezone.utc).isoformat()
    doc_ts = d.get("generated_at") or d.get("last_updated") or now

    fixed = 0
    for s in stories:
        if "generated_at" not in s:
            s["generated_at"] = doc_ts
            fixed += 1

    if fixed:
        DATA_FILE.write_text(json.dumps(d, indent=2, ensure_ascii=False))
        print(f"✓ Added generated_at to {fixed}/{len(stories)} stories")

    # Verify
    missing = sum(1 for s in stories if "generated_at" not in s)
    if missing:
        print(f"✗ {missing} stories still missing generated_at", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
