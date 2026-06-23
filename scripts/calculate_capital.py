#!/usr/bin/env python3
"""
calculate_capital.py -- Multi-source capital volume computation
================================================================
Phase 3: Bridges CFTC institutional positioning + FRED macro regime
into real dollar-value capital-at-stake per narrative.

Reads:  cftc_positions.json, fred_series.json, market_prices.json, stories.json
Writes: stories.json (atomic swap) — adds capital_at_stake_usd, data_fidelity,
        materiality_pass, tier, rci, narrative_alpha

Governor step 6 — runs after classify, before gen_flows.
"""

import json
import os
import statistics
import sys
from pathlib import Path

# -- config ----------------------------------------------------------
PROJECT = Path(__file__).resolve().parent.parent
PUBLIC_DATA = PROJECT / "public" / "data"
DATA_DIR = PROJECT / "data"
STORIES_FILE = PUBLIC_DATA / "stories.json"
CFTC_FILE = DATA_DIR / "cftc_positions.json"
FRED_FILE = DATA_DIR / "fred_series.json"
PRICES_FILE = DATA_DIR / "market_prices.json"

MATERIALITY_THRESHOLD_USD = 50_000_000   # $50M minimum to pass gate
GAP_MATERIALITY_FLOOR = 20               # stories below this GAP are never material
FIDELITY_MULTIPLIERS = {"TIER_1": 1.0, "TIER_2": 0.8, "TIER_3": 0.5}

# Approximate contract notional values (June 2026) for dollar-value conversion
# CFTC data gives us contract counts; multiply by these to get USD exposure
CONTRACT_NOTIONALS = {
    "GC": 100 * 3300,        # Gold: 100 oz × ~$3300/oz = $330K
    "SI": 5000 * 33,         # Silver: 5000 oz × ~$33/oz = $165K
    "PL": 50 * 1000,         # Platinum: 50 oz × ~$1000/oz = $50K
    "CL": 1000 * 68,         # WTI Crude: 1000 bbl × ~$68/bbl = $68K
    "NG": 10000 * 3.50,      # Natural Gas: 10K MMBtu × ~$3.50 = $35K
    "RB": 42000 * 2.20,      # RBOB Gasoline: 42K gal × ~$2.20 = $92.4K
    "HO": 42000 * 2.40,      # Heating Oil: 42K gal × ~$2.40 = $100.8K
    "HG": 25000 * 4.60,      # Copper: 25K lbs × ~$4.60/lb = $115K
    "ZC": 5000 * 4.50,       # Corn: 5000 bu × ~$4.50/bu = $22.5K
    "ZW": 5000 * 5.50,       # Wheat: 5000 bu × ~$5.50/bu = $27.5K
    "ZS": 5000 * 10.50,      # Soybeans: 5000 bu × ~$10.50 = $52.5K
    "ZM": 100 * 350,         # Soybean Meal: 100 tons × ~$350 = $35K
    "SB": 112000 * 0.19,     # Sugar: 112K lbs × ~$0.19/lb = $21.3K
    "KC": 37500 * 2.70,      # Coffee: 37.5K lbs × ~$2.70/lb = $101.3K
    "CC": 10 * 6500,         # Cocoa: 10 metric tons × ~$6500 = $65K
    "AL": 25 * 2500,         # Aluminum: 25 metric tons × ~$2500 = $62.5K
    "ST": 20 * 700,          # Steel: 20 short tons × ~$700 = $14K
    "JF": 42000 * 2.20,      # Jet Fuel (proxy RBOB sizing)
    "JH": 42000 * 0.15,      # Jet/Heat spread
}

# Narrative → primary data source mapping
NARRATIVE_DATA_SOURCE = {
    "dollar_decline":      "cftc",  # Gold/Silver/Platinum positioning
    "energy_sovereignty":  "cftc",  # Crude/NatGas product positioning
    "commodity_supercycle":"cftc",  # Copper/Grains/Softs positioning
    "deglobalization":     "cftc",  # Industrial metals → defense supply chain
    "rate_cycle":          "fred",  # Yield curve, Fed Funds, inflation
    "china_ascent":        "fred",  # CNY exchange rate, trade balance proxy
    "tech_convergence":    "prices",# ETF AUM (no CFTC futures for tech)
    "space_economy":       "prices",# ETF AUM
    "gene_editing":        "prices",# ETF AUM
    "wealthy_sports":      "prices",# ETF AUM
    "ai_chips":            "prices",# ETF AUM
    "crypto_reserve":      "prices",# ETF AUM + CoinGecko
}


