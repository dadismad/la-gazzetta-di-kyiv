#!/usr/bin/env python3
"""db_to_json.py — Compile SQLite database to static JSON files for frontend.

Queries gazzetta.db, reconstructs nested JSON structures, resolves
relational story_flow_links back into impacted_flows arrays, and outputs
data/stories.json and data/flows.json.

Also outputs site/data/ copies for deployment.

Usage:
  python3 scripts/db_to_json.py               # write data/ + site/data/
  python3 scripts/db_to_json.py --data-only    # write data/ only
"""

import json
import os
import sys
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT / "gazzetta.db"
DATA = PROJECT / "data"
SITE_DATA = PROJECT / "site" / "data"


def compile_stories(conn):
    """Query stories, reconstruct full JSON, resolve impact_flows links."""
    rows = conn.execute("""
        SELECT id, full_json FROM stories
        ORDER BY
            CASE tier
                WHEN 'BREAKING'   THEN 0
                WHEN 'DEVELOPING' THEN 1
                WHEN 'ACTIVE'     THEN 2
                WHEN 'SETTLING'   THEN 3
                ELSE 4
            END,
            contradiction_score DESC,
            generated_at DESC
    """).fetchall()

    # Resolve story_flow_links → impacted_flows AND inject real flow metrics
    links = conn.execute("SELECT story_id, flow_id FROM story_flow_links").fetchall()
    story_to_flow_ids = {}
    for story_id, flow_id in links:
        story_to_flow_ids.setdefault(story_id, []).append(flow_id)

    # Fetch ALL flow data upfront for JOIN injection
    flow_rows = conn.execute(
        "SELECT id, amount_b, velocity, net_direction, category, full_json FROM flows"
    ).fetchall()
    flow_by_id = {}
    for fid, amt, vel, direction, cat, fj in flow_rows:
        flow_by_id[fid] = {
            "amount_b": amt or 0, "velocity": vel or 1.0,
            "direction": direction or "neutral", "category": cat or "",
            "full_json": fj,
        }

    stories = []
    for sid, full_json_str in rows:
        if not full_json_str:
            continue
        story = json.loads(full_json_str)

        # Inject resolved impacted_flows (IDs)
        impacted_ids = story_to_flow_ids.get(sid, [])
        if impacted_ids:
            story["impacted_flows"] = impacted_ids

            # JOIN: inject REAL flow metrics into capital_flow dict
            # Use the first linked flow's actual DB values
            primary_flow = flow_by_id.get(impacted_ids[0])
            if primary_flow:
                cf = story.get("capital_flow", {})
                cf["amount_b"] = primary_flow["amount_b"]
                cf["pace_multiplier"] = primary_flow["velocity"]
                cf["direction"] = primary_flow["direction"]
                cf["asset_class"] = cf.get("asset_class") or primary_flow["category"]
                cf["confidence_pct"] = cf.get("confidence_pct", 50)
                cf["confidence_level"] = cf.get("confidence_level", "medium")
                cf["claim"] = f"${primary_flow['amount_b']}B {primary_flow['direction']} {cf.get('asset_class', '')}"
                if primary_flow["amount_b"] > 0:
                    cf["confidence"] = f"{cf.get('confidence_pct', 50)}%"
                story["capital_flow"] = cf

        # Ensure story_id is set
        story["story_id"] = sid
        stories.append(story)

    # Detect lead story (highest contradiction, most recent)
    lead = stories[0] if stories else None

    generated_at = datetime.now(timezone.utc).isoformat()
    doc = {
        "generated_at": generated_at,
        "lead": lead,
        "stories": stories[1:] if lead else stories,  # exclude lead from array (prevents double-render)
    }

    # Write data/stories.json
    out_path = DATA / "stories.json"
    with open(out_path, "w") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)

    story_count = len(stories)
    print(f"  ✓ stories.json — {story_count} stories, lead: {lead['story_id'][:60] if lead else 'none'}...")

    return story_count


def compile_flows(conn):
    """Query flows, reconstruct full JSON with envelope."""
    rows = conn.execute("""
        SELECT id, full_json FROM flows
        ORDER BY amount_b DESC, velocity DESC
    """).fetchall()

    flows = []
    for fid, full_json_str in rows:
        if full_json_str:
            flow = json.loads(full_json_str)
            flow["id"] = fid
            flows.append(flow)

    # Compute aggregate stats
    total_inflows = sum(1 for f in flows if f.get("direction") == "inflow")
    total_outflows = sum(1 for f in flows if f.get("direction") == "outflow")
    confidences = [f.get("confidence_pct", 70) for f in flows]
    avg_conf = round(sum(confidences) / len(confidences)) if confidences else 70

    generated_at = datetime.now(timezone.utc).isoformat()
    doc = {
        "generated_at": generated_at,
        "generated_by": "db_to_json.py",
        "next_update": "",
        "update_frequency": "60m",
        "summary": f"{total_inflows} inflows · {total_outflows} outflows",
        "aggregate_confidence": avg_conf,
        "aggregate_confidence_label": "Flow confidence",
        "aggregate_direction": "bullish" if total_inflows > total_outflows else "bearish" if total_outflows > total_inflows else "neutral",
        "total_flows_tracked": len(flows),
        "lead_insight": flows[0] if flows else {},
        "sector_summary": {},
        "flows": flows,
    }

    # Build sector summary
    sector_summary = {}
    for f in flows:
        cat = f.get("asset_class", f.get("category", "unknown"))
        if cat not in sector_summary:
            sector_summary[cat] = {
                "total_b": 0, "inflows": 0, "outflows": 0,
                "avg_pace": 0, "avg_confidence": 0, "direction": "neutral", "count": 0
            }
        ss = sector_summary[cat]
        ss["total_b"] += f.get("amount_b", 0)
        if f.get("direction") == "inflow":
            ss["inflows"] += 1
        else:
            ss["outflows"] += 1
        ss["avg_pace"] += f.get("pace_multiplier", 0)
        ss["avg_confidence"] += f.get("confidence_pct", 70)
        ss["count"] += 1

    for ss in sector_summary.values():
        if ss["count"]:
            ss["avg_pace"] = round(ss["avg_pace"] / ss["count"], 2)
            ss["avg_confidence"] = round(ss["avg_confidence"] / ss["count"])
        ss["direction"] = "inflow" if ss["inflows"] >= ss["outflows"] else "outflow"

    doc["sector_summary"] = sector_summary

    # Write data/flows.json
    out_path = DATA / "flows.json"
    with open(out_path, "w") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)

    print(f"  ✓ flows.json — {len(flows)} flows, aggregate confidence: {avg_conf}%")

    return len(flows)


def main():
    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found. Run init_db.py and import_json_to_db.py first.")
        sys.exit(1)

    data_only = "--data-only" in sys.argv

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    try:
        print("Compiling from gazzetta.db → JSON...")
        story_count = compile_stories(conn)
        flow_count = compile_flows(conn)

        # Copy to site/data/ for deployment
        if not data_only:
            os.makedirs(str(SITE_DATA), exist_ok=True)

            for fname in ["stories.json", "flows.json"]:
                src = DATA / fname
                dst = SITE_DATA / fname
                if src.exists():
                    dst.write_text(src.read_text())
                    print(f"  ✓ site/data/{fname} synced")

        print(f"\n  DB → JSON compiled: {story_count} stories, {flow_count} flows")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
