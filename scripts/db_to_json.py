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
import shutil
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
        WHERE (
            json_extract(full_json, '$.source') NOT LIKE 'osint%'
            OR json_extract(full_json, '$.source') IS NULL
        )
        ORDER BY
            CASE tier
                WHEN 'BREAKING'   THEN 0
                WHEN 'DEVELOPING' THEN 1
                WHEN 'ACTIVE'     THEN 2
                WHEN 'SETTLING'   THEN 3
                ELSE 4
            END,
            CASE WHEN json_extract(full_json, '$.capital_flow.contradiction_flag') IS NOT NULL THEN 0 ELSE 1 END,
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
            # Use flow values ONLY as fallbacks — preserve story-derived values
            primary_flow = flow_by_id.get(impacted_ids[0])
            if primary_flow:
                cf = story.get("capital_flow", {})
                # Only use flow values when story doesn't have its own
                # Exception: override the known $5.0B default (intel_to_stories.py default)
                is_default_amount = (cf.get("amount_b") == 5.0 and not cf.get("_amount_derived"))
                if not cf.get("amount_b") or is_default_amount:
                    cf["amount_b"] = primary_flow["amount_b"]
                if not cf.get("pace_multiplier"):
                    cf["pace_multiplier"] = primary_flow["velocity"]
                if not cf.get("direction") or cf.get("direction") == "neutral":
                    cf["direction"] = primary_flow["direction"]
                if not cf.get("asset_class"):
                    cf["asset_class"] = primary_flow["category"]
                cf["confidence_pct"] = cf.get("confidence_pct", 50)
                cf["confidence_level"] = cf.get("confidence_level", "medium")
                cf["claim"] = f"${primary_flow['amount_b']}B {primary_flow['direction']} {cf.get('asset_class', '')}"
                if primary_flow["amount_b"] > 0:
                    cf["confidence"] = f"{cf.get('confidence_pct', 50)}%"
                story["capital_flow"] = cf

        # v23.12: Source transparency label on every capital_flow
        source = story.get("source", "")
        cf = story.get("capital_flow", {})
        if source and source.startswith("telegram_"):
            cf["source_label"] = "[LIVE-DATA]"
        else:
            cf["source_label"] = "[CALC-EST]"
        story["capital_flow"] = cf

        # v23.11: Strategic Recommendation for high-asymmetry stories (>55 contradiction)
        cs = story.get("contradiction_score", 0)
        if cs and isinstance(cs, (int, float)) and cs >= 55:
            cf = story.get("capital_flow", {})
            ac = cf.get("asset_class", "macro")
            direction = cf.get("direction", "neutral")
            amount = cf.get("amount_b", 0)
            headline = (story.get("headline") or "")[:80]
            play = story.get("portfolio_implication") or story.get("actionable_trade") or "Monitor for directional break."

            tier = "MAX CONVICTION" if cs >= 75 else ("HIGH CONVICTION" if cs >= 67 else "ELEVATED")
            bias = "LONG" if direction == "inflow" else ("SHORT" if direction == "outflow" else "NEUTRAL")

            story["strategic_recommendation"] = {
                "tier": tier,
                "bias": bias,
                "asset_class": ac,
                "capital_at_stake": f"${amount}B",
                "rationale": play if isinstance(play, str) else str(play)[:200],
                "horizon": story.get("horizon", "24-72h"),
                "action": f"Position for {ac} {bias.lower()} exposure. {play if isinstance(play, str) else ''}"[:250],
                "gated": True,  # Lead-gen gate signal
            }

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
        "aggregate_confidence_label": "Flow Sentiment",
        "aggregate_direction": "bullish" if total_inflows > total_outflows else "bearish" if total_outflows > total_inflows else "neutral",
        "sentiment_meter": {
            "inflow_ratio": round(total_inflows / max(total_inflows + total_outflows, 1) * 100),
            "outflow_ratio": round(total_outflows / max(total_inflows + total_outflows, 1) * 100),
            "total_inflows_b": round(total_inflows, 1),
            "total_outflows_b": round(total_outflows, 1),
            "net_flow_b": round(total_inflows - total_outflows, 1),
            "scale": "systemic" if (total_inflows + total_outflows) >= 5 else "speculative",
        },
        "contextual_scale": {
            "speculative": {"min_b": 0.01, "max_b": 2.0, "description": "Speculative capital flows ($10M–$2B)"},
            "systemic": {"min_b": 2.0, "max_b": 500.0, "description": "Systemic institutional flows ($2B–$500B)"},
        },
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

    
    # ── v23.8: Asymmetric Signal Engine ──
    # Compare Narrative (Story direction) vs Telemetry (Flow direction)
    # If they diverge, flag as CRITICAL CONTRADICTION
    # Load stories from compiled JSON
    stories_path = DATA / "stories.json"
    all_stories = []
    if stories_path.exists():
        with open(stories_path) as f:
            sd = json.load(f)
        if sd.get("lead"):
            all_stories.append(sd["lead"])
        all_stories.extend(sd.get("stories", []))
    
    contradictions_detected = 0
    for story in all_stories:
        cf = story.get("capital_flow", {})
        narrative_dir = cf.get("direction", "")
        if not narrative_dir:
            continue
        
        # Find linked flows
        impacted = story.get("impacted_flows", [])
        if not impacted:
            continue
        
        # Compare: if story says inflow but linked flows are outflow → contradiction
        linked_flow_dirs = []
        for fid in impacted:
            for fl in flows:
                if fl.get("id") == fid:
                    linked_flow_dirs.append(fl.get("direction", ""))
        
        if linked_flow_dirs:
            # If majority of flows oppose the narrative direction → contradiction
            opposite = sum(1 for d in linked_flow_dirs if d != narrative_dir and d != "neutral")
            if opposite >= len(linked_flow_dirs) / 2:
                # Flag as critical contradiction
                if cf.get("confidence_pct", 50) < 80:
                    cf["confidence_pct"] = min(cf.get("confidence_pct", 50) - 10, 40)
                    cf["contradiction_flag"] = "NARRATIVE_VS_FLOW_DIVERGENCE"
                    cf["contradiction_detail"] = f"Narrative says {narrative_dir} but {opposite}/{len(linked_flow_dirs)} linked flows show opposite direction"
                    story["capital_flow"] = cf
                    contradictions_detected += 1
    
    if contradictions_detected:
        print(f"  ⚡ Asymmetric Signal: {contradictions_detected} narrative-flow contradictions detected")

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

        # ── Atomic EN/RU output (v23.6) ──
        # English: canonical paths (backward compatible)
        EN_DIR = DATA / "en"
        RU_DIR = DATA / "ru"

        # 1) Copy EN to data/en/ for atomic bilingual structure
        os.makedirs(str(EN_DIR), exist_ok=True)
        for fname in ["stories.json", "flows.json"]:
            src = DATA / fname
            dst = EN_DIR / fname
            if src.exists():
                dst.write_text(src.read_text())

        # 2) Sync RU from existing translations (translate_content.py output)
        os.makedirs(str(RU_DIR), exist_ok=True)
        ru_stories = DATA / "stories_ru.json"
        ru_flows = DATA / "flows_ru.json"
        if ru_stories.exists():
            shutil.copy(str(ru_stories), str(RU_DIR / "stories.json"))
        if ru_flows.exists():
            shutil.copy(str(ru_flows), str(RU_DIR / "flows.json"))

        # 3) Copy to site/data/ for deployment
        if not data_only:
            os.makedirs(str(SITE_DATA / "en"), exist_ok=True)
            os.makedirs(str(SITE_DATA / "ru"), exist_ok=True)
            os.makedirs(str(SITE_DATA), exist_ok=True)

            for fname in ["stories.json", "flows.json"]:
                src = DATA / fname
                dst = SITE_DATA / fname
                if src.exists():
                    dst.write_text(src.read_text())
                    print(f"  ✓ site/data/{fname} synced")

            # Also sync to site/data/en/ and site/data/ru/
            en_dst = SITE_DATA / "en" / fname
            ru_dst = SITE_DATA / "ru" / fname
            if (EN_DIR / fname).exists():
                en_dst.write_text((EN_DIR / fname).read_text())
            if (RU_DIR / fname).exists():
                ru_dst.write_text((RU_DIR / fname).read_text())

            # Also sync RU files to site/data/
            for fname in ["stories_ru.json", "flows_ru.json"]:
                src = DATA / fname
                dst = SITE_DATA / fname
                if src.exists():
                    dst.write_text(src.read_text())
                    print(f"  ✓ site/data/{fname} synced")

            # Also sync to site/data/en/ and site/data/ru/
            en_dst = SITE_DATA / "en" / fname
            ru_dst = SITE_DATA / "ru" / fname
            if (EN_DIR / fname).exists():
                en_dst.write_text((EN_DIR / fname).read_text())
            if (RU_DIR / fname).exists():
                ru_dst.write_text((RU_DIR / fname).read_text())

            # Verify translation sync
            en_count = story_count
            if ru_stories.exists():
                with open(ru_stories) as f:
                    ru_data = json.load(f)
                ru_count = len(ru_data.get("stories", []))
                if ru_count < en_count:
                    print(f"  ⚠ TRANSLATION GAP: EN={en_count} stories, RU={ru_count} — run translate_content.py")
                else:
                    print(f"  ✓ Translation sync: {en_count} EN = {ru_count} RU")

        print(f"\n  DB → JSON compiled: {story_count} stories, {flow_count} flows")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
