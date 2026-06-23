#!/usr/bin/env python3
"""Map Gazzetta stories to tradeable assets based on sector, entity tags, and headline analysis.

Reads data/stories.json, enriches each story's asset_claim dict with:
- primary_ticker: the most relevant tradeable ticker
- tickers: list of related tickers
- confidence: mapping confidence (low/medium/high)

Called by: gazzetta_pipeline_unified.sh (Stage 3: ENRICH)
"""

import json, re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
STORIES_PATH = PROJECT / "data" / "stories.json"
OUTPUT = STORIES_PATH  # Overwrite in-place

# ── Sector → Ticker mapping ──
SECTOR_TICKERS = {
    "tech": ["QQQ", "NVDA", "MSFT", "AAPL", "SMH"],
    "crypto": ["BTC", "ETH", "SOL", "COIN", "MSTR"],
    "commodities": ["GSG", "DBC", "GLD", "USO", "SLV"],
    "energy": ["XLE", "USO", "XOP", "OIH"],
    "equities": ["SPY", "QQQ", "IWM", "DIA"],
    "defense": ["ITA", "PPA", "LMT", "RTX", "NOC"],
    "fixed_income": ["TLT", "IEF", "SHY", "AGG", "LQD"],
    "fx": ["UUP", "FXY", "FXE", "USDU"],
    "real_estate": ["VNQ", "IYR", "XLRE"],
    "healthcare": ["XLV", "IBB", "UNH", "JNJ"],
    "gold": ["GLD", "GDX", "IAU"],
}

# ── Keyword → Ticker mapping ──
KEYWORD_TICKERS = {
    "nvidia": "NVDA", "nvda": "NVDA",
    "apple": "AAPL", "microsoft": "MSFT", "msft": "MSFT",
    "bitcoin": "BTC", "btc": "BTC", "ethereum": "ETH", "eth": "ETH",
    "solana": "SOL", "sol": "SOL",
    "gold": "GLD", "oil": "USO", "crude": "USO", "brent": "BNO",
    "spx": "SPY", "s&p": "SPY", "nasdaq": "QQQ", "dow": "DIA",
    "treasury": "TLT", "bond": "AGG", "fed": "TLT",
    "iran": "USO", "hormuz": "USO", "strait": "USO",
    "defense": "ITA", "military": "ITA", "missile": "ITA",
    "crypto": "BTC", "blockchain": "BTC",
    "dollar": "UUP", "dxy": "UUP", "eur": "FXE", "yen": "FXY",
    "semiconductor": "SMH", "chip": "SMH", "ai": "NVDA",
    "energy": "XLE", "gas": "UNG", "natgas": "UNG",
    "copper": "CPER", "silver": "SLV", "platinum": "PLTM",
    "shipping": "BOAT", "freight": "BOAT",
    "real estate": "VNQ", "housing": "XHB",
    "healthcare": "XLV", "pharma": "XLV", "biotech": "IBB",
    "bank": "XLF", "financial": "XLF",
    "corn": "CORN", "wheat": "WEAT", "soy": "SOYB",
}

def map_asset(story):
    """Map a story to tradeable tickers."""
    tickers = set()
    sector = story.get("sector", "").lower().replace(" ", "_")
    headline = (story.get("headline", "") or "").lower()
    they_say = (story.get("they_say", "") or "").lower()
    reality = (story.get("reality", "") or "").lower()
    text = f"{headline} {they_say} {reality}"
    
    # 1. Sector-based mapping
    if sector in SECTOR_TICKERS:
        tickers.update(SECTOR_TICKERS[sector][:3])  # Top 3 tickers per sector
    
    # 2. Keyword matching
    matches = []
    for keyword, ticker in KEYWORD_TICKERS.items():
        if keyword in text and ticker not in tickers:
            matches.append((keyword, ticker))
    # Sort by keyword length (longer match = more specific)
    matches.sort(key=lambda x: -len(x[0]))
    for _, ticker in matches[:5]:
        tickers.add(ticker)
    
    # 3. Entity tag matching
    entities = story.get("entity_tags", {})
    for tag_list in [entities.get("organizations", []), entities.get("people", []),
                     entities.get("geographies", []), entities.get("tickers", [])]:
        for tag in (tag_list or []):
            tag_lower = tag.lower()
            if tag_lower in KEYWORD_TICKERS:
                tickers.add(KEYWORD_TICKERS[tag_lower])
    
    if not tickers:
        return {"primary_ticker": None, "tickers": [], "confidence": "low"}
    
    ticker_list = list(tickers)[:5]
    primary = ticker_list[0]
    
    # Confidence based on match quality
    if len(ticker_list) >= 5:
        confidence = "high"
    elif len(ticker_list) >= 3:
        confidence = "medium"
    else:
        confidence = "low"
    
    return {
        "primary_ticker": primary,
        "tickers": ticker_list,
        "confidence": confidence,
    }

def main():
    if not STORIES_PATH.exists():
        print(f"ERROR: {STORIES_PATH} not found")
        return 1
    
    with open(STORIES_PATH) as f:
        data = json.load(f)
    
    stories = data.get("stories", [])
    mapped = 0
    
    for story in stories:
        if not story.get("asset_claim") or story["asset_claim"] == {}:
            story["asset_claim"] = map_asset(story)
            if story["asset_claim"]["primary_ticker"]:
                mapped += 1
    
    with open(OUTPUT, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"asset_claim mapped: {mapped}/{len(stories)} stories")
    print(f"  → {OUTPUT}")
    return 0

if __name__ == "__main__":
    exit(main())
