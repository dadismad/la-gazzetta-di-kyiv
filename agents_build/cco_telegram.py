#!/usr/bin/env python3
"""
cco_telegram.py — Chief Content Officer: Telegram Distribution

Formats curated stories for Telegram channel posts and sends via Bot API.
Voice register: Contradiction-first, institutional, notification-optimized.

STRUCTURE (v3.0 — June 2026):
  HOOK  — notification-preview line, data-driven suspense, 50-80 chars
  STORY — consensus vs reality block + capital flow impact + contradiction score
  LINK  — direct anchor URL to full report on lagazzettadikyiv.com

Idempotency: checked before sending via posted_stories.jsonl.

Usage:
  python3 scripts/cco_telegram.py --story-id abc123 --headline "..." --they-say "..." --reality "..."
  python3 scripts/cco_telegram.py --dry-run  # test formatting only
"""

import json
import os
import sys
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta


TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "-1003990434181")

FRESHNESS_HOURS = 12


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_fresh(story: dict) -> tuple[bool, str]:
    """Check if story was published within the freshness window.
    Returns (is_fresh, reason_string)."""
    ts_raw = (story.get("published_at") or story.get("generated_at") or
              story.get("created_at") or "")
    if not ts_raw:
        return False, "no timestamp — cannot verify freshness"

    try:
        # Handle ISO format with/without Z and microseconds
        ts_clean = ts_raw.replace("Z", "+00:00")
        published = datetime.fromisoformat(ts_clean)
    except (ValueError, TypeError):
        return False, f"unparseable timestamp: {ts_raw}"

    cutoff = datetime.now(timezone.utc) - timedelta(hours=FRESHNESS_HOURS)
    if published < cutoff:
        age_hours = (datetime.now(timezone.utc) - published).total_seconds() / 3600
        return False, f"published {age_hours:.1f}h ago (cutoff: {FRESHNESS_HOURS}h)"

    return True, "fresh"


def format_story(story: dict) -> str:
    """Format a story for Telegram — contradiction-first structure (v3.0).

    Three-line structure (industry-standard Telegram publishing):
      Hook     — notification-preview line, creates genuine curiosity
      Story    — the contradiction (consensus vs reality) and implications
      Link     — direct URL to full report on lagazzettadikyiv.com

    Principles:
      - Hook must captivate from notification preview alone
      - Story focuses on the contradiction, not just reporting the news
      - Link is direct to the story anchor, not just the homepage
    """
    import html as html_mod

    headline = (story.get("headline", "") or "Untitled").strip()
    # Decode HTML entities in headline
    headline = html_mod.unescape(headline)

    they_say = (story.get("they_say", "") or "").strip()
    reality = (story.get("reality", "") or story.get("summary", "") or "").strip()
    contradiction = story.get("contradiction_score", 0)
    cf = story.get("capital_flow", {}) or {}
    story_id = story.get("story_id", "")
    tier = story.get("tier", "flow")

    direction = (cf.get("direction", "") or "").strip()
    amount_b = cf.get("amount_b", 0) or 0
    asset = (cf.get("asset_class", "") or "").upper().strip()
    pace = cf.get("pace_multiplier", 1) or 1

    # ── Build story page link ──
    if story_id:
        story_link = f"https://www.lagazzettadikyiv.com/stories.html#story-{story_id}"
    else:
        story_link = "https://www.lagazzettadikyiv.com"

    # ── LINE 1: THE HOOK (notification-preview, stand-alone, contradiction-focused) ──
    hook = _generate_hook(headline, they_say, reality, direction, amount_b, asset, contradiction)

    # ── LINE 2: THE STORY (contradiction + implications) ──
    story_lines = []

    # Contradiction block: "They say" vs "Reality"
    if they_say and reality:
        short_they = they_say[:200].strip()
        short_reality = reality[:200].strip()
        if not short_they.endswith(('.', '!', '?')):
            short_they += '...'
        if not short_reality.endswith(('.', '!', '?')):
            short_reality += '...'
        story_lines.append(f'<b>Consensus:</b> {html_mod.escape(short_they)}')
        story_lines.append(f'<b>Reality:</b> {html_mod.escape(short_reality)}')
    elif they_say and contradiction >= 50:
        # No explicit reality field but high contradiction score
        story_lines.append(f'{html_mod.escape(they_say[:300])}')
    else:
        # News story — summarize headline as narrative
        story_lines.append(f'{html_mod.escape(headline[:300])}')

    # Capital flow impact (the "so what" for institutional readers)
    flow_parts = []
    if direction and amount_b >= 0.1:
        flow_parts.append(f'{direction}: ${amount_b:.1f}B')
    if asset and asset != "NONE":
        flow_parts.append(asset)
    if pace and pace >= 1.2:
        flow_parts.append(f'{pace:.1f}x velocity')

    if flow_parts:
        story_lines.append('')
        story_lines.append(f'<b>Capital flow impact:</b> {" in ".join(flow_parts)}')

    # Contradiction metadata
    if contradiction >= 50:
        story_lines.append(f'<i>Contradiction score: {int(contradiction)}/100 — significant divergence from consensus</i>')
    elif contradiction >= 30:
        story_lines.append(f'<i>Contradiction score: {int(contradiction)}/100</i>')

    story_block = '\n'.join(story_lines)

    # ── LINE 3: THE LINK ──
    link_line = (
        f'<a href="{story_link}">'
        f'Read the full report: lagazzettadikyiv.com</a>'
    )

    # ── Assemble ──
    lines = [
        f"<b>{html_mod.escape(hook)}</b>",
        "",
        story_block,
        "",
        link_line,
    ]

    text = "\n".join(lines)

    # Truncate to Telegram's 4096 char limit
    if len(text) > 4000:
        text = text[:3997] + "..."

    return text


