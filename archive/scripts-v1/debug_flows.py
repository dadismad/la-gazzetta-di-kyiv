#!/usr/bin/env python3
"""debug_flows.py — Diagnostic: trace the $5B bug end-to-end.

Prints:
  1) All flows in gazzetta.db with amount_b + net_direction
  2) All story_flow_links (which stories map to which flows)
  3) Compiled site/data/stories.json — capital_flow values for stories with links
  4) Distribution check — count of stories at $5.0B vs other values
"""

import json, sqlite3, sys
from pathlib import Path
from collections import Counter

PROJECT = Path(__file__).resolve().parent.parent
DB = PROJECT / "gazzetta.db"
STORIES = PROJECT / "public" / "data" / "stories.json"

print("═══════════════════════════════════════════")
print("  DIAGNOSTIC: $5B Flow Default Bug")
print("═══════════════════════════════════════════\n")

# ── 1) All flows in DB ──
print("── 1) FLOWS IN gazzetta.db ──")
if not DB.exists():
    print("  ERROR: gazzetta.db not found")
    sys.exit(1)

conn = sqlite3.connect(str(DB))
flows = conn.execute(
    "SELECT id, amount_b, net_direction, category, story_id FROM flows ORDER BY amount_b DESC"
).fetchall()
print(f"  Total flows: {len(flows)}")
for f in flows:
    fid, amt, direction, cat, sid = f
    marker = " ← DEFAULT" if amt == 5.0 else ""
    print(f"  ${amt:>8.1f}B  {direction:8s}  {cat:15s}  {fid[:50]}...{marker}")
print()

# ── 2) Story-flow links ──
print("── 2) STORY_FLOW_LINKS ──")
links = conn.execute("SELECT story_id, flow_id FROM story_flow_links").fetchall()
print(f"  Total links: {len(links)}")
for sid, fid in links:
    # Get story headline for context
    story = conn.execute("SELECT headline FROM stories WHERE id = ?", (sid,)).fetchone()
    headline = (story[0] or sid)[:70] if story else sid[:70]
    print(f"  {headline}")
    print(f"    → {fid[:60]}...")
print()

# ── 3) Compiled JSON output ──
print("── 3) COMPILED site/data/stories.json ──")
with open(STORIES) as f:
    data = json.load(f)

stories_with_links = [s for s in data["stories"] if s.get("impacted_flows")]
print(f"  Stories with impacted_flows: {len(stories_with_links)}")

amounts = []
for s in stories_with_links:
    cf = s.get("capital_flow", {})
    amt = cf.get("amount_b", 0)
    direction = cf.get("direction", "?")
    claim = cf.get("claim", "?")
    headline = (s.get("headline", "") or "")[:65]
    amounts.append(amt)
    marker = " ← STILL DEFAULT" if amt == 5.0 else ""
    print(f"  ${amt:>8.1f}B  {direction:8s}  claim: {claim:35s}  {headline}{marker}")

print()

# ── 4) Distribution ──
print("── 4) DISTRIBUTION ANALYSIS ──")
counter = Counter(amounts)
total = len(amounts)
print(f"  Total linked stories: {total}")
for amt, count in counter.most_common():
    pct = count / total * 100
    bar = "█" * int(pct / 5)
    print(f"  ${amt:>8.1f}B : {count:2d} stories ({pct:5.1f}%) {bar}")

default_count = counter.get(5.0, 0)
default_pct = default_count / total * 100 if total else 0
print(f"\n  Default ($5.0B) prevalence: {default_count}/{total} = {default_pct:.0f}%")

# ── 5) Root cause section ──
print("\n── 5) ROOT CAUSE DETECTION ──")
# Check flows table: how many have $5.0B?
flow_amounts = [f[1] for f in flows]
flow_counter = Counter(flow_amounts)
default_flows = flow_counter.get(5.0, 0)
print(f"  Flows at $5.0B: {default_flows}/{len(flows)} = {default_flows/len(flows)*100:.0f}%")

# Check if the problem is in the flows table or the compiler
if default_flows / len(flows) > 0.7:
    print("\n  ═══ ROOT CAUSE: FLOWS TABLE ═══")
    print("  Most flows have $5.0B because the data source defaults to 5.0.")
    print("  The fetch_intel.py extract_amount() returns 5.0 when no $XB pattern is found.")
    print("  The approve_draft.py draft_to_flow() also defaults to 5.0.")
    print("  FIX: Real enrichment needed — diversify flow amounts from actual news text.")
else:
    # Check if compiler is mis-mapping
    print("\n  ═══ ROOT CAUSE: COMPILER or LINKING ═══")
    print("  Flows table has diverse values, but stories aren't linking correctly.")
    
    # Check: do story_flow_links have real different flows mapped?
    unique_flow_ids = set()
    for sid, fid in links:
        unique_flow_ids.add(fid)
    print(f"  Unique flows linked: {len(unique_flow_ids)}/{len(flows)}")
    
    # Check if db_to_json is mapping the correct flow
    flow_by_id = {f[0]: f[1] for f in flows}
    for sid, fid in links:
        if fid in flow_by_id and flow_by_id[fid] != 5.0:
            # This flow has a non-default amount — check if story gets it
            story = conn.execute("SELECT full_json FROM stories WHERE id=?", (sid,)).fetchone()
            if story:
                sj = json.loads(story[0])
                cf = sj.get("capital_flow", {})
                if cf.get("amount_b") == 5.0:
                    print(f"  BUG: story {sid[:40]} linked to flow ${flow_by_id[fid]}B but capital_flow has $5.0B")
                    print(f"       → db_to_json.py JOIN is failing for this story")

conn.close()
print("\n═══════════════════════════════════════════")
