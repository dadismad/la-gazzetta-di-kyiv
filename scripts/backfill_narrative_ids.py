#!/usr/bin/env python3
"""backfill_narrative_ids.py — Classify all 411 stories into narratives."""
import os, sys, json, shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from contradiction_synthesizer import assemble_story

SEED_KEYWORDS = {
    "ai_chips": ["nvidia", "tsmc", "semiconductor", "chip", "gpu", "tpu", "h100", "b200"],
    "crypto_reserve": ["bitcoin", "ethereum", "btc", "eth", "stablecoin", "defi", "crypto etf"],
    "rate_cycle": ["fed", "fomc", "rate cut", "rate hike", "powell", "treasury yield", "bond"],
    "commodity_supercycle": ["gold", "copper", "oil price", "crude", "commodity", "lithium", "rare earth"],
}

def main():
    data_path = Path(__file__).parent.parent / "data" / "stories.json"
    if not data_path.exists():
        print(f"[-] Error: {data_path} not found.")
        sys.exit(1)

    backup_path = data_path.with_suffix('.json.bak')
    shutil.copy(data_path, backup_path)
    print(f"[*] Backup saved to {backup_path}")

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_stories = data.get("all_stories", [])
    print(f"[*] Loaded {len(all_stories)} stories from production file.")

    try:
        CANONICAL_DEFAULTS = assemble_story((0, "", "", "", "", ""), {}, {})
        CANONICAL_FIELDS = set(CANONICAL_DEFAULTS.keys())
    except Exception as e:
        print(f"[-] Failed to extract dynamic schema: {e}")
        sys.exit(1)

    updated_stories = []
    for story in all_stories:
        hydrated_story = CANONICAL_DEFAULTS.copy()
        for key in CANONICAL_FIELDS:
            if key in story:
                hydrated_story[key] = story[key]

        narrative_id = "unassigned"
        headline_lower = story.get("headline", "").lower()

        for nid, keywords in SEED_KEYWORDS.items():
            if any(kw in headline_lower for kw in keywords):
                narrative_id = nid
                hydrated_story["narrative_confidence"] = 0.7
                break

        if narrative_id == "unassigned":
            legacy_tag = story.get("pillar") or story.get("container")
            narrative_id = legacy_tag if legacy_tag else "unassigned"
            hydrated_story["narrative_confidence"] = 0.5 if legacy_tag else 0.0

        hydrated_story["narrative_id"] = narrative_id
        hydrated_story["capital_at_stake_usd"] = hydrated_story.get("capital_volume_usd", 0)
        updated_stories.append(hydrated_story)

    # Rebuild containers
    for nid, meta in data.get("containers", {}).items():
        matched = [s for s in updated_stories if s.get("narrative_id") == nid]
        meta["count"] = len(matched)
        meta["stories"] = matched[:4]

    data["all_stories"] = updated_stories

    tmp_path = data_path.with_suffix('.json.tmp')
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, data_path)

    print(f"[+] Step 5a Complete: Backfilled {len(updated_stories)} items with {len(CANONICAL_FIELDS)} canonical fields.")
    # Print distribution
    from collections import Counter
    dist = Counter(s["narrative_id"] for s in updated_stories)
    for nid, count in dist.most_common():
        print(f"    {nid}: {count}")

if __name__ == "__main__":
    main()
