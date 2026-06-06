#!/usr/bin/env python3
"""generate_candidates_fallback.py — Generate narrative candidates from setups.json when Reddit ingest is down.

Input:  site/api/v1/home/setups.json
Output: data/reddit_candidates.json
"""

import json
import os
from datetime import datetime, timezone

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(PROJECT, "data")
API_HOME = os.path.join(PROJECT, "site", "api", "v1", "home")


def main():
    os.makedirs(DATA, exist_ok=True)
    candidates = []

    # Try setups.json
    setups_path = os.path.join(API_HOME, "setups.json")
    if os.path.exists(setups_path):
        with open(setups_path) as f:
            setups = json.load(f)
            for s in setups.get("setups", []):
                candidates.append({
                    "id": s.get("id", f"fallback_{len(candidates)}"),
                    "title": s.get("headline", s.get("title", "Untitled")),
                    "source": "fallback_setups",
                    "created_utc": s.get("generated_at", datetime.now(timezone.utc).isoformat()),
                    "score": s.get("score", s.get("confidence", 0)),
                })

    # Also try narratives.json
    narratives_path = os.path.join(DATA, "narratives.json")
    if os.path.exists(narratives_path):
        with open(narratives_path) as f:
            n = json.load(f)
            items = n.get("narratives", n.get("items", []))
            if isinstance(n, list):
                items = n
            for item in items:
                candidates.append({
                    "id": item.get("id", f"narrative_{len(candidates)}"),
                    "title": item.get("title", item.get("name", "Untitled")),
                    "source": "narratives",
                    "created_utc": item.get("generated_at", datetime.now(timezone.utc).isoformat()),
                    "score": item.get("score", item.get("intensity", 0)),
                })

    # Also try flows.json as last resort
    if not candidates:
        flows_path = os.path.join(DATA, "flows.json")
        if os.path.exists(flows_path):
            with open(flows_path) as f:
                flows = json.load(f)
                for fl in flows.get("flows", []):
                    candidates.append({
                        "id": fl.get("id", f"flow_{len(candidates)}"),
                        "title": fl.get("headline", "Untitled"),
                        "source": "flows",
                        "created_utc": flows.get("generated_at", ""),
                        "score": fl.get("confidence_pct", 0),
                    })

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "fallback",
        "count": len(candidates),
        "candidates": candidates,
    }

    out_path = os.path.join(DATA, "reddit_candidates.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(json.dumps({"ok": True, "candidates": len(candidates), "source": output["source"]}, indent=2))


if __name__ == "__main__":
    main()
