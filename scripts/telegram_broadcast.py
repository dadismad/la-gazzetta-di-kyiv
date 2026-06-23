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
THROTTLE_HOURS = 4          # Suppress same narrative for 4h
THROTTLE_GAP_JUMP = 15      # ...unless GAP increases by 15+
THROTTLE_PATH = PUBLIC_DATA / "telegram_throttle.json"
FRESHNESS_HOURS = 48


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_posted_ids() -> set:
    """Load confirmed story IDs from the broadcast ledger (JSONL).
    Only returns 'confirmed' entries — ignores 'pending' (intent lock not yet resolved)."""
    if not POSTED_LOG.exists():
        return set()
    ids = set()
    with open(POSTED_LOG) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("status") == "confirmed":
                    ids.add(entry.get("story_id", ""))
                # Legacy: plain story_id lines (pre-intent-lock) — treat as confirmed
            except json.JSONDecodeError:
                ids.add(line)
    return ids


def load_pending_intents() -> dict:
    """Load pending broadcast intents: {story_id: iso_timestamp}.
    These are stories where send_telegram() was called but the response
    was never confirmed (timeout, network failure)."""
    if not POSTED_LOG.exists():
        return {}
    pending = {}
    with open(POSTED_LOG) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("status") == "pending":
                    pending[entry["story_id"]] = entry.get("sent_at", "")
            except json.JSONDecodeError:
                pass
    return pending


def save_pending_intent(story_id: str):
    """Pre-send intent lock: write 'pending' BEFORE calling send_telegram.
    Prevents double-posts on API timeout: if send fails, next cycle sees 'pending'
    and verifies before retrying."""
    entry = json.dumps({
        "story_id": story_id,
        "status": "pending",
        "sent_at": now()
    })
    with open(POSTED_LOG, "a") as f:
        f.write(f"{entry}\n")


def confirm_intent(story_id: str, message_id):
    """After successful Telegram send: write 'confirmed' with message_id.
    Rewrites the ledger line atomically by appending the confirmed entry.
    The load functions only return 'confirmed' entries, so the pending line
    becomes dead weight (pruned periodically)."""
    entry = json.dumps({
        "story_id": story_id,
        "status": "confirmed",
        "message_id": int(message_id) if message_id else 0,
        "sent_at": now()
    })
    with open(POSTED_LOG, "a") as f:
        f.write(f"{entry}\n")


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
                msg_id = body.get("result", {}).get("message_id")
                print(f"[{now()}] Telegram: posted message {msg_id}")
                return msg_id
            else:
                print(f"[{now()}] Telegram API error: {body}")
                return None
    except Exception as e:
        print(f"[{now()}] Telegram send failed: {e}")
        return None


