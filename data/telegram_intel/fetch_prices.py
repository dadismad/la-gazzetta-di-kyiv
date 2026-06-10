#!/usr/bin/env python3
"""Fetch current market prices."""
import json
import urllib.request

TICKERS = [
    ("CL=F", "WTI Crude"),
    ("BTC-USD", "Bitcoin"),
    ("SPY", "S&P 500"),
    ("BZ=F", "Brent Crude"),
    ("GC=F", "Gold"),
]

for ticker, name in TICKERS:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1d&interval=5m"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            if data.get("chart") and data["chart"].get("result") and data["chart"]["result"][0]:
                r = data["chart"]["result"][0]
                meta = r.get("meta", {})
                price = meta.get("regularMarketPrice", "N/A")
                prev_close = meta.get("previousClose", "N/A")
                print(f"{name} ({ticker}): ${price} | Prev Close: ${prev_close}")
            else:
                print(f"{name} ({ticker}): No data")
    except Exception as e:
        print(f"{name} ({ticker}): Error - {e}")
