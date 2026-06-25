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
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from zoneinfo import ZoneInfo
from pathlib import Path


PROJECT = Path(__file__).resolve().parent.parent
PUBLIC_DATA = PROJECT / "public" / "data"
SCRIPTS_DIR = PROJECT / "scripts"
POSTED_LOG = PUBLIC_DATA / "posted_stories.jsonl"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_BROADCAST_CHAT_ID", os.environ.get("TELEGRAM_CHAT_ID", "-1003990434181"))

MAX_POSTS = 3
THROTTLE_HOURS = 4          # Suppress same narrative for 4h
THROTTLE_GAP_JUMP = 15      # ...unless GAP increases by 15+
THROTTLE_PATH = PUBLIC_DATA / "telegram_throttle.json"

# Format rotation: prevents identical formats in a single cycle
FALLBACK_FORMAT = {
    "THE_PLAY": "CAPITAL_VS_MEDIA",
    "STRUCTURAL_SHIFT": "CONTRADICTION_HOOK",
    "CONTRADICTION_HOOK": "CAPITAL_VS_MEDIA",
    "CAPITAL_VS_MEDIA": "CONTRADICTION_HOOK"
}
FRESHNESS_HOURS = 48


def now() -> str:
    return datetime.now(ZoneInfo("Europe/Kyiv")).strftime("%Y-%m-%dT%H:%M:%SZ")


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
                if isinstance(entry, dict) and entry.get("status") == "confirmed":
                    ids.add(entry.get("story_id", ""))
                elif isinstance(entry, dict) and entry.get("status") == "pending":
                    continue  # Skip pending intents
                elif isinstance(entry, (int, str)):
                    # Legacy: plain story_id lines (pre-intent-lock) — treat as confirmed
                    ids.add(str(entry))
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
                if isinstance(entry, dict) and entry.get("status") == "pending":
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
    cutoff = datetime.now(ZoneInfo("Europe/Kyiv")) - timedelta(hours=FRESHNESS_HOURS)
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


def words_truncate(text: str, max_words: int) -> str:
    """Truncate to first N words. Always ends at word boundary for natural reading."""
    text = (text or "").strip()
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "…"


def smart_truncate(text: str, max_chars: int) -> str:
    """Truncate at sentence boundary, falling back to word boundary. Appends … if cut."""
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    # Try sentence boundary: .!? followed by space or quote+space or end
    truncated = text[:max_chars]
    for end_char in (". ", "! ", "? ", '." ', '!" ', '?" ', ".' ", "!' ", "?' "):
        idx = truncated.rfind(end_char)
        if idx > max_chars * 0.4:  # at least 40% of limit — don't cut on first word
            return truncated[:idx + 1] + "…"
    # Fallback: word boundary
    last_space = truncated.rfind(" ")
    if last_space > max_chars * 0.4:
        return truncated[:last_space] + "…"
    # Last resort: hard cut with ellipsis
    return truncated.rstrip() + "…"


