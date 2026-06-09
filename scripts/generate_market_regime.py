#!/usr/bin/env python3
"""generate_market_regime.py — Mike Green's top 3 retail indicators from COT + ICI + existing data.

Reads: data/market_data/cot.json, data/market_data/ici_flows.json,
       data/market_data/alpha_vantage.json, data/market_data/fred.json
Writes: site/data/market_regime.json — single file consumed by flows page

Mike Green's Top 3 Retail Indicators (focus-group validated June 2026):
  1. Money Flow — passive/active flow momentum from ICI + COT
  2. Top Heavy — equity concentration from COT S&P 500 positioning
  3. Bond Fear — MOVE Index proxy from bond futures COT + yield curve
"""

import json
from datetime import datetime, timezone
from pathlib import Path

PROJ = Path(__file__).parent.parent
DATA_DIR = PROJ / "data" / "market_data"
COT_PATH = DATA_DIR / "cot.json"
ICI_PATH = DATA_DIR / "ici_flows.json"
AV_PATH = DATA_DIR / "alpha_vantage.json"
FRED_PATH = DATA_DIR / "fred.json"
OUT_PATH = PROJ / "site" / "data" / "market_regime.json"


def load_json(path):
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def compute_money_flow(ici_data, cot_data):
    """Money Flow — passive/active flow momentum.
    ETF flows are proxy for passive. COT Lev_Money (CTAs) + Asset_Mgr for active.
    Returns: direction (BULLISH/BEARISH/NEUTRAL), strength (0-100), weekly_change_billions.
    """
    result = {
        "indicator": "Money Flow",
        "description": "Passive + active flow momentum — are markets absorbing capital or bleeding?",
        "direction": "NEUTRAL",
        "strength": 50,
        "components": {}
    }

    # ETF flows (passive proxy)
    etf_b = 0
    if ici_data:
        weekly = None
        data_block = ici_data.get("data", {})
        cf = data_block.get("combined_flows", {})
        wf = cf.get("weekly", [])
        if wf:
            weekly = wf[-1]  # latest week
        elif cf.get("monthly"):
            weekly = cf["monthly"][-1]  # fallback to latest month

        if weekly:
            total_m = weekly.get("total_flows", 0)
            etf_b = total_m / 1000  # millions → billions
            result["components"]["etf_flows_billions"] = round(etf_b, 1)
            result["components"]["etf_flows_date"] = weekly.get("date", "?")

    # COT positioning (active proxy)
    cot_signals = 0  # bullish - bearish count
    cot_count = 0
    if cot_data:
        mkts = cot_data.get("markets", {})
        for key, m in mkts.items():
            if not isinstance(m, dict):
                continue
            cats = m.get("categories", {})
            lev = cats.get("Lev_Money") or cats.get("M_Money")
            if lev:
                net = lev.get("net", 0)
                if net > 0:
                    cot_signals += 1
                elif net < 0:
                    cot_signals -= 1
                cot_count += 1

        result["components"]["cot_positioning_count"] = cot_count
        result["components"]["cot_bullish_bias"] = cot_signals

    # Combined direction
    if etf_b > 5 and cot_signals > 0:
        result["direction"] = "BULLISH"
        result["strength"] = min(100, 50 + int(abs(etf_b) * 2) + cot_signals * 5)
    elif etf_b < -5 and cot_signals < 0:
        result["direction"] = "BEARISH"
        result["strength"] = min(100, 50 + int(abs(etf_b) * 2) + abs(cot_signals) * 5)
    elif etf_b > 0 or cot_signals > 0:
        result["direction"] = "BULLISH"
        result["strength"] = 55
    else:
        result["direction"] = "NEUTRAL"
        result["strength"] = 50

    return result


