#!/usr/bin/env python3
"""approve_draft.py — Approve a draft and promote it into the stories pipeline.

Reads a draft by ID from the drafts table, converts it into a full story,
inserts into stories table, creates linked flow entries, auto-links via
story_flow_links, and updates draft status to 'approved'.

After processing, automatically runs db_to_json.py to rebuild static site files.

Usage:
  python3 scripts/approve_draft.py --id 3          # approve draft ID 3
  python3 scripts/approve_draft.py --id 3,5,7      # approve multiple
  python3 scripts/approve_draft.py --list           # list pending drafts
  python3 scripts/approve_draft.py --list --limit 10  # list with limit
"""

import json
import os
import re
import sys
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT / "gazzetta.db"


# ═══════════════════════════════════════════════════════
# STORY GENERATION FROM DRAFT
# ═══════════════════════════════════════════════════════

def slugify(text, max_len=80):
    """URL-friendly slug from text."""
    if not text:
        return "untitled"
    slug = text.lower()[:max_len]
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    return slug.strip('-') or "untitled"


def generate_story_id(headline, source):
    """Generate a stable story_id from headline + source."""
    slug = headline.lower()[:60]
    slug = "".join(c if c.isalnum() or c in "_-" else "_" for c in slug)
    slug = slug.strip("_").replace("__", "_")
    # Include source prefix for uniqueness
    src = source.replace(" ", "_")[:20]
    return f"n21_osint__{src}__{slug}"[:120]


def detect_pillar(text):
    """Detect paradigm pillar from text — simplified inline version."""
    pillars = {
        "china_ascendancy": ["china", "beijing", "xi", "ccp", "chinese", "pla", "taiwan"],
        "dollar_decline": ["dollar", "dedollar", "brics", "imf", "cofer", "treasury", "fed"],
        "eu_fragmentation": ["eu", "european", "nato", "eurozone", "ecb", "brussels"],
        "abundance_tech": ["fusion", "space", "spacex", "nasa", "quantum"],
        "blockchain_agentic": ["crypto", "bitcoin", "token", "defi", "rwa", "blockchain", "stablecoin"],
        "multi_pillar": ["iran", "war", "strike", "missile", "hormuz", "oil", "crude", "brent", "sanctions"],
    }
    t = text.lower()
    scores = {}
    for pillar, keywords in pillars.items():
        score = sum(1 for k in keywords if k in t)
        if score > 0:
            scores[pillar] = score
    return max(scores, key=scores.get) if scores else "multi_pillar"