def format_story_for_telegram(story: dict, flow_ledger: dict = None, used_formats: set = None) -> str:
    """5-format deterministic dispatch. Format selected by asset_class x conviction tier.
    THE PLAY (equity + HIGH/ELEVATED) | STRUCTURAL SHIFT (commodity/crypto + HIGH/ELEVATED)
    CAPITAL VS MEDIA (any + ELEVATED/SPECULATIVE) | HOLD -> skip."""

    if flow_ledger is None:
        flow_ledger = {}

    headline = words_truncate(story.get("headline", "") or "Untitled", 15)
    they_say = story.get("they_say", "") or ""
    reality = story.get("reality", "") or ""
    gap = int(story.get("contradiction_gap", 0) or 0)
    narrative_id = story.get("narrative_id", story.get("container", "unclassified"))

    # ── Asset class routing ──
    ASSET_CLASS = {
        "critical_resource_control": "commodity", "commodity_supercycle": "commodity",
        "ai_chips": "equity", "tech_convergence": "equity", "space_economy": "equity",
        "gene_editing": "equity", "wealthy_sports": "equity",
        "deglobalization": "macro", "dollar_decline": "macro", "rate_cycle": "macro",
        "china_ascent": "macro", "crypto_reserve": "crypto",
    }
    asset_class = ASSET_CLASS.get(narrative_id, "macro")

    # ── Ticker resolution ──
    _ticker_defaults = {
        "dollar_decline": "EURUSD=X", "critical_resource_control": "XOM",
        "deglobalization": "CAT", "china_ascent": "BABA",
        "space_economy": "RKLB", "gene_editing": "CRSP",
        "tech_convergence": "AAPL", "wealthy_sports": "BATRK",
        "crypto_reserve": "BTC-USD", "rate_cycle": "TLT",
        "ai_chips": "NVDA", "commodity_supercycle": "XOM",
    }

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
    if capital_total_b >= 1:
        cap_str = f"${capital_total_b:.1f}B"
    elif capital_total_b > 0:
        cap_str = f"${capital_total_b*1000:.0f}M"
    else:
        cap_str = ""

    # ── Trade thesis fields ──
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
        direction = "NEUTRAL"; entry = ""; stop = ""; target = ""
        invalidation = ""; horizon = 14; alpha = ""; conviction = "SPECULATIVE"

    # ── R-multiple ──
    r_multiple = ""
    if entry and stop and target:
        try:
            e = float(str(entry).replace("$","").replace(",",""))
            s = float(str(stop).replace("$","").replace(",",""))
            t = float(str(target).replace("$","").replace(",",""))
            risk = abs(e - s); reward = abs(t - e)
            if risk > 0: r_multiple = f" | {round(reward/risk,1)}R"
        except (ValueError, TypeError): pass

    # ── Labels ──
    conviction_emoji = {"HIGH": "🔥", "ELEVATED": "📈",
                        "SPECULATIVE": "🧪", "HOLD": "⚠️"}
    c_emoji = conviction_emoji.get(conviction, "")

    narrative_labels = {
        "dollar_decline": "Sovereign Liquidity Migration", "critical_resource_control": "Energy Sovereignty",
        "deglobalization": "Industrial Reshoring", "china_ascent": "Eurasia Capital Architecture",
        "space_economy": "Orbital Industrialization", "gene_editing": "Longevity & Bioreality",
        "tech_convergence": "Enterprise Intelligence", "wealthy_sports": "Trophy Asset Financialization",
        "crypto_reserve": "Decentralized Capital", "rate_cycle": "Liquidity Regime Transition",
        "ai_chips": "Compute Hegemony", "commodity_supercycle": "Physical Resource Revaluation",
    }
    narrative_label = narrative_labels.get(narrative_id, narrative_id.upper().replace("_", " "))
    link = "https://www.lagazzettadikyiv.com"

    # ── Format selection ──
    if not has_trade_thesis:
        return ""

    if conviction in ("HIGH", "ELEVATED") and asset_class == "equity":
        fmt = "THE_PLAY"
    elif conviction in ("HIGH", "ELEVATED") and asset_class in ("commodity", "crypto"):
        fmt = "STRUCTURAL_SHIFT"
    elif conviction in ("HIGH", "ELEVATED") and they_say and reality and len(they_say) < 300 and len(reality) < 300:
        # CONTRADICTION HOOK: clean quotable they_say vs reality → Scene/Tension/Insight/Resolution
        fmt = "CONTRADICTION_HOOK"
    elif conviction in ("ELEVATED", "SPECULATIVE"):
        fmt = "CAPITAL_VS_MEDIA"
    else:
        return ""

    # ── Format rotation: if primary format already used, fall back ──
    if used_formats is not None:
        if fmt in used_formats and fmt in FALLBACK_FORMAT:
            fmt = FALLBACK_FORMAT[fmt]
        used_formats.add(fmt)

    # ══════════════════════════════════════════════════════════
    # FORMAT: THE PLAY — equity single-name execution card
    # ══════════════════════════════════════════════════════════
    if fmt == "THE_PLAY":
        lines = []
        _nmc = _nmc_str(narrative_id)
        if gap >= 75:
            lines.append(f"🔥 THE PLAY: {direction} {narrative_ticker}{r_multiple}" + (f" | {_nmc} in play" if _nmc else ""))
        else:
            lines.append(f"📈 THE PLAY: {direction} {narrative_ticker}{r_multiple}" + (f" | {_nmc} in play" if _nmc else ""))
        lines.append("")
        lines.append(headline)
        lines.append("")
        if they_say and reality:
            lines.append(f"📰 MEDIA: {words_truncate(they_say, 20)}")
            lines.append(f"💰 CAPITAL: {words_truncate(reality, 20)}")
            lines.append("")
        if alpha:
            lines.append(f"💡 THESIS: {alpha}")
            lines.append("")
        lines.append(f"🎯 {direction} {narrative_ticker} @ {entry}" if entry else f"🎯 {direction} {narrative_ticker}")
        if stop: lines.append(f"• Stop: {stop}")
        if target: lines.append(f"• Target: {target}")
        if invalidation: lines.append(f"• Invalidation: {invalidation}")
        lines.append(f"⏱ {horizon}d | Conviction: {conviction} {c_emoji} | {narrative_label}")
        src = story.get("source_name", story.get("feed_source", ""))
        if src: lines.append(f"📦 Source: {src}")
        lines.append("")
        lines.append(f"{gap_to_tag(gap)} #{narrative_id.replace('_','').upper()} #{narrative_ticker}")
        lines.append("")
        lines.append(f"Full brief: {link}")
        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════
    # FORMAT: STRUCTURAL SHIFT — commodity/crypto dislocation
    # ══════════════════════════════════════════════════════════
    if fmt == "STRUCTURAL_SHIFT":
        lines = []
        _nmc = _nmc_str(narrative_id)
        direction_word = {"LONG": "BID", "SHORT": "PRESSURE", "NEUTRAL": "FLUX"}
        dw = direction_word.get(direction, "FLUX")
        lines.append(f"📊 STRUCTURAL {dw}: {narrative_label}" + (f" | {_nmc} in play" if _nmc else ""))
        lines.append("")
        lines.append(headline)
        lines.append("")
        if they_say and reality:
            lines.append(f"📰 Consensus: {words_truncate(they_say, 18)}")
            lines.append(f"📈 Flow data: {words_truncate(reality, 18)}")
            lines.append("")
        if cap_str:
            lines.append(f"💴 Capital at stake: {cap_str} | GAP: {gap}/100")
            lines.append("")
        if alpha:
            lines.append(f"💡 {alpha}")
            lines.append("")
        if direction != "NEUTRAL":
            lines.append(f"🎯 {direction} {narrative_ticker}{r_multiple} | {conviction} {c_emoji}")
            if entry: lines.append(f"• Entry zone: {entry}")
            if stop: lines.append(f"• Stop: {stop}")
            if target: lines.append(f"• Target: {target}")
            lines.append("")
        lines.append(f"{gap_to_tag(gap)} #{narrative_id.replace('_','').upper()} #{narrative_ticker}")
        lines.append("")
        lines.append(f"Full brief: {link}")
        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════
    # FORMAT: CONTRADICTION HOOK — Scene→Tension→Insight→Resolution
    # Trigger: HIGH/ELEVATED with clean quotable they_say vs reality
    # ══════════════════════════════════════════════════════════
    if fmt == "CONTRADICTION_HOOK":
        lines = []
        # SCENE (35%) — the consensus narrative
        lines.append(f"🗞️ THE SCENE: {words_truncate(they_say, 22)}")
        lines.append("")
        # TENSION (35%) — the capital-ledger contradiction
        lines.append(f"⚡ THE TENSION: Yet, the capital ledger shows {words_truncate(reality, 22)}")
        lines.append("")
        # INSIGHT (15%) — what the gap means
        if gap >= 75:
            lines.append(f"🧠 THE INSIGHT: The market isn't pricing the narrative—it's pricing the opposite. GAP {gap}/100.")
        else:
            lines.append(f"🧠 THE INSIGHT: The consensus narrative and institutional positioning are diverging fast. GAP {gap}/100.")
        lines.append("")
        # RESOLUTION (15%) — the action
        if direction != "NEUTRAL":
            lines.append(f"🎯 THE RESOLUTION: {direction} {narrative_ticker}{r_multiple}")
            if entry: lines.append(f"• Entry: {entry}")
            if stop: lines.append(f"• Stop: {stop}")
            if target: lines.append(f"• Target: {target}")
        else:
            lines.append(f"🎯 THE RESOLUTION: Watch {narrative_ticker} for the break. {conviction} conviction {c_emoji}")
        lines.append("")
        lines.append(f"{gap_to_tag(gap)} #{narrative_id.replace('_','').upper()}")
        lines.append("")
        lines.append(f"Full brief: {link}")
        return "\\n".join(lines)

    # ══════════════════════════════════════════════════════════
    # FORMAT: CAPITAL VS MEDIA — contradiction duel
    # ══════════════════════════════════════════════════════════
    if fmt == "CAPITAL_VS_MEDIA":
        lines = []
        _nmc = _nmc_str(narrative_id)
        lines.append(f"🧪 CAPITAL vs MEDIA: {narrative_label} | GAP {gap}/100" + (f" | {_nmc} in play" if _nmc else ""))
        lines.append("")
        lines.append(headline)
        lines.append("")
        if they_say and reality:
            lines.append(f"📺 Media says: {words_truncate(they_say, 18)}")
            lines.append(f"💰 Capital says: {words_truncate(reality, 18)}")
            lines.append("")
        if cap_str:
            lines.append(f"📊 Flow: {cap_str} | Conviction: {conviction} {c_emoji}")
            lines.append("")
        if alpha:
            lines.append(f"💡 Alpha thesis: {alpha}")
            lines.append("")
        if direction != "NEUTRAL":
            lines.append(f"🎯 {direction} {narrative_ticker}{r_multiple}")
            if entry: lines.append(f"• Entry: {entry}")
            if stop: lines.append(f"• Stop: {stop}")
            if target: lines.append(f"• Target: {target}")
            lines.append("")
        lines.append(f"{gap_to_tag(gap)} #{narrative_id.replace('_','').upper()}")
        lines.append("")
        lines.append(f"Full brief: {link}")
        return "\n".join(lines)

    return ""