def _generate_hook(headline: str, they_say: str, reality: str,
                   direction: str, amount_b: float, asset: str,
                   contradiction_score: int) -> str:
    """Generate a notification-optimized hook (50-80 chars, standalone, contradiction-focused).

    Rules:
      - Must captivate from notification preview alone (no message open required)
      - Contradiction between consensus and capital flow reality
      - No emojis, no clickbait — data-driven suspense only
      - Max 80 characters; 60-70 ideal for Telegram mobile notifications
    """
    headline_lower = headline.lower()

    # Pattern 1: High contradiction story — frame the divergence
    if they_say and reality and contradiction_score >= 70:
        return "The consensus and the capital flows are telling opposite stories."

    # Pattern 2: Capital flow with specific numbers — most compelling
    if direction and amount_b >= 0.1 and asset and asset != "NONE":
        direction_word = "into" if "inflow" in direction.lower() else "out of"
        if amount_b >= 100:
            return f"${amount_b:.0f}B moving {direction_word} {asset}. The reason is not consensus."
        elif amount_b >= 10:
            return f"${amount_b:.0f}B repositioning {direction_word} {asset}. Capital is voting."
        else:
            return f"${amount_b:.1f}B shift in {asset}. Data contradicts the narrative."

    # Pattern 3: Strong contradiction without specific flow amounts
    if they_say and reality:
        return "Markets are pricing one thing. Capital flows show another."

    # Pattern 4: High-contradiction story with headline substance
    if contradiction_score >= 75:
        return "The data refuses to confirm what the market believes."

    # Pattern 5: Sector/event-driven hooks
    if any(w in headline_lower for w in ["rate", "fed", "ecb", "central bank", "inflation"]):
        return "The rate decision was expected. The capital reaction was not."
    if any(w in headline_lower for w in ["war", "conflict", "sanction", "defense"]):
        return "Geopolitics is moving capital. Track where it flows."
    if any(w in headline_lower for w in ["china", "beijing", "xi", "yuan"]):
        return "What Beijing is doing vs what Western capital is assuming."
    if any(w in headline_lower for w in ["ai", "openai", "nvidia", "chip", "semiconductor"]):
        return "AI capital flows are diverging from AI headlines."
    if any(w in headline_lower for w in ["crypto", "bitcoin", "ethereum", "defi"]):
        return "Crypto prices move. Capital flows reveal why."
    if any(w in headline_lower for w in ["energy", "oil", "gas", "power", "nuclear"]):
        return "Energy repricing is underway. Here is where capital is moving."
    if any(w in headline_lower for w in ["crash", "plunge", "collapse", "crisis"]):
        return "Behind the selloff: the capital flow signal most are missing."
    if any(w in headline_lower for w in ["surge", "rally", "boom", "breakout"]):
        return "This rally has a capital flow dimension no one is discussing."

    # Pattern 6: Generic — use headline essence, contradiction-first framing
    short = f"{headline[:80]} — the flows tell a different story."
    return short