def format_story_for_telegram(story: dict, flow_ledger: dict = None) -> str:
    """Dynamic-layout GapFire Dispatch. Adapts format based on conviction and data profile.
    HIGH/ELEVATED → THE PLAY execution card. SPECULATIVE → lighter signal format. HOLD → skip."""

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

    # ── Tickermap: narrative → best single-name defaults (FALLBACK ONLY) ──
    _ticker_defaults = {
        "dollar_decline": "EURUSD=X", "energy_sovereignty": "XOM",
        "deglobalization": "CAT", "china_ascent": "BABA",
        "space_economy": "RKLB", "gene_editing": "CRSP",
        "tech_convergence": "AAPL", "wealthy_sports": "BATRK",
        "crypto_reserve": "BTC-USD", "rate_cycle": "TLT",
        "ai_chips": "NVDA", "commodity_supercycle": "XOM",
    }

    # ── Resolve ticker: trade_thesis > affected_tickers > narrative default ──
    tt = story.get("trade_thesis")
    has_trade_thesis = bool(tt and tt.get("alpha_trigger"))
    affected = story.get("affected_tickers") or []

    if has_trade_thesis and tt.get("primary_ticker"):
        narrative_ticker = tt["primary_ticker"]
    elif affected:
        narrative_ticker = affected[0]
    else:
        narrative_ticker = _ticker_defaults.get(narrative_id, narrative_id.upper()[:6])

    # ── Flow ledger ──
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
        cap_str = ""

    # ── Extract trade thesis fields ──
    if has_trade_thesis:
        direction = tt.get("direction", "NEUTRAL")
        entry = tt.get("limit_entry_price", tt.get("entry_zone", ""))
        stop = tt.get("stop_loss", "")
        target = tt.get("take_profit", "")
        invalidation = tt.get("invalidation", stop)
        conviction = tt.get("conviction", "SPECULATIVE")
        horizon = int(tt.get("horizon_days", 14))
        alpha = tt.get("alpha_trigger", "")
    else:
        # Legacy: derive from flow ledger
        if dominant_dir == "inflow":
            direction = "LONG"
        elif dominant_dir == "outflow":
            direction = "SHORT"
        else:
            direction = "NEUTRAL"
        entry = ""
        stop = ""
        target = ""
        invalidation = ""
        horizon = 14
        alpha = ""
        conviction = "SPECULATIVE"

    # ── Compute R-multiple ──
    r_multiple = ""
    if entry and stop and target:
        try:
            e = float(str(entry).replace("$","").replace(",",""))
            s = float(str(stop).replace("$","").replace(",",""))
            t = float(str(target).replace("$","").replace(",",""))
            risk = abs(e - s)
            reward = abs(t - e)
            if risk > 0:
                r = round(reward / risk, 1)
                r_multiple = f" | {r}R"
        except (ValueError, TypeError):
            pass

    # ── Conviction emoji ──
    conviction_emoji = {"HIGH": "\U0001f525", "ELEVATED": "\U0001f4c8",
                        "SPECULATIVE": "\U0001f9ea", "HOLD": "\u26a0\ufe0f"}
    c_emoji = conviction_emoji.get(conviction, "")

    # ── Narrative label ──
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

    # ═══════════════════════════════════════════════════════════════
    # DYNAMIC LAYOUT: HIGH/ELEVATED → THE PLAY card
    # ═══════════════════════════════════════════════════════════════
    if conviction in ("HIGH", "ELEVATED") and has_trade_thesis:
        lines = []
        # Curiosity gap hook as opener
        if gap >= 70:
            lines.append(f"\U0001f525 EVERYONE'S WRONG ABOUT {narrative_label}")
        else:
            lines.append(f"\U0001f4c8 CONTRARIAN SIGNAL: {narrative_label}")

        lines.append("")
        lines.append(headline)
        lines.append("")

        # One-line contradiction punch
        if they_say and reality:
            lines.append(f"The retail consensus is trading the narrative, but the capital ledger shows a massive divergence. GAP: {gap}/100.")
        lines.append("")

        # Alpha trigger
        if alpha:
            lines.append(f"{alpha}")
            lines.append("")

        # THE PLAY execution card
        lines.append(f"\U0001f680 THE PLAY: {direction} {narrative_ticker}{r_multiple}")
        if entry:
            lines.append(f"\u2022 Limit Entry: {entry}")
        if stop:
            lines.append(f"\u2022 Stop Loss: {stop}")
        if target:
            lines.append(f"\u2022 Target: {target}")
        if horizon:
            lines.append(f"\u2022 Strategy Window: {horizon} days | Conviction: {conviction} {c_emoji}")
        lines.append("")

        # Why this edge exists
        if alpha:
            lines.append(f"Why this edge exists: {alpha}")
            lines.append("")

        # Tags
        lines.append(f"{gap_to_tag(gap)} #{narrative_id.replace('_','').upper()} #{narrative_ticker}")
        lines.append("")
        lines.append(f"Full brief: {link}")

        return "\n".join(lines)

    # ═══════════════════════════════════════════════════════════════
    # SPECULATIVE: lighter signal format — no fake bull/bear cases
    # ═══════════════════════════════════════════════════════════════
    if conviction == "SPECULATIVE" and has_trade_thesis:
        lines = []
        lines.append(f"\U0001f9ea SIGNAL: {narrative_label} | GAP {gap}/100")
        lines.append("")
        lines.append(headline)
        lines.append("")

        if they_say and reality:
            they_say_short = they_say[:120]
            reality_short = reality[:120]
            lines.append(f"Media says: {they_say_short}")
            lines.append(f"Capital says: {reality_short}")
            lines.append("")

        if alpha:
            lines.append(f"Alpha thesis: {alpha}")
            lines.append("")

        if direction != "NEUTRAL":
            lines.append(f"\U0001f3af {direction} {narrative_ticker}{r_multiple} | Conviction: {conviction}")
            if entry:
                lines.append(f"Entry: {entry}")
            if invalidation:
                lines.append(f"Stop: {invalidation}")
            if target:
                lines.append(f"Target: {target}")
            lines.append("")

        lines.append(f"{gap_to_tag(gap)} #{narrative_id.replace('_','').upper()} #{narrative_ticker}")
        lines.append("")
        lines.append(f"Full brief: {link}")

        return "\n".join(lines)

    # ═══════════════════════════════════════════════════════════════
    # HOLD / no thesis: skip broadcast — return empty
    # ═══════════════════════════════════════════════════════════════
    return ""


def gap_to_tag(gap: int) -> str:
    """Map GAP score to a canonical hashtag."""
    if gap >= 70:
        return "#GAP_ALERT"
    elif gap >= 40:
        return "#GAP_ACTIVE"
    return "#GAP_MONITOR"



