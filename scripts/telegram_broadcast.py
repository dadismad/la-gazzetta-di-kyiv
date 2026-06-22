#!/usr/bin/env python3
"""
telegram_broadcast.py -- Governor pipeline step for Telegram content distribution.

Picks the top 1-2 highest-contradiction stories from the current cycle's output,
formats them using cco_telegram.py's Sovereign Auditor 3-block format, and posts
to the configured Telegram channel.

Idempotent: Tracks posted story_ids in public/data/posted_stories.jsonl.
Freshness filter: Only posts stories generated within the last 2 hours.

Usage:
  python3 scripts/telegram_broadcast.py
  python3 scripts/telegram_broadcast.py --max-posts 2
  python3 scripts/telegram_broadcast.py --dry-run
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path


PROJECT = Path(__file__).resolve().parent.parent
PUBLIC_DATA = PROJECT / "public" / "data"
SCRIPTS_DIR = PROJECT / "scripts"
POSTED_LOG = PUBLIC_DATA / "posted_stories.jsonl"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "-1003990434181")

MAX_POSTS = 2
FRESHNESS_HOURS = 48


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_posted_ids() -> set:
    """Load previously posted story IDs for idempotency."""
    if not POSTED_LOG.exists():
        return set()
    ids = set()
    with open(POSTED_LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                ids.add(line)
    return ids


def save_posted_id(story_id: str):
    """Append a posted story ID to the idempotency log."""
    with open(POSTED_LOG, "a") as f:
        f.write(f"{story_id}\n")


def load_flow_ledger() -> dict:
    """Load flows.json for per-narrative capital aggregation.
    Returns dict keyed by narrative_id with total_capital_b, dominant_direction, etc.
    Used by GapFire dispatch to show real $XB numbers instead of story-level defaults."""
    path = PUBLIC_DATA / "flows.json"
    if not path.exists():
        print(f"[{now()}] flows.json not found at {path}")
        return {}
    try:
        with open(path) as f:
            data = json.load(f)
        return data.get("narrative_flows", {})
    except Exception as e:
        print(f"[{now()}] ERROR loading flows.json: {e}")
        return {}


def load_stories() -> list:
    """Load all stories from stories.json, sorted by contradiction gap desc."""
    path = PUBLIC_DATA / "stories.json"
    if not path.exists():
        print(f"[{now()}] stories.json not found at {path}")
        return []

    with open(path) as f:
        data = json.load(f)

    stories = data.get("all_stories", [])
    # Sort by contradiction_gap descending
    stories.sort(key=lambda s: s.get("contradiction_gap", 0) or 0, reverse=True)
    return stories


def is_recent(story: dict) -> bool:
    """Check if story was generated within the freshness window."""
    ts = story.get("generated_at", "")
    if not ts:
        return False
    try:
        ts_clean = ts.replace("Z", "+00:00")
        generated = datetime.fromisoformat(ts_clean)
    except (ValueError, TypeError):
        return False
    cutoff = datetime.now(timezone.utc) - timedelta(hours=FRESHNESS_HOURS)
    return generated >= cutoff


def send_telegram(text: str) -> bool:
    """Send a message to the configured Telegram channel."""
    if not TELEGRAM_BOT_TOKEN:
        print(f"[{now()}] WARNING: TELEGRAM_BOT_TOKEN not set")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode())
            if body.get("ok"):
                msg_id = body.get("result", {}).get("message_id", "?")
                print(f"[{now()}] Telegram: posted message {msg_id}")
                return True
            else:
                print(f"[{now()}] Telegram API error: {body}")
                return False
    except Exception as e:
        print(f"[{now()}] Telegram send failed: {e}")
        return False


def format_story_for_telegram(story: dict, flow_ledger: dict = None) -> str:
    """Phase B2 — 6-block GapFire Dispatch with real capital numbers from flows.json.
    Falls back to story-level fields if flow_ledger unavailable."""

    if flow_ledger is None:
        flow_ledger = {}

    headline = (story.get("headline", "") or "Untitled")[:100]
    they_say = (story.get("they_say", "") or "")[:150]
    reality = (story.get("reality", "") or "")[:150]
    gap = int(story.get("contradiction_gap", 0) or 0)
    story_id = story.get("story_id", "")
    narrative_id = story.get("narrative_id", story.get("container", "unclassified"))
    source_name = story.get("feed_source", story.get("source_name", ""))
    tier = story.get("tier", "")

    # ── Pre-resolve ticker (needed before trade_thesis check) ──
    ticker_map = {
        "dollar_decline": "DXY", "energy_sovereignty": "CL=F", "deglobalization": "XLI",
        "china_ascent": "FXI", "space_economy": "ROKT", "gene_editing": "ARKG",
        "tech_convergence": "QQQ", "wealthy_sports": "BATRK", "crypto_reserve": "BTC-USD",
        "rate_cycle": "TLT", "ai_chips": "NVDA", "commodity_supercycle": "DBC",
    }
    ticker = ticker_map.get(narrative_id, narrative_id.upper()[:6])

    # ── Phase B1 integration: story-level trade_thesis takes priority ──
    tt = story.get("trade_thesis")
    has_trade_thesis = bool(tt and tt.get("alpha_trigger"))

    # ── Phase B2: pull REAL capital numbers from flow ledger ──
    flow_entry = flow_ledger.get(narrative_id, {})
    capital_total_b = flow_entry.get("total_capital_b", 0) or 0
    dominant_dir = flow_entry.get("dominant_direction", "")
    avg_gap = flow_entry.get("avg_contradiction_gap", 0) or 0
    story_count = flow_entry.get("story_count", 0) or 0

    # ── Capital formatting ──
    if capital_total_b >= 1:
        cap_str = f"${capital_total_b:.1f}B"
    elif capital_total_b > 0:
        cap_str = f"${capital_total_b*1000:.0f}M"
    else:
        cap_str = "N/A — data pending"

    if has_trade_thesis:
        # Story-level trade thesis overrides flow-ledger defaults
        direction = tt.get("direction", "NEUTRAL")
        ticker_override = tt.get("primary_ticker", ticker)
        entry = tt.get("limit_entry_price", tt.get("entry_zone", "current levels"))
        stop = tt.get("stop_loss", "")
        target = tt.get("take_profit", "")
        invalidation = tt.get("invalidation", "")
        conviction = tt.get("conviction", "SPECULATIVE")
        horizon = int(tt.get("horizon_days", 14))
        alpha = tt.get("alpha_trigger", "")
        source_tag = "Source: DeepSeek trade thesis"
        flow_str = f"Story-level thesis ({direction} {ticker_override})"
        # Use the trade thesis ticker
        narrative_ticker = ticker_override
    else:
        # Flow-ledger defaults for legacy stories
        if dominant_dir == "inflow":
            direction = "LONG"
            flow_str = f"Net inflow {cap_str}"
        elif dominant_dir == "outflow":
            direction = "SHORT"
            flow_str = f"Net outflow {cap_str}"
        else:
            direction = "NEUTRAL"
            flow_str = f"Neutral flow — {cap_str} tracked, no dominant direction"
        entry = ""
        invalidation = ""
        horizon = 14
        alpha = ""
        conviction = "MODERATE" if gap >= 40 else "SPECULATIVE"
        source_tag = f"Source: flows.json aggregate ({story_count} stories, avg GAP {avg_gap:.0f})"
        narrative_ticker = ticker

    # ── Narrative + ticker mapping ──
    narrative_labels = {
        "dollar_decline": "DOLLAR DECLINE", "energy_sovereignty": "ENERGY SOVEREIGNTY",
        "deglobalization": "DEGLOBALIZATION", "china_ascent": "CHINA ASCENT",
        "space_economy": "SPACE ECONOMY", "gene_editing": "GENE EDITING",
        "tech_convergence": "TECH CONVERGENCE", "wealthy_sports": "WEALTHY SPORTS",
        "crypto_reserve": "CRYPTO RESERVE", "rate_cycle": "RATE CYCLE",
        "ai_chips": "AI CHIPS", "commodity_supercycle": "COMMODITY SUPERCYCLE",
    }
    narrative_label = narrative_labels.get(narrative_id, narrative_id.upper().replace("_", " "))

    link = "https://www.lagazzettadikyiv.com"
    they_say_short = they_say[:120] if they_say else "Media narrative pending"
    reality_short = reality[:120] if reality else "Capital reality pending"

    lines = []
    lines.append("\u2501" * 46)
    lines.append(f"\u26a1 GAP {gap} | {narrative_label}")
    lines.append("\u2501" * 46)
    lines.append("")
    lines.append(headline)
    lines.append("")
    lines.append(f"\U0001f4b0 CAPITAL FLOW: {cap_str} tracked across {story_count} stories in {narrative_label} ({narrative_ticker})")
    lines.append(f"   \u25a0 {flow_str} | Avg narrative GAP: {avg_gap:.0f}/100 | Conviction: {conviction}")
    lines.append(f"   \u25a0 {source_tag}")
    lines.append("")
    lines.append("\u26a1 CONTRADICTION:")
    lines.append(f"   Media says: {they_say_short}")
    lines.append(f"   Capital says: {reality_short}")
    lines.append("")
    lines.append(f"\U0001f4ca TWO VIEWS:")
    if has_trade_thesis and alpha:
        lines.append(f"   Alpha trigger: {alpha}")
        lines.append(f"   Entry: {entry} | Invalidation: {invalidation}")
    elif direction == "LONG":
        lines.append(f"   Bull case: {narrative_ticker} capital inflows of {cap_str} signal institutional conviction "
                     f"despite media narrative. Momentum favors continuation to the upside.")
        lines.append(f"   Bear case: If media narrative proves correct and triggers reversal, "
                     f"{narrative_ticker} faces repricing risk as GAP {gap} closes. Tight stops required.")
    elif direction == "SHORT":
        lines.append(f"   Bear case: {cap_str} in outflows confirm institutional exit despite bullish media. "
                     f"Downside pressure likely to persist.")
        lines.append(f"   Bull case: If media narrative prevails and inflows resume, "
                     f"short positions face squeeze risk. Monitor {narrative_ticker} for reversal signals.")
    else:
        lines.append(f"   Bull case: If capital flows break decisively above {cap_str}, "
                     f"{narrative_ticker} enters momentum phase — follow the money.")
        lines.append(f"   Bear case: If GAP {gap} holds and narrative intensifies, "
                     f"expect volatility spike. Straddle/strangle opportunity.")
    lines.append("")
    lines.append(f"\U0001f3af THE BET:")
    if has_trade_thesis:
        lines.append(f"   {direction} {narrative_ticker} | Conviction: {conviction} | Horizon: {horizon} days")
        if entry:
            lines.append(f"   Entry: {entry}")
        if invalidation:
            lines.append(f"   Stop: {invalidation}")
    else:
        lines.append(f"   {direction} {narrative_ticker} | Conviction: {conviction}")
        lines.append(f"   Horizon: 14 days | {source_tag}")
    lines.append("")
    lines.append(f"{gap_to_tag(gap)} #{narrative_id.replace('_','').upper()} #{narrative_ticker}")
    lines.append("")
    lines.append(f"Full data: {link}")

    return "\n".join(lines)


def gap_to_tag(gap: int) -> str:
    """Map GAP score to a canonical hashtag."""
    if gap >= 70:
        return "#GAP_ALERT"
    elif gap >= 40:
        return "#GAP_ACTIVE"
    return "#GAP_MONITOR"


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Telegram broadcast -- governor pipeline step")
    ap.add_argument("--max-posts", type=int, default=MAX_POSTS,
                    help=f"Max posts per cycle (default: {MAX_POSTS})")
    ap.add_argument("--dry-run", action="store_true",
                    help="Preview only, don't send")
    args = ap.parse_args()

    stories = load_stories()
    if not stories:
        print(f"[{now()}] No stories to broadcast.")
        return

    flow_ledger = load_flow_ledger()
    if flow_ledger:
        narratives_with_capital = sum(1 for v in flow_ledger.values() if v.get("total_capital_b", 0) > 0)
        print(f"[{now()}] Flow ledger loaded: {len(flow_ledger)} narratives, "
              f"{narratives_with_capital} with real capital")
    else:
        print(f"[{now()}] WARNING: Flow ledger unavailable — GapFire will show N/A")

    posted_ids = load_posted_ids()
    recent_stories = [s for s in stories if is_recent(s)]

    print(f"[{now()}] Stories: {len(stories)} total, {len(recent_stories)} recent, "
          f"{len(posted_ids)} already posted")

    posted_count = 0
    for story in recent_stories:
        if posted_count >= args.max_posts:
            break

        sid = str(story.get("story_id", ""))
        if sid in posted_ids:
            continue

        text = format_story_for_telegram(story, flow_ledger)

        if args.dry_run:
            print(f"\n{'='*60}")
            print(f"[{now()}] DRY RUN — would post story {sid}:")
            print(text)
            print(f"{'='*60}")
            posted_count += 1
            continue

        if send_telegram(text):
            save_posted_id(sid)
            posted_count += 1
            # Rate limit: 1 post per 3 seconds
            import time
            time.sleep(3)

    print(f"[{now()}] Broadcast complete: {posted_count} posted")


if __name__ == "__main__":
    main()
