#!/usr/bin/env python3
"""
Bridge: Enrich editorial writer stories with minimum capital_flow dicts.
Editorial writer produces stories without capital_flow, generated_at, etc.
This script adds derived capital_flow + generated_at so all stories
have consistent field sets regardless of pipeline source.

Usage: python scripts/enrich_editorial_stories.py
"""

import json, sys, re
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EDITORIAL = PROJECT_ROOT / "data" / "publish" / "stories.json"
MAIN = PROJECT_ROOT / "data" / "stories.json"

# Simplified asset class detection
ASSET_KEYWORDS = {
    "commodities": ["oil", "crude", "brent", "wti", "energy", "gold", "silver", "metal", "copper", "wheat", "grain"],
    "crypto": ["btc", "bitcoin", "crypto", "eth", "ethereum", "solana", "stablecoin", "defi", "token"],
    "defense": ["defense", "missile", "military", "drone", "weapon", "nato", "pentagon"],
    "fixed_income": ["bond", "treasury", "yield", "tlt", "fed", "ecb", "rate hike", "interest"],
    "equities": ["stock", "equity", "nasdaq", "sp500", "s&p", "dow"],
    "fx": ["dollar", "euro", "yuan", "yen", "forex", "currency", "dxy"],
    "tech": ["ai ", "semiconductor", "chip", "nvidia", "openai", "cloud", "saas"],
}


def detect_asset_class(headline, text):
    combined = f"{headline} {text}".lower()
    for ac, keywords in ASSET_KEYWORDS.items():
        if any(k in combined for k in keywords):
            return ac
    return "equities"


def detect_direction(headline, text):
    combined = f"{headline} {text}".lower()
    bearish = ["drop", "fall", "crash", "decline", "plunge", "sell-off", "bear", "short", "outflow", "sanction", "ban"]
    bullish = ["surge", "rally", "rise", "boom", "grow", "bull", "long", "inflow", "breakthrough", "record high"]
    bear_count = sum(1 for w in bearish if w in combined)
    bull_count = sum(1 for w in bullish if w in combined)
    return "outflow" if bear_count > bull_count else "inflow"


def derive_amount(headline, asset_class):
    """Derive approximate amount from story context."""
    text = headline.lower()
    # Explicit amounts
    m = re.search(r'\$(\d+\.?\d*)\s*([BbTtMm])', headline)
    if m:
        val = float(m.group(1))
        unit = m.group(2).upper()
        if unit == 'T':
            return val * 1000
        elif unit == 'M':
            return val / 1000
        return val
    # Asset-class defaults
    defaults = {
        "defense": 8.0, "commodities": 12.0, "energy": 15.0,
        "tech": 20.0, "crypto": 3.5, "fixed_income": 25.0,
        "fx": 30.0, "equities": 10.0,
    }
    return defaults.get(asset_class, 10.0)


def main():
    now = datetime.now(timezone.utc).isoformat()

    # Enrich editorial stories
    if EDITORIAL.exists():
        ed = json.loads(EDITORIAL.read_text())
        ed_stories = ed.get("stories", [])
        enriched = 0
        for s in ed_stories:
            if "capital_flow" not in s:
                headline = s.get("headline", "")
                text = f"{s.get('they_say','')} {s.get('reality','')} {s.get('portfolio_implication','')}"
                ac = detect_asset_class(headline, text)
                direction = detect_direction(headline, text)
                amount = derive_amount(headline, ac)

                s["capital_flow"] = {
                    "direction": direction,
                    "amount_b": amount,
                    "asset_class": ac,
                    "projected": s.get("portfolio_implication", "")[:200],
                    "pace_multiplier": 1.5,  # editorial stories are medium velocity
                    "confidence_pct": 65,
                    "confidence_level": "medium",
                    "claim": f"${amount}B {direction} {ac}",
                    "confidence": "65%",
                }
                enriched += 1
            if "generated_at" not in s:
                s["generated_at"] = ed.get("generated_at") or now

        EDITORIAL.write_text(json.dumps(ed, indent=2, ensure_ascii=False))
        print(f"Editorial: enriched {enriched}/{len(ed_stories)} stories with capital_flow + generated_at")

    # Ensure main stories.json has generated_at on every story
    if MAIN.exists():
        d = json.loads(MAIN.read_text())
        stories = d.get("stories", [])
        doc_ts = d.get("generated_at") or d.get("last_updated") or now
        fixed = 0
        for s in stories:
            if "generated_at" not in s:
                s["generated_at"] = doc_ts
                fixed += 1
        if fixed:
            MAIN.write_text(json.dumps(d, indent=2, ensure_ascii=False))
            print(f"Main: added generated_at to {fixed}/{len(stories)} stories")


if __name__ == "__main__":
    main()
