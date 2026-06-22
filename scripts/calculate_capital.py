#!/usr/bin/env python3
"""
La Gazzetta di Kyiv — Phase 1, Task 1.5
Module: calculate_capital.py
Purpose: Compute capital_at_stake_usd from TIER_1/2/3 data + apply materiality gate.
Reads: cftc_cot.json, fred_macro.json, coingecko_data.json, stories.json
Writes: stories.json (atomic)
"""

import os, sys, json, math
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
PUBLIC_DATA = PROJECT / "public" / "data"
DATA_DIR = PROJECT / "data"
STORIES_FILE = PUBLIC_DATA / "stories.json"
CFTC_FILE = DATA_DIR / "cftc_cot.json"
FRED_FILE = DATA_DIR / "fred_macro.json"
COINGECKO_FILE = DATA_DIR / "coingecko_data.json"

MATERIALITY_THRESHOLD_USD = 50_000_000   # $50M minimum
BREAKING_GAP_THRESHOLD = 65

# Real notional values per contract (approximate, June 2026)
CONTRACT_NOTIONALS = {
    "GOLD - COMMODITY EXCHANGE INC.": 100 * 3300,             # 100 oz × ~$3300
    "SILVER - COMMODITY EXCHANGE INC.": 5000 * 33,            # 5000 oz × ~$33
    "WTI FINANCIAL CRUDE OIL - NEW YORK MERCANTILE EXCHANGE": 1000 * 68,  # 1000 bbl × ~$68
    "UST BOND - CHICAGO BOARD OF TRADE": 1000 * 115,          # $1000 × ~115 pts
    "E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE": 50 * 5900,  # $50 × ~5900
    "BITCOIN - CHICAGO MERCANTILE EXCHANGE": 5 * 64000,       # 5 BTC × ~$64K
}

FIDELITY_MULTIPLIERS = {"TIER_1": 1.0, "TIER_2": 0.8, "TIER_3": 0.5}


def fix_ownership(path_str: str):
    if sys.platform != "linux":
        return
    try:
        import pwd, grp
        uid = pwd.getpwnam("gazzetta").pw_uid
        gid = grp.getgrnam("gazzetta").gr_gid
        os.chown(path_str, uid, gid)
    except (KeyError, OSError):
        pass


def load_json(path: Path) -> dict:
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {}


def get_asset_base(narrative_id: str, cftc: dict, fred: dict, cg: dict):
    """
    Return (asset_base_usd, fidelity_tier) for a narrative.
    Uses real positioning data where available; falls back to proxies.
    """
    cftc_data = cftc.get("data", {})
    fred_m = fred.get("metrics", {})
    cg_assets = cg.get("assets", {})

    # ── crypto_reserve → CoinGecko BTC market cap (TIER_2) ──
    if narrative_id == "crypto_reserve":
        btc = cg_assets.get("bitcoin", {})
        mc = btc.get("market_cap_usd", 0)
        # Use 5% of BTC market cap as "at stake" base (rest is passive hold)
        return mc * 0.05, "TIER_2"

    # ── commodity_supercycle → CFTC net positioning notional (TIER_1) ──
    if narrative_id == "commodity_supercycle":
        total_notional = 0.0
        for market_key in ["GOLD - COMMODITY EXCHANGE INC.",
                           "WTI FINANCIAL CRUDE OIL - NEW YORK MERCANTILE EXCHANGE",
                           "SILVER - COMMODITY EXCHANGE INC."]:
            snap = cftc_data.get(market_key, {})
            net = abs(snap.get("noncommercial_net", 0))
            notional_per = CONTRACT_NOTIONALS.get(market_key, 100_000)
            total_notional += net * notional_per
        return total_notional, "TIER_1"

    # ── rate_cycle → S&P 500 + UST Bond CFTC + FRED proxy (TIER_1/TIER_3 blend) ──
    if narrative_id == "rate_cycle":
        # S&P 500 futures positioning (TIER_1)
        sp = cftc_data.get("E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE", {})
        sp_net = abs(sp.get("noncommercial_net", 0))
        sp_notional = CONTRACT_NOTIONALS.get(
            "E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE", 300_000)
        sp_exposure = sp_net * sp_notional

        # UST Bond positioning (TIER_1)
        ust = cftc_data.get("UST BOND - CHICAGO BOARD OF TRADE", {})
        ust_net = abs(ust.get("noncommercial_net", 0))
        ust_notional = CONTRACT_NOTIONALS.get(
            "UST BOND - CHICAGO BOARD OF TRADE", 115_000)
        ust_exposure = ust_net * ust_notional

        # FRED WALCL as macro proxy (TIER_3, additive but discounted)
        walcl = fred_m.get("WALCL", {}).get("current_value", 0)
        walcl_absolute = walcl * 1_000_000 * 0.0001  # ~$673M scale

        base = sp_exposure + ust_exposure + walcl_absolute
        # Blend: CFTC is TIER_1, FRED is TIER_3 → effective TIER_2
        return base, "TIER_2"

    # ── dollar_decline → CFTC Bitcoin + Gold as dollar-hedge proxies ──
    if narrative_id == "dollar_decline":
        btc_snap = cftc_data.get("BITCOIN - CHICAGO MERCANTILE EXCHANGE", {})
        gold_snap = cftc_data.get("GOLD - COMMODITY EXCHANGE INC.", {})
        btc_net = abs(btc_snap.get("noncommercial_net", 0))
        gold_net = abs(gold_snap.get("noncommercial_net", 0))
        btc_notional = CONTRACT_NOTIONALS.get(
            "BITCOIN - CHICAGO MERCANTILE EXCHANGE", 320_000)
        gold_notional = CONTRACT_NOTIONALS.get(
            "GOLD - COMMODITY EXCHANGE INC.", 330_000)
        base = btc_net * btc_notional + gold_net * gold_notional
        return base, "TIER_1"

    # ── Fallback for narratives without data ──
    return 50_000_000.0, "TIER_3"


