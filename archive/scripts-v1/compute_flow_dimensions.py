#!/usr/bin/env python3
"""
compute_flow_dimensions.py — Enrich flows.json with Duration, Counterparty, Scale.

Reads public/data/flows.json, adds three portfolio-manager-grade fields to each
flow object, writes back. Called from deploy_routine.sh after generate_signal_api.

Fields:
  duration     — "intraday" | "positional" | "structural"
  counterparty — "retail" | "institutional" | "sovereign" | "corporate" | "mixed"
  scale        — 1-10 integer, normalized across all flows

No database access. Operates purely on the JSON output.
"""

import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
FLOWS_PATH = PROJECT / "data" / "flows.json"


def compute_duration(pace_multiplier: float) -> str:
    """Duration from pace_multiplier — portfolio holding horizon signal."""
    if pace_multiplier >= 1.5:
        return "intraday"
    elif pace_multiplier >= 0.5:
        return "positional"
    else:
        return "structural"


def compute_counterparty(flow_sources: list[str]) -> str:
    """Counterparty from flow_sources array — who's on the other side."""
    if not flow_sources:
        return "mixed"
    
    mapping = {
        "institutional": "institutional",
        "funds": "institutional",
        "pension": "institutional",
        "endowment": "institutional",
        "sovereign": "sovereign",
        "central_bank": "sovereign",
        "government": "sovereign",
        "retail": "retail",
        "individual": "retail",
        "corporate": "corporate",
        "banking": "corporate",
        "treasury": "corporate",
        "family_office": "institutional",
        "hedge_fund": "institutional",
    }
    
    types = set()
    for src in flow_sources:
        key = src.lower().replace(" ", "_").replace("-", "_")
        mapped = mapping.get(key, "institutional")
        types.add(mapped)
    
    if len(types) == 1:
        return types.pop()
    return "mixed"


def compute_scale(amount_b: float, confidence_pct: int, pace_multiplier: float,
                  max_amount_b: float) -> int:
    """1-10 scale score: normalized amount * confidence * pace."""
    if max_amount_b == 0:
        return 1
    
    # Normalize amount to 0-1 against sector max
    normalized = min(amount_b / max_amount_b, 1.0)
    # Apply confidence weight (0-1)
    conf_weight = confidence_pct / 100.0
    # Apply pace modifier (capped at 2.0)
    pace_mod = min(pace_multiplier, 2.0)
    
    raw = normalized * conf_weight * pace_mod * 10
    return max(1, min(10, round(raw)))


def enrich_flows(flows_path: Path) -> dict:
    """Read flows.json, add dimensions, return updated data."""
    with open(flows_path) as f:
        data = json.load(f)
    
    flows = data.get("flows", [])
    if not flows:
        print("  No flows to enrich")
        return data
    
    # Find max amount_b per sector for scale normalization
    sector_max = {}
    for flow in flows:
        sector = flow.get("asset_class", "unknown")
        amt = flow.get("amount_b", 0) or 0
        sector_max[sector] = max(sector_max.get(sector, 0), amt)
    
    # Global max as fallback
    global_max = max(sector_max.values()) if sector_max else 1
    
    enriched = 0
    for flow in flows:
        pace = flow.get("pace_multiplier", 1.0) or 1.0
        amt = flow.get("amount_b", 0) or 0
        conf = flow.get("confidence_pct", 50) or 50
        sources = flow.get("flow_sources", []) or []
        sector = flow.get("asset_class", "unknown")
        
        flow["duration"] = compute_duration(pace)
        flow["counterparty"] = compute_counterparty(sources)
        flow["scale"] = compute_scale(
            amt, conf, pace,
            sector_max.get(sector, global_max)
        )
        enriched += 1
    
    print(f"  Enriched {enriched} flows with duration/counterparty/scale")
    
    # Add schema metadata
    data["flow_dimensions"] = {
        "generated_by": "compute_flow_dimensions.py",
        "duration_values": ["intraday", "positional", "structural"],
        "counterparty_values": ["retail", "institutional", "sovereign", "corporate", "mixed"],
        "scale_range": [1, 10],
        "scale_description": "1-10 normalized: amount_b * confidence_pct * pace_multiplier"
    }
    
    return data


def main():
    if not FLOWS_PATH.exists():
        print(f"ERROR: {FLOWS_PATH} not found")
        sys.exit(1)
    
    print(f"Reading {FLOWS_PATH}...")
    data = enrich_flows(FLOWS_PATH)
    
    with open(FLOWS_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"  Written {FLOWS_PATH} ({FLOWS_PATH.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
