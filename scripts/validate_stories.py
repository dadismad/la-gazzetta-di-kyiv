#!/usr/bin/env python3
"""validate_stories.py — Validate and repair story capital_flow dicts before flow generation.

Fixes missing fields in capital_flow dicts that cause "undefined" on the frontend.
Required fields: direction, amount_b, projected, pace_multiplier, confidence_pct, confidence_level

Run as part of pipeline_chain.sh between decay_stories and generate_flows.
"""

import json
import os
import re
from datetime import datetime, timezone

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(PROJECT, "data")
STORIES_PATH = os.path.join(DATA, "stories.json")

REQUIRED_FLOW_FIELDS = {
    "direction": "inflow",
    "amount_b": 5.0,
    "projected": "Capital flow tracked — direction forming",
    "pace_multiplier": 1.0,
    "confidence_pct": 65,
    "confidence_level": "medium",
    "asset_class": "equities",
}


def repair_capital_flow(story):
    """Ensure capital_flow dict has all required fields."""
    cf = story.get("capital_flow", {})
    if not cf or not isinstance(cf, dict):
        cf = {}
    
    repaired = False
    for field, default in REQUIRED_FLOW_FIELDS.items():
        if field not in cf or cf[field] is None:
            cf[field] = default
            repaired = True
    
    # Fix direction: normalize text to "inflow" or "outflow"
    direction = str(cf.get("direction", "")).lower()
    if direction not in ("inflow", "outflow"):
        # Try to derive from story text
        thesis = (story.get("thesis", "") + " " + story.get("capital_flow_implication", "")).lower()
        if any(w in thesis for w in ["long", "buy", "accumulate", "inflow", "bid"]):
            cf["direction"] = "inflow"
        elif any(w in thesis for w in ["short", "sell", "distribute", "outflow", "exit"]):
            cf["direction"] = "outflow"
        else:
            cf["direction"] = "inflow"  # default
        repaired = True
    
    # Fix confidence_pct: ensure it's a number
    if not isinstance(cf.get("confidence_pct"), (int, float)):
        # Try to extract from story
        conf = story.get("confidence", 65)
        if isinstance(conf, str):
            conf_map = {"high": 80, "medium": 65, "low": 50, "elevated": 75}
            cf["confidence_pct"] = conf_map.get(conf.lower(), 65)
        elif isinstance(conf, (int, float)):
            cf["confidence_pct"] = float(conf)
        else:
            cf["confidence_pct"] = 65
        repaired = True
    
    # Fix confidence_level
    pct = cf.get("confidence_pct", 65)
    if pct >= 80:
        cf["confidence_level"] = "high"
    elif pct >= 60:
        cf["confidence_level"] = "medium"
    else:
        cf["confidence_level"] = "low"
    
    # Fix claim — app.js renders cf.claim for card header
    if not cf.get("claim"):
        direction = cf.get("direction", "inflow")
        amt = cf.get("amount_b", 5.0)
        asset = cf.get("asset_class", "equities")
        arrow = "↑" if direction == "inflow" else "↓"
        cf["claim"] = f"${amt:.1f}B {arrow} {asset}"
        repaired = True
    
    # Fix confidence string for cf.confidence display
    if not cf.get("confidence"):
        level = cf.get("confidence_level", "medium")
        pct_val = cf.get("confidence_pct", 65)
        cf["confidence"] = f"{pct_val}%"
        repaired = True
    
    # Fix projected: ensure it's a non-empty string
    if not cf.get("projected") or cf["projected"] == "MISSING":
        # Derive from story content
        benefit = story.get("portfolio_implication", "") or story.get("benefit", "")
        event = story.get("reality", "") or story.get("event", "")
        headline = story.get("headline", "")
        cf["projected"] = (benefit or event or f"Flow implications from: {headline}")[:200]
        repaired = True
    
    # Fix pace_multiplier
    if not isinstance(cf.get("pace_multiplier"), (int, float)):
        cf["pace_multiplier"] = 1.0
        repaired = True
    
    # Fix asset_class
    if not cf.get("asset_class"):
        cf["asset_class"] = story.get("sector", "equities")
        repaired = True
    
    story["capital_flow"] = cf
    return repaired


def main():
    if not os.path.exists(STORIES_PATH):
        print(json.dumps({"ok": False, "error": "no stories.json"}))
        return
    
    with open(STORIES_PATH) as f:
        data = json.load(f)
    
    stories = data.get("stories", [])
    repaired_count = 0
    
    for story in stories:
        if repair_capital_flow(story):
            repaired_count += 1
    
    # Also repair the lead story
    if data.get("lead"):
        if repair_capital_flow(data["lead"]):
            repaired_count += 1
    
    # Write back
    with open(STORIES_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Sync to public/data/
    site_path = os.path.join(PROJECT, "site", "data", "stories.json")
    os.makedirs(os.path.dirname(site_path), exist_ok=True)
    with open(site_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(json.dumps({
        "ok": True,
        "total_stories": len(stories),
        "repaired": repaired_count,
    }, indent=2))


if __name__ == "__main__":
    main()