def compute_tier(gap: int, materiality_pass: bool) -> str:
    if not materiality_pass:
        return "SETTLING"
    if gap >= 65:
        return "BREAKING"
    if gap >= 40:
        return "ACTIVE"
    return "SETTLING"


def main():
    print("[Task 1.5] Computing Capital at Stake + RCI Alpha + Materiality Gate...")

    stories_data = load_json(STORIES_FILE)
    cftc = load_json(CFTC_FILE)
    fred = load_json(FRED_FILE)
    cg = load_json(COINGECKO_FILE)
    macro = load_json(DATA_DIR / "macro_baselines.json")

    baselines = macro.get("baselines", {})
    narrative_segments = macro.get("narrative_segments", {})
    saturation_threshold = macro.get("saturation_threshold", 0.15)

    all_stories = stories_data.get("all_stories", [])
    if not all_stories:
        print("[-] No stories found.")
        sys.exit(0)

    processed = 0
    material = 0
    # narrative_data: {nid: {asset_base: [gaps], 'fidelity': tier}}
    narrative_data = {}

    for story in all_stories:
        nid = story.get("narrative_id", "")
        gap = int(story.get("contradiction_gap", 0))

        # 1. Get asset base + fidelity from real data
        asset_base, fidelity = get_asset_base(nid, cftc, fred, cg)
        multiplier = FIDELITY_MULTIPLIERS.get(fidelity, 0.5)

        # 2. Capital at stake = asset_base × (gap/100) × fidelity_multiplier
        capital_usd = asset_base * (gap / 100.0) * multiplier

        # 3. Materiality gate
        is_material = (capital_usd >= MATERIALITY_THRESHOLD_USD) and (gap >= 40)

        # 4. RCI — Relative Capital Intensity (Phase 6)
        segment_key = narrative_segments.get(nid)
        segment_cap = baselines.get(segment_key, 1) if segment_key else 1
        velocity_mod = gap / 100.0 if gap > 0 else 0.01
        rci = (capital_usd / max(segment_cap, 1)) * velocity_mod
        dominance = capital_usd / max(segment_cap, 1)

        # 5. Update story fields
        story["capital_at_stake_usd"] = int(capital_usd)
        story["capital_base_usd"] = int(asset_base)
        story["data_fidelity"] = fidelity
        story["materiality_pass"] = is_material
        story["tier"] = compute_tier(gap, is_material)
        story["rci"] = round(rci, 8)
        story["dominance_ratio"] = round(dominance, 8)
        story["segment_cap_usd"] = int(segment_cap)

        processed += 1
        if is_material:
            material += 1

        # Group gaps by unique asset_base to avoid double-counting
        if nid and nid != "unassigned" and asset_base > 0:
            if nid not in narrative_data:
                narrative_data[nid] = {}
            if asset_base not in narrative_data[nid]:
                narrative_data[nid][asset_base] = {"gaps": [], "fidelity": fidelity}
            narrative_data[nid][asset_base]["gaps"].append(gap)

    # ── Narrative-level Alpha Metrics (median-gap per unique asset base) ──
    import statistics
    narrative_alpha = {}
    for nid in sorted(narrative_data.keys()):
        bases = narrative_data[nid]
        total_cap = 0
        for asset_base, info in bases.items():
            median_gap = statistics.median(info["gaps"]) if info["gaps"] else 0
            mult = FIDELITY_MULTIPLIERS.get(info["fidelity"], 0.5)
            total_cap += asset_base * (median_gap / 100.0) * mult

        segment_key = narrative_segments.get(nid)
        segment_cap = baselines.get(segment_key, 1) if segment_key else 1
        dominance = total_cap / max(segment_cap, 1)
        saturated = dominance >= saturation_threshold
        narrative_alpha[nid] = {
            "total_capital_usd": int(total_cap),
            "segment": segment_key or "unknown",
            "segment_cap_usd": int(segment_cap),
            "dominance_ratio": round(dominance, 6),
            "flow_saturated": saturated,
        }

    stories_data["all_stories"] = all_stories
    stories_data["narrative_alpha"] = narrative_alpha

    # Atomic write
    tmp_path = STORIES_FILE.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(stories_data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, STORIES_FILE)

    fix_ownership(str(STORIES_FILE))
    print(f"[+] {processed} stories processed. {material} passed materiality gate.")
    print(f"[+] Narrative alpha computed for {len(narrative_alpha)} narratives.")


if __name__ == "__main__":
    main()
