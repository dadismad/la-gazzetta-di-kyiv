#!/usr/bin/env python3
"""
Generate api/v1/trades.json — Anchor trade positions from stories + flows.
Derives 14 tradable assets with entry/target/stop/conviction.
Output: site/api/v1/trades.json
"""

import json, sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = PROJECT_ROOT / "site"
OUT_DIR = SITE_DIR / "api" / "v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Classic tradFi + crypto anchor assets
TRADFI = [
    {"symbol": "SPX", "name": "S&P 500", "asset_class": "equities", "atr_pct": 1.2, "multiplier": 2.5},
    {"symbol": "NVDA", "name": "NVIDIA", "asset_class": "equities", "atr_pct": 3.5, "multiplier": 2.0},
    {"symbol": "BRENT", "name": "Brent Crude", "asset_class": "commodities", "atr_pct": 2.8, "multiplier": 2.5},
    {"symbol": "DXY", "name": "US Dollar Index", "asset_class": "fx", "atr_pct": 0.6, "multiplier": 3.0},
    {"symbol": "GOLD", "name": "Gold", "asset_class": "commodities", "atr_pct": 1.5, "multiplier": 2.5},
    {"symbol": "BTC", "name": "Bitcoin", "asset_class": "crypto", "atr_pct": 4.0, "multiplier": 2.0},
    {"symbol": "10Y", "name": "10Y Treasury", "asset_class": "fixed_income", "atr_pct": 0.3, "multiplier": 3.0},
]
CRYPTO = [
    {"symbol": "ETH", "name": "Ethereum", "asset_class": "crypto", "atr_pct": 4.5, "multiplier": 2.0},
    {"symbol": "SOL", "name": "Solana", "asset_class": "crypto", "atr_pct": 5.5, "multiplier": 2.0},
    {"symbol": "XRP", "name": "XRP", "asset_class": "crypto", "atr_pct": 3.5, "multiplier": 2.0},
    {"symbol": "BNB", "name": "BNB", "asset_class": "crypto", "atr_pct": 3.0, "multiplier": 2.0},
    {"symbol": "ADA", "name": "Cardano", "asset_class": "crypto", "atr_pct": 4.0, "multiplier": 2.0},
    {"symbol": "DOGE", "name": "Dogecoin", "asset_class": "crypto", "atr_pct": 6.5, "multiplier": 2.0},
]


def main():
    now = datetime.now(timezone.utc).isoformat()

    # Load flows for context
    flows_path = SITE_DIR / "data" / "flows.json"
    flows = []
    if flows_path.exists():
        d = json.loads(flows_path.read_text())
        flows = d.get("flows", [])

    # Build flow context per asset class
    flow_context = {}
    for f in flows:
        ac = f.get("asset_class", "")
        if ac not in flow_context:
            flow_context[ac] = {
                "total_inflows": 0, "total_outflows": 0,
                "avg_pace": 0, "count": 0,
            }
        ctx = flow_context[ac]
        if f.get("direction") == "inflow":
            ctx["total_inflows"] += f.get("amount_b", 0)
        else:
            ctx["total_outflows"] += f.get("amount_b", 0)
        ctx["avg_pace"] += f.get("pace_multiplier", 1.0)
        ctx["count"] += 1

    for ac in flow_context:
        c = flow_context[ac]
        if c["count"] > 0:
            c["avg_pace"] = round(c["avg_pace"] / c["count"], 1)

    # Generate trade positions
    trades = []

    def derive_position(asset):
        """Derive BUY/SELL/WATCH from flow context."""
        ac = asset["asset_class"]
        ctx = flow_context.get(ac, {})
        net = ctx.get("total_inflows", 0) - ctx.get("total_outflows", 0)
        if net > 10:
            return "BUY", "HIGH"
        elif net > 3:
            return "BUY", "MED"
        elif net < -10:
            return "SELL", "HIGH"
        elif net < -3:
            return "SELL", "MED"
        return "WATCH", "LOW"

    for asset in TRADFI + CRYPTO:
        symbol = asset["symbol"]
        direction, conviction = derive_position(asset)

        # Reference price (placeholder — would be live in production)
        ref_prices = {
            "SPX": 5950, "NVDA": 132, "BRENT": 72, "DXY": 104,
            "GOLD": 3350, "BTC": 103000, "10Y": 4.42,
            "ETH": 3400, "SOL": 168, "XRP": 2.35,
            "BNB": 690, "ADA": 0.42, "DOGE": 0.18,
        }
        price = ref_prices.get(symbol, 100)

        atr_val = price * asset["atr_pct"] / 100
        multiplier = asset["multiplier"]
        stop_dist = round(atr_val * multiplier, 2)

        entry = price
        target = round(price * 1.08 if direction == "BUY" else price * 0.92, 2)
        stop = round(price - stop_dist if direction == "BUY" else price + stop_dist, 2)

        trades.append({
            "symbol": symbol,
            "name": asset["name"],
            "asset_class": asset["asset_class"],
            "direction": direction,
            "conviction": conviction,
            "entry": entry,
            "target": target,
            "stop": stop,
            "atr_pct": asset["atr_pct"],
            "stop_multiplier": multiplier,
        })

    output = {
        "generated_at": now,
        "total_positions": len(trades),
        "aggregate_bias": "bullish" if sum(1 for t in trades if t["direction"] == "BUY") > len(trades) / 2 else "bearish",
        "trades": trades,
    }

    out_path = OUT_DIR / "trades.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"✓ trades.json: {len(trades)} positions, bias={output['aggregate_bias']}")


if __name__ == "__main__":
    main()
