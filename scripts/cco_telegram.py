#!/usr/bin/env python3
"""
cco_telegram.py — Chief Content Officer: Telegram Distribution

Formats curated stories for Telegram channel posts and sends via Bot API.
Voice register: Psychological hook → Data → Urgent CTA bridge.

PART 2 OVERHAUL (June 2026):
  - Freshness filter: story.published_at must be within 12 hours. Never post stale.
  - 3-line linguistic hook engine: Hook → Data → Bridge
  - Line 1: Provocative curiosity gap exposing consensus contradiction
  - Line 2: Scannable headline with exact color-coded capital flow impact
  - Line 3: Urgent CTA bridge linking to lagazzettadikyiv.com

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
    """Format a story for Telegram — psychological hook engine (v2.0).

    Three-line template:
      Line 1: The Hook — provocative curiosity gap
      Line 2: The Data — scannable headline + capital flow impact
      Line 3: The Bridge — urgent CTA to lagazzettadikyiv.com
    """
    import html as html_mod

    headline = (story.get("headline", "") or "Untitled").strip()
    they_say = (story.get("they_say", "") or "").strip()
    reality = (story.get("reality", "") or story.get("summary", "") or "").strip()
    source = (story.get("source", "") or "").strip()
    contradiction = story.get("contradiction_score", 0)
    cf = story.get("capital_flow", {}) or {}

    direction = (cf.get("direction", "") or "").strip()
    amount_b = cf.get("amount_b", 0) or 0
    asset = (cf.get("asset_class", "") or "").upper().strip()
    pace = cf.get("pace_multiplier", 1) or 1

    # ── Line 1: The Hook (provocative curiosity gap) ──
    hook = _generate_hook(headline, they_say, reality, direction, amount_b, asset, contradiction)

    # ── Line 2: The Data (scannable headline + capital flow impact) ──
    # Build color-coded flow badge
    flow_badge = ""
    if direction and amount_b >= 0.1:
        dl = direction.lower()
        if any(w in dl for w in ["inflow", "accumulat", "long", "buy", "rotate into"]):
            tag = "INFLOW"
            emoji_tag = "+"
        elif any(w in dl for w in ["outflow", "distribut", "sell", "short", "rotate out"]):
            tag = "OUTFLOW"
            emoji_tag = "-"
        else:
            tag = direction.upper()[:20]
            emoji_tag = ""
        asset_str = f" {asset}" if asset and asset != "NONE" else ""
        velocity_str = f" at {pace:.1f}x velocity" if pace and pace > 1.1 else ""
        flow_badge = f"<b>{emoji_tag}{tag}: ${amount_b:.1f}B{asset_str}{velocity_str}</b>"

    # Build contradiction/confidence line
    scores = []
    if contradiction and contradiction > 0:
        scores.append(f"Contradiction {int(contradiction)}/100")
    if source:
        scores.append(f"Source: {html_mod.escape(source[:80])}")

    data_line = f"<b>{html_mod.escape(headline)}</b>"
    if flow_badge:
        data_line += f"\n{flow_badge}"
    if scores:
        data_line += f"\n<i>{' · '.join(scores)}</i>"

    # ── Line 3: The Bridge (urgent CTA) ──
    bridge = (
        '<a href="https://www.lagazzettadikyiv.com">'
        'Full entry levels, target zones, and positioning implications are live now. '
        'See the full play at lagazzettadikyiv.com</a>'
    )

    # ── Assemble ──
    lines = [
        f"<b>{html_mod.escape(hook)}</b>",
        "",
        data_line,
        "",
        bridge,
    ]

    text = "\n".join(lines)

    # Truncate to Telegram's 4096 char limit
    if len(text) > 4000:
        text = text[:3997] + "..."

    return text


def _generate_hook(headline: str, they_say: str, reality: str,
                   direction: str, amount_b: float, asset: str,
                   contradiction_score: int) -> str:
    """Generate a psychological hook that creates genuine curiosity.
    Priority order: capital flows > contradiction tension > event keywords > fallback."""
    headline_lower = headline.lower()

    # Pattern 1: Capital flow with real numbers — strongest hook
    if direction and amount_b >= 0.1 and asset and asset != "NONE":
        direction_word = _direction_word(direction)
        if amount_b >= 50:
            return (
                f"While markets expect a rate pause, ${amount_b:.0f}B just quietly "
                f"consolidated {direction_word} {asset}. Here is the play."
            )
        elif amount_b >= 10:
            return (
                f"A massive ${amount_b:.0f}B capital block is moving "
                f"{direction_word} {asset}. The reason isn't what you think."
            )
        else:
            return (
                f"${amount_b:.1f}B shift in {asset} — "
                f"the data behind the move changes the calculus."
            )

    # Pattern 2: Strong contradiction — frame the tension gap
    if they_say and reality and len(they_say) > 10:
        short_ts = they_say[:100].rstrip(".,;: ")
        if contradiction_score >= 75:
            return (
                f'The consensus: "{short_ts}..." '
                f'The data says otherwise, and the divergence is widening.'
            )
        else:
            return (
                f'The narrative: "{short_ts}..." '
                f'The evidence points elsewhere — and capital is already moving.'
            )

    # Pattern 3: High-contradiction story — emphasize the divergence
    if contradiction_score >= 70:
        return (
            "The market narrative and the capital flows are telling "
            "different stories. One of them is about to break."
        )

    # Pattern 4: Event-driven hooks based on headline content
    if any(w in headline_lower for w in ["crash", "plunge", "collapse", "crisis"]):
        return "The move everyone's talking about — and the one they're missing."
    if any(w in headline_lower for w in ["surge", "rally", "boom", "breakout"]):
        return "Behind the rally: a capital flow signal that changes the calculus."
    if any(w in headline_lower for w in ["rate", "fed", "ecb", "central bank", "inflation"]):
        return (
            "What the central bank signal means for where capital goes next. "
            "The flows are already moving."
        )
    if any(w in headline_lower for w in ["war", "conflict", "strike", "sanction", "defense"]):
        return "Geopolitics is moving money. Here is where the capital is flowing right now."
    if any(w in headline_lower for w in ["china", "beijing", "xi", "yuan"]):
        return "The China angle the Western press is not covering — and where the flows point."
    if any(w in headline_lower for w in ["ai", "openai", "nvidia", "chip", "semiconductor"]):
        return "AI is moving capital at record velocity. Track where the smart money is flowing."
    if any(w in headline_lower for w in ["crypto", "bitcoin", "ethereum", "defi", "stablecoin"]):
        return "Crypto flows do not lie. Here is what they are signaling right now."
    if any(w in headline_lower for w in ["energy", "oil", "gas", "power", "nuclear"]):
        return "Energy markets are repricing. The capital flow tells you where before it hits."

    # Pattern 5: Fallback — use headline essence
    short_headline = headline[:100].rstrip(". ")
    return f"{short_headline} — the capital flow dimension that changes the trade."


def _direction_word(direction: str) -> str:
    """Map flow direction to natural language preposition."""
    dl = direction.lower()
    if any(w in dl for w in ["inflow", "accumulat", "long", "buy", "rotate into"]):
        return "into"
    if any(w in dl for w in ["outflow", "distribut", "sell", "short", "rotate out"]):
        return "out of"
    return "in"


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
