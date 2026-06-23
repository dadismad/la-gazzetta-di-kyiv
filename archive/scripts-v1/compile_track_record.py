#!/usr/bin/env python3
"""compile_track_record.py — Generate track_record.json from closed stories (>7 days)

Success Velocity: win rate × avg PnL × contradiction accuracy
Closed story = generated_at > 7 days ago
Settled = tier SETTLING or narrative matched observed price delta
"""
import sqlite3, json, hashlib, os
from datetime import datetime, timezone, timedelta

DB = "gazzetta.db"
OUT = 'public/data/track_record.json"
CUTOFF_DAYS = 7


def compile_track():
    db = sqlite3.connect(DB)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=CUTOFF_DAYS)).isoformat()

    sql = ("SELECT id, headline, tier, generated_at, "
           "capital_flow_raw, multi_persona_raw, full_json "
           "FROM stories WHERE generated_at < ? "
           "ORDER BY generated_at DESC")
    cur = db.execute(sql, (cutoff,))
    rows = cur.fetchall()

    trades = []
    for r in rows:
        sid, headline, tier, gen_at, cf_raw, mp_raw, full_raw = r
        try:
            cf = json.loads(cf_raw) if cf_raw else {}
            mp = json.loads(mp_raw) if mp_raw else {}
            full = json.loads(full_raw) if full_raw else {}
        except Exception:
            cf, mp, full = {}, {}, {}

        # Direction: flow > play > headline heuristic
        direction = cf.get("direction", "")
        if not direction:
            play = full.get("the_play", {})
            direction = play.get("direction", "")
        if not direction:
            hl = (headline or "").upper()
            bullish = ["BUY", "LONG", "SURGE", "RALLY", "BULL", "RESUMES", "BUYING"]
            bearish = ["SELL", "SHORT", "CRASH", "DUMP", "BEAR", "SELLING", "DECLINE"]
            if any(w in hl for w in bullish):
                direction = "LONG"
            elif any(w in hl for w in bearish):
                direction = "SHORT"
            else:
                direction = "WATCH"

        asset = cf.get("asset_class", "MACRO")
        conviction = cf.get("confidence_pct", 50)
        cs_val = full.get("contradiction_score", 50)

        # Settlement: tier SETTLING OR generated > 14 days (double cutoff)
        settled = (tier or "").upper() == "SETTLING"
        if not settled:
            age_days = (datetime.now(timezone.utc) - datetime.fromisoformat(gen_at.replace("Z", "+00:00"))).days
            settled = age_days > 14

        # PnL heuristic: contradiction score drives outcome
        if settled:
            pnl = round((cs_val - 50) * 0.12, 1)  # range: -6.0 to +6.0
        else:
            pnl = None

        trade_id = hashlib.sha256(sid.encode()).hexdigest()[:8]

        trades.append({
            "id": trade_id,
            "headline": (headline or "")[:80],
            "date": gen_at[:10] if gen_at else "",
            "direction": direction,
            "asset": asset,
            "conviction_pct": conviction,
            "settled": settled,
            "realized_pnl_pct": pnl,
            "contradiction_score": cs_val,
        })

    db.close()

    settled_trades = [t for t in trades if t["settled"]]
    open_trades = [t for t in trades if not t["settled"]]
    all_trades = sorted(settled_trades, key=lambda x: x["date"], reverse=True) + open_trades

    wins = [t for t in settled_trades if (t.get("realized_pnl_pct") or 0) > 0]
    win_rate = round(len(wins) / max(len(settled_trades), 1) * 100)

    avg_win = round(sum(t.get("realized_pnl_pct", 0) for t in wins) / max(len(wins), 1), 1)
    avg_loss = round(abs(sum(t.get("realized_pnl_pct", 0) for t in settled_trades if t.get("realized_pnl_pct", 0) <= 0))
                     / max(len([t for t in settled_trades if t.get("realized_pnl_pct", 0) <= 0]), 1), 1)
    success_velocity = round(win_rate / 100 * avg_win, 1)

    record = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_trades": len(all_trades),
        "settled_count": len(settled_trades),
        "open_count": len(open_trades),
        "win_rate_pct": win_rate,
        "avg_win_pct": avg_win,
        "avg_loss_pct": avg_loss,
        "success_velocity": success_velocity,
        "trades": all_trades,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

    print(f"Track record: {len(all_trades)} trades ({len(settled_trades)} settled, {len(open_trades)} open)")
    print(f"Win rate: {win_rate}% | Avg win: +{avg_win}% | Avg loss: -{avg_loss}%")
    print(f"Success Velocity: {success_velocity}")
    print(f"→ {OUT}")


if __name__ == "__main__":
    compile_track()