# ── NMC data loader ──────────────────────────────────────────────
def _load_nmc_cache():
    """Load narrative_cap.json for Capital-in-Play context. Returns {} on failure."""
    try:
        p = Path(__file__).resolve().parent.parent / "data" / "narrative_cap.json"
        if p.exists():
            with open(p) as f:
                return json.load(f)
    except Exception:
        pass
    return {}

NMC_CACHE = _load_nmc_cache()

def _nmc_str(narrative_id: str) -> str:
    """Return a formatted NMC string like '$5.56T' or empty string."""
    cap = (NMC_CACHE.get(narrative_id, {}) or {}).get("narrative_cap_usd", 0) or 0
    if cap >= 1_000_000_000_000:
        return f"${cap / 1e12:.2f}T"
    elif cap >= 1_000_000_000:
        return f"${cap / 1e9:.1f}B"
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
    state[narrative_id] = [datetime.now(ZoneInfo("Europe/Kyiv")).isoformat(), gap]
    # Prune entries older than 24h
    cutoff = datetime.now(ZoneInfo("Europe/Kyiv")) - timedelta(hours=24)
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
    used_formats = set()
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
                pending_age = (datetime.now(ZoneInfo("Europe/Kyiv")) - datetime.fromisoformat(pending_ts)).total_seconds()
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
            hours_ago = (datetime.now(ZoneInfo("Europe/Kyiv")) - datetime.fromisoformat(last_ts)).total_seconds() / 3600
            if hours_ago < THROTTLE_HOURS and gap <= last_gap + THROTTLE_GAP_JUMP:
                continue  # Suppress — same narrative, no material GAP increase

        text = format_story_for_telegram(story, flow_ledger, used_formats)
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

    # ── MACRO BRIEFING: bundle 3+ SETTLING/ACTIVE stories by narrative ──
    # Fires at 09:00, 14:00, 19:00 Kyiv time. Groups unposted stories
    # by narrative_id and posts thematic roll-ups when ≥3 coalesce.
    if not args.dry_run:
        _kyiv_hour = datetime.now(ZoneInfo("Europe/Kyiv")).hour
        if _kyiv_hour in (9, 14, 19):
            _briefing_path = PUBLIC_DATA / "briefing_sent.json"
            _last_briefing = ""
            if _briefing_path.exists():
                try:
                    with open(_briefing_path) as _f:
                        _last_briefing = json.load(_f).get("sent_at", "")
                except: pass
            _today = datetime.now(ZoneInfo("Europe/Kyiv")).strftime("%Y-%m-%d")
            _window_key = f"{_today}-{_kyiv_hour}"
            # Skip if already sent for this window
            if _last_briefing != _window_key:
                # Gather unposted ACTIVE+SETTLING (GAP 20-50) stories
                _bundle_stories = [s for s in stories 
                                   if is_recent(s)
                                   and 20 <= ((s.get("contradiction_gap", 0) or 0)) <= 50
                                   and str(s.get("story_id", "")) not in posted_ids]
                # Group by narrative_id
                _by_narrative = {}
                for s in _bundle_stories:
                    _nid = s.get("narrative_id", s.get("container", ""))
                    if _nid not in _by_narrative:
                        _by_narrative[_nid] = []
                    _by_narrative[_nid].append(s)
                # Post briefing for the narrative with the MOST qualifying stories only (max 1 per cycle, max 3 headlines)
                _best_nid = None
                _best_group = []
                for _nid, _group in _by_narrative.items():
                    if len(_group) >= 3 and len(_group) > len(_best_group):
                        _best_nid = _nid
                        _best_group = _group
                if _best_nid and _best_group:
                    _nl = {"dollar_decline": "Sovereign Liquidity Migration", "critical_resource_control": "Energy Sovereignty", "deglobalization": "Industrial Reshoring", "china_ascent": "Eurasia Capital Architecture", "space_economy": "Orbital Industrialization", "gene_editing": "Longevity & Bioreality", "tech_convergence": "Enterprise Intelligence", "wealthy_sports": "Trophy Assets", "crypto_reserve": "Decentralized Capital", "rate_cycle": "Liquidity Regime", "ai_chips": "Compute Hegemony", "commodity_supercycle": "Physical Resource Revaluation"}.get(_best_nid, _best_nid.upper().replace("_", " "))
                    _lines = [f"🌐 MACRO BRIEFING: {_nl}"]
                    _lines.append("")
                    _lines.append(f"{len(_best_group)} signals coalescing into a structural trend:")
                    _lines.append("")
                    for _s in sorted(_best_group, key=lambda x: (x.get("contradiction_gap", 0) or 0), reverse=True)[:3]:
                        _h = words_truncate(_s.get("headline", "") or "", 14)
                        _g = int(_s.get("contradiction_gap", 0) or 0)
                        _lines.append(f"• [{_g}] {_h}")
                    _lines.append("")
                    _lines.append(f"Full analysis: https://www.lagazzettadikyiv.com")
                    _brief_text = "\\n".join(_lines)
                    if send_telegram(_brief_text):
                        posted_count += 1
                        print(f"[{now()}] MACRO BRIEFING: {_nl} ({len(_best_group)} stories)")
                        import time as _t2
                        _t2.sleep(2)
                # Mark window as sent
                with open(_briefing_path, "w") as _f:
                    json.dump({"sent_at": _window_key}, _f)

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
                _nmc_str = _nmc_str_val = ""
                _nmc_data = NMC_CACHE.get(_nid, {}) or {}
                _nmc_cap = _nmc_data.get("narrative_cap_usd", 0) or 0
                if _nmc_cap >= 1_000_000_000_000:
                    _nmc_str = f"${_nmc_cap/1e12:.2f}T in play"
                elif _nmc_cap >= 1_000_000_000:
                    _nmc_str = f"${_nmc_cap/1e9:.1f}B in play"
                else:
                    _nmc_str = ""
                _title = s.get("_container_title", _nid)
                _lines.append(f"{_title:45s} GAP {_gap:>3} {_arrow}  | {_nmc_str}")
            _pulse_text = "\U0001f4e1 THE FLOW — " + datetime.now(ZoneInfo("Europe/Kyiv")).strftime("%H:%M") + " Kyiv\n\n" + "\n".join(_lines) + "\n\nlagazzettadikyiv.com?utm_source=telegram&utm_medium=pulse"
            # Throttle: only send pulse once per 2 hours
            import time as _time
            _pulse_path = PUBLIC_DATA / "pulse_sent.json"
            _send_pulse = True
            if _pulse_path.exists():
                try:
                    with open(_pulse_path) as _f:
                        _last = json.load(_f).get("sent_at", "")
                    _age = (datetime.now(ZoneInfo("Europe/Kyiv")) - datetime.fromisoformat(_last)).total_seconds()
                    if _age < 7200:
                        _send_pulse = False
                except Exception:
                    pass
            if _send_pulse and send_telegram(_pulse_text):
                with open(_pulse_path, "w") as _f:
                    json.dump({"sent_at": datetime.now(ZoneInfo("Europe/Kyiv")).isoformat()}, _f)
                print(f"[{now()}] Signal Pulse sent")
                posted_count += 1

    print(f"[{now()}] Broadcast complete: {posted_count} posted")


if __name__ == "__main__":
    main()
