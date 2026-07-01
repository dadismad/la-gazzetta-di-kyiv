#!/usr/bin/env python3
"""
settle_trades.py — Track Record Settlement Engine
===================================================
Queries stories.json for trade theses older than 3 days.
Fetches current prices via yfinance, compares against trade parameters,
and computes Win/Loss/Open status with PnL percentages.

Output: public/data/track_record.json — frontend-consumable verified track record.
"""

import json
import os
import sys
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

# -- config ----------------------------------------------------------
PROJECT = Path(__file__).resolve().parent.parent
STORIES_PATH = PROJECT / "public" / "data" / "stories.json"
OUTPUT_PATH = PROJECT / "public" / "data" / "track_record.json"
CUTOFF_DAYS = 3                    # Only settle trades older than this
CACHE_PRICES_PATH = PROJECT / "data" / "market_prices.json"

# -- helpers ---------------------------------------------------------
def strip_dollar(val):
    """Strip '$' prefix and ',' from price strings, return float or None."""
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


def parse_trade_thesis(story):
    """Extract trade parameters from story. Returns dict or None if no trade."""
    tt = story.get("trade_thesis")
    if not tt or not isinstance(tt, dict):
        return None

    direction = str(tt.get("direction", "")).upper().strip()
    if direction in ("NEUTRAL", "", "WATCH", "NONE"):
        return None
    if direction not in ("LONG", "SHORT"):
        return None

    primary_ticker = str(tt.get("primary_ticker", "")).strip().upper()
    if not primary_ticker or primary_ticker == "NONE":
        return None

    entry_price = strip_dollar(tt.get("limit_entry_price"))
    stop_loss = strip_dollar(tt.get("stop_loss"))
    take_profit = strip_dollar(tt.get("take_profit"))
    horizon_days = int(tt.get("horizon_days", 0)) or None

    return {
        "story_id": story.get("story_id", story.get("id", "")),
        "headline": str(story.get("headline", ""))[:100],
        "generated_at": story.get("generated_at", ""),
        "direction": direction,
        "ticker": primary_ticker,
        "entry_price": entry_price,      # None = "market" order
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "horizon_days": horizon_days,
        "conviction": str(tt.get("conviction", "")).upper(),
        "narrative": story.get("container", story.get("narrative_tag", "")),
        "tier": story.get("tier", ""),
        "capital_at_stake_usd": story.get("capital_at_stake_usd", 0),
    }


def fetch_current_prices(tickers, cache_prices=None):
    """Fetch current prices for a list of tickers via yfinance.
    Falls back to market_prices.json cache if yfinance fails."""
    import yfinance as yf

    prices = {}
    if cache_prices is None:
        cache_prices = {}

    # Try yfinance batch download
    try:
        tickers_str = " ".join(tickers)
        data = yf.download(tickers_str, period="5d", progress=False, auto_adjust=True)

        if data is not None and not data.empty:
            close_col = data.get("Close", data)
            for t in tickers:
                try:
                    if isinstance(close_col, dict):
                        series = close_col.get(t)
                    elif len(tickers) == 1:
                        series = close_col
                    else:
                        series = close_col[t] if t in close_col.columns else None

                    if series is not None and len(series) > 0:
                        val = float(series.dropna().iloc[-1])
                        if val > 0:
                            prices[t] = val
                except Exception:
                    pass
    except Exception as e:
        print(f"  [settle] yfinance batch failed: {e}", file=sys.stderr)

    # Fallback: try individual ticker fetch for any missed
    remaining = [t for t in tickers if t not in prices]
    for t in remaining:
        try:
            tk = yf.Ticker(t)
            hist = tk.history(period="5d", auto_adjust=True)
            if not hist.empty:
                val = float(hist["Close"].iloc[-1])
                if val > 0:
                    prices[t] = val
        except Exception:
            pass

    # Last resort: cached market_prices.json
    for t in tickers:
        if t not in prices and t in cache_prices:
            cp = cache_prices[t]
            if isinstance(cp, dict):
                p = cp.get("price") or cp.get("last") or cp.get("close")
                if p:
                    prices[t] = float(p)
            elif isinstance(cp, (int, float)):
                prices[t] = float(cp)

    return prices


def fetch_historical_price(ticker, date_str, fallback_prices=None):
    """Fetch approximate price for a ticker on a given date (YYYY-MM-DD).
    Tries yfinance history first, falls back to any available price."""
    import yfinance as yf
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        end_date = (dt + timedelta(days=3)).strftime("%Y-%m-%d")
        start_date = (dt - timedelta(days=3)).strftime("%Y-%m-%d")

        tk = yf.Ticker(ticker)
        hist = tk.history(start=start_date, end=end_date, auto_adjust=True)
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception:
        pass

    # Fallback: any current price is better than nothing
    if fallback_prices and ticker in fallback_prices:
        return fallback_prices[ticker]
    return None


def load_cache_prices():
    """Load market_prices.json for fallback data."""
    if not CACHE_PRICES_PATH.exists():
        return {}
    try:
        with open(CACHE_PRICES_PATH) as f:
            data = json.load(f)
        return data.get("prices", {})
    except Exception:
        return {}


