#!/usr/bin/env python3
"""
generate_broadcasts.py — Multi-Channel Distribution Engine

Pulls top 3 CRITICAL CONTRADICTIONs from the database.
Generates Telegram-ready posts (emoji + bold) and Reddit-ready posts (Markdown).
Outputs to distribution/pending_broadcasts.txt during shipit runs.

Usage:
  python3 scripts/generate_broadcasts.py
  python3 scripts/generate_broadcasts.py --channel telegram
  python3 scripts/generate_broadcasts.py --channel reddit
"""

import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DATA = PROJECT / "data"
DIST = PROJECT / "distribution"
SITE_URL = "https://www.lagazzettadikyiv.com"

def load_stories():
    with open(DATA / "stories.json") as f:
        return json.load(f)

def find_top_contradictions(data, limit=3):
    """Find stories with highest contradiction tier (CONTRADICTED)."""
    all_stories = [data.get("lead")] if data.get("lead") else []
    all_stories.extend(data.get("stories", []))
    
    # Score: CONTRADICTED tier + high confidence
    scored = []
    for s in all_stories:
        if not s: continue
        cf = s.get("capital_flow", {})
        cs = s.get("contradiction_score", 0)
        tier = "CONTRADICTED" if cs >= 67 else "DIVERGENT" if cs >= 34 else "ALIGNED"
        pace = cf.get("pace_multiplier", 1)
        score = cs + pace * 5  # Boost by velocity
        scored.append((score, s, tier, cf))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:limit]

def generate_telegram_post(story, tier, cf):
    """Generate Telegram-ready post with emoji and clear sections."""
    headline = story.get("headline", "Untitled")[:120]
    summary = (story.get("summary") or story.get("reality") or "")[:200]
    play = story.get("the_play", "")[:150]
    they_say = (story.get("they_say") or "")[:200]
    reality = (story.get("reality") or "")[:200]
    story_id = story.get("story_id", "")
    url = f"{SITE_URL}/story.html?id={story_id}"
    
    direction = cf.get("direction", "")
    amount = cf.get("amount_b", "?")
    asset = cf.get("asset_class", "").upper()
    pace = cf.get("pace_multiplier", 1)
    confidence = cf.get("confidence_pct", 50)
    
    emoji_map = {"CONTRADICTED": "🔴", "DIVERGENT": "🟡", "ALIGNED": "🟢"}
    dir_emoji = "📈" if direction == "inflow" else "📉"
    emoji = emoji_map.get(tier, "🟢")
    
    lines = []
    lines.append(f"{emoji} **{headline}**")
    
    # Flow data row
    flow_parts = [f"{dir_emoji} {direction.upper()}"]
    if amount != "?":
        flow_parts.append(f"${amount}B")
    flow_parts.append(asset)
    if pace != 1.0:
        flow_parts.append(f"{pace}× velocity")
    flow_parts.append(f"{confidence}% confidence")
    lines.append(" · ".join(flow_parts))
    lines.append(f"Contradiction: {story.get('contradiction_score', 0)}/100")
    lines.append("")
    
    # They Say / Reality
    if they_say:
        lines.append("**THEY SAY**")
        lines.append(they_say)
        lines.append("")
    if reality:
        lines.append("**REALITY**")
        lines.append(reality)
        lines.append("")
    
    # The Play
    if play:
        lines.append("**🎯 THE PLAY**")
        lines.append(play)
        lines.append("")
    
    # Footer
    lines.append(f"🔗 {url}")
    lines.append("#GazzettaDiKyiv #CapitalFlows")
    
    return "\n".join(lines)

def generate_reddit_post(story, tier, cf):
    """Generate Reddit-ready Markdown post."""
    headline = story.get("headline", "Untitled")[:120]
    summary = (story.get("summary") or story.get("reality") or "")[:300]
    play = story.get("the_play", "")
    they_say = story.get("they_say", "")
    reality = story.get("reality", "")
    story_id = story.get("story_id", "")
    url = f"{SITE_URL}/story.html?id={story_id}"
    
    direction = cf.get("direction", "")
    amount = cf.get("amount_b", "?")
    asset = cf.get("asset_class", "").upper()
    pace = cf.get("pace_multiplier", 1)
    confidence = cf.get("confidence_pct", 50)
    
    post = f"""# {headline}

## INTEL (They Say vs Reality)

**They Say:** {they_say[:150]}

**Reality:** {reality[:150]}

{summary}

## ALPHA: ${amount}B {direction} {asset} at {pace}× velocity, {confidence}% confidence

**THE PLAY:** {play}

---

*Source: [La Gazzetta di Kyiv]({url}) — Contradiction-first capital flow intelligence.*
"""
    return post

def main():
    os.makedirs(str(DIST), exist_ok=True)
    
    data = load_stories()
    top = find_top_contradictions(data)
    
    if not top:
        print("No contradictions found.")
        return
    
    channel = "all"
    if "--channel" in sys.argv:
        idx = sys.argv.index("--channel") + 1
        if idx < len(sys.argv):
            channel = sys.argv[idx]
    
    output = []
    output.append(f"═══ GAZZETTA BROADCASTS — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} ═══\n")
    
    for i, (score, story, tier, cf) in enumerate(top):
        headline = story.get("headline", "?")[:80]
        output.append(f"\n── Broadcast {i+1}: {tier} (score: {score:.0f}) ──")
        output.append(f"  Story: {headline}...")
        
        if channel in ("telegram", "all"):
            tg = generate_telegram_post(story, tier, cf)
            output.append(f"\n  📱 TELEGRAM:\n{tg}\n")
        
        if channel in ("reddit", "all"):
            rd = generate_reddit_post(story, tier, cf)
            output.append(f"\n  🤖 REDDIT:\n{rd}\n")
    
    out_path = DIST / "pending_broadcasts.txt"
    with open(out_path, "w") as f:
        f.write("\n".join(output))
    
    print(f"✓ {len(top)} broadcasts written to {out_path}")
    print(f"  Channels: {channel}")
    
    # Also output to stdout for CLI use
    if "--stdout" in sys.argv:
        print("\n".join(output))

if __name__ == "__main__":
    main()
