#!/usr/bin/env python3
"""decay_stories.py — Apply freshness decay to stories in stories.json.

Downgrades freshness labels based on age:
  breaking (< 2h) → new (2-6h) → active (6-24h) → developing (24-72h) → background (>72h)

Rotates the lead story to the freshest high-contradiction story.
Archives stories older than 7 days to stories_archive.json.

Run as part of pipeline_chain.sh BEFORE generate_flows.py.
"""

import json
import os
from datetime import datetime, timezone, timedelta

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(PROJECT, "data")
STORIES_PATH = os.path.join(DATA, "stories.json")
ARCHIVE_PATH = os.path.join(DATA, "stories_archive.json")

FRESHNESS_TIERS = {
    "breaking": {"max_age_h": 2, "label": "Breaking", "css_class": "freshness-breaking"},
    "new": {"max_age_h": 6, "label": "New", "css_class": "freshness-new"},
    "active": {"max_age_h": 24, "label": "Active", "css_class": "freshness-active"},
    "developing": {"max_age_h": 72, "label": "Developing", "css_class": "freshness-developing"},
    "background": {"max_age_h": 168, "label": "Background", "css_class": "freshness-background"},
}

FRESHNESS_ORDER = ["breaking", "new", "active", "developing", "background"]


def get_age_hours(story):
    """Get story age in hours from generated_at."""
    gen = story.get("generated_at", "")
    if not gen:
        return 999  # Unknown age → background

    try:
        gen_dt = datetime.fromisoformat(gen.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return (now - gen_dt).total_seconds() / 3600
    except (ValueError, TypeError):
        return 999


def compute_freshness(age_h):
    """Determine freshness tier from age in hours."""
    if age_h < 2:
        return "breaking"
    elif age_h < 6:
        return "new"
    elif age_h < 24:
        return "active"
    elif age_h < 72:
        return "developing"
    else:
        return "background"


def freshness_score(tier):
    """Numerical score for sorting (higher = fresher)."""
    return {"breaking": 100, "new": 75, "active": 50, "developing": 25, "background": 0}.get(tier, 0)


def pick_lead(stories):
    """Pick the best lead story: freshest high-contradiction story."""
    if not stories:
        return None

    # Score each story: freshness * 2 + contradiction_score
    scored = []
    for s in stories:
        age_h = get_age_hours(s)
        tier = compute_freshness(age_h)
        f_score = freshness_score(tier)
        c_score = s.get("contradiction_score", 50)
        total = f_score * 2 + c_score
        scored.append((total, s))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1] if scored else None


def main():
    if not os.path.exists(STORIES_PATH):
        print(json.dumps({"ok": False, "error": "no stories.json"}))
        return

    with open(STORIES_PATH) as f:
        data = json.load(f)

    stories = data.get("stories", [])
    if not stories:
        print(json.dumps({"ok": True, "decayed": 0, "message": "no stories to decay"}))
        return

    now = datetime.now(timezone.utc)

    # Archive stories older than 7 days
    archive = []
    if os.path.exists(ARCHIVE_PATH):
        with open(ARCHIVE_PATH) as f:
            archive = json.load(f)

    active_stories = []
    changes = {"decayed": 0, "archived": 0, "lead_changed": False, "freshness_updates": []}

    for story in stories:
        age_h = get_age_hours(story)
        old_freshness = story.get("freshness", "new")
        new_freshness = compute_freshness(age_h)

        if age_h > 168:  # 7 days → archive
            archive.append(story)
            changes["archived"] += 1
            continue

        # Update freshness if degraded
        if FRESHNESS_ORDER.index(new_freshness) > FRESHNESS_ORDER.index(old_freshness):
            story["freshness"] = new_freshness
            changes["decayed"] += 1
            changes["freshness_updates"].append({
                "story_id": story.get("story_id", "?")[:40],
                "from": old_freshness,
                "to": new_freshness,
            })
        elif "freshness" not in story:
            story["freshness"] = new_freshness

        # Update generated_at if missing
        if not story.get("generated_at"):
            story["generated_at"] = now.isoformat()

        active_stories.append(story)

    # Rotate lead story
    old_lead_id = data.get("lead", {}).get("story_id", "")
    new_lead = pick_lead(active_stories)
    if new_lead and new_lead.get("story_id") != old_lead_id:
        # Remove new lead from stories list, make it the lead
        active_stories = [s for s in active_stories if s.get("story_id") != new_lead.get("story_id")]
        # Old lead becomes a regular story
        if data.get("lead") and data["lead"].get("story_id"):
            old_lead = data["lead"]
            old_lead["freshness"] = compute_freshness(get_age_hours(old_lead))
            active_stories.insert(0, old_lead)
        data["lead"] = new_lead
        changes["lead_changed"] = True

    data["stories"] = active_stories
    data["generated_at"] = now.isoformat()

    # Write back
    with open(STORIES_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Sync to public/data/
    site_path = os.path.join(PROJECT, "site", "data", "stories.json")
    os.makedirs(os.path.dirname(site_path), exist_ok=True)
    with open(site_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Save archive if any archived
    if changes["archived"] > 0:
        with open(ARCHIVE_PATH, "w") as f:
            json.dump(archive, f, indent=2, ensure_ascii=False)

    print(json.dumps({
        "ok": True,
        "stories_active": len(active_stories),
        "archived": changes["archived"],
        "decayed": changes["decayed"],
        "lead_changed": changes["lead_changed"],
        "freshness_updates": changes["freshness_updates"],
    }, indent=2))


if __name__ == "__main__":
    main()
