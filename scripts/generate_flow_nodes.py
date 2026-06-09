#!/usr/bin/env python3
"""
Generate flow_nodes.json from editorial pipeline stories.

Reads data/stories.json (source of truth), extracts capital_flow dicts,
maps each flow to source→target node types based on asset class and direction.
Outputs site/data/flow_nodes.json — consumed by flow-nodes.html visualization.
"""
import json, re, os
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_SOURCE = PROJECT_ROOT / "data" / "stories.json"
OUTPUT = PROJECT_ROOT / "site" / "data" / "flow_nodes.json"

EET = timezone(timedelta(hours=3))

NODE_TYPES = {
    "gov":           {"label": "Governmental",         "color": "#D4AF37", "order": 0},
    "institutional": {"label": "Private/Institutional", "color": "#3B82F6", "order": 1},
    "corporate":     {"label": "Corporate",             "color": "#10B981", "order": 2},
    "retail":        {"label": "Retail",                "color": "#A78BFA", "order": 3},
    "crypto":        {"label": "Crypto",                "color": "#F59E0B", "order": 4},
}

# Asset class → primary node type mapping
ASSET_TO_NODE = {
    "equities":    "institutional",
    "crypto":      "crypto",
    "commodities": "corporate",
    "bonds":       "gov",
    "tech":        "corporate",
    "gold":        "retail",
    "real_estate": "corporate",
    "defense":     "gov",
    "energy":      "corporate",
    "agriculture": "corporate",
    "forex":       "gov",
    "infrastructure": "gov",
}

def safe_str(s):
    return str(s or "").strip()

def parse_amount(text):
    """Parse '$37.2B', '$3-5B' → (amount_b, denomination)."""
    if not text: return (0, "unknown")
    m = re.search(r'[\$€]\s*([\d.]+)\s*(?:-|–|to)\s*[\$€]?\s*([\d.]+)\s*([BM])', text)
    if m:
        amt = (float(m.group(1)) + float(m.group(2))) / 2
        if m.group(3) == 'M': amt /= 1000
        return (round(amt, 1), "billion")
    m = re.search(r'[\$€]\s*([\d.]+)\s*([BM])\b', text)
    if m:
        amt = float(m.group(1))
        if m.group(2) == 'M': amt /= 1000
        return (round(amt, 1), "billion")
    return (0, "unknown")

def parse_amount_from_cf(cf):
    """Parse amount from capital_flow dict — tries amount field, then claim, then pacing."""
    # Try amount field first
    amt_str = cf.get("amount", "")
    amt_b, denom = parse_amount(amt_str)
    if amt_b > 0:
        return amt_b, denom
    
    # Fallback: parse claim text (e.g., "$5.0B ↑ crypto")
    claim = cf.get("claim", "")
    if claim:
        amt_b, denom = parse_amount(claim)
        if amt_b > 0:
            return amt_b, denom
    
    # Last resort: pacing/amount_b field
    amt_b = cf.get("amount_b", 0)
    if amt_b > 0:
        return amt_b, "billion"
    
    return 0, "unknown"

def extract_pace(cf):
    """Extract pace multiplier from capital_flow dict field."""
    # Try numeric pace_multiplier first (actual field name in stories.json)
    pm = cf.get("pace_multiplier", 0)
    if pm and pm > 0:
        return float(pm)
    # Fallback: parse pacing or pace string fields
    p = cf.get("pacing", "") or cf.get("pace", "")
    if not p: return 1.0
    m = re.search(r'(\d+\.?\d*)\s*x', str(p).lower())
    return float(m.group(1)) if m else 1.0

def normalize_direction(text):
    if not text: return "inflow"
    r = str(text).lower()
    if any(kw in r for kw in ['inflow','into','buy','long','accumulat','overweight','add']):
        return "inflow"
    if any(kw in r for kw in ['outflow','out of','sell','short','distribut','underweight','trim']):
        return "outflow"
    return "inflow"

def asset_to_node_type(asset_class):
    """Map asset class string → primary node type."""
    if not asset_class: return "institutional"
    ac = asset_class.lower().strip()
    for key, ntype in ASSET_TO_NODE.items():
        if key in ac: return ntype
    return "institutional"

def compute_confidence(amount_b, pace_mult):
    score = 50
    if amount_b >= 5: score += 15
    elif amount_b >= 3: score += 12
    elif amount_b >= 1: score += 10
    else: score += 5
    if pace_mult >= 3: score += 8
    elif pace_mult >= 2: score += 7
    elif pace_mult >= 1.5: score += 7
    else: score += 5
    return min(score, 100)