def compute_top_heavy(cot_data):
    """Top Heavy — equity concentration from S&P 500 COT positioning.
    Asset_Mgr net long as % of open interest = passive weight.
    Lev_Money short = active skepticism. Gap = concentration risk.
    """
    result = {
        "indicator": "Top Heavy",
        "description": "Equity concentration risk — how top-heavy is the market?",
        "level": "MODERATE",
        "concentration_pct": 0,
        "components": {}
    }

    if not cot_data:
        return result

    spx = cot_data.get("markets", {}).get("S&P_500", {})
    if not spx:
        return result

    oi = spx.get("open_interest", 1)
    cats = spx.get("categories", {})
    am = cats.get("Asset_Mgr", {})
    lm = cats.get("Lev_Money", {})

    am_net_pct = am.get("net_pct_oi", 0)
    lm_net_pct = lm.get("net_pct_oi", 0)
    concentration = abs(am_net_pct)  # how concentrated in one direction

    result["components"]["asset_mgr_net_pct_oi"] = round(am_net_pct, 1)
    result["components"]["lev_money_net_pct_oi"] = round(lm_net_pct, 1)
    result["components"]["spx_open_interest"] = oi

    if concentration > 40:
        result["level"] = "EXTREME"
        result["concentration_pct"] = round(concentration)
    elif concentration > 25:
        result["level"] = "HIGH"
        result["concentration_pct"] = round(concentration)
    elif concentration > 15:
        result["level"] = "MODERATE"
        result["concentration_pct"] = round(concentration)
    else:
        result["level"] = "LOW"
        result["concentration_pct"] = round(concentration)

    return result


def compute_bond_fear(cot_data, fred_data):
    """Bond Fear — MOVE Index proxy from Treasury futures + yield curve.
    VIX for bonds. High bond fear = rate volatility expectations.
    """
    result = {
        "indicator": "Bond Fear",
        "description": "Treasury volatility expectations — VIX for bonds.",
        "level": "MODERATE",
        "score": 50,
        "components": {}
    }

    # Treasury COT: large spec positioning divergence = fear
    if cot_data:
        mkts = cot_data.get("markets", {})
        bond_positions = []
        for key in ["UST_10Y", "UST_2Y", "UST_5Y", "UST_Bond"]:
            m = mkts.get(key)
            if m and isinstance(m, dict):
                cats = m.get("categories", {})
                lev = cats.get("Lev_Money", {})
                am = cats.get("Asset_Mgr", {})
                if lev and am:
                    # Divergence between fast money (Lev) and slow money (AM)
                    divergence = lev.get("net_pct_oi", 0) - am.get("net_pct_oi", 0)
                    bond_positions.append(abs(divergence))

        if bond_positions:
            avg_divergence = sum(bond_positions) / len(bond_positions)
            result["components"]["treasury_position_divergence"] = round(avg_divergence, 1)

    # Yield curve spread
    if fred_data:
        yc = fred_data.get("yield_curve", {})
        if yc:
            spread = yc.get("spread", 0)
            result["components"]["yield_curve_spread"] = round(spread, 2)

    # Score
    div = result["components"].get("treasury_position_divergence", 0)
    spread = abs(result["components"].get("yield_curve_spread", 0))

    fear_score = min(100, div * 2 + spread * 20)
    result["score"] = round(fear_score)

    if fear_score > 70:
        result["level"] = "HIGH"
    elif fear_score > 40:
        result["level"] = "MODERATE"
    else:
        result["level"] = "LOW"

    return result


def main():
    cot = load_json(COT_PATH)
    ici = load_json(ICI_PATH)
    av = load_json(AV_PATH)
    fred = load_json(FRED_PATH)

    regime = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Mike Green Framework — Gazzetta di Kyiv Market Regime Monitor",
        "indicators": [
            compute_money_flow(ici, cot),
            compute_top_heavy(cot),
            compute_bond_fear(cot, fred),
        ]
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(regime, f, indent=2, ensure_ascii=False)

    print(f"✓ Market regime generated → {OUT_PATH}")
    for ind in regime["indicators"]:
        score_or_level = ind.get("strength", ind.get("score", ind.get("concentration_pct", "?")))
        direction_or_level = ind.get("direction", ind.get("level", "?"))
        print(f"  {ind['indicator']}: {direction_or_level} ({score_or_level})")


if __name__ == "__main__":
    main()
