#!/usr/bin/env python3
"""enrich_market_data.py — Merge Alpha Vantage + FRED data into stories/flows.

Reads: data/stories.json, data/market_data/alpha_vantage.json, data/market_data/fred.json
Writes: site/data/stories.json (enriched), data/market_data/signals.json

Enriches stories with real market context:
- Commodity stories get actual prices
- Rate/FX stories get real yield curve and FX data
- Adds market_signal annotations to capital_flow dicts
"""

import json
from datetime import datetime, timezone
from pathlib import Path

PROJ = Path(__file__).parent.parent
STORIES_PATH = PROJ / "data" / "stories.json"
AV_PATH = PROJ / "data" / "market_data" / "alpha_vantage.json"
FRED_PATH = PROJ / "data" / "market_data" / "fred.json"
SIGNALS_PATH = PROJ / "data" / "market_data" / "signals.json"

# Asset class → Alpha Vantage commodity mapping
ASSET_COMMODITY_MAP = {
    "commodities": ["WTI", "BRENT", "NATURAL_GAS", "GOLD"],
    "oil": ["WTI", "BRENT"],
    "gold": ["GOLD"],
    "energy": ["WTI", "BRENT", "NATURAL_GAS"],
    "agriculture": ["WHEAT", "CORN"],
    "metals": ["COPPER", "ALUMINUM", "GOLD"],
}

# Keyword → FRED series mapping for story enrichment
KEYWORD_FRED_MAP = {
    "yield": "DGS10",
    "treasury": "DGS10",
    "bond": "DGS10",
    "fed": "DFEDTARU",
    "rate hike": "DFEDTARU",
    "rate cut": "DFEDTARU",
    "inflation": "CPIAUCSL",
    "cpi": "CPIAUCSL",
    "money supply": "M2SL",
    "m2": "M2SL",
    "credit": "TOTALSL",
    "dollar": None,  # Handled via DXY FX pair
    "dxy": None,
    "eur": "EUR/USD",
    "yen": "USD/JPY",
    "yuan": "USD/CNY",
    "ruble": "USD/RUB",
}


def load_json(path):
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def compute_market_signals(av_data, fred_data):
    """Derive market-wide signals from external data."""
    signals = {"generated_at": datetime.now(timezone.utc).isoformat(), "signals": []}

    # Yield curve signal
    yc = (fred_data or {}).get("yield_curve", {})
    if yc:
        spread = yc.get("spread", 0)
        if spread < -0.5:
            signals["signals"].append({
                "type": "yield_curve",
                "level": "critical",
                "message": f"Yield curve deeply inverted ({spread}%) — recession signal active.",
                "data": yc,
            })
        elif spread < 0:
            signals["signals"].append({
                "type": "yield_curve",
                "level": "warning",
                "message": f"Yield curve inverted ({spread}%) — monitor for reversal.",
                "data": yc,
            })
        else:
            signals["signals"].append({
                "type": "yield_curve",
                "level": "normal",
                "message": f"Yield curve normalized ({spread}%).",
                "data": yc,
            })

    # VIX signal
    vix = (av_data or {}).get("vix", {})
    vix_price = vix.get("price", 0) if vix else 0
    if vix_price > 30:
        signals["signals"].append({
            "type": "vix",
            "level": "critical",
            "message": f"VIX at {vix_price} — extreme fear, expect volatility event.",
            "data": vix,
        })
    elif vix_price > 20:
        signals["signals"].append({
            "type": "vix",
            "level": "warning",
            "message": f"VIX elevated at {vix_price} — above normal range.",
            "data": vix,
        })

    # Fed funds signal
    fed = (fred_data or {}).get("series", {}).get("DFEDTARU", {})
    if fed:
        rate = fed.get("latest")
        prev = fed.get("previous")
        if rate and prev and rate != prev:
            direction = "hike" if rate > prev else "cut"
            signals["signals"].append({
                "type": "fed_funds",
                "level": "info",
                "message": f"Fed funds rate changed: {prev}% → {rate}% ({direction}).",
                "data": fed,
            })

    return signals


def enrich_stories(stories, av_data, fred_data):
    """Add market context to story capital_flow dicts."""
    if not stories:
        return

    for story in stories:
        cf = story.get("capital_flow", {})
        if not isinstance(cf, dict):
            continue

        asset_class = (cf.get("asset_class", "") or "").lower()
        headline = (story.get("headline", "") or "").lower()
        market_context = {}

        # Commodity prices
        if av_data and av_data.get("commodities"):
            for tag, symbols in ASSET_COMMODITY_MAP.items():
                if tag in asset_class or tag in headline:
                    for sym in symbols:
                        c = av_data["commodities"].get(sym)
                        if c:
                            market_context[f"price_{sym}"] = {
                                "value": c["price"],
                                "unit": c.get("unit", ""),
                                "date": c.get("date", ""),
                            }

        # FRED context from keywords
        if fred_data and fred_data.get("series"):
            for keyword, series_id in KEYWORD_FRED_MAP.items():
                if keyword in headline:
                    if series_id and series_id in fred_data["series"]:
                        s = fred_data["series"][series_id]
                        market_context[f"fred_{series_id}"] = {
                            "value": s["latest"],
                            "unit": s.get("unit", ""),
                            "date": s.get("latest_date", ""),
                            "name": s.get("name", ""),
                        }

        if market_context:
            cf["market_data"] = market_context
            story["capital_flow"] = cf


def main():
    av = load_json(AV_PATH)
    fred = load_json(FRED_PATH)

    if not av and not fred:
        print("⚠ No market data available — run fetch_alpha_vantage.py and fetch_fred.py first")
        return

    # Compute signals
    signals = compute_market_signals(av, fred)
    with open(SIGNALS_PATH, "w") as f:
        json.dump(signals, f, indent=2, ensure_ascii=False)
    print(f"✓ Generated market signals → {SIGNALS_PATH}")

    # Enrich stories
    stories_data = load_json(STORIES_PATH)
    if stories_data:
        stories = stories_data.get("stories", [])
        enrich_stories(stories, av, fred)
        if stories_data.get("lead"):
            enrich_stories([stories_data["lead"]], av, fred)
        with open(STORIES_PATH, "w") as f:
            json.dump(stories_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Enriched {len(stories)} stories with market context")

        # Copy to site/data
        import shutil
        shutil.copy(STORIES_PATH, PROJ / "site" / "data" / "stories.json")

    print("✓ Enrichment complete")


if __name__ == "__main__":
    main()