def settle_trade(trade, current_price, historical_price=None):
    """Compute settlement outcome for a single trade.
    Returns dict with outcome, PnL, and hit_level fields."""

    direction = trade["direction"]
    entry = trade["entry_price"]
    stop = trade["stop_loss"]
    target = trade["take_profit"]

    # Determine effective entry price
    if entry and entry > 0:
        effective_entry = entry
        entry_note = f"limit ${entry:,.2f}"
    elif historical_price and historical_price > 0:
        effective_entry = historical_price
        entry_note = f"market (hist ~${historical_price:,.2f})"
    else:
        effective_entry = None
        entry_note = "market (no hist data)"

    result = {
        "trade_id": str(trade.get("story_id", "")),
        "headline": trade.get("headline", ""),
        "date": trade.get("generated_at", "")[:10],
        "ticker": trade["ticker"],
        "direction": direction,
        "conviction": trade.get("conviction", ""),
        "narrative": trade.get("narrative", ""),
        "tier": trade.get("tier", ""),
        "capital_at_stake_usd": trade.get("capital_at_stake_usd", 0),
        "entry_price": effective_entry,
        "entry_note": entry_note,
        "stop_loss": stop,
        "take_profit": target,
        "current_price": current_price,
        "status": "OPEN",
        "pnl_pct": 0,
        "hit_level": None,
    }

    if effective_entry is None or not current_price or current_price <= 0:
        result["status"] = "PENDING_DATA"
        result["note"] = "Missing entry price or current price"
        return result
    if effective_entry <= 0:
        result["status"] = "PENDING_DATA"
        result["note"] = "Invalid entry price"
        return result

    # Compute PnL relative to direction
    if direction == "LONG":
        pnl = (current_price - effective_entry) / effective_entry * 100
    else:  # SHORT
        pnl = (effective_entry - current_price) / effective_entry * 100

    result["pnl_pct"] = round(pnl, 2)

    # Determine if take-profit or stop-loss was hit (based on current price)
    hit_tp = False
    hit_sl = False

    if target and target > 0:
        if direction == "LONG":
            hit_tp = pnl > 0 and current_price >= target * 0.995  # within 0.5% tolerance
        else:
            hit_tp = pnl > 0 and current_price <= target * 1.005
    if stop and stop > 0:
        if direction == "LONG":
            hit_sl = pnl < 0 and current_price <= stop * 1.005
        else:
            hit_sl = pnl < 0 and current_price >= stop * 0.995

    if hit_tp:
        result["status"] = "WIN"
        result["hit_level"] = "take_profit"
    elif hit_sl:
        result["status"] = "LOSS"
        result["hit_level"] = "stop_loss"
    elif pnl > 0:
        result["status"] = "WINNING"
    elif pnl < 0:
        result["status"] = "LOSING"
    else:
        result["status"] = "FLAT"

    return result


