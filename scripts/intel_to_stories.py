#!/usr/bin/env python3
"""intel_to_stories.py — Bridge: telegram_intel/latest.json → stories.json

Reads actionable stories from telegram intel, converts to Gazzetta story format,
appends to stories.json with deduplication. Creates capital flow entries inline.

Run after: gazzetta-telegram-monitor (every 30m)
Run before: generate_flows.py
"""

import json
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(PROJECT, "data")
INTEL_PATH = os.path.join(DATA, "telegram_intel", "latest.json")
STORIES_PATH = os.path.join(DATA, "stories.json")

# Pillar detection keywords
PILLAR_KEYWORDS = {
    "china_ascendancy": ["china", "beijing", "xi", "ccp", "chinese", "pla", "taiwan"],
    "dollar_decline": ["dollar", "dedollar", "brics", "imf", "cofer", "treasury", "fed", "central bank"],
    "eu_fragmentation": ["eu", "european", "nato", "eurozone", "ecb", "brussels", "migration"],
    "abundance_tech": ["fusion", "space", "spacex", "nasa", "longevity", "breakthrough", "quantum"],
    "blockchain_agentic": ["crypto", "bitcoin", "token", "defi", "rwa", "blockchain", "stablecoin"],
    "multi_pillar": ["iran", "war", "strike", "missile", "hormuz", "oil", "crude", "brent", "sanctions"],
}


def detect_pillar(text):
    """Detect paradigm pillar from text content."""
    text_lower = text.lower()
    scores = {}
    for pillar, keywords in PILLAR_KEYWORDS.items():
        score = sum(1 for k in keywords if k in text_lower)
        if score > 0:
            scores[pillar] = score
    if not scores:
        return "multi_pillar"
    return max(scores, key=lambda k: scores[k])


def generate_story_id(headline, pillar):
    """Generate a stable story_id from headline + pillar."""
    slug = headline.lower()[:60]
    slug = "".join(c if c.isalnum() or c in "_-" else "_" for c in slug)
    slug = slug.strip("_").replace("__", "_")
    return f"n21_{pillar}__{slug}"


def intel_story_to_gazzetta(intel_story, pillar):
    """Convert a telegram intel story into Gazzetta story format."""
    headline = intel_story.get("title", intel_story.get("headline", "Untitled"))
    story_id = intel_story.get("story_id") or generate_story_id(headline, pillar)
    now = datetime.now(timezone.utc).isoformat()

    return {
        "story_id": story_id,
        "headline": headline[:200],
        "sector": intel_story.get("sector", "multi"),
        "pillar": pillar,
        "they_say": intel_story.get("consensus_narrative", intel_story.get("they_say", "")),
        "reality": intel_story.get("contradiction", intel_story.get("reality", "")),
        "thesis": intel_story.get("bet", intel_story.get("thesis", "")),
        "actors": intel_story.get("actors", []),
        "horizon": intel_story.get("horizon", "24-72h"),
        "confidence": intel_story.get("confidence", 75),
        "actionable_trade": intel_story.get("bet", intel_story.get("positioning", "")),
        "contradiction_score": intel_story.get("contradiction_score", 55),
        "capital_flow": {
            "direction": "inflow" if "LONG" in intel_story.get("bet", "") else "outflow",
            "amount_b": intel_story.get("amount_b", 8.0),
            "asset_class": intel_story.get("asset_class", "equities"),
            "pace": "accelerating",
        },
        "capital_flow_implication": intel_story.get("bet", ""),
        "evidence": intel_story.get("sources", []),
        "source": "telegram_intel",
        "generated_at": now,
        "freshness": "breaking",
    }


def main():
    if not os.path.exists(INTEL_PATH):
        print(json.dumps({"ok": False, "error": "no telegram intel file"}))
        return

    # Load intel
    with open(INTEL_PATH) as f:
        intel = json.load(f)

    actionable = intel.get("actionable_stories", [])
    if not actionable:
        print(json.dumps({"ok": True, "stories_added": 0, "reason": "no actionable stories in intel"}))
        return

    # Load current stories
    if os.path.exists(STORIES_PATH):
        with open(STORIES_PATH) as f:
            stories_data = json.load(f)
    else:
        stories_data = {"generated_at": "", "lead": None, "stories": []}

    existing_ids = {s.get("story_id", "") for s in stories_data.get("stories", [])}
    if stories_data.get("lead") and stories_data["lead"].get("story_id"):
        existing_ids.add(stories_data["lead"]["story_id"])

    # Convert and deduplicate
    added = 0
    for intel_story in actionable:
        headline = intel_story.get("title", intel_story.get("headline", ""))
        if not headline:
            continue

        pillar = detect_pillar(headline + " " + intel_story.get("event", ""))
        story_id = intel_story.get("story_id") or generate_story_id(headline, pillar)

        if story_id in existing_ids:
            continue

        gazzetta_story = intel_story_to_gazzetta(intel_story, pillar)
        stories_data["stories"].insert(0, gazzetta_story)  # newest first
        existing_ids.add(story_id)
        added += 1

    if added == 0:
        print(json.dumps({"ok": True, "stories_added": 0, "reason": "all stories already exist"}))
        return

    # Update timestamp
    stories_data["generated_at"] = datetime.now(timezone.utc).isoformat()

    # Write back
    with open(STORIES_PATH, "w") as f:
        json.dump(stories_data, f, indent=2, ensure_ascii=False)

    # Also sync to site/data/
    site_data = os.path.join(PROJECT, "site", "data", "stories.json")
    os.makedirs(os.path.dirname(site_data), exist_ok=True)
    with open(site_data, "w") as f:
        json.dump(stories_data, f, indent=2, ensure_ascii=False)

    print(json.dumps({
        "ok": True,
        "stories_added": added,
        "total_stories": len(stories_data["stories"]),
        "new_ids": [s["story_id"] for s in stories_data["stories"][:added]],
    }, indent=2))


if __name__ == "__main__":
    main()
