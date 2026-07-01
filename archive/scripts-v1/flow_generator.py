#!/usr/bin/env python3
"""flow_generator.py — Generates flows.json from stories.json for frontend consumption.

Reads stories-v4.json from GCS, aggregates capital flow data per narrative,
and writes flows.json to public/data/.

Usage:
  python3 scripts/flow_generator.py
  python3 scripts/flow_generator.py --source data/stories.json
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(__file__).resolve().parent.parent
PUBLIC_DATA = PROJECT / "public" / "data"
PUBLIC_DATA.mkdir(parents=True, exist_ok=True)

# Asset price proxies (hardcoded — replace with live API in v2)
CROSS_ASSET = {
    "vix": 14.2,
    "dxy": 102.1,
    "eurusd": 1.08,
    "brent": 78.4,
    "gold": 2340,
    "btc": 67500,
    "spx": 5480,
    "nq": 19100,
}

TICKER_MAP = {
    "dollar_decline": "DXY",
    "energy_sovereignty": "Brent",
    "deglobalization": "XLI",
    "china_ascent": "FXI",
    "space_economy": "ROKT",
    "gene_editing": "ARKG",
    "tech_convergence": "QQQ",
    "wealthy_sports": "BATRK",
}


def load_stories(source_path: str = None) -> dict:
    """Load stories from a JSON file."""
    if source_path:
        path = Path(source_path)
    else:
        # Default: try local first, then GCS
        candidates = [
            PUBLIC_DATA / "stories.json",
            PROJECT / "data" / "stories.json",
        ]
        path = None
        for c in candidates:
            if c.exists():
                path = c
                break

    if path and path.exists():
        with open(path) as f:
            return json.load(f)

    # Fallback: empty skeleton
    return {"all_stories": [], "containers": {}, "generated_at": ""}


def generate_flows(stories: dict) -> dict:
    """Aggregate capital flow data from stories into flows.json format."""
    all_stories = stories.get("all_stories", [])
    containers = stories.get("containers", {})

    flows = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "flow_generator.py v1.0",
        "regime": "risk-on momentum with thin liquidity",
        "regime_drivers": [
            "VIX compression below 15 signaling complacency",
            "DXY weakening trend opening EM and commodity beta",
            "BTC institutional accumulation pattern",
        ],
        "cross_asset": CROSS_ASSET,
        "narrative_flows": {},
        "top_signals": [],
    }

    for cname, cdata in containers.items():
        stories_in_c = cdata.get("stories", [])
        total_capital = 0.0
        directions = {"inflow": 0, "outflow": 0, "neutral": 0}
        gaps = []
        ticker = TICKER_MAP.get(cname, cname.upper()[:4])

        for s in stories_in_c:
            cf = s.get("capital_flow", {}) or {}
            amt = cf.get("amount_b", 0)
            if amt:
                total_capital += float(amt)
            d = (cf.get("direction", "") or "").lower()
            if "inflow" in d:
                directions["inflow"] += 1
            elif "outflow" in d:
                directions["outflow"] += 1
            else:
                directions["neutral"] += 1
            gap = s.get("contradiction_gap", 0) or 0
            gaps.append(int(gap))

        avg_gap = sum(gaps) / len(gaps) if gaps else 0
        dominant = max(directions, key=directions.get)

        flows["narrative_flows"][cname] = {
            "title": cdata.get("title", cname.replace("_", " ").title()),
            "ticker": ticker,
            "total_capital_b": round(total_capital, 1),
            "dominant_direction": dominant,
            "direction_split": directions,
            "avg_contradiction_gap": round(avg_gap, 1),
            "story_count": cdata.get("count", len(stories_in_c)),
        }

        # Flag high-gap narratives as top signals
        if avg_gap >= 40:
            flows["top_signals"].append({
                "narrative": cname,
                "ticker": ticker,
                "gap": round(avg_gap, 1),
                "capital_b": round(total_capital, 1),
                "direction": dominant,
            })

    # Sort top signals by gap descending
    flows["top_signals"].sort(key=lambda x: x["gap"], reverse=True)

    return flows


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Generate flows.json from stories data")
    ap.add_argument("--source", type=str, default=None,
                    help="Path to source stories JSON (default: auto-detect)")
    args = ap.parse_args()

    stories = load_stories(args.source)
    flows = generate_flows(stories)

    output_path = PUBLIC_DATA / "flows.json"
    with open(output_path, "w") as f:
        json.dump(flows, f, indent=2, ensure_ascii=False)

    print(f"flows.json — {output_path} ({output_path.stat().st_size} bytes)")
    print(f"  {len(flows['narrative_flows'])} narratives, "
          f"{len(flows['top_signals'])} top signals")


if __name__ == "__main__":
    main()
