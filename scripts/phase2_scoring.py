#!/usr/bin/env python3
"""phase2_scoring.py — Score narrative candidates from reddit_candidates.json or fallback.

Input:  data/reddit_candidates.json (from devvit_ingest.py or generate_candidates_fallback.py)
Output: data/phase2_scores.json — scored items with hook_strength, actionability, contradiction, credibility
"""

import json
import os
import sys
from datetime import datetime, timezone

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(PROJECT, "data")


def load_candidates():
    candidates_path = os.path.join(DATA, "reddit_candidates.json")
    if os.path.exists(candidates_path):
        with open(candidates_path) as f:
            data = json.load(f)
            # Handle {"candidates": [...]} wrapper from fallback
            if isinstance(data, dict) and "candidates" in data:
                return data["candidates"]
            if isinstance(data, list):
                return data
            return data.get("candidates", data.get("items", []))

    # Fallback: try setups.json
    setups_path = os.path.join(PROJECT, "site", "api", "v1", "home", "setups.json")
    if os.path.exists(setups_path):
        with open(setups_path) as f:
            setups = json.load(f)
            return setups.get("setups", [])

    # Last fallback: narratives.json
    narratives_path = os.path.join(DATA, "narratives.json")
    if os.path.exists(narratives_path):
        with open(narratives_path) as f:
            n = json.load(f)
            if isinstance(n, dict):
                return n.get("narratives", n.get("items", []))
            return n if isinstance(n, list) else []

    return []


def score_item(item, idx):
    """Simple heuristic scoring when LLM scoring is unavailable."""
    title = item.get("title", item.get("headline", ""))
    body = item.get("selftext", item.get("body", item.get("description", "")))
    text = f"{title} {body}".lower()

    # Heuristic scoring
    hook_keywords = ["breaking", "alert", "urgent", "crisis", "surge", "crash", "rally"]
    action_keywords = ["buy", "sell", "long", "short", "position", "trade", "entry", "exit", "target"]
    contradiction_keywords = ["but", "however", "despite", "unexpected", "surprising", "contrary", "diverging"]
    credibility_keywords = ["data", "report", "fed", "ecb", "cpi", "gdp", "earnings", "treasury"]

    hook = min(10, sum(1 for k in hook_keywords if k in text) * 2)
    action = min(10, sum(1 for k in action_keywords if k in text) * 2)
    contradiction = min(10, sum(1 for k in contradiction_keywords if k in text) * 2)
    credibility = min(10, sum(1 for k in credibility_keywords if k in text) * 2)

    total = hook + action + contradiction + credibility

    return {
        "id": item.get("id", f"candidate_{idx}"),
        "title": title[:120],
        "source": item.get("source", item.get("subreddit", "unknown")),
        "hook_strength": hook,
        "actionability": action,
        "contradiction": contradiction,
        "credibility": credibility,
        "total_score": total,
        "scored_at": datetime.now(timezone.utc).isoformat(),
        "original": item,
    }


def main():
    candidates = load_candidates()
    if not candidates:
        result = {"ok": False, "error": "no candidates found", "scored": 0}
        print(json.dumps(result, indent=2))
        return result

    scored = [score_item(item, i) for i, item in enumerate(candidates)]
    scored.sort(key=lambda x: x["total_score"], reverse=True)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_scored": len(scored),
        "top_score": scored[0]["total_score"] if scored else 0,
        "candidates": scored,
    }

    out_path = os.path.join(DATA, "phase2_scores.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(json.dumps({"ok": True, "scored": len(scored), "top_score": output["top_score"]}, indent=2))
    return output


if __name__ == "__main__":
    main()
