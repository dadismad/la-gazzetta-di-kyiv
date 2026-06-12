#!/usr/bin/env python3
"""One-time migration: backfill pace_multiplier for all existing stories
that still have the old default of 1.0. Uses the same derivation logic
as intel_to_stories.py v22.45."""

import json, re, sys

URGENCY_KEYWORDS = [
    "breaking", "urgent", "flash", "alert", "crash", "spike",
    "plunge", "surge", "rout", "panic", "soar", "tumble",
    "crisis", "emergency", "imminent", "warning", "red alert"
]

HORIZON_BASE = {
    "1-6h": 3.0, "6-24h": 2.2, "24-72h": 1.5,
    "1w+": 1.1, "structural": 0.8
}

ASSET_VELOCITY = {
    "crypto": 1.3, "defense": 1.2, "commodities": 1.1,
    "equities": 0.95, "fixed_income": 0.8, "fx": 0.9, "tech": 1.1
}

def derive_pace(story):
    """Derive pace from story content using same logic as intel_to_stories.py v22.45."""
    cf = story.get("capital_flow", {})
    headline = story.get("headline", "")
    bet = story.get("actionable_trade", "")
    thesis = story.get("thesis", "")
    text_combined = f"{headline} {bet} {thesis}".lower()
    
    urgency_hits = sum(1 for k in URGENCY_KEYWORDS if k in text_combined)
    horizon = story.get("horizon", "24-72h")
    horizon_base = HORIZON_BASE.get(horizon, 1.3)
    
    cs = story.get("contradiction_score", 50)
    contra_mult = 1.0 + (cs - 50) * 0.01 if cs > 50 else 1.0
    
    urgency_bonus = urgency_hits * 0.3
    asset_class = cf.get("asset_class", "equities")
    asset_velocity = ASSET_VELOCITY.get(asset_class, 1.0)
    
    pace = round((horizon_base + urgency_bonus) * contra_mult * asset_velocity, 1)
    return max(0.5, min(5.0, pace))

def main():
    path = "data/stories.json"
    d = json.load(open(path))
    stories = d.get("stories", [])
    updated = 0
    for s in stories:
        cf = s.setdefault("capital_flow", {})
        old_pace = cf.get("pace_multiplier", 1.0)
        if old_pace == 1.0:
            new_pace = derive_pace(s)
            if new_pace != 1.0:
                cf["pace_multiplier"] = new_pace
                updated += 1
                print(f"  {s['headline'][:45]:45s} pace: 1.0 → {new_pace}")
    
    json.dump(d, open(path, "w"), indent=2, ensure_ascii=False)
    print(f"\nUpdated {updated}/{len(stories)} stories with derived pace values")
    return 0

if __name__ == "__main__":
    sys.exit(main())