# -- main ------------------------------------------------------------
def main():
    print("[settle] Track Record Settlement Engine")

    # 1. Load stories
    if not STORIES_PATH.exists():
        print(f"[settle] FATAL: {STORIES_PATH} not found", file=sys.stderr)
        return 1

    with open(STORIES_PATH) as f:
        data = json.load(f)
    all_stories = data.get("all_stories", [])
    print(f"[settle] Loaded {len(all_stories)} stories")

    # 2. Filter: stories older than CUTOFF_DAYS with valid trade thesis
    cutoff = datetime.now(timezone.utc) - timedelta(days=CUTOFF_DAYS)
    trades = []

    for s in all_stories:
        gen_at = s.get("generated_at", "")
        if not gen_at:
            continue
        try:
            gen_dt = datetime.fromisoformat(gen_at.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue
        if gen_dt > cutoff:
            continue  # Too recent — let it age

        trade = parse_trade_thesis(s)
        if trade:
            trades.append(trade)

    if not trades:
        print(f"[settle] No trades older than {CUTOFF_DAYS}d with valid trade theses")
        # Write empty record
        empty = {"generated_at": datetime.now(timezone.utc).isoformat(),
                 "total_trades": 0, "win_rate_pct": 0, "status": "no_eligible_trades"}
        with open(OUTPUT_PATH, "w") as f:
            json.dump(empty, f, indent=2)
        return 0

    print(f"[settle] {len(trades)} eligible trades (>{CUTOFF_DAYS}d old)")

    # 3. Fetch current prices for all tickers
    tickers = list(set(t["ticker"] for t in trades))
    print(f"[settle] Fetching prices for {len(tickers)} unique tickers...")

    cache_prices = load_cache_prices()
    current_prices = fetch_current_prices(tickers, cache_prices)
    print(f"[settle] Got prices for {len(current_prices)}/{len(tickers)} tickers")

    # 4. Settle each trade
    settled = []
    pending_data = []
    for trade in trades:
        ticker = trade["ticker"]
        current_price = current_prices.get(ticker)

        # For "market" entries, try to get historical price
        historical_price = None
        if trade["entry_price"] is None and trade.get("generated_at"):
            historical_price = fetch_historical_price(
                ticker, trade["generated_at"], current_prices
            )

        result = settle_trade(trade, current_price, historical_price)

        # ── SANITY GATE: reject hallucinated trade data ──
        pnl = result.get("pnl_pct", 0)
        entry_px = result.get("entry_price")
        curr_px = result.get("current_price")

        if pnl > 100 or pnl < -100:
            result["status"] = "REJECTED_DATA"
            result["note"] = f"PnL {pnl:+.2f}% exceeds ±100% sanity bound — probable hallucinated entry price"
        elif (entry_px and curr_px and entry_px > 0 and curr_px > 0
              and abs(entry_px - curr_px) / curr_px > 0.15):
            result["status"] = "REJECTED_DATA"
            result["note"] = (f"Entry ${entry_px:,.2f} deviates {abs(entry_px - curr_px)/curr_px*100:.1f}% "
                              f"from market ${curr_px:,.2f} (max 15%) — probable hallucinated limit")
        # ── END SANITY GATE ──

        settled.append(result)

    # 5. Compute aggregate stats (REJECTED_DATA excluded from all aggregates)
    closed = [t for t in settled if t["status"] in ("WIN", "LOSS")]
    wins = [t for t in closed if t["status"] == "WIN"]
    losses = [t for t in closed if t["status"] == "LOSS"]
    active = [t for t in settled if t["status"] in ("WINNING", "LOSING", "FLAT", "OPEN")]
    pending = [t for t in settled if t["status"] == "PENDING_DATA"]
    rejected = [t for t in settled if t["status"] == "REJECTED_DATA"]

    total = len(settled)
    win_count = len(wins)
    loss_count = len(losses)
    closed_count = len(closed)
    win_rate = round(win_count / max(closed_count, 1) * 100, 1)
    avg_win_pnl = round(sum(t["pnl_pct"] for t in wins) / max(len(wins), 1), 2)
    avg_loss_pnl = round(sum(t["pnl_pct"] for t in losses) / max(len(losses), 1), 2)
    profit_factor = round(
        abs(sum(t["pnl_pct"] for t in wins) / max(abs(sum(t["pnl_pct"] for t in losses)), 0.01)), 2
    )
    total_pnl = round(sum(t["pnl_pct"] for t in closed), 2)

    # Conviction-weighted stats
    conviction_map = {"MAXIMAL": 1.5, "ELEVATED": 1.2, "HOLD": 1.0, "SPECULATIVE": 0.5}
    weighted_wins = sum(1 for t in wins if t.get("conviction") in ("MAXIMAL", "ELEVATED"))
    weighted_total = sum(1 for t in closed if t.get("conviction") in ("MAXIMAL", "ELEVATED"))
    high_conv_win_rate = round(weighted_wins / max(weighted_total, 1) * 100, 1)

    # 6. Build output record
    record = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "settle_trades.py v1.1",
        "cutoff_days": CUTOFF_DAYS,
        "summary": {
            "total_trades": total,
            "closed": closed_count,
            "active": len(active),
            "pending_data": len(pending),
            "rejected_data": len(rejected),
            "wins": win_count,
            "losses": loss_count,
            "win_rate_pct": win_rate,
            "high_conviction_win_rate_pct": high_conv_win_rate,
            "avg_win_pnl_pct": avg_win_pnl,
            "avg_loss_pnl_pct": avg_loss_pnl,
            "total_realized_pnl_pct": total_pnl,
            "profit_factor": profit_factor,
        },
        "trades": sorted(settled, key=lambda t: t.get("date", ""), reverse=True),
    }

    # 7. Atomic write
    tmp = str(OUTPUT_PATH) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    os.replace(tmp, OUTPUT_PATH)

    # 8. Report
    print(f"\n{'='*50}")
    print(f"  TRACK RECORD SETTLEMENT")
    print(f"  {'='*50}")
    print(f"  Total trades:      {total}")
    print(f"  Closed (settled):  {closed_count} (W: {win_count} / L: {loss_count})")
    print(f"  Active:            {len(active)}")
    print(f"  Pending data:      {len(pending)}")
    print(f"  Rejected (sanity): {len(rejected)}")
    print(f"  Win Rate:          {win_rate}%")
    print(f"  High-Conv Win Rt:  {high_conv_win_rate}%")
    print(f"  Avg Win PnL:       +{avg_win_pnl}%")
    print(f"  Avg Loss PnL:      {avg_loss_pnl}%")
    print(f"  Total PnL:         {total_pnl:+.2f}%")
    print(f"  Profit Factor:     {profit_factor}")
    print(f"  → {OUTPUT_PATH}")

    # Gate check
    if closed_count < 5:
        print(f"\n  ⚠ GATE: Only {closed_count} settled trades (need ≥5 for statistical significance)")
    else:
        print(f"\n  ✓ Statistical significance met ({closed_count} settled)")

    return 0 if closed_count >= 1 else 2


if __name__ == "__main__":
    sys.exit(main())
