#!/usr/bin/env python3
"""
purge_bad_trades.py — Remove trades with >15% entry/current price deviation
=====================================================================
Reads public/data/track_record.json, filters out trades where
  abs(entry_price - current_price) / current_price * 100 > 15
recomputes summary stats, and writes the cleaned file back atomically.
Moves itself to scripts/archived/ on success.
"""

import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime, timezone

# -- config ----------------------------------------------------------
PROJECT = Path(__file__).resolve().parent.parent
TRACK_RECORD_PATH = PROJECT / "public" / "data" / "track_record.json"
ARCHIVE_DIR = PROJECT / "scripts" / "archived"

DEVIATION_THRESHOLD_PCT = 15.0


def deviation_pct(entry_price, current_price):
    """Compute absolute percentage deviation between entry and current price."""
    if entry_price is None or current_price is None or current_price <= 0:
        return 0.0  # can't compute — keep the trade
    if entry_price <= 0:
        return 0.0
    return abs(entry_price - current_price) / max(current_price, 0.01) * 100


def main():
    print("=" * 50)
    print("  PURGE BAD TRADES")
    print("  Deviation threshold: >{}%".format(DEVIATION_THRESHOLD_PCT))
    print("=" * 50)

    # 1. Load track record
    if not TRACK_RECORD_PATH.exists():
        print(f"[purge] FATAL: {TRACK_RECORD_PATH} not found", file=sys.stderr)
        return 1

    with open(TRACK_RECORD_PATH) as f:
        record = json.load(f)

    trades = record.get("trades", [])
    before_count = len(trades)
    print(f"\n  Before: {before_count} trades")

    # 2. Before stats
    old_summary = record.get("summary", {})
    print(f"  Old win rate:    {old_summary.get('win_rate_pct', 'N/A')}%")
    print(f"  Old closed:      {old_summary.get('closed', 0)}")
    print(f"  Old total PnL:   {old_summary.get('total_realized_pnl_pct', 'N/A')}%")

    # 3. Filter — remove trades where entry deviates >15% from current price
    kept = []
    removed = []
    for t in trades:
        entry = t.get("entry_price")
        current = t.get("current_price")
        dev = deviation_pct(entry, current)
        if dev > DEVIATION_THRESHOLD_PCT:
            removed.append(t)
            print(f"    REMOVED trade_id={t.get('trade_id','?')} ticker={t.get('ticker','?')} "
                  f"entry={entry} current={current} dev={dev:.1f}%")
        else:
            kept.append(t)

    removed_count = len(removed)
    after_count = len(kept)
    print(f"\n  Removed: {removed_count} trades")
    print(f"  After:  {after_count} trades")

    if removed_count == 0:
        print("\n  No bad trades found — nothing to purge.")
        # Still mark as cleaned
        record["cleaned_by"] = "purge_bad_trades.py v1.0"
        record["purged_count"] = 0
        record["purge_threshold_pct"] = DEVIATION_THRESHOLD_PCT
        record["generated_at"] = datetime.now(timezone.utc).isoformat()

        # Atomic write (even though nothing removed, we update metadata)
        tmp = str(TRACK_RECORD_PATH) + ".tmp"
        with open(tmp, "w") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
        os.replace(tmp, TRACK_RECORD_PATH)
        print(f"  → {TRACK_RECORD_PATH} (metadata updated)")
        return 0

    # 4. Recompute stats (mirroring settle_trades.py logic)
    closed = [t for t in kept if t.get("status") in ("WIN", "LOSS")]
    wins = [t for t in closed if t.get("status") == "WIN"]
    losses = [t for t in closed if t.get("status") == "LOSS"]
    active = [t for t in kept if t.get("status") in ("WINNING", "LOSING", "FLAT", "OPEN")]
    pending = [t for t in kept if t.get("status") == "PENDING_DATA"]

    total = len(kept)
    win_count = len(wins)
    loss_count = len(losses)
    closed_count = len(closed)
    win_rate = round(win_count / max(closed_count, 1) * 100, 1)
    avg_win_pnl = round(sum(t.get("pnl_pct", 0) for t in wins) / max(len(wins), 1), 2)
    avg_loss_pnl = round(sum(t.get("pnl_pct", 0) for t in losses) / max(len(losses), 1), 2)
    profit_factor = round(
        abs(sum(t.get("pnl_pct", 0) for t in wins) / max(abs(sum(t.get("pnl_pct", 0) for t in losses)), 0.01)), 2
    )
    total_pnl = round(sum(t.get("pnl_pct", 0) for t in closed), 2)

    # Conviction-weighted stats (same as settle_trades.py)
    conviction_map = {"MAXIMAL": 1.5, "ELEVATED": 1.2, "HOLD": 1.0, "SPECULATIVE": 0.5}
    weighted_wins = sum(1 for t in wins if t.get("conviction") in ("MAXIMAL", "ELEVATED"))
    weighted_total = sum(1 for t in closed if t.get("conviction") in ("MAXIMAL", "ELEVATED"))
    high_conv_win_rate = round(weighted_wins / max(weighted_total, 1) * 100, 1)

    # 5. Update record
    record["generated_at"] = datetime.now(timezone.utc).isoformat()
    record["generated_by"] = "settle_trades.py v1.0 (purged by purge_bad_trades.py v1.0)"
    record["cleaned_by"] = "purge_bad_trades.py v1.0"
    record["purged_count"] = removed_count
    record["purge_threshold_pct"] = DEVIATION_THRESHOLD_PCT
    record["summary"] = {
        "total_trades": total,
        "closed": closed_count,
        "active": len(active),
        "pending_data": len(pending),
        "wins": win_count,
        "losses": loss_count,
        "win_rate_pct": win_rate,
        "high_conviction_win_rate_pct": high_conv_win_rate,
        "avg_win_pnl_pct": avg_win_pnl,
        "avg_loss_pnl_pct": avg_loss_pnl,
        "total_realized_pnl_pct": total_pnl,
        "profit_factor": profit_factor,
    }
    record["trades"] = sorted(kept, key=lambda t: t.get("date", ""), reverse=True)

    # 6. Atomic write
    tmp = str(TRACK_RECORD_PATH) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    os.replace(tmp, TRACK_RECORD_PATH)

    # 7. Report
    print(f"\n{'='*50}")
    print(f"  POST-PURGE SUMMARY")
    print(f"  {'='*50}")
    print(f"  Total trades:      {total} (was {before_count})")
    print(f"  Purged:            {removed_count}")
    print(f"  Closed (settled):  {closed_count} (W: {win_count} / L: {loss_count})")
    print(f"  Active:            {len(active)}")
    print(f"  Pending data:      {len(pending)}")
    print(f"  Win Rate:          {win_rate}% (was {old_summary.get('win_rate_pct','?')}%)")
    print(f"  High-Conv Win Rt:  {high_conv_win_rate}%")
    print(f"  Avg Win PnL:       +{avg_win_pnl}%")
    print(f"  Avg Loss PnL:      {avg_loss_pnl}%")
    print(f"  Total PnL:         {total_pnl:+.2f}% (was {old_summary.get('total_realized_pnl_pct','?')}%)")
    print(f"  Profit Factor:     {profit_factor}")
    print(f"  → {TRACK_RECORD_PATH}")

    # Gate check
    if closed_count < 5:
        print(f"\n  ⚠ GATE: Only {closed_count} settled trades (need ≥5 for statistical significance)")
    else:
        print(f"\n  ✓ Statistical significance met ({closed_count} settled)")

    return 0


if __name__ == "__main__":
    rc = main()

    # On success, move this script to archived/
    if rc == 0:
        script_path = Path(__file__).resolve()
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        dest = ARCHIVE_DIR / script_path.name
        try:
            shutil.move(str(script_path), str(dest))
            print(f"\n  ✓ Archived script to {dest}")
        except Exception as e:
            print(f"\n  ⚠ Could not archive script: {e}", file=sys.stderr)

    sys.exit(rc)