def generate():
    if not DATA_SOURCE.exists():
        print(f"ERROR: {DATA_SOURCE} not found", file=__import__('sys').stderr)
        return False

    with open(DATA_SOURCE) as f:
        data = json.load(f)
    stories = data.get("stories", [])

    # Dynamic node registry (built from flow data)
    nodes = {}
    edges = []

    for story in stories:
        cf = story.get("capital_flow", {})
        if not cf or not isinstance(cf, dict):
            continue

        direction = normalize_direction(cf.get("direction", ""))
        amount_b, _ = parse_amount_from_cf(cf)
        if amount_b < 0.1:
            continue

        asset_class = safe_str(cf.get("asset_class", story.get("sector", "equities")))
        pace_mult = extract_pace(cf)
        confidence_pct = compute_confidence(amount_b, pace_mult)
        story_id = story.get("story_id", "")
        headline = safe_str(story.get("headline", ""))[:80]

        # Determine source and target node types
        target_type = asset_to_node_type(asset_class)

        if direction == "inflow":
            source_type = "institutional"  # money flows from institutions
        else:
            source_type = target_type
            target_type = "gov"  # money flows to safety (government bonds)

        # Create node IDs from types + asset class
        source_id = f"{source_type}-source"
        target_id = f"{target_type}-{asset_class.replace(' ','-').lower()}"

        # Accumulate node metrics
        for nid, ntype in [(source_id, source_type), (target_id, target_type)]:
            if nid not in nodes:
                # v22.35: Fix label — distinguish inflow vs outflow
                is_source = (nid == source_id)
                asset_label = asset_class.replace(' ','-').lower()
                if direction == 'inflow':
                    label = f"{NTYPES[ntype]['label']} → {asset_class}"
                else:
                    # Outflow: source sends money out, target receives safety
                    label = f"{NTYPES[ntype]['label']} {'→' if is_source else '←'} {asset_class}"
                nodes[nid] = {
                    "id": nid,
                    "type": ntype,
                    "label": label,
                    "total_inflow_b": 0,
                    "total_outflow_b": 0,
                    "flow_count": 0,
                    "confidence_sum": 0,
                    "pace_sum": 0,
                }
            n = nodes[nid]
            if direction == "inflow":
                n["total_inflow_b"] += amount_b
            else:
                n["total_outflow_b"] += amount_b
            n["flow_count"] += 1
            n["confidence_sum"] += confidence_pct
            n["pace_sum"] += pace_mult

        # Create edge
        edges.append({
            "source": source_id,
            "target": target_id,
            "amount_b": amount_b,
            "direction": direction,
            "pace_mult": pace_mult,
            "confidence_pct": confidence_pct,
            "story_id": story_id,
            "headline": headline,
            "asset_class": asset_class,
            "data_source": "stories.json → capital_flow",
        })

    # Finalize nodes: compute averages, add metadata
    node_list = []
    for nid, n in nodes.items():
        fc = max(n["flow_count"], 1)
        node_list.append({
            "id": n["id"],
            "type": n["type"],
            "label": n["label"],
            "description": f"Auto-generated from {n['flow_count']} stories",
            "metrics": {
                "total_inflow_b": round(n["total_inflow_b"], 1),
                "total_outflow_b": round(n["total_outflow_b"], 1),
                "net_flow_b": round(n["total_inflow_b"] - n["total_outflow_b"], 1),
                "confidence_pct": round(n["confidence_sum"] / fc),
                "pace_avg": round(n["pace_sum"] / fc, 1),
            },
            "flow_count": n["flow_count"],
        })

    # Sort nodes by type order, then by net flow descending
    type_order = {k: v["order"] for k, v in NODE_TYPES.items()}
    node_list.sort(key=lambda n: (type_order.get(n["type"], 99), -n["metrics"]["net_flow_b"]))

    # Sort edges by amount descending
    edges.sort(key=lambda e: -e["amount_b"])

    output = {
        "generated_at": datetime.now(EET).isoformat(),
        "generated_by": "generate_flow_nodes.py",
        "update_frequency": "60m",
        "node_types": NODE_TYPES,
        "nodes": node_list,
        "edges": edges,
        "summary": {
            "total_nodes": len(node_list),
            "total_edges": len(edges),
            "total_flow_b": round(sum(e["amount_b"] for e in edges), 1),
            "inflow_count": sum(1 for e in edges if e["direction"] == "inflow"),
            "outflow_count": sum(1 for e in edges if e["direction"] == "outflow"),
        }
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"  Nodes: {len(node_list)}")
    print(f"  Edges: {len(edges)}")
    print(f"  Total flow: ${output['summary']['total_flow_b']:.1f}B")
    print(f"  Inflows: {output['summary']['inflow_count']} | Outflows: {output['summary']['outflow_count']}")
    return True

if __name__ == "__main__":
    NTYPES = NODE_TYPES
    ok = generate()
    exit(0 if ok else 1)
