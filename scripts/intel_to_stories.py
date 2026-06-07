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
    """Convert a telegram intel story into Gazzetta story format matching pipeline expectations."""
    headline = intel_story.get("title", intel_story.get("headline", "Untitled"))
    story_id = intel_story.get("story_id") or generate_story_id(headline, pillar)
    now = datetime.now(timezone.utc).isoformat()
    
    bet_raw = intel_story.get("bet", {})
    bet_text = bet_raw if isinstance(bet_raw, str) else bet_raw.get("direction", "")
    benefit_raw = intel_story.get("benefit", {})
    if isinstance(benefit_raw, str):
        benefit_text = benefit_raw
    else:
        benefit_text = benefit_raw.get("Bet&Benefit", "") or benefit_raw.get("Gazzetta di Kyiv", "") or json.dumps(benefit_raw)
    event_text = intel_story.get("event", "")
    
    # Determine direction from bet text
    is_long = "LONG" in bet_text.upper()
    direction = "inflow" if is_long else "outflow"
    
    # Extract amount: search for $XB patterns in bet/event
    amount_b = 5.0  # default
    import re
    amounts = re.findall(r'\$(\d+\.?\d*)\s*[Bb]', bet_text + " " + event_text)
    if amounts:
        amount_b = float(amounts[0])
    
    # Build projected: use benefit or event, truncate at word boundary (never mid-word)
    raw_proj = benefit_text or event_text
    if raw_proj:
        if len(raw_proj) > 200:
            cut = raw_proj[:200].rstrip()
            last_space = cut.rfind(' ')
            projected = (cut[:last_space] if last_space > 150 else cut) + '…'
        else:
            projected = raw_proj
    else:
        projected = f"Capital repositioning on {headline[:80]}"
    
    # Confidence tier
    conf = intel_story.get("confidence", 75)
    if conf >= 80:
        confidence_level = "high"
    elif conf >= 60:
        confidence_level = "medium"
    else:
        confidence_level = "low"
    
    # Contradiction score: use intel value if provided, otherwise compute from content
    raw_contradiction = intel_story.get("contradiction_score")
    if raw_contradiction is not None and raw_contradiction != 55:  # reject the stale default
        contradiction_score = raw_contradiction
    else:
        # Compute heuristic contradiction score from they_say/reality divergence
        they_say = (intel_story.get("consensus_narrative", "") or "").lower()
        reality = (intel_story.get("contradiction", "") or "").lower()
        combined = they_say + " " + reality
        contradiction_keywords = [
            "but", "however", "despite", "unexpected", "surprising", "contrary",
            "diverging", "contradiction", "paradox", "irony", "ironically",
            "yet", "nonetheless", "nevertheless", "whereas", "while",
            "in reality", "actually", "the truth", "the reality",
        ]
        kw_count = sum(1 for k in contradiction_keywords if k in combined)
        # Base score 45-65 range based on keyword density, length-adjusted
        base = 45 + min(kw_count * 5, 20)
        # Add variance from content length (longer content = more likely real analysis)
        length_bonus = min(len(combined) // 200, 10)
        contradiction_score = min(base + length_bonus, 95)
    
    # Compute tier from contradiction score
    tier = "DEVELOPING" if contradiction_score >= 55 else "ALIGNED"
    
    # Positioning from bet
    positioning = bet_text[:300]
    
    # Asset class detection
    asset_class = "equities"
    text_lower = (bet_text + " " + event_text).lower()
    if any(w in text_lower for w in ["oil", "crude", "brent", "wti", "energy"]):
        asset_class = "commodities"
    elif any(w in text_lower for w in ["btc", "bitcoin", "crypto", "eth"]):
        asset_class = "crypto"
    elif any(w in text_lower for w in ["gold", "silver", "metal"]):
        asset_class = "commodities"
    elif any(w in text_lower for w in ["bond", "treasury", "yield", "tlt"]):
        asset_class = "fixed_income"
    elif any(w in text_lower for w in ["defense", "missile", "military"]):
        asset_class = "defense"

    return {
        "story_id": story_id,
        "headline": headline[:200],
        "sector": asset_class,
        "pillar": pillar,
        "paradigm_pillar": pillar,  # app.js reads paradigm_pillar for data-pillar attribute
        "paradigm_implications": [benefit_text[:200]] if benefit_text else [],
        "they_say": intel_story.get("consensus_narrative", ""),
        "reality": intel_story.get("contradiction", ""),
        "thesis": bet_text[:300],
        "actors": intel_story.get("actors", []),
        "horizon": intel_story.get("horizon", "24-72h"),
        "confidence": confidence_level,
        "tier": tier,
        "actionable_trade": bet_text[:300],
        "contradiction_score": contradiction_score,
        "invalidation_trigger": "Narrative reversal or event resolution",
        "portfolio_implication": benefit_text[:300],
        "capital_flow": {
            "direction": direction,
            "amount_b": amount_b,
            "asset_class": asset_class,
            "projected": projected,
            "pace_multiplier": 1.0,
            "confidence_pct": conf,
            "confidence_level": confidence_level,
        },
        "capital_flow_implication": bet_text[:300],
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

    # Support both "stories" (newer intel format) and "actionable_stories" (legacy)
    actionable = intel.get("stories") or intel.get("actionable_stories", [])
    if not actionable:
        print(json.dumps({"ok": True, "stories_added": 0, "reason": "no stories in intel", "intel_keys": list(intel.keys())[:10]}))
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
