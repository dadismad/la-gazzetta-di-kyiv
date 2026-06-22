#!/usr/bin/env python3
"""
La Gazzetta di Kyiv — Phase 3
Module: classify_stories.py
Purpose: Re-assign narrative_id to all stories after synthesis merges.
         Uses keyword matching from narratives.json descriptions + tickers.
Runs: between synthesis and calc_capital in governor loop.
"""

import os, sys, json, re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT / "public" / "data"
STORIES_FILE = DATA_DIR / "stories.json"
NARRATIVES_FILE = PROJECT / "data" / "narratives.json"

# Keyword boosters from the proven backfill — catches stories missed by ticker matching
SEED_KEYWORDS = {
    "ai_chips": ["nvidia", "tsmc", "semiconductor", "chip", "gpu", "h100", "b200", "amd", "intel", "taiwan semiconductor"],
    "crypto_reserve": ["bitcoin", "ethereum", "btc", "eth", "stablecoin", "defi", "crypto", "coinbase", "digital asset"],
    "rate_cycle": ["fed", "fomc", "rate cut", "rate hike", "powell", "treasury yield", "bond yield", "interest rate", "central bank", "inflation", "world bank", "global growth", "ppi", "wholesale price"],
    "commodity_supercycle": ["crude oil", "copper", "corn futures", "soybean", "wheat futures", "gold price", "silver price", "oil price", "oil market", "commodity price", "brent", "wti crude", "natural gas"],
    "space_economy": ["spacex", "nasa", "blue origin", "rocket", "satellite", "orbital", "lunar", "mars mission", "starship"],
    "gene_editing": ["biopharma", "biotech", "crispr", "fda approval", "gene therapy", "clinical trial", "pharma", "drug"],
    "china_ascent": ["china etf", "chinese market", "hong kong", "shanghai", "beijing", "xi jinping", "chinese economy", "china stock"],
    "dollar_decline": ["dollar index", "usd weakness", "fed reserve", "currency war", "dedollarization", "brics currency", "gold sinks", "gold rally", "gold hits"],
    "energy_sovereignty": ["nuclear", "uranium", "energy independence", "power grid", "renewable energy", "iran", "opec", "hormuz", "persian gulf", "gulf shock", "oil export", "gas price", "solar", "coal", "russia ukraine", "samara refinery", "eia", "oil tanker", "crude export"],
    "deglobalization": ["supply chain", "tariff", "trade war", "protectionist", "reshoring", "nearshoring", "merger", "acquisition"],
    "tech_convergence": ["artificial intelligence", "cloud computing", "enterprise software", "ai model", "machine learning", "openai", "anthropic", "data center", "aws", "google", "rivian", "amazon"],
    "wealthy_sports": ["sports franchise", "premier league", "nba team", "sovereign fund", "private equity sports", "frasers", "soccer club"],
}


def fix_ownership(path_str: str):
    if sys.platform != "linux":
        return
    try:
        import pwd, grp
        uid = pwd.getpwnam("gazzetta").pw_uid
        gid = grp.getgrnam("gazzetta").gr_gid
        os.chown(path_str, uid, gid)
    except (KeyError, OSError):
        pass


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_classifier(narratives: dict) -> dict:
    """Build per-narrative regex patterns from display_name + tickers."""
    matchers = {}
    for nid, meta in narratives.items():
        terms = [meta["display_name"].lower()]
        for t in meta.get("tickers", []):
            terms.append(t.lower().replace("=f", "").replace("-usd", "").replace("^", ""))
        pattern = r'\b(' + '|'.join(map(re.escape, terms)) + r')\b'
        matchers[nid] = re.compile(pattern, re.IGNORECASE)
    return matchers


def classify_story(story: dict, matchers: dict, keywords: dict) -> str:
    """Assign narrative_id using ticker/name matching + seed keywords."""
    headline = story.get("headline", "").lower()
    they_say = story.get("they_say", "").lower()
    content = headline + " " + they_say

    # 1. Try ticker/display_name regex matching
    best_nid = None
    best_len = 0
    for nid, regex in matchers.items():
        matches = regex.findall(content)
        if matches and len(matches) > best_len:
            best_nid = nid
            best_len = len(matches)

    if best_nid:
        return best_nid

    # 2. Try seed keyword matching for emergent narratives
    for nid, kws in keywords.items():
        if any(kw in content for kw in kws):
            return nid

    # 3. Fallback: use container/pillar only if it's a canonical narrative_id
    legacy = story.get("pillar") or story.get("container")
    CANONICAL = {
        "dollar_decline", "energy_sovereignty", "deglobalization",
        "china_ascent", "space_economy", "gene_editing",
        "tech_convergence", "wealthy_sports", "ai_chips",
        "crypto_reserve", "rate_cycle", "commodity_supercycle",
    }
    if legacy and legacy in CANONICAL:
        return legacy

    return "unassigned"


def main():
    print("[classify] Re-assigning narrative_ids...")
    stories_data = load_json(STORIES_FILE)
    narratives_data = load_json(NARRATIVES_FILE)

    narratives = narratives_data.get("narratives", {})
    matchers = build_classifier(narratives)

    all_stories = stories_data.get("all_stories", [])
    classified = 0
    changed = 0

    for story in all_stories:
        # DeepSeek multi-vector bypass: preserve LLM-assigned routing
        if story.get("narrative_weights"):
            # Ensure containers list exists (rebuild from weights at 0.40 threshold)
            if "containers" not in story:
                story["containers"] = [
                    nid for nid, score in story["narrative_weights"].items()
                    if score >= 0.40
                ]
            classified += 1
            continue

        old_nid = story.get("narrative_id", "")
        new_nid = classify_story(story, matchers, SEED_KEYWORDS)

        # Reclassify if: no narrative_id, unassigned, or not in current taxonomy
        if not old_nid or old_nid == "unassigned" or old_nid not in narratives:
            story["narrative_id"] = new_nid
            story["narrative_confidence"] = 0.7 if new_nid != "unassigned" else 0.0
            changed += 1
        # Also reclassify legacy tags that aren't in the 12-narrative taxonomy
        elif old_nid in ("china_ascendancy", "multi_pillar", "eu_fragmentation",
                         "abundance_tech", "neutral", "blockchain_agentic"):
            story["narrative_id"] = new_nid
            story["narrative_confidence"] = 0.5
            changed += 1
        classified += 1

    stories_data["all_stories"] = all_stories

    # Rebuild tags_index from current all_stories (eliminates orphans)
    tags_index = {}
    for s in all_stories:
        sid = str(s.get("story_id", ""))
        # Index by containers list (multi-vector) or narrative_id (legacy)
        index_ids = s.get("containers") or [s.get("narrative_id", "")]
        for nid in index_ids:
            if nid and nid != "unassigned":
                tags_index.setdefault(nid, [])
                if sid and sid not in tags_index[nid]:
                    tags_index[nid].append(sid)
        for tag in (s.get("entity_tags") or []):
            tags_index.setdefault(tag, [])
            if sid and sid not in tags_index[tag]:
                tags_index[tag].append(sid)
    stories_data["tags_index"] = tags_index

    tmp_path = STORIES_FILE.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(stories_data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, STORIES_FILE)

    fix_ownership(str(STORIES_FILE))

    print(f"[classify] {classified} stories checked, {changed} re-classified.")


if __name__ == "__main__":
    main()
