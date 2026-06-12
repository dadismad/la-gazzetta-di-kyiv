#!/usr/bin/env python3
"""enrich_stories.py — T2 micro-update runner for Gazzetta Living Stories.

Zero-LLM-cost enrichment pass. Runs every 2 hours.
- Tags stale stories (no updates > 48h)
- Resolves stories dormant > 7 days
- Generates living_stories.json for frontend
- Updates story_registry.json status fields

Evolution scoring: Jaccard similarity on actors/geography/pillar
  score = actor_match * 0.4 + geography_match * 0.3 + pillar_match * 0.2 + recency * 0.1
  >= 0.6: evidence update
  >= 0.85: sub-thread spawn
  < 0.6 for 48h: mark as stable
  7 days no updates: resolve/archive
"""

import json
import os
from datetime import datetime, timezone, timedelta

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(PROJECT, "data")
REGISTRY_PATH = os.path.join(DATA, "story_registry.json")
PUBLISH_DIR = os.path.join(DATA, "publish")
LIVING_STORIES_PATH = os.path.join(PUBLISH_DIR, "living_stories.json")

STALE_THRESHOLD_H = 48   # No updates in 48h → stable
RESOLVE_THRESHOLD_H = 168  # No updates in 7 days → resolve


def load_registry():
    if not os.path.exists(REGISTRY_PATH):
        return None
    with open(REGISTRY_PATH) as f:
        return json.load(f)


def save_registry(registry):
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def parse_ts(ts_str):
    """Parse ISO timestamp string to datetime."""
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def jaccard(set_a, set_b):
    """Jaccard similarity between two sets."""
    if not set_a or not set_b:
        return 0.0
    a = set(str(x).lower() for x in set_a)
    b = set(str(x).lower() for x in set_b)
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union > 0 else 0.0


def compute_recency(last_updated):
    """Recency score: 1.0 if updated < 2h ago, decaying to 0 at 48h."""
    if not last_updated:
        return 0.0
    age_h = (datetime.now(timezone.utc) - last_updated).total_seconds() / 3600
    if age_h < 0:
        return 1.0
    if age_h < 2:
        return 1.0
    if age_h > 48:
        return 0.0
    return max(0.0, 1.0 - (age_h - 2) / 46)


def compute_evolution_score(story_a, story_b):
    """Compute Jaccard-based evolution score between two stories."""
    actor_match = jaccard(story_a.get("actors", []), story_b.get("actors", []))
    geo_match = jaccard(story_a.get("geography", []), story_b.get("geography", []))
    pillar_match = 1.0 if story_a.get("paradigm_pillar") == story_b.get("paradigm_pillar") else 0.0
    recency = compute_recency(parse_ts(story_a.get("last_updated")))
    score = actor_match * 0.4 + geo_match * 0.3 + pillar_match * 0.2 + recency * 0.1
    return round(score, 4)


def check_status_transitions(story, now):
    """Check if a story's status should transition based on age."""
    last_updated = parse_ts(story.get("last_updated"))
    current_status = story.get("status", "new")

    if not last_updated:
        return None, None

    age_h = (now - last_updated).total_seconds() / 3600

    # Status transition logic (check highest threshold first)
    transitions = {
        "new": [
            (48, "stable"),      # new → stable after 48h (check first!)
            (2, "active"),       # new → active after 2h
        ],
        "active": [
            (48, "stable"),      # active → stable after 48h
        ],
        "evolving": [
            (48, "stable"),      # evolving → stable after 48h no updates
        ],
        "stable": [
            (168, "background"), # stable → background after 7 days
        ],
    }

    for threshold, target in transitions.get(current_status, []):
        if age_h > threshold:
            return target, f"Age {age_h:.0f}h exceeds {threshold}h threshold for {current_status} → {target}"

    return None, None


