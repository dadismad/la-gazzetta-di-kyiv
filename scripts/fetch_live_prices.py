#!/usr/bin/env python3
"""
fetch_live_prices.py — Fetch live asset prices from CoinGecko + Alpha Vantage

CoinGecko (free tier): BTC, ETH, SOL, SPX (via ETF proxy), gold, oil
Alpha Vantage: SPX (^GSPC), VIX, US10Y, DXY

Output: site/data/market_prices.json
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

# ── CoinGecko ────────────────────────────────────────────
COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum", 
    "SOL": "solana",
    "XAU": "tether-gold",  # gold proxy
}

def fetch_coingecko():
    """Fetch crypto + gold prices from CoinGecko."""
    import urllib.request
    
    ids = ",".join(COINGECKO_IDS.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
    
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        
        prices = {}
        for ticker, cg_id in COINGECKO_IDS.items():
            if cg_id in data:
                prices[ticker] = {
                    "price": data[cg_id].get("usd"),
                    "change_24h": data[cg_id].get("usd_24h_change"),
                    "source": "CoinGecko"
                }
        return prices
    except Exception as e:
        print(f"  ⚠ CoinGecko: {e}", file=sys.stderr)
        return {}


# ── Alpha Vantage ────────────────────────────────────────
def fetch_alphavantage():
    """Fetch equities/indices from Alpha Vantage."""
    import urllib.request
    
    key = os.environ.get("ALPHA_VANTAGE_KEY", "")
    if not key:
        # Try custom_providers
        try:
            providers = json.loads(os.environ.get("custom_providers", "[]"))
            for p in providers:
                if "alpha" in p.get("name", "").lower():
                    key = p.get("api_key", "")
                    break
        except (json.JSONDecodeError, KeyError):
            pass
    
    if not key:
        print("  ⚠ Alpha Vantage: no API key", file=sys.stderr)
        return {}
    
    symbols = {
        "SPX": "^GSPC",
        "VIX": "^VIX",
        "DXY": "DX-Y.NYB",
        "US10Y": "^TNX",
        "WTI": "CL=F",
        "QQQ": "QQQ",
    }
    
    prices = {}
    for ticker, av_sym in symbols.items():
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={av_sym}&apikey={key}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            
            quote = data.get("Global Quote", {})
            if quote.get("05. price"):
                prices[ticker] = {
                    "price": float(quote["05. price"]),
                    "change_pct": float(quote.get("10. change percent", "0%").replace("%", "")),
                    "source": "Alpha Vantage"
                }
        except Exception as e:
            print(f"  ⚠ AV/{ticker}: {e}", file=sys.stderr)
        
        # Rate limit: Alpha Vantage free tier = 5 calls/min
        time.sleep(0.3)
    
    return prices


def main():
    print("[fetch_live_prices] Starting...")
    
    prices = {}
    
    # Fetch from both sources
    cg_prices = fetch_coingecko()
    prices.update(cg_prices)
    print(f"  CoinGecko: {len(cg_prices)} assets")
    
    av_prices = fetch_alphavantage()
    prices.update(av_prices)
    print(f"  Alpha Vantage: {len(av_prices)} assets")
    
    # Add timestamp
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "assets": prices,
        "total": len(prices)
    }
    
    # Write
    out_path = PROJECT / "site" / "data" / "market_prices.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"  ✓ market_prices.json: {len(prices)} assets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