# -- helpers ---------------------------------------------------------
def load_json(path):
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def fix_ownership(path_str):
    if sys.platform != "linux":
        return
    try:
        import pwd, grp
        uid = pwd.getpwnam("gazzetta").pw_uid
        gid = grp.getgrnam("gazzetta").gr_gid
        os.chown(path_str, uid, gid)
    except (KeyError, OSError):
        pass


# -- capital computation ---------------------------------------------
def compute_cftc_capital(narrative_id, cftc_data):
    """
    Convert CFTC speculative net positioning to dollar-value capital at stake.
    Uses managed_money_net (specs) as the primary signal.
    """
    positions = cftc_data.get("positions_by_narrative", {}).get(narrative_id)
    if not positions:
        return 0, "TIER_3"

    total_usd = 0
    for ticker in positions.get("contracts", []):
        contract = cftc_data.get("positions_by_contract", {}).get(ticker, {})
        if contract.get("status") != "ok":
            continue
        mm_net = abs(contract.get("managed_money_net", 0) or 0)
        notional = CONTRACT_NOTIONALS.get(ticker, 100_000)
        total_usd += mm_net * notional

    fidelity = "TIER_1" if total_usd > 0 else "TIER_3"
    return total_usd, fidelity


def compute_fred_capital(narrative_id, fred_data):
    """
    Derive capital-flow proxy from FRED macro series.
    Uses key series relevant to each narrative.
    """
    series = fred_data.get("series", {})
    regime = fred_data.get("macro_regime", "UNKNOWN")

    # Narrative → relevant FRED series + scaling factors
    narrative_series = {
        "rate_cycle": ["DGS10", "T10Y2Y", "DFEDTARU", "UNRATE"],
        "china_ascent": ["DEXCHUS", "BOPGSTB", "INDPRO"],
        "dollar_decline": ["DTWEXBGS", "DEXUSEU", "DEXJPUS"],
        "deglobalization": ["BOPGSTB", "GPDI", "INDPRO"],
        "commodity_supercycle": ["PPIACO", "CPIAUCSL", "DCOILWTICO"],
        "energy_sovereignty": ["DCOILWTICO", "DHHNGSP", "PPIACO"],
    }

    keys = narrative_series.get(narrative_id, [])
    if not keys:
        return 0, "TIER_3"

    # Sum absolute values of key series, scaled to approximate capital scale
    total_value = 0
    count = 0
    for key in keys:
        s = series.get(key, {})
        val = s.get("value")
        if val is not None:
            total_value += abs(val)
            count += 1

    if count == 0:
        return 0, "TIER_3"

    avg = total_value / count

    # FRED series are rates/indices — need scaling to capital-dollar space
    # Base: $10B × average series value normalized to plausible ranges
    if narrative_id == "rate_cycle":
        capital = avg * 2_000_000_000     # yield % → $2B per point
    elif narrative_id == "china_ascent":
        capital = avg * 500_000_000        # exchange rate/balance → $500M
    elif narrative_id == "dollar_decline":
        capital = avg * 1_000_000_000      # dollar index → $1B
    else:
        capital = avg * 250_000_000        # generic macro → $250M

    # Regime modifier
    regime_mod = {
        "INVERSION": 1.5,
        "TIGHTENING": 1.3,
        "ACCOMMODATIVE": 1.2,
        "EASING": 1.0,
        "NEUTRAL": 0.8,
    }.get(regime, 0.8)

    capital *= regime_mod
    fidelity = "TIER_2"
    return capital, fidelity


def compute_prices_capital(narrative_id, prices_data):
    """
    Fallback: use ETF AUM from market_prices.json.
    This is the pre-existing method; CFTC/FRED override when available.
    """
    narrative_tickers = {
        "tech_convergence": ["QQQ", "SMH", "SOXX", "ARKK"],
        "space_economy": ["ROKT", "UFO", "ARKX"],
        "gene_editing": ["ARKG", "XBI", "IBB"],
        "wealthy_sports": ["BATRK", "MSGS", "MANU"],
        "ai_chips": ["SMH", "SOXX", "QQQ"],
        "crypto_reserve": [],  # handled separately
    }

    tickers = narrative_tickers.get(narrative_id, [])
    if not tickers:
        # crypto_reserve: use BTC market cap proxy
        if narrative_id == "crypto_reserve":
            # Estimate from BTC at ~$65K with active trading float ~5%
            return 64_000 * 19_700_000 * 0.05, "TIER_3"
        return 0, "TIER_3"

    # Sum AUM from market_prices.json for these tickers
    total_aum = 0
    for t in tickers:
        info = prices_data.get(t, {})
        aum = info.get("aum", 0) or info.get("market_cap", 0) or 0
        total_aum += aum

    # ETF AUM is total passive — active positioning is fraction
    active_share = 0.15  # ~15% of ETF AUM is active positioning
    capital = total_aum * active_share
    fidelity = "TIER_3"
    return capital, fidelity


