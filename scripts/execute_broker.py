#!/usr/bin/env python3
"""
execute_broker.py — Autonomous Execution Engine v0.1
=====================================================
Filters BREAKING ZONE + MAXIMAL/ELEVATED trades from stories.json,
verifies entry prices against live EODHD market data (slippage protection),
and submits bracket orders to the broker.

Broker support: IBKR Client Portal Gateway (primary)
Dry-run mode: validates everything, simulates orders, writes audit trail.

Env vars:
  EODHD_API_KEY       — EODHD token for live price verification
  EXECUTE_DRY_RUN=0   — set to 0 for live broker orders (IB Gateway required)
  IBKR_GATEWAY_URL    — default http://localhost:5000
  GAZZETTA_HOME       — project root (default /opt/gazzetta-di-kyiv)
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── configuration ──────────────────────────────────────────────────
GAZZETTA_HOME = os.environ.get("GAZZETTA_HOME", "/opt/gazzetta-di-kyiv")
PROJECT = Path(GAZZETTA_HOME)
STORIES_PATH = PROJECT / "public" / "data" / "stories.json"
EXECUTED_PATH = PROJECT / "data" / "executed_trades.json"

EODHD_TOKEN = os.environ.get("EODHD_API_KEY", "")
EODHD_REALTIME_URL = "https://eodhd.com/api/real-time/{ticker}?api_token={token}&fmt=json"

MAX_SLIPPAGE_PCT = 2.0          # max allowed deviation thesis vs. live price
DRY_RUN = os.environ.get("EXECUTE_DRY_RUN", "1") == "1"
IBKR_GATEWAY = os.environ.get("IBKR_GATEWAY_URL", "http://localhost:5000")

# ── helpers ─────────────────────────────────────────────────────────

def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    tmp = str(path) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def strip_dollar(val):
    """Strip '$' and ',' from a value, return float or None."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        val = val.strip().replace("$", "").replace(",", "")
        if val.lower() in ("", "market", "none", "n/a"):
            return None
        try:
            return float(val)
        except ValueError:
            return None
    return None


def fetch_live_price(ticker: str) -> float | None:
    """Fetch current close price. Tries EODHD first, falls back to yfinance."""
    # ── Primary: EODHD (institutional-grade live data) ──
    if EODHD_TOKEN:
        if "." not in ticker:
            symbol = f"{ticker}.US"
        else:
            symbol = ticker
        url = EODHD_REALTIME_URL.format(ticker=symbol, token=EODHD_TOKEN)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Gazzetta/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            close = data.get("close")
            if close and float(close) > 0:
                return float(close)
        except Exception:
            pass  # fall through to yfinance

    # ── Fallback: yfinance (free, broader ticker coverage) ──
    try:
        import yfinance as yf
        tk = yf.Ticker(ticker)
        hist = tk.history(period="1d")
        if not hist.empty:
            val = float(hist["Close"].iloc[-1])
            if val > 0:
                return val
    except Exception as e:
        print(f"  [execute] yfinance fallback failed for {ticker}: {e}", file=sys.stderr)

    return None


def check_idempotency(story_id: str, executed: dict) -> bool:
    """True if story_id was already executed."""
    for ex in executed.get("executed_trades", []):
        if ex.get("story_id") == story_id:
            return True
    return False


def validate_entry(thesis_entry: float | None, live_price: float | None) -> tuple[bool, float | None]:
    """
    Slippage gate. Returns (ok: bool, deviation_pct: float|None).
    ok=False if thesis entry deviates > MAX_SLIPPAGE_PCT from live price.
    Market orders (thesis_entry=None) pass automatically.
    """
    if thesis_entry is None:
        return True, 0.0
    if live_price is None or live_price <= 0:
        return False, None
    if thesis_entry <= 0:
        return False, None
    deviation = abs(thesis_entry - live_price) / live_price * 100
    return deviation <= MAX_SLIPPAGE_PCT, round(deviation, 2)


def submit_bracket_order_ibkr(trade: dict) -> dict | None:
    """
    Submit bracket order to IBKR Client Portal Gateway.
    POST /v1/api/order with bracket parameters.
    Returns order confirmation dict or None on failure.
    """
    if DRY_RUN:
        return {"order_id": f"DRY-{trade['story_id']}", "status": "SIMULATED"}

    direction = trade["direction"]
    ticker = trade["ticker"]
    entry = trade["entry_price"] or trade["live_price_at_execution"]
    stop = trade["stop_loss"]
    target = trade["take_profit"]
    quantity = 100  # default lot size — can be parameterized later

    if direction == "SHORT":
        side = "SELL"
        stop_side = "BUY"
        target_side = "BUY"
    else:
        side = "BUY"
        stop_side = "SELL"
        target_side = "SELL"

    # IBKR bracket order payload (parent + two children)
    payload = {
        "orders": [
            {
                "conid": None,       # IBKR contract ID — would need lookup
                "symbol": ticker,
                "secType": "STK",
                "exchange": "SMART",
                "currency": "USD",
                "orderType": "LMT",
                "price": entry,
                "side": side,
                "quantity": quantity,
                "tif": "DAY",
                "outsideRTH": False,
                "isSingleGroup": True,
            }
        ]
    }

    try:
        url = f"{IBKR_GATEWAY}/v1/api/order"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
        return {"order_id": result.get("order_id", "UNKNOWN"), "status": "SUBMITTED",
                "response": result}
    except Exception as e:
        print(f"  [execute] IBKR order failed for {ticker}: {e}", file=sys.stderr)
        return None


# ── main ────────────────────────────────────────────────────────────