def load_throttle_state() -> dict:
    """Load narrative throttle state {narrative_id: (iso_ts, gap)}."""
    try:
        if THROTTLE_PATH.exists():
            with open(THROTTLE_PATH) as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_throttle_state(narrative_id: str, gap: int):
    """Update throttle state for a narrative after posting."""
    state = load_throttle_state()
    state[narrative_id] = [datetime.now(timezone.utc).isoformat(), gap]
    # Prune entries older than 24h
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    state = {k: v for k, v in state.items() 
             if datetime.fromisoformat(v[0]) > cutoff}
    try:
        with open(THROTTLE_PATH, "w") as f:
            json.dump(state, f)
    except Exception:
        pass

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
    # Phase 8c: BREAKING only (GAP > 50) + must carry trade thesis
    recent_stories = [s for s in stories if is_recent(s) 
                      and (s.get("contradiction_gap", 0) or 0) > 50
                      and s.get("trade_thesis")]

    print(f"[{now()}] Stories: {len(stories)} total, {len(recent_stories)} recent, "
          f"{len(posted_ids)} already posted")

    posted_count = 0
    for story in recent_stories:
        if posted_count >= args.max_posts:
            break

        sid = str(story.get("story_id", ""))
        if sid in posted_ids:
            continue

        # Intent lock: skip if this story has a pending intent (prevents double-post
        # on API timeout from a prior cycle that didn't get confirmation).
        pending = load_pending_intents()
        if sid in pending:
            # Check if the pending intent is stale (>10 min)
            pending_ts = pending[sid]
            try:
                pending_age = (datetime.now(timezone.utc) - datetime.fromisoformat(pending_ts)).total_seconds()
                if pending_age < 600:  # < 10 min — could still be in-flight
                    continue
                # Stale pending: the prior attempt failed. Fall through to retry.
                print(f"[{now()}] Retrying stale pending intent for {sid} ({pending_age:.0f}s old)")
            except (ValueError, TypeError):
                pass

        # Phase 8c: Narrative throttle — 4h cooldown unless GAP jumps +15
        narrative_id = story.get("narrative_id", story.get("container", ""))
        gap = int(story.get("contradiction_gap", 0) or 0)
        throttle = load_throttle_state()
        if narrative_id in throttle:
            last_ts, last_gap = throttle[narrative_id]
            hours_ago = (datetime.now(timezone.utc) - datetime.fromisoformat(last_ts)).total_seconds() / 3600
            if hours_ago < THROTTLE_HOURS and gap <= last_gap + THROTTLE_GAP_JUMP:
                continue  # Suppress — same narrative, no material GAP increase

        text = format_story_for_telegram(story, flow_ledger)
        if not text:
            continue  # HOLD conviction or no actionable setup — skip broadcast

        if args.dry_run:
            print(f"\n{'='*60}")
            print(f"[{now()}] DRY RUN — would post story {sid}:")
            print(text)
            print(f"{'='*60}")
            posted_count += 1
            continue

        # PRE-SEND INTENT LOCK: write pending BEFORE the network call.
        # If send_telegram times out but Telegram actually posted, the next
        # cycle will see 'pending' and skip (preventing double-post).
        save_pending_intent(sid)
        msg_id = send_telegram(text)
        if msg_id is not None:
            confirm_intent(sid, msg_id)
            save_throttle_state(narrative_id, gap)
            posted_count += 1
            import time
            time.sleep(3)

    # SIGNAL PULSE: if no Tier 1 alert fired, send heartbeat with top 3 narratives
    if posted_count == 0 and not args.dry_run:
        _pulse_stories = [s for s in stories if (s.get("contradiction_gap", 0) or 0) >= 20][:3]
        if _pulse_stories:
            _lines = []
            for s in _pulse_stories:
                _nid = s.get("narrative_id", s.get("container", ""))
                _gap = int(s.get("contradiction_gap", 0) or 0)
                _dir = (s.get("trade_thesis", {}) or {}).get("direction", "NEUTRAL")
                _arrow = "▲" if _dir == "LONG" else ("▼" if _dir == "SHORT" else "—")
                _cap = (s.get("capital_volume_usd", 0) or 0) / 1e9
                _cap_str = f"${_cap:.1f}B" if abs(_cap) >= 1 else f"${_cap*1000:.0f}M"
                _title = s.get("_container_title", _nid)
                _lines.append(f"{_title:45s} GAP {_gap:>3} {_arrow}  | {_cap_str}")
            _pulse_text = "\U0001f4e1 THE FLOW — " + datetime.now(timezone.utc).strftime("%H:%M") + " Kyiv\n\n" + "\n".join(_lines) + "\n\nlagazzettadikyiv.com?utm_source=telegram&utm_medium=pulse"
            # Throttle: only send pulse once per 2 hours
            import time as _time
            _pulse_path = PUBLIC_DATA / "pulse_sent.json"
            _send_pulse = True
            if _pulse_path.exists():
                try:
                    with open(_pulse_path) as _f:
                        _last = json.load(_f).get("sent_at", "")
                    _age = (datetime.now(timezone.utc) - datetime.fromisoformat(_last)).total_seconds()
                    if _age < 7200:
                        _send_pulse = False
                except Exception:
                    pass
            if _send_pulse and send_telegram(_pulse_text):
                with open(_pulse_path, "w") as _f:
                    json.dump({"sent_at": datetime.now(timezone.utc).isoformat()}, _f)
                print(f"[{now()}] Signal Pulse sent")
                posted_count += 1

    print(f"[{now()}] Broadcast complete: {posted_count} posted")


if __name__ == "__main__":
    main()