def get_asset_base(narrative_id, cftc, fred, prices):
    """Return (capital_at_stake_base_usd, fidelity_tier) for a narrative."""
    source = NARRATIVE_DATA_SOURCE.get(narrative_id, "prices")

    # Tier 1: CFTC — highest fidelity
    if source == "cftc":
        capital, fidelity = compute_cftc_capital(narrative_id, cftc)
        if capital > 0:
            return capital, fidelity
        # Fall through to prices if CFTC has no data for this narrative

    # Tier 2: FRED — macro overlay
    if source == "fred":
        capital, fidelity = compute_fred_capital(narrative_id, fred)
        if capital > 0:
            return capital, fidelity

    # Try CFTC as secondary if FRED is primary
    if source == "fred":
        capital, fidelity = compute_cftc_capital(narrative_id, cftc)
        if capital > 0:
            return capital, fidelity

    # Tier 3: ETF AUM fallback
    return compute_prices_capital(narrative_id, prices)


def compute_tier(gap, materiality_pass):
    if not materiality_pass:
        return "SETTLING"
    if gap >= 65:
        return "BREAKING"
    if gap >= 40:
        return "ACTIVE"
    return "SETTLING"


# -- main ------------------------------------------------------------
def main():
    print("[calc_capital] Computing Capital at Stake + RCI Alpha + Materiality Gate...")

    stories_data = load_json(STORIES_FILE)
    cftc = load_json(CFTC_FILE)
    fred = load_json(FRED_FILE)
    prices = load_json(PRICES_FILE)

    all_stories = stories_data.get("all_stories", [])
    if not all_stories:
        print("[-] No stories found.")
        sys.exit(0)

    processed = 0
    material_count = 0
    narrative_accum = {}  # {nid: {"capital_bases": [], "fidelity": tier}}

    for story in all_stories:
        nid = story.get("narrative_id", "")
        gap = int(story.get("contradiction_gap", 0))

        # 1. Get asset base from best available source
        asset_base, fidelity = get_asset_base(nid, cftc, fred, prices)
        multiplier = FIDELITY_MULTIPLIERS.get(fidelity, 0.5)

        # 2. Capital at stake = asset_base × (gap/100) × fidelity
        capital_usd = asset_base * (gap / 100.0) * multiplier

        # 3. Materiality gate
        is_material = (
            capital_usd >= MATERIALITY_THRESHOLD_USD and gap >= GAP_MATERIALITY_FLOOR
        )

        # 4. Update story fields
        story["capital_at_stake_usd"] = int(capital_usd)
        story["capital_base_usd"] = int(asset_base)
        story["data_fidelity"] = fidelity
        story["materiality_pass"] = is_material
        story["tier"] = compute_tier(gap, is_material)

        processed += 1
        if is_material:
            material_count += 1

        # Accumulate for narrative alpha
        if nid and nid != "unassigned" and asset_base > 0:
            if nid not in narrative_accum:
                narrative_accum[nid] = {"capital_bases": [], "fidelity": fidelity}
            narrative_accum[nid]["capital_bases"].append(asset_base)
            narrative_accum[nid]["fidelity"] = fidelity  # latest wins

    # -- Narrative Alpha: median-gap capital per narrative --
    narrative_alpha = {}
    for nid in sorted(narrative_accum.keys()):
        bases = narrative_accum[nid]["capital_bases"]
        fid = narrative_accum[nid]["fidelity"]
        mult = FIDELITY_MULTIPLIERS.get(fid, 0.5)

        # Median capital base × fidelity multiplier
        median_base = statistics.median(bases) if bases else 0
        total_cap = median_base * mult

        narrative_alpha[nid] = {
            "total_capital_usd": int(total_cap),
            "story_count": len(bases),
            "median_capital_base_usd": int(median_base),
            "data_fidelity": fid,
        }

    stories_data["all_stories"] = all_stories
    stories_data["narrative_alpha"] = narrative_alpha

    # Atomic write
    tmp_path = STORIES_FILE.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(stories_data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, STORIES_FILE)

    fix_ownership(str(STORIES_FILE))

    cftc_ok = cftc.get("status") == "ok"
    fred_ok = fred.get("status") == "ok"
    print(
        f"[+] {processed} stories processed. {material_count} passed materiality gate."
    )
    print(
        f"[+] Data sources: CFTC={'OK' if cftc_ok else 'DEGRADED'}, "
        f"FRED={'OK' if fred_ok else 'DEGRADED'}, "
        f"Prices={'OK' if prices else 'DEGRADED'}"
    )
    print(f"[+] Narrative alpha computed for {len(narrative_alpha)} narratives.")


if __name__ == "__main__":
    main()