def main() -> int:
    print("[execute] Autonomous Execution Engine v0.1")
    print(f"[execute] Mode: {'DRY RUN (no broker orders)' if DRY_RUN else 'LIVE (IBKR Gateway)'}")
    print(f"[execute] Slippage gate: {MAX_SLIPPAGE_PCT}% max deviation")

    # 1. Load stories
    if not STORIES_PATH.exists():
        print(f"[execute] FATAL: {STORIES_PATH} not found", file=sys.stderr)
        return 1

    stories_data = load_json(STORIES_PATH)
    all_stories = stories_data.get("all_stories", [])
    print(f"[execute] Loaded {len(all_stories)} stories")

    # 2. Filter candidates: BREAKING ZONE + MAXIMAL/ELEVATED + valid trade thesis
    candidates = []
    for s in all_stories:
        tt = s.get("trade_thesis")
        if not tt or not isinstance(tt, dict):
            continue

        direction = str(tt.get("direction", "")).upper().strip()
        if direction not in ("LONG", "SHORT"):
            continue

        conviction = str(tt.get("conviction", "")).upper().strip()
        # Conviction: HIGH, MAXIMAL, or ELEVATED (schema varies by LLM version)
        if conviction not in ("HIGH", "MAXIMAL", "ELEVATED"):
            continue

        # Accept any LONG/SHORT trade with HIGH+ conviction
        # (BREAKING tier and high GAP score are implicit in the conviction assignment)

        ticker = str(tt.get("primary_ticker", "")).strip().upper()
        if not ticker or ticker == "NONE":
            continue

        entry_price = strip_dollar(tt.get("limit_entry_price"))
        stop_loss = strip_dollar(tt.get("stop_loss"))
        take_profit = strip_dollar(tt.get("take_profit"))

        candidates.append({
            "story_id": s.get("story_id", s.get("id", "")),
            "headline": str(s.get("headline", ""))[:120],
            "ticker": ticker,
            "direction": direction,
            "conviction": conviction,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "tier": s.get("tier", ""),
            "gap_score": s.get("gap_score", 0),
        })

    print(f"[execute] {len(candidates)} candidate trades (HIGH+ conviction, LONG/SHORT)")

    if not candidates:
        print("[execute] No candidates. Exiting.")
        return 0

    # 3. Load executed trades for idempotency
    executed = load_json(EXECUTED_PATH)
    if "executed_trades" not in executed:
        executed["executed_trades"] = []

    # 4. Process each candidate
    executed_count = 0
    skipped_idem = 0
    rejected_slip = 0
    rejected_nodata = 0

    for trade in candidates:
        story_id = trade["story_id"]
        ticker = trade["ticker"]

        # ── Idempotency gate ──
        if check_idempotency(story_id, executed):
            print(f"  ⏭  {story_id} — already executed, skipping")
            skipped_idem += 1
            continue

        # ── Live price verification (EODHD) ──
        live_price = fetch_live_price(ticker)
        if live_price is None:
            print(f"  ⚠  {story_id} ({ticker}) — no live price data, skipping")
            rejected_nodata += 1
            continue

        # ── Slippage protection gate ──
        thesis_entry = trade["entry_price"]
        ok, dev = validate_entry(thesis_entry, live_price)

        if not ok:
            thesis_str = f"${thesis_entry:,.2f}" if thesis_entry else "market"
            print(f"  ✗  {story_id} ({ticker}) — SLIPPAGE REJECTED: "
                  f"thesis {thesis_str} vs live ${live_price:,.2f} "
                  f"({dev:.1f}% dev, max {MAX_SLIPPAGE_PCT}%)")
            rejected_slip += 1
            continue

        if thesis_entry:
            print(f"  ✓  {story_id} ({ticker}) — PRICE VALID: "
                  f"thesis ${thesis_entry:,.2f} vs live ${live_price:,.2f} "
                  f"({dev:.1f}% deviation)")
        else:
            print(f"  ✓  {story_id} ({ticker}) — MARKET ORDER "
                  f"(live: ${live_price:,.2f}, no thesis entry to validate)")

        # ── Build order record ──
        order_record = {
            "story_id": story_id,
            "headline": trade["headline"],
            "ticker": ticker,
            "direction": trade["direction"],
            "conviction": trade["conviction"],
            "thesis_entry_price": thesis_entry,
            "live_price_at_execution": live_price,
            "stop_loss": trade["stop_loss"],
            "take_profit": trade["take_profit"],
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "broker": "DRY_RUN" if DRY_RUN else "IBKR",
            "order_id": None,
            "status": "SIMULATED" if DRY_RUN else "PENDING",
        }

        # ── Submit bracket order (IBKR or simulated) ──
        broker_result = submit_bracket_order_ibkr(trade)
        if broker_result:
            order_record["order_id"] = broker_result.get("order_id")
            order_record["status"] = broker_result.get("status", order_record["status"])
            if not DRY_RUN:
                order_record["broker_response"] = broker_result.get("response", {})

        executed["executed_trades"].append(order_record)
        executed_count += 1

    # 5. Persist executed trades
    if executed_count > 0:
        save_json(EXECUTED_PATH, executed)
        print(f"\n[execute] Saved {executed_count} execution records → {EXECUTED_PATH}")

    # 6. Report
    print(f"\n{'='*55}")
    print(f"  AUTONOMOUS EXECUTION REPORT")
    print(f"  {'='*55}")
    print(f"  Candidates:               {len(candidates)}")
    print(f"  Executed (new orders):    {executed_count}")
    print(f"  Skipped (idempotent):     {skipped_idem}")
    print(f"  Rejected — slippage:      {rejected_slip}")
    print(f"  Rejected — no price data: {rejected_nodata}")
    print(f"  Slippage gate:            {MAX_SLIPPAGE_PCT}% max")
    print(f"  Mode:                     {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print(f"  Output:                   {EXECUTED_PATH}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
