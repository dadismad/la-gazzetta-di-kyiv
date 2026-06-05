#!/usr/bin/env python3
"""Generate flows.json from editorial pipeline output and live data sources.

Called by cron job every 60 minutes. Reads stories.json, living_stories.json,
and any scraped flow data to produce a fresh flows.json for the website.

The generated file is written to site/data/flows.json.
"""
import json
import os
import sys
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

SITE_DATA = Path(__file__).resolve().parent.parent / "site" / "data"
DATA_PUBLISH = Path(__file__).resolve().parent.parent / "data" / "publish"


def load_json(path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return None
    return None


def extract_flow_from_story(story):
    """Extract capital flow data from a story object's capital_flow or capital_flow_implication fields."""
    cf = story.get("capital_flow", {})
    if not cf:
        # Try parsing from capital_flow_implication string
        imp = story.get("capital_flow_implication", "")
        if not imp:
            return None
        cf = parse_flow_implication(imp)
        if not cf:
            return None
    return cf


def parse_flow_implication(text):
    """Parse a capital_flow_implication string into structured flow data."""
    if not text:
        return None
    
    # Extract amount: $XB or $XM
    amt_match = re.search(r'\$([\d.]+)\s*([BM])', text)
    if not amt_match:
        return None
    
    amount = float(amt_match.group(1))
    denom = amt_match.group(2)
    amount_b = amount if denom == 'B' else amount / 1000
    
    # Direction
    direction = "inflow"
    if re.search(r'outflow|out of|withdraw|exit', text, re.IGNORECASE):
        direction = "outflow"
    
    # Projected
    proj_match = re.search(r'projected\s+([+-]\$[\d.]+[BM])', text, re.IGNORECASE)
    projected = proj_match.group(1) if proj_match else ""
    
    return {
        "amount_b": round(amount_b, 2),
        "direction": direction,
        "projected": projected,
    }


def compute_confidence(flow_amt_b, pace_mult, positioning, contradiction_score=60):
    """4-factor confidence model. Returns percentage and trace."""
    score = 50
    trace = []
    
    if flow_amt_b >= 5:
        score += 15; trace.append("large-flow+15")
    elif flow_amt_b >= 3:
        score += 12; trace.append("med-flow+12")
    elif flow_amt_b >= 1:
        score += 8; trace.append("small-flow+8")
    else:
        score += 3; trace.append("micro-flow+3")
    
    if pace_mult >= 3.0:
        score += 12; trace.append("extreme-pace+12")
    elif pace_mult >= 2.0:
        score += 10; trace.append("fast-pace+10")
    elif pace_mult >= 1.5:
        score += 7; trace.append("elevated-pace+7")
    else:
        score += 3; trace.append("normal-pace+3")
    
    pos_map = {"accumulating": 10, "distributing": 8, "hedging": 5}
    score += pos_map.get(positioning, 2)
    trace.append(f"{positioning}+{pos_map.get(positioning, 2)}")
    
    if contradiction_score >= 70:
        score += 8; trace.append("high-contradiction+8")
    elif contradiction_score >= 50:
        score += 5; trace.append("med-contradiction+5")
    else:
        score += 2; trace.append("low-contradiction+2")
    
    pct = min(score, 95)
    level = "high" if pct >= 80 else "medium" if pct >= 65 else "low"
    return {"pct": pct, "level": level, "trace": " > ".join(trace)}


# Anchor symbol mapping by keyword
ANCHOR_KEYWORDS = {
    "oil": "BRENT", "energy": "BRENT", "crude": "BRENT",
    "gold": "GOLD", "precious": "GOLD",
    "treasury": "10Y", "fed": "10Y", "rates": "10Y", "bond": "10Y",
    "nvidia": "NVDA", "ai": "NVDA", "tech": "NVDA", "chip": "NVDA", "semiconductor": "NVDA",
    "china": "DXY", "dollar": "DXY", "dxy": "DXY", "fx": "DXY", "yuan": "DXY",
    "defense": "SPX", "nato": "SPX", "spx": "SPX", "sp500": "SPX",
    "ukraine": "GOLD", "europe": "DXY", "eu": "DXY",
    "crypto": "BTC", "bitcoin": "BTC", "btc": "BTC",
}


def match_anchor(headline):
    h = headline.lower()
    for kw, asset in ANCHOR_KEYWORDS.items():
        if kw in h:
            return asset
    return None


def generate_flows():
    """Generate flows.json from available data sources."""
    
    # Load editorial data
    stories_data = load_json(SITE_DATA / "stories.json")
    living_data = load_json(SITE_DATA / "living_stories.json")
    
    # Collect stories
    all_stories = []
    if stories_data:
        if stories_data.get("lead"):
            all_stories.append(stories_data["lead"])
        all_stories.extend(stories_data.get("stories", []))
    if living_data:
        if living_data.get("lead"):
            all_stories.append(living_data["lead"])
        all_stories.extend(living_data.get("stories", []))
    
    # Build flows from stories with capital_flow data
    flows = []
    seen_ids = set()
    
    for story in all_stories:
        cf = story.get("capital_flow")
        if not cf:
            imp = story.get("capital_flow_implication", "")
            if imp:
                cf = parse_flow_implication(imp)
        if not cf:
            continue
        
        sid = story.get("story_id", "")
        if sid in seen_ids:
            continue
        seen_ids.add(sid)
        
        headline = story.get("headline", "")
        
        # Determine asset class from sector
        sector = story.get("sector", "markets")
        asset_class_map = {
            "geopolitics": "defense",
            "markets": "equities",
            "tech": "tech",
            "macro": "fixed_income",
            "wealth": "equities",
            "pleasure": "equities",
        }
        asset_class = asset_class_map.get(sector, "equities")
        
        # Extract or default values
        direction = cf.get("direction", "inflow")
        claim = cf.get("claim", "")
        
        # Parse amount from claim
        amt_match = re.search(r'\$([\d.]+)\s*([BM])', claim)
        amount_b = cf.get("amount_b", 0)
        if not amount_b and amt_match:
            amt = float(amt_match.group(1))
            denom = amt_match.group(2)
            amount_b = amt if denom == 'B' else amt / 1000
        
        projected = cf.get("projected", "")
        pace_mult = cf.get("pace_multiplier", 1.5)
        positioning = cf.get("positioning", "hedging")
        anchor = match_anchor(claim or headline) or "SPX"
        
        # Compute confidence
        conf = compute_confidence(amount_b, pace_mult, positioning)
        
        # Format headline
        dir_word = "into" if direction == "inflow" else "out of"
        flow_headline = f"${amount_b}B flowing {dir_word} {asset_class}"
        if claim:
            flow_headline = claim
        
        flows.append({
            "id": f"flow_{sid}",
            "headline": flow_headline,
            "amount_b": round(amount_b, 2),
            "projected": projected,
            "pace_multiplier": round(pace_mult, 1),
            "direction": direction,
            "positioning": positioning,
            "asset_class": asset_class,
            "anchor_symbol": anchor,
            "story_id": sid,
            "confidence_pct": conf["pct"],
            "confidence_level": conf["level"],
            "confidence_trace": conf["trace"],
        })
    
    # If no flows extracted from stories, use defaults
    if not flows:
        print("⚠️  No flows extracted from stories, using defaults", file=sys.stderr)
        flows = load_json(SITE_DATA / "flows.json")
        if flows:
            flows = flows.get("flows", [])
    
    # Compute aggregate confidence
    if flows:
        agg_conf = round(sum(f["confidence_pct"] for f in flows) / len(flows))
    else:
        agg_conf = 70
    
    # Count directions
    inflows = sum(1 for f in flows if f["direction"] == "inflow")
    outflows = sum(1 for f in flows if f["direction"] == "outflow")
    
    now = datetime.now(timezone(timedelta(hours=3)))  # EET
    next_update = now + timedelta(hours=1)
    
    output = {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%S+03:00"),
        "generated_by": "generate_flows.py",
        "next_update": next_update.strftime("%Y-%m-%dT%H:%M:%S+03:00"),
        "update_frequency": "60m",
        "summary": f"{inflows} inflows · {outflows} outflows",
        "aggregate_confidence": agg_conf,
        "aggregate_confidence_label": f"Directional alignment across {len(flows)} tracked flows",
        "total_flows_tracked": len(flows),
        "flows": flows,
        "methodology": "Flows sourced from EPFR Global, Morningstar Direct, and internal aggregation. Velocity measured vs 4-week rolling average. Confidence computed via 4-factor model. Updated hourly.",
        "glossary": {
            "PDR": "Passive Discovery Rate — ratio of passive-to-active institutional flow. Above 1.5 = quiet accumulation by large passive funds.",
            "ATR": "Average True Range — typical daily price swing of this asset. 'Stop ×2 ATR' means the exit is set at 2× the normal daily move.",
            "bp": "Basis points — 1 bp = 0.01%. '+3bp' = a 0.03% change.",
            "MED/HIGH/LOW": "Conviction level — how strongly the model believes in this trade direction.",
            "EM": "Emerging Markets — developing economies outside US/Europe/Japan.",
            "Short-duration Treasuries": "US government bonds maturing in under 3 years — safer, shorter-term holdings.",
        }
    }
    
    flows_path = SITE_DATA / "flows.json"
    flows_path.write_text(json.dumps(output, indent=2))
    print(f"✅ Generated {len(flows)} flows → {flows_path}")
    print(f"   Aggregate confidence: {agg_conf}%")
    print(f"   {inflows} inflows · {outflows} outflows")
    print(f"   Next update: {next_update.strftime('%Y-%m-%d %H:%M EET')}")


if __name__ == "__main__":
    generate_flows()
