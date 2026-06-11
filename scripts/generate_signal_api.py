#!/usr/bin/env python3
"""
Generate api/v1/signal.json — Triangulation signals from stories + flows + trades.
Cross-references stories, flows, and anchor positions to compute 0-100 signal scores.
Output: site/api/v1/signal.json
"""

import json, sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SITE_DIR = PROJECT_ROOT / "site"
OUT_DIR = SITE_DIR / "api" / "v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Anchor asset definitions (from app.js ANCHOR_ASSETS)
ANCHOR_MAP = {
    "SPX": "equities", "NVDA": "equities", "BRENT": "commodities",
    "DXY": "fx", "GOLD": "commodities", "BTC": "crypto", "10Y": "fixed_income",
    "ETH": "crypto", "SOL": "crypto", "XRP": "crypto",
    "BNB": "crypto", "ADA": "crypto", "DOGE": "crypto",
}


def main():
    now = datetime.now(timezone.utc).isoformat()

    # Load stories
    stories_path = DATA_DIR / "stories.json"
    stories = []
    if stories_path.exists():
        d = json.loads(stories_path.read_text())
        stories = d.get("stories", [])

    # Load flows
    flows_path = SITE_DIR / "data" / "flows.json"
    flows = []
    if flows_path.exists():
        d = json.loads(flows_path.read_text())
        flows = d.get("flows", [])

    # Build flow lookup by asset_class
    flow_by_asset = {}
    for f in flows:
        ac = f.get("asset_class", "")
        if ac:
            flow_by_asset.setdefault(ac, []).append(f)

    # Compute triangulation signals for each story
    signals = []
    for s in stories:
        cf = s.get("capital_flow", {})
        ac = cf.get("asset_class", "equities")
        direction = cf.get("direction", "inflow")
        amount = cf.get("amount_b") or 0  # None → 0 guard
        pace = cf.get("pace_multiplier", 1.0)
        cs = s.get("contradiction_score", 50)

        # FLOW ALIGNMENT (max 50)
        flow_score = 0
        if amount >= 5:
            flow_score += 20
        elif amount >= 3:
            flow_score += 15
        elif amount >= 1:
            flow_score += 10
        else:
            flow_score += 5

        if pace >= 3.0:
            flow_score += 15
        elif pace >= 2.5:
            flow_score += 12
        elif pace >= 2.0:
            flow_score += 10
        elif pace >= 1.5:
            flow_score += 7
        else:
            flow_score += 4

        pos = cf.get("positioning", "hedging")
        if pos == "accumulating":
            flow_score += 10
        elif pos == "distributing":
            flow_score += 8
        else:
            flow_score += 5
        flow_score = min(50, flow_score)

        # CONTRADICTION (max 30)
        contra_score = 0
        if cs >= 70:
            contra_score = 30
        elif cs >= 60:
            contra_score = 22
        elif cs >= 50:
            contra_score = 15
        else:
            contra_score = 8

        # EVENT STRENGTH (max 20)
        event_score = 10
        if s.get("they_say") and s.get("reality"):
            event_score += 5
        if s.get("extremum"):
            event_score += 5
        event_score = min(20, event_score)

        total = flow_score + contra_score + event_score

        if total >= 85:
            tier = "MAX CONVICTION"
        elif total >= 70:
            tier = "HIGH CONVICTION"
        elif total >= 55:
            tier = "MODERATE"
        else:
            tier = "WATCH"

        signals.append({
            "story_id": s.get("story_id", ""),
            "headline": s.get("headline", "")[:100],
            "score": total,
            "tier": tier,
            "flow_alignment": flow_score,
            "contradiction": contra_score,
            "event_strength": event_score,
            "asset_class": ac,
            "direction": direction,
        })

    # Sort by score descending
    signals.sort(key=lambda x: x["score"], reverse=True)

    output = {
        "generated_at": now,
        "total_signals": len(signals),
        "aggregate_score": round(sum(s["score"] for s in signals) / max(len(signals), 1)),
        "signals": signals[:15],  # Top 15
    }

    out_path = OUT_DIR / "signal.json"
    
    # ── v23.9: Inject Asymmetry Scores from market data ──
    market_path = PROJECT_ROOT / "data" / "market_prices.json"
    if market_path.exists():
        try:
            market_data = json.loads(market_path.read_text())
            asym_scores = market_data.get("asymmetry_scores", {})
            high_asym = [v for v in asym_scores.values() if v.get("asymmetry_score", 0) >= 60]
            if high_asym:
                output["asymmetry"] = {
                    "high_count": len(high_asym),
                    "top_scores": sorted(high_asym, key=lambda x: x.get("asymmetry_score", 0), reverse=True)[:5],
                    "aggregate_asymmetry": round(sum(v.get("asymmetry_score", 0) for v in high_asym) / len(high_asym)),
                }
        except Exception as e:
            pass
    
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"✓ signal.json: {len(signals[:15])} signals, aggregate={output['aggregate_score']}")


if __name__ == "__main__":
    main()