def draft_to_story(draft_row):
    """Convert a draft row into a full Gazzetta story dict."""
    draft_id, source, raw_content, headline, mp_json, flows_json, created_at, status = draft_row

    pillar = detect_pillar(f"{headline} {raw_content or ''}")

    # Parse suggested_flows
    suggested_flows = {}
    if flows_json:
        try:
            suggested_flows = json.loads(flows_json)
        except json.JSONDecodeError:
            pass

    # Parse suggested multi_persona
    multi_persona = {}
    if mp_json:
        try:
            multi_persona = json.loads(mp_json)
        except json.JSONDecodeError:
            pass

    direction = suggested_flows.get("direction", "neutral")
    asset_class = suggested_flows.get("asset_class", "equities")
    amount_b = suggested_flows.get("amount_b")  # None = no real amount extracted
    confidence_pct = suggested_flows.get("confidence_pct", 50)
    projected = suggested_flows.get("projected", raw_content or "")[:200]
    pace = suggested_flows.get("pace_multiplier", 1.0)

    confidence_level = "high" if confidence_pct >= 80 else "medium" if confidence_pct >= 60 else "low"
    tier = "DEVELOPING" if confidence_pct >= 50 else "ALIGNED"
    contradiction_score = min(50 + confidence_pct // 2, 85)

    now = datetime.now(timezone.utc).isoformat()
    story_id = generate_story_id(headline, source)

    story = {
        "story_id": story_id,
        "headline": headline[:200],
        "sector": asset_class,
        "pillar": pillar,
        "paradigm_pillar": pillar,
        "paradigm_implications": [projected[:200]] if projected else [],
        "they_say": f"Source: {source}. {raw_content[:300] if raw_content else ''}",
        "reality": raw_content[:300] if raw_content else "",
        "thesis": f"OSINT draft #{draft_id}: {headline[:200]}",
        "actors": [],
        "horizon": "24-72h",
        "confidence": confidence_level,
        "tier": tier,
        "actionable_trade": f"OSINT signal: {direction.upper()} {asset_class}. Review before execution.",
        "contradiction_score": contradiction_score,
        "invalidation_trigger": "Manual review required — OSINT draft, unvetted source",
        "portfolio_implication": projected[:300],
        "capital_flow": {
            "direction": direction,
            "amount_b": amount_b,
            "asset_class": asset_class,
            "projected": projected,
            "pace_multiplier": pace,
            "confidence_pct": confidence_pct,
            "confidence_level": confidence_level,
        },
        "capital_flow_implication": f"OSINT draft #{draft_id}. Source: {source}.",
        "evidence": [f"source: {source}", f"draft_id: {draft_id}"],
        "source": f"osint_{source}",
        "generated_at": now,
        "freshness": "breaking",
        "entity_tags": {"assets": [], "geographies": [], "actors": [], "instruments": []},
        "time_decay": {
            "half_life_hours": 36.0,
            "decay_curve": "exponential",
            "current_freshness": 1.0,
            "hours_elapsed": 0.0,
            "renewal_triggers": ["new_intel", "price_breach", "flow_confirmation"],
        },
        "impacted_flows": [],
        "associated_positions": [],
        "multi_persona": multi_persona,
    }

    return story


def draft_to_flow(draft_row, story_id):
    """Convert a draft's suggested flows into a flow entry."""
    draft_id, source, raw_content, headline, mp_json, flows_json, created_at, status = draft_row

    suggested_flows = {}
    if flows_json:
        try:
            suggested_flows = json.loads(flows_json)
        except json.JSONDecodeError:
            pass

    direction = suggested_flows.get("direction", "neutral")
    asset_class = suggested_flows.get("asset_class", "equities")
    amount_b = suggested_flows.get("amount_b")  # None = no real amount extracted
    confidence_pct = suggested_flows.get("confidence_pct", 50)
    pace = suggested_flows.get("pace_multiplier", 1.0)
    projected = suggested_flows.get("projected", "")[:200]
    confidence_level = "high" if confidence_pct >= 80 else "medium" if confidence_pct >= 60 else "low"

    now = datetime.now(timezone.utc).isoformat()
    flow_id = f"flow_{story_id}"

    amt_str = f"${amount_b}B" if amount_b is not None else "—"
    flow = {
        "id": flow_id,
        "story_id": story_id,
        "headline": f"{amt_str} {direction} {asset_class}",
        "amount_b": amount_b,
        "projected": projected,
        "pace_multiplier": pace,
        "direction": direction,
        "positioning": "accumulating" if direction == "inflow" else "distributing" if direction == "outflow" else "hedging",
        "asset_class": asset_class,
        "anchor_symbol": asset_class.upper()[:8],
        "source": f"osint_{source}",
        "confidence_pct": confidence_pct,
        "confidence_level": confidence_level,
        "confidence_trace": f"osint-draft+{confidence_pct}",
        "flow_sources": ["osint", source],
        "divergence": "unverified",
        "heat_score": 50,
        "trade_signal": "WATCH",
        "trade_emoji": "\U0001f7e1",
        "pdr": round(amount_b / 4, 1) if amount_b else 0,
        "flow_type": "passive_dominant",
    }

    return flow


# ═══════════════════════════════════════════════════════
# DATABASE OPERATIONS
# ═══════════════════════════════════════════════════════

def approve_draft(conn, draft_id):
    """Approve a single draft: move to stories + flows + links, update status."""
    # Read draft
    row = conn.execute(
        "SELECT id, source, raw_content, suggested_headline, suggested_multi_persona, "
        "suggested_flows, created_at, status FROM drafts WHERE id = ?",
        (draft_id,)
    ).fetchone()

    if not row:
        return {"ok": False, "error": f"Draft {draft_id} not found"}, None

    if row[7] == "approved":
        return {"ok": False, "error": f"Draft {draft_id} already approved"}, None

    # Generate story
    story = draft_to_story(row)
    story_id = story["story_id"]

    # Check for existing story with same ID
    existing = conn.execute("SELECT 1 FROM stories WHERE id = ?", (story_id,)).fetchone()
    if existing:
        return {"ok": False, "error": f"Story {story_id} already exists"}, None

    # Insert story
    conn.execute("""
        INSERT INTO stories (
            id, slug, headline, sector, pillar, tier, confidence,
            contradiction_score, generated_at,
            time_decay_raw, entity_tags_raw, multi_persona_raw,
            capital_flow_raw, full_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        story_id,
        slugify(story.get("headline", "")),
        story.get("headline", ""),
        story.get("sector", ""),
        story.get("pillar", ""),
        story.get("tier", "active"),
        story.get("confidence", "medium"),
        story.get("contradiction_score", 0),
        story.get("generated_at", ""),
        json.dumps(story.get("time_decay", {})) if story.get("time_decay") else None,
        json.dumps(story.get("entity_tags", {})) if story.get("entity_tags") else None,
        json.dumps(story.get("multi_persona", {})) if story.get("multi_persona") else None,
        json.dumps(story.get("capital_flow", {})) if story.get("capital_flow") else None,
        json.dumps(story, ensure_ascii=False),
    ))

    # Generate and insert flow
    flow = draft_to_flow(row, story_id)
    flow_id = flow["id"]

    conn.execute("""
        INSERT OR REPLACE INTO flows (
            id, story_id, name, category, net_direction,
            amount_b, velocity, last_updated, full_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        flow_id,
        story_id,
        flow.get("headline", ""),
        flow.get("asset_class", ""),
        flow.get("direction", "inflow"),
        flow.get("amount_b", 0.0),
        flow.get("pace_multiplier", 1.0),
        flow.get("generated_at", datetime.now(timezone.utc).isoformat()),
        json.dumps(flow, ensure_ascii=False),
    ))

    # Auto-link story ↔ flow
    conn.execute(
        "INSERT OR IGNORE INTO story_flow_links (story_id, flow_id) VALUES (?, ?)",
        (story_id, flow_id)
    )

    # Update draft status
    conn.execute(
        "UPDATE drafts SET status = 'approved' WHERE id = ?",
        (draft_id,)
    )

    return {"ok": True, "story_id": story_id, "flow_id": flow_id, "headline": story["headline"][:80]}, story


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def list_drafts(conn, limit=20, status_filter="pending_review"):
    """List drafts in the queue."""
    rows = conn.execute(
        "SELECT id, source, suggested_headline, created_at, status FROM drafts "
        "WHERE status = ? ORDER BY created_at DESC LIMIT ?",
        (status_filter, limit)
    ).fetchall()

    if not rows:
        print(f"No {status_filter} drafts found.")
        return

    print(f"\n{'ID':>4}  {'Source':20s}  {'Headline':70s}  {'Created'}")
    print("-" * 110)
    for row in rows:
        did, source, headline, created, status = row
        hl = (headline or "")[:68]
        ts = (created or "")[:19]
        print(f"{did:4d}  {source:20s}  {hl:70s}  {ts}")


def main():
    if "--list" in sys.argv:
        limit = 20
        for arg in sys.argv[1:]:
            if arg.startswith("--limit="):
                limit = int(arg.split("=", 1)[1])

        if not DB_PATH.exists():
            print("ERROR: gazzetta.db not found.")
            sys.exit(1)

        conn = sqlite3.connect(str(DB_PATH))
        try:
            # Show counts
            pending = conn.execute("SELECT COUNT(*) FROM drafts WHERE status='pending_review'").fetchone()[0]
            approved = conn.execute("SELECT COUNT(*) FROM drafts WHERE status='approved'").fetchone()[0]
            print(f"Drafts: {pending} pending · {approved} approved")
            list_drafts(conn, limit)
        finally:
            conn.close()
        return

    # ── Approve mode ──
    draft_ids = []
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--id":
            # Space-separated: --id 3,5,7
            i += 1
            if i < len(args):
                for part in args[i].split(","):
                    try:
                        draft_ids.append(int(part.strip()))
                    except ValueError:
                        print(f"ERROR: invalid draft ID: {part}")
                        sys.exit(1)
        elif arg.startswith("--id="):
            # Equals-separated: --id=3,5,7
            ids_str = arg.split("=", 1)[1]
            for part in ids_str.split(","):
                try:
                    draft_ids.append(int(part.strip()))
                except ValueError:
                    print(f"ERROR: invalid draft ID: {part}")
                    sys.exit(1)
        i += 1

    if not draft_ids:
        print("Usage: python3 scripts/approve_draft.py --id <draft_id>")
        print("       python3 scripts/approve_draft.py --id 3,5,7")
        print("       python3 scripts/approve_draft.py --list")
        sys.exit(1)

    if not DB_PATH.exists():
        print("ERROR: gazzetta.db not found.")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys=ON")

    approved = 0
    failed = 0

    try:
        for did in draft_ids:
            result, _ = approve_draft(conn, did)
            if result["ok"]:
                print(f"  ✓ Draft #{did} → {result['story_id'][:60]}")
                approved += 1
            else:
                print(f"  ✗ Draft #{did}: {result['error']}")
                failed += 1

        conn.commit()

        print(f"\n  Approved: {approved} · Failed: {failed}")

        if approved > 0:
            # Run db_to_json.py to rebuild site files
            db_to_json = Path(__file__).resolve().parent / "db_to_json.py"
            if db_to_json.exists():
                print("  Running db_to_json.py...")
                result = subprocess.run(
                    [sys.executable, str(db_to_json)],
                    capture_output=True, text=True, cwd=str(PROJECT)
                )
                if result.returncode == 0:
                    story_count = conn.execute("SELECT COUNT(*) FROM stories").fetchone()[0]
                    flow_count = conn.execute("SELECT COUNT(*) FROM flows").fetchone()[0]
                    print(f"  ✓ Static files rebuilt — {story_count} stories, {flow_count} flows")
                else:
                    print(f"  ⚠ db_to_json failed: {result.stderr[:200]}")

    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
