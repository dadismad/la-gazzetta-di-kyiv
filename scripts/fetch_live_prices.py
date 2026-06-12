#!/usr/bin/env python3
"""
fetch_live_prices.py — Fetch live asset prices from CoinGecko + Alpha Vantage
Output: public/data/market_prices.json — writes to 'prices' key, preserves existing keys.
"""

import json, os, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
OUT_PATH = PROJECT / "site" / "data" / "market_prices.json"

COINGECKO_IDS = {"BTC":"bitcoin","ETH":"ethereum","SOL":"solana","XAU":"tether-gold"}

def fetch_coingecko():
    ids = ",".join(COINGECKO_IDS.values())
    url = "https://api.coingecko.com/api/v3/simple/price?ids=" + ids + "&vs_currencies=usd&include_24hr_change=true"
    try:
        req = urllib.request.Request(url, headers={"Accept":"application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        prices = {}
        for ticker, cg_id in COINGECKO_IDS.items():
            if cg_id in data:
                prices[ticker] = {"price":data[cg_id].get("usd"),"change_pct":data[cg_id].get("usd_24h_change"),"source":"CoinGecko"}
        return prices
    except Exception as e:
        print("  [WARN] CoinGecko:", e, file=sys.stderr)
        return {}

def get_api_key(provider_name):
    key = os.environ.get("ALPHA_VANTAGE_KEY","")
    if not key:
        try:
            providers = json.loads(os.environ.get("custom_providers","[]"))
            for p in providers:
                if provider_name in p.get("name","").lower():
                    key = p.get("api_key","")
                    break
        except:
            pass
    return key

def fetch_alphavantage():
    key = get_api_key("alpha")
    if not key:
        return {}
    symbols = {"SPX":"^GSPC","VIX":"^VIX","DXY":"DX-Y.NYB","US10Y":"^TNX","WTI":"CL=F","QQQ":"QQQ"}
    prices = {}
    for ticker, av_sym in symbols.items():
        try:
            url = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=" + av_sym + "&apikey=" + key
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                j = json.loads(resp.read())
            quote = j.get("Global Quote",{})
            if quote.get("05. price"):
                chg = quote.get("10. change percent","0%").replace("%","")
                prices[ticker] = {"price":float(quote["05. price"]),"change_pct":float(chg),"source":"Alpha Vantage"}
        except Exception as e:
            print("  [WARN] AV/" + ticker + ":", e, file=sys.stderr)
        time.sleep(0.3)
    return prices

def main():
    print("[fetch_live_prices] Starting...")
    existing = {}
    if OUT_PATH.exists():
        try:
            with open(OUT_PATH) as f:
                existing = json.load(f)
        except:
            existing = {}
    prices = {}
    cg = fetch_coingecko()
    prices.update(cg)
    print("  CoinGecko:", len(cg), "assets")
    av = fetch_alphavantage()
    prices.update(av)
    print("  Alpha Vantage:", len(av), "assets")
    existing["generated_at"] = datetime.now(timezone.utc).isoformat()
    existing["prices"] = prices
    existing["total"] = len(prices)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(existing, f, indent=2)
    preserved = len(existing) - 3
    msg = "  [OK] market_prices.json: " + str(len(prices)) + " assets"
    if preserved:
        msg += " (preserved " + str(preserved) + " existing keys)"
    print(msg)
    return 0

if __name__ == "__main__":
    sys.exit(main())
