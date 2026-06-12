#!/usr/bin/env python3
"""build_track_record.py — The Trust Machine

Queries gazzetta.db for stories >48h old.
For each: compares narrative sentiment direction against actual price delta.
Settles bets: 'Correct' when sentiment matches price direction.
Generates track_record.json with 'Total Realized Alpha Signals' and 'Avg Asymmetry Success'.
"""
import sqlite3, json, hashlib, os, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DB = str(PROJECT / "gazzetta.db")
MARKET_DATA = str(PROJECT / "data" / "market_prices.json")
OUT = str(PROJECT / "site" / "data" / "track_record.json")
CUTOFF_HOURS = 48

# Asset class → ticker mapping for market data lookup
ASSET_TICKER = {
    "crypto": "crypto",
    "commodities": "commodities",
    "equities": "equities",
    "fixed_income": "fixed_income",
    "fx": "fx",
    "defense": "defense",
    "tech": "tech",
    "gold": "gold",
}


def load_market_prices():
    if not os.path.exists(MARKET_DATA):
        print(f"  ⚠ No market data at {MARKET_DATA} — using direction-only settlement")
        return {}
    with open(MARKET_DATA) as f:
        md = json.load(f)
    return md.get("prices", {})


def settle_story(story, market_prices):
    """Compare narrative direction to actual price delta. Return settlement dict."""
    sid = story.get("story_id") or story.get("id", "")
    headline = story.get("headline", "")[:80]
    tier = story.get("tier", "")
    gen_at = story.get("generated_at", "")

    # Parse capital_flow
    cf_raw = story.get("capital_flow_raw", "{}")
    try:
        cf = json.loads(cf_raw) if cf_raw else {}
    except Exception:
        cf = {}

    direction = cf.get("direction", "")
    asset_class = cf.get("asset_class", "MACRO")
    confidence = cf.get("confidence_pct", 50)
    amount_b = cf.get("amount_b", 0)

    # Determine narrative sentiment: inflow=bullish (+1), outflow=bearish (-1)
    narrative_sentiment = +1 if direction == "inflow" else (-1 if direction == "outflow" else 0)

    # Look up actual price delta
    ticker_key = ASSET_TICKER.get(asset_class.lower(), asset_class.lower())
    price_info = market_prices.get(ticker_key, {})
    price_delta = price_info.get("change_pct", 0)

    # Settlement: narrative matches price direction?
    price_direction = 1 if price_delta > 0 else (-1 if price_delta < 0 else 0)

    if narrative_sentiment == 0 or price_direction == 0:
        correct = None  # indeterminate
        outcome = "INDETERMINATE"
    elif narrative_sentiment == price_direction:
        correct = True
        outcome = "CORRECT"
    else:
        correct = False
        outcome = "INCORRECT"

    # Derive realized PnL from price delta × narrative direction
    # If narrative was RIGHT: PnL ≈ |price_delta|. If WRONG: PnL ≈ −|price_delta|
    realized_pnl = round(price_delta * narrative_sentiment * 1.0, 2)

    trade_id = hashlib.sha256((sid or headline).encode()).hexdigest()[:8]

    return {
        "id": trade_id,
        "headline": headline,
        "date": gen_at[:10] if gen_at else "",
        "direction": direction.upper() if direction else "WATCH",
        "asset": asset_class.upper(),
        "conviction_pct": confidence,
        "amount_b": amount_b,
        "narrative_sentiment": narrative_sentiment,
        "price_delta_pct": price_delta,
        "outcome": outcome,
        "correct": correct,
        "settled": correct is not None,
        "realized_pnl_pct": realized_pnl,
        "tier": tier,
    }


def compile():
    db = sqlite3.connect(DB)
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=CUTOFF_HOURS)).isoformat()

    cur = db.execute(
        "SELECT id, headline, tier, confidence, generated_at, "
        "capital_flow_raw, full_json, contradiction_score "
        "FROM stories WHERE generated_at < ? "
        "ORDER BY generated_at DESC",
        (cutoff,),
    )
    rows = cur.fetchall()
    db.close()

    print(f"  DB query: {len(rows)} stories older than {CUTOFF_HOURS}h")

    market_prices = load_market_prices()
    print(f"  Market data: {len(market_prices)} tickers loaded")

    trades = []
    for r in rows:
        story = {
            "story_id": r[0],
            "headline": r[1],
            "tier": r[2],
            "confidence": r[3],
            "generated_at": r[4],
            "capital_flow_raw": r[5],
            "full_json": r[6],
            "contradiction_score": r[7],
        }
        trade = settle_story(story, market_prices)
        trades.append(trade)

    # Split by settlement
    settled = [t for t in trades if t["settled"]]
    open_positions = [t for t in trades if not t["settled"]]

    correct_trades = [t for t in settled if t["correct"]]
    incorrect_trades = [t for t in settled if t["correct"] is False]
    indeterminate = [t for t in trades if t["correct"] is None]

    total_realized = len(correct_trades)
    win_rate = round(len(correct_trades) / max(len(settled), 1) * 100)
    avg_correct_pnl = round(sum(t["realized_pnl_pct"] for t in correct_trades) / max(len(correct_trades), 1), 2)
    avg_incorrect_pnl = round(sum(t["realized_pnl_pct"] for t in incorrect_trades) / max(len(incorrect_trades), 1), 2)
    success_velocity = round(win_rate / 100 * avg_correct_pnl, 1)

    record = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_trades": len(trades),
        "settled_count": len(settled),
        "open_count": len(open_positions),
        "indeterminate_count": len(indeterminate),
        "total_realized_alpha": total_realized,
        "correct_count": len(correct_trades),
        "incorrect_count": len(incorrect_trades),
        "win_rate_pct": win_rate,
        "avg_correct_pnl_pct": avg_correct_pnl,
        "avg_incorrect_pnl_pct": avg_incorrect_pnl,
        "success_velocity": success_velocity,
        "cutoff_hours": CUTOFF_HOURS,
        "trades": sorted(settled, key=lambda x: x["date"], reverse=True) + open_positions,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

    print(f"\n═══ TRACK RECORD ═══")
    print(f"  Total trades:         {len(trades)}")
    print(f"  Settled:              {len(settled)} (correct: {len(correct_trades)}, incorrect: {len(incorrect_trades)}, indeterminate: {len(indeterminate)})")
    print(f"  Open:                 {len(open_positions)}")
    print(f"  Total Realized Alpha: {total_realized}")
    print(f"  Win Rate:             {win_rate}%")
    print(f"  Avg Correct PnL:      +{avg_correct_pnl}%")
    print(f"  Avg Incorrect PnL:    {avg_incorrect_pnl}%")
    print(f"  Success Velocity:     {success_velocity}")
    print(f"  → {OUT}")

    # Gate check
    if total_realized < 5:
        print(f"\n  ⚠ GATE FAIL: Only {total_realized} realized alpha signals (need ≥5)")
        print(f"  Consider extending cutoff or seeding historical data.")
        return False
    return True


if __name__ == "__main__":
    ok = compile()
    sys.exit(0 if ok else 1)