def build_living_stories(registry):
    """Build living_stories.json payload for frontend."""
    stories = registry.get("stories", {})
    active = []
    for sid, story in stories.items():
        status = story.get("status", "new")
        if status in ("resolved", "archived", "background"):
            continue
        active.append({
            "story_id": sid,
            "headline": story.get("current_headline", story.get("original_headline", "")),
            "status": status,
            "update_count": story.get("update_count", 0),
            "last_updated": story.get("last_updated", ""),
            "thread_ids": story.get("thread_ids", []),
            "evolution_score_current": story.get("evolution_score_current", 0.0),
            "confidence": story.get("confidence", 0.0),
            "sector": story.get("sector", ""),
            "paradigm_pillar": story.get("paradigm_pillar", ""),
            "actors": story.get("actors", []),
            "geography": story.get("geography", []),
            "asset_claim": story.get("asset_claim", {}),
        })

    # Sort: evolving first, then by update_count desc
    active.sort(key=lambda s: (
        0 if s["status"] == "evolving" else 1,
        -s["update_count"]
    ))

    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "active_count": len(active),
        "stories": active,
    }


def main():
    now = datetime.now(timezone.utc)
    errors = []
    stories_updated = 0
    sub_threads_spawned = 0
    new_stories_created = 0
    stories_tagged_stale = 0

    registry = load_registry()
    if not registry:
        print(json.dumps({"ok": False, "error": "story_registry.json not found"}))
        return

    stories = registry.get("stories", {})
    if not stories:
        print(json.dumps({"ok": True, "stories_updated": 0, "sub_threads_spawned": 0,
                          "new_stories_created": 0, "stories_tagged_stale": 0, "errors": []}))
        return

    # Phase 1: Check status transitions (staleness, resolution)
    for sid, story in stories.items():
        old_status = story.get("status", "new")
        new_status, reason = check_status_transitions(story, now)

        if new_status and new_status != old_status:
            story["status"] = new_status
            story["status_reason"] = reason
            # Do NOT reset last_updated — that tracks actual content changes
            stories_updated += 1
            if new_status in ("stable", "background"):
                stories_tagged_stale += 1

    # Phase 2: Cross-story similarity checks (lightweight — only between evolving stories)
    evolving = {sid: s for sid, s in stories.items() if s.get("status") == "evolving"}
    active_stories = {sid: s for sid, s in stories.items()
                      if s.get("status") in ("new", "active", "evolving")}

    for sid_a, story_a in evolving.items():
        for sid_b, story_b in active_stories.items():
            if sid_a >= sid_b:
                continue  # avoid duplicate pairs
            score = compute_evolution_score(story_a, story_b)
            # Record peak scores
            if score > story_a.get("evolution_score_peak", 0):
                story_a["evolution_score_peak"] = round(score, 4)
            if score > story_b.get("evolution_score_peak", 0):
                story_b["evolution_score_peak"] = round(score, 4)
            story_a["evolution_score_current"] = round(score, 4)
            story_b["evolution_score_current"] = round(score, 4)

    # Update registry metadata
    registry["updated_at"] = now.isoformat()
    active_count = sum(1 for s in stories.values()
                       if s.get("status") not in ("resolved", "archived", "background"))
    registry["active_count"] = active_count
    registry["story_count"] = len(stories)

    # Save registry
    save_registry(registry)

    # Build and save living_stories.json
    living = build_living_stories(registry)
    os.makedirs(PUBLISH_DIR, exist_ok=True)
    with open(LIVING_STORIES_PATH, "w") as f:
        json.dump(living, f, indent=2, ensure_ascii=False)

    # Also copy to public/data for deploy
    site_living_path = os.path.join(PROJECT, "site", "data", "living_stories.json")
    os.makedirs(os.path.dirname(site_living_path), exist_ok=True)
    with open(site_living_path, "w") as f:
        json.dump(living, f, indent=2, ensure_ascii=False)

    result = {
        "ok": True,
        "stories_updated": stories_updated,
        "sub_threads_spawned": sub_threads_spawned,
        "new_stories_created": new_stories_created,
        "stories_tagged_stale": stories_tagged_stale,
        "active_count": active_count,
        "errors": errors,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
