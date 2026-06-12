#!/usr/bin/env python3
"""
build_related_links.py — Auto-interlinking engine for Gazzetta di Kyiv

Generates related_stories and related_flows for each story based on:
- Shared entity_tags, sectors, paradigms (stories)
- Shared asset_class, direction (flows)

Output: writes related_stories and related_flows directly into stories.json
"""

import json
import os
import sys
from collections import defaultdict
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
STORIES_PATH = PROJECT / "site" / "data" / "stories.json"
FLOWS_PATH = PROJECT / "site" / "data" / "flows.json"


def load_json(path):
    if not path.exists():
        print(f"  ✗ {path.name} not found", file=sys.stderr)
        return None
    with open(path) as f:
        return json.load(f)


def story_keywords(story):
    """Extract keyword set from a story for matching."""
    kw = set()
    
    # Entity tags (dict of lists: assets, geographies, actors, instruments)
    entity_tags = story.get("entity_tags") or {}
    for tag_list in entity_tags.values():
        for tag in (tag_list or []):
            kw.add(tag.lower())
    
    # Sector
    sector = story.get("sector", "").lower()
    if sector:
        kw.add(sector)
    
    # Paradigm / pillar
    paradigm = story.get("paradigm", "").lower()
    if paradigm:
        kw.add(paradigm)
    
    # Asset class from capital flow
    cf = story.get("capital_flow") or {}
    asset = cf.get("asset_class", "").lower()
    if asset:
        kw.add(asset)
    
    # Direction
    direction = cf.get("direction", "").lower()
    if direction:
        kw.add(direction)
    
    # Severity
    severity = (story.get("severity") or "").lower()
    if severity:
        kw.add(severity)
    
    return kw


def compute_related_stories(stories):
    """For each story, find top 3 related stories by keyword overlap."""
    # Build keyword index
    story_kw = {}
    for i, s in enumerate(stories):
        story_kw[i] = story_keywords(s)
    
    related = {}
    for i, s in enumerate(stories):
        sid = s.get("story_id", "")
        if not sid:
            continue
        
        scores = []
        my_kw = story_kw[i]
        
        for j, other in enumerate(stories):
            if i == j:
                continue
            other_sid = other.get("story_id", "")
            if not other_sid:
                continue
            
            overlap = len(my_kw & story_kw[j])
            if overlap > 0:
                scores.append({
                    "story_id": other_sid,
                    "headline": other.get("headline", ""),
                    "sector": other.get("sector", ""),
                    "score": overlap,
                    "shared_tags": sorted(list(my_kw & story_kw[j]))[:5]
                })
        
        # Sort by score descending, take top 3
        scores.sort(key=lambda x: x["score"], reverse=True)
        related[sid] = scores[:3]
    
    return related


def compute_related_flows(stories, flows_data):
    """For each story, find flows with matching asset_class."""
    flows = flows_data.get("flows", []) if flows_data else []
    
    related = {}
    for s in stories:
        sid = s.get("story_id", "")
        if not sid:
            continue
        
        cf = s.get("capital_flow") or {}
        asset = cf.get("asset_class", "").lower()
        direction = cf.get("direction", "").lower()
        
        matches = []
        for f in flows:
            f_asset = f.get("asset_class", "").lower()
            f_dir = f.get("direction", "").lower()
            
            # Match: same asset class OR same direction with different asset (divergence signal)
            score = 0
            if asset and f_asset == asset:
                score += 2
            if direction and f_dir == direction:
                score += 1
            
            if score > 0:
                matches.append({
                    "flow_id": f.get("id", ""),
                    "asset_class": f.get("asset_class", ""),
                    "direction": f.get("direction", ""),
                    "amount_formatted": f.get("amount_formatted", ""),
                    "confidence_pct": f.get("confidence_pct", 0),
                    "pace_multiplier": f.get("pace_multiplier", 1.0),
                    "score": score
                })
        
        matches.sort(key=lambda x: x["score"], reverse=True)
        related[sid] = matches[:3]
    
    return related


def main():
    print("[build_related_links] Building interlinking index...")
    
    stories_data = load_json(STORIES_PATH)
    flows_data = load_json(FLOWS_PATH)
    
    if not stories_data:
        print("  ✗ Cannot proceed without stories.json")
        sys.exit(1)
    
    stories = stories_data.get("stories", [])
    if stories_data.get("lead"):
        stories = [stories_data["lead"]] + stories
    
    print(f"  Stories: {len(stories)}")
    
    # Compute related links
    related_stories = compute_related_stories(stories)
    related_flows = compute_related_flows(stories, flows_data)
    
    # Inject into story data
    enriched = 0
    for s in stories:
        sid = s.get("story_id", "")
        if sid in related_stories:
            s["related_stories"] = related_stories[sid]
            enriched += 1
        if sid in related_flows:
            s["related_flows"] = related_flows[sid]
    
    # Write back
    # Preserve lead structure
    if stories_data.get("lead"):
        lead_id = stories_data["lead"].get("story_id", "")
        for s in stories:
            if s.get("story_id") == lead_id:
                stories_data["lead"] = s
                break
        stories_data["stories"] = [s for s in stories if s.get("story_id") != lead_id]
    else:
        stories_data["stories"] = stories
    
    with open(STORIES_PATH, "w") as f:
        json.dump(stories_data, f, ensure_ascii=False, indent=2)
    
    # Also sync to data/ for pipeline
    data_stories = PROJECT / "data" / "stories.json"
    with open(data_stories, "w") as f:
        json.dump(stories_data, f, ensure_ascii=False, indent=2)
    
    total_links = sum(len(v) for v in related_stories.values())
    total_flow_links = sum(len(v) for v in related_flows.values())
    print(f"  ✓ {enriched} stories enriched")
    print(f"  ✓ {total_links} story→story links ({total_links//max(len(stories),1)} avg/story)")
    print(f"  ✓ {total_flow_links} story→flow links ({total_flow_links//max(len(stories),1)} avg/story)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
