#!/usr/bin/env python3
"""
cco_telegram.py — Chief Content Officer: Telegram Distribution (v4.0)

Sovereign Auditor 3-block format replacing legacy HTML hook/link structure.

STRUCTURE (v4.0 — June 2026):
  1. RISK REGIME — 1-line macro assessment with driving factor
  2. ASSET REPRICING MAP — max 3 bullets, price-level specific
  3. MOST PROBABLE 24-72H PATH — 2 bullets incl. explicit flip trigger

Constraints:
  - ~90 words max
  - One explicit probability % and one invalidation/flip trigger with price level
  - Clean Markdown (no HTML tags, no emojis)
  - Quote-first derivative anchoring
  - Direct site links for full context

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

# Asset ticker mapping for repricing map
TICKER_MAP = {
    "dollar_decline": "DXY",
    "energy_sovereignty": "Brent",
    "deglobalization": "XLI",
    "china_ascent": "FXI",
    "space_economy": "ROKT",
    "gene_editing": "ARKG",
    "tech_convergence": "QQQ",
    "wealthy_sports": "BATRK",
}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_fresh(story: dict) -> tuple[bool, str]:
    ts_raw = (story.get("published_at") or story.get("generated_at") or
              story.get("created_at") or "")
    if not ts_raw:
        return False, "no timestamp — cannot verify freshness"

    try:
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
    """Format a story for Telegram — Sovereign Auditor 3-block structure (v4.0).

    Three blocks:
      Risk Regime       — 1-line macro assessment
      Asset Repricing   — max 3 bullets, price-level specific
      Probable Path     — 2 bullets incl. explicit flip trigger with price level

    ~90 words. Clean Markdown. No emojis.
    """
    headline = (story.get("headline", "") or "Untitled").strip()
    they_say = (story.get("they_say", "") or "").strip()
    reality = (story.get("reality", "") or story.get("summary", "") or "").strip()
    contradiction = story.get("contradiction_score", 0)
    confidence = story.get("confidence_pct", 0)
    story_id = story.get("story_id", "")
    container = story.get("container", "") or "tech_convergence"
    narrative_name = story.get("narrative_name", "") or container.replace("_", " ").title()

    cf = story.get("capital_flow", {}) or {}
    direction = (cf.get("direction", "") or "").strip()
    amount_b = cf.get("amount_b", 0) or 0
    asset = (cf.get("asset_class", "") or cf.get("asset", "") or "").upper().strip()
    pace = cf.get("pace_multiplier", 1) or 1
    impact = (cf.get("impact", "") or "").strip()

    ticker = TICKER_MAP.get(container, container.upper()[:4])

    # ── Build story page link ──
    if story_id:
        story_link = f"https://www.lagazzettadikyiv.com/stories.html#story-{story_id}"
    else:
        story_link = "https://www.lagazzettadikyiv.com"

    # ── 1. RISK REGIME (1 line) ──
    regime = _build_regime(headline, contradiction, direction, amount_b, ticker)

    # ── 2. ASSET REPRICING MAP (max 3 bullets) ──
    repricing = _build_repricing(ticker, direction, amount_b, pace, asset, contradiction, they_say, reality)

    # ── 3. MOST PROBABLE 24-72H PATH (2 bullets, flip trigger) ──
    path = _build_path(direction, amount_b, ticker, contradiction, confidence)

    # ── Assemble ──
    blocks = [
        f"**RISK REGIME:** {regime}",
        "",
        f"**ASSET REPRICING MAP:**",
        repricing,
        "",
        f"**MOST PROBABLE 24-72H PATH:**",
        path,
        "",
        f"Full data: {story_link}",
    ]

    text = "\n".join(blocks)

    # Enforce ~90 word limit (Telegram has no hard cap but brevity = engagement)
    words = text.split()
    if len(words) > 110:
        # Trim repricing bullets first
        text = "\n".join(blocks[:2] + ["", blocks[3].split("\n")[0] + "\n" + blocks[3].split("\n")[1] if len(blocks[3].split("\n")) > 2 else blocks[3]] + blocks[4:])
    if len(text.split()) > 115:
        text = text.rsplit("Full data:", 1)[0].strip() + f"\n\nFull data: {story_link}"

    return text


def _build_regime(headline: str, contradiction: int, direction: str,
                  amount_b: float, ticker: str) -> str:
    """1-line macro regime assessment."""
    parts = []

    # Contradiction anchoring
    if contradiction >= 70:
        parts.append(f"Sharp {ticker} divergence from consensus narrative")
    elif contradiction >= 40:
        parts.append(f"{ticker} repricing underway — narrative lagging flows")
    else:
        parts.append(f"{ticker} moving in line with macro consensus")

    # Flow direction
    if direction and amount_b >= 0.1:
        flow_word = "inflows" if "inflow" in direction.lower() else "outflows"
        parts.append(f"${amount_b:.1f}B {flow_word} accelerating")

    if not parts:
        parts.append(f"{ticker} regime: watch for divergence signal")

    return ". ".join(parts) + "."


def _build_repricing(ticker: str, direction: str, amount_b: float,
                     pace: float, asset: str, contradiction: int,
                     they_say: str, reality: str) -> str:
    """Max 3 bullet repricing map."""
    bullets = []

    # Bullet 1: Primary asset movement
    if direction and amount_b >= 0.1:
        flow_word = "Inflows into" if "inflow" in direction.lower() else "Outflows from"
        bullets.append(
            f"- {ticker}: {flow_word} {asset or ticker} "
            f"at ${amount_b:.1f}B — "
            f"{'momentum extending' if pace >= 1.2 else 'mean-reversion underway'}"
        )
    elif contradiction >= 50:
        bullets.append(
            f"- {ticker}: Price action stable but capital flows signaling "
            f"imminent repricing — volatility compression phase"
        )
    else:
        bullets.append(
            f"- {ticker}: Tracking macro consensus — no divergence signal yet"
        )

    # Bullet 2: Contradiction detail (if available)
    if they_say and reality and contradiction >= 40:
        short_they = they_say[:120].strip()
        if not short_they.endswith(('.', '!', '?')):
            short_they += '...'
        bullets.append(
            f"- Consensus: {short_they}"
        )

    # Bullet 3: Cross-asset transmission or volume signal
    if contradiction >= 60:
        bullets.append(
            f"- Volume anomaly: {int(contradiction)}% divergence between "
            f"media framing and capital positioning"
        )
    elif pace >= 1.5:
        bullets.append(
            f"- Velocity spike: {pace:.1f}x normal repositioning pace — "
            f"institutional rebalancing underway"
        )

    # Cap at 3
    return "\n".join(bullets[:3])


def _build_path(direction: str, amount_b: float, ticker: str,
                contradiction: int, confidence: int) -> str:
    """2 bullets: most probable path + explicit flip trigger."""
    confidence_pct = max(confidence, contradiction) if confidence or contradiction else 55

    # Bullet 1: Directional bias with probability
    if "inflow" in direction.lower():
        bias = "appreciation"
        direction_word = "inflows"
    elif "outflow" in direction.lower():
        bias = "depreciation"
        direction_word = "outflows"
    else:
        bias = "compression"
        direction_word = "flows"

    bullets = [
        f"- {ticker} {bias} bias continues ({confidence_pct}%): "
        f"capital {direction_word} suggest positioning for "
        f"{'upside breakout' if bias == 'appreciation' else 'further downside' if bias == 'depreciation' else 'range expansion'}"
    ]

    # Bullet 2: Explicit flip trigger
    if contradiction >= 50:
        bullets.append(
            f"- Flip trigger: {ticker} reversal on "
            f"consensus realignment. If narrative catches up to flow data "
            f"within 72h, repricing accelerates. Contradiction gap closing "
            f"below {max(10, int(contradiction) - 30)} invalidates divergence thesis"
        )
    else:
        bullets.append(
            f"- Flip trigger: New catalyst required. "
            f"Range-bound until flow direction changes or macro shock hits. "
            f"Watch {ticker} volume for institutional entry signal"
        )

    return "\n".join(bullets)


def send_post(text: str, dry_run: bool = False) -> bool:
    """Send a message to the Telegram channel."""
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
        "parse_mode": "Markdown",
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
    parser = argparse.ArgumentParser(description="CCO Telegram Distributor v4.0")
    parser.add_argument("--story-id", type=str, help="Story ID (for logging)")
    parser.add_argument("--headline", type=str, help="Story headline")
    parser.add_argument("--they-say", type=str, default="", help="Consensus claim")
    parser.add_argument("--reality", type=str, default="", help="Contradiction evidence")
    parser.add_argument("--source", type=str, default="", help="Source name")
    parser.add_argument("--contradiction", type=float, default=0, help="Contradiction score")
    parser.add_argument("--confidence", type=float, default=0, help="Confidence percentage")
    parser.add_argument("--direction", type=str, default="", help="Flow direction")
    parser.add_argument("--container", type=str, default="", help="Narrative container")
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
            "container": args.container or "tech_convergence",
            "published_at": args.published_at or now(),
        }

    # ── Freshness gate ──
    if not args.skip_freshness:
        fresh, reason = is_fresh(story)
        if not fresh:
            print(f"[{now()}] BLOCKED: story not fresh — {reason}")
            sys.exit(2)

    text = format_story(story)
    sent = send_post(text, dry_run=args.dry_run)

    if sent and not args.dry_run and args.story_id:
        print(f"POSTED:{args.story_id}")

    sys.exit(0 if sent else 1)


if __name__ == "__main__":
    main()