def send_post(text: str, dry_run: bool = False) -> bool:
    """Send a message to the Telegram channel.

    Text content must already be HTML-escaped (done by format_story).
    HTML tags (<b>, <i>, <a href="...">) are preserved for Telegram's parse_mode=HTML.
    """
    if dry_run:
        print(f"[{now()}] DRY RUN -- would send:\n{text[:300]}...")
        return True

    if not TELEGRAM_BOT_TOKEN:
        print(f"[{now()}] WARNING: TELEGRAM_BOT_TOKEN not set")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode())
            if body.get("ok"):
                msg_id = body.get("result", {}).get("message_id", "?")
                print(f"[{now()}] Telegram: posted message {msg_id} to channel")
                return True
            else:
                print(f"[{now()}] Telegram API error: {body}")
                return False
    except Exception as e:
        print(f"[{now()}] Telegram send failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="CCO Telegram Distributor")
    parser.add_argument("--story-id", type=str, help="Story ID (for logging)")
    parser.add_argument("--headline", type=str, help="Story headline")
    parser.add_argument("--they-say", type=str, default="", help="Consensus claim")
    parser.add_argument("--reality", type=str, default="", help="Contradiction evidence")
    parser.add_argument("--source", type=str, default="", help="Source name")
    parser.add_argument("--contradiction", type=float, default=0, help="Contradiction score")
    parser.add_argument("--confidence", type=float, default=0, help="Confidence percentage")
    parser.add_argument("--direction", type=str, default="", help="Flow direction")
    parser.add_argument("--published-at", type=str, default="", help="Published timestamp (ISO)")
    parser.add_argument("--json", type=str, help="Story JSON string (alternative to individual args)")
    parser.add_argument("--dry-run", action="store_true", help="Format only, don't send")
    parser.add_argument("--skip-freshness", action="store_true",
                       help="Bypass freshness filter (emergency/debug only)")
    args = parser.parse_args()

    if args.json:
        story = json.loads(args.json)
    else:
        story = {
            "story_id": args.story_id or "",
            "headline": args.headline or "Untitled",
            "they_say": args.they_say or "",
            "reality": args.reality or "",
            "source": args.source or "",
            "contradiction_score": args.contradiction,
            "confidence_pct": args.confidence,
            "capital_flow": {"direction": args.direction},
            "published_at": args.published_at or now(),
        }

    # ── Freshness gate ──
    if not args.skip_freshness:
        fresh, reason = is_fresh(story)
        if not fresh:
            print(f"[{now()}] BLOCKED: story not fresh — {reason}")
            sys.exit(2)  # exit 2 = freshness block (distinct from send failure)

    text = format_story(story)
    sent = send_post(text, dry_run=args.dry_run)

    if sent and not args.dry_run and args.story_id:
        # Print for entrypoint to log
        print(f"POSTED:{args.story_id}")

    sys.exit(0 if sent else 1)


if __name__ == "__main__":
    main()
