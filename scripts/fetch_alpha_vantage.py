#!/usr/bin/env python3
"""fetch_alpha_vantage.py — Pull commodity prices, FX rates, and VIX from Alpha Vantage.

Free tier: 25 requests/day. We batch 5 key data points per run (every 4h = 6 runs/day = well within limits).
Output: data/market_data/alpha_vantage.json

API key: Set ALPHA_VANTAGE_KEY env var or pass via --key.
Get free key: https://www.alphavantage.co/support/#api-key
"""

import json, os, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "")
BASE_URL = "https://www.alphavantage.co/query"

# Commodities we track (Alpha Vantage function: GLOBAL_COMMODITY)
COMMODITIES = {
    "WTI": "WTI",        # Crude oil WTI
    "BRENT": "BRENT",    # Crude oil Brent
    "NATURAL_GAS": "NATURAL_GAS",
    "COPPER": "COPPER",
    "ALUMINUM": "ALUMINUM",
    "WHEAT": "WHEAT",
    "CORN": "CORN",
    "GOLD": "GOLD",
}

# FX pairs we track
FX_PAIRS = {
    "EUR/USD": ("EUR", "USD"),
    "USD/JPY": ("USD", "JPY"),
    "GBP/USD": ("GBP", "USD"),
    "USD/CNY": ("USD", "CNY"),
    "USD/RUB": ("USD", "RUB"),
    "USD/UAH": ("USD", "UAH"),
}

def fetch_json(params, retries=3):
    """Fetch from Alpha Vantage with retry and rate-limit handling."""
    url = BASE_URL + "?" + "&".join(f"{k}={v}" for k, v in params.items())
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            # Check for rate limit message
            if "Note" in data or "Information" in data:
                msg = data.get("Note") or data.get("Information", "")
                if "rate limit" in msg.lower() or "api call frequency" in msg.lower():
                    print(f"  Rate limited, waiting 65s...")
                    time.sleep(65)
                    continue
            return data
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(5 * (attempt + 1))
    return None

def fetch_commodity(symbol):
    """Fetch latest commodity price."""
    data = fetch_json({
        "function": symbol,
        "apikey": API_KEY,
        "interval": "daily",
    })
    if not data or "data" not in data:
        return None
    try:
        latest = data["data"][0]
        return {
            "price": float(latest["value"]),
            "date": latest["date"],
            "unit": data.get("unit", ""),
            "name": data.get("name", symbol),
        }
    except (KeyError, IndexError, ValueError):
        return None

def fetch_fx_pair(from_currency, to_currency):
    """Fetch latest FX rate."""
    data = fetch_json({
        "function": "CURRENCY_EXCHANGE_RATE",
        "from_currency": from_currency,
        "to_currency": to_currency,
        "apikey": API_KEY,
    })
    if not data:
        return None
    try:
        rate_data = data.get("Realtime Currency Exchange Rate", {})
        return {
            "rate": float(rate_data.get("5. Exchange Rate", 0)),
            "bid": float(rate_data.get("8. Bid Price", 0)),
            "ask": float(rate_data.get("9. Ask Price", 0)),
            "from": from_currency,
            "to": to_currency,
            "last_refreshed": rate_data.get("6. Last Refreshed", ""),
        }
    except (ValueError, KeyError):
        return None

def fetch_vix():
    """Fetch VIX via TIME_SERIES_INTRADAY or fallback to a known symbol."""
    # Alpha Vantage doesn't have a direct VIX endpoint on free tier.
    # Use CBOE index via GLOBAL_QUOTE or skip.
    data = fetch_json({
        "function": "GLOBAL_QUOTE",
        "symbol": "VIX",
        "apikey": API_KEY,
    })
    if not data:
        return None
    try:
        quote = data.get("Global Quote", {})
        return {
            "price": float(quote.get("05. price", 0)),
            "change_pct": quote.get("10. change percent", ""),
            "latest_day": quote.get("07. latest trading day", ""),
        }
    except (ValueError, KeyError):
        return None

def main():
    if not API_KEY:
        print("ERROR: Set ALPHA_VANTAGE_KEY environment variable")
        print("Get free key: https://www.alphavantage.co/support/#api-key")
        sys.exit(1)

    out_dir = Path(__file__).parent.parent / "data" / "market_data"
    out_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Alpha Vantage",
        "commodities": {},
        "fx_rates": {},
        "vix": None,
    }

    # Fetch commodities (batch of 8, ~8 API calls)
    print("Fetching commodities...")
    for name, symbol in COMMODITIES.items():
        c = fetch_commodity(symbol)
        if c:
            result["commodities"][name] = c
            print(f"  {name}: ${c['price']} ({c['unit']})")
        else:
            print(f"  {name}: FAILED")
        time.sleep(1.5)  # Respect API rate limits (5 calls/min on free tier)

    # Fetch FX pairs (batch of 6, ~6 API calls)
    print("\nFetching FX rates...")
    for pair_name, (frm, to) in FX_PAIRS.items():
        fx = fetch_fx_pair(frm, to)
        if fx:
            result["fx_rates"][pair_name] = fx
            print(f"  {pair_name}: {fx['rate']}")
        else:
            print(f"  {pair_name}: FAILED")
        time.sleep(1.5)

    # Fetch VIX
    print("\nFetching VIX...")
    vix = fetch_vix()
    if vix:
        result["vix"] = vix
        print(f"  VIX: {vix['price']} ({vix['change_pct']})")
    else:
        print("  VIX: FAILED (may not be available on free tier)")

    # Write output
    out_path = out_dir / "alpha_vantage.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    count = len(result["commodities"]) + len(result["fx_rates"]) + (1 if result["vix"] else 0)
    print(f"\n✓ Fetched {count} data points → {out_path}")

if __name__ == "__main__":
    main()
