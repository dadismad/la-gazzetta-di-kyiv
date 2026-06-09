#!/usr/bin/env python3
"""fetch_fred.py — Pull Treasury yields, Fed funds rate, CPI, M2 from FRED.

Free tier: 120 requests/minute. We fetch ~8 series per run (every 4h).
Output: data/market_data/fred.json

API key: Set FRED_API_KEY env var or pass via --key.
Get free key: https://fred.stlouisfed.org/docs/api/api_key.html
"""

import json, os, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_KEY = os.environ.get("FRED_API_KEY", "")
BASE_URL = "https://api.stlouisfed.org/fred"

# Key indicators for Gazzetta
SERIES = {
    "DGS10": {"name": "10Y Treasury Yield", "unit": "%", "category": "bonds"},
    "DGS2": {"name": "2Y Treasury Yield", "unit": "%", "category": "bonds"},
    "T10Y2Y": {"name": "10Y-2Y Spread", "unit": "%", "category": "bonds"},
    "DFEDTARU": {"name": "Fed Funds Rate (Upper)", "unit": "%", "category": "rates"},
    "DFEDTARL": {"name": "Fed Funds Rate (Lower)", "unit": "%", "category": "rates"},
    "CPIAUCSL": {"name": "CPI (All Urban)", "unit": "index", "category": "inflation"},
    "M2SL": {"name": "M2 Money Supply", "unit": "billions", "category": "money"},
    "TOTALSL": {"name": "Total Consumer Credit", "unit": "billions", "category": "credit"},
}

def fetch_series(series_id, months=3):
    """Fetch recent observations for a FRED series."""
    url = (
        f"{BASE_URL}/series/observations"
        f"?series_id={series_id}"
        f"&api_key={API_KEY}"
        f"&file_type=json"
        f"&sort_order=desc"
        f"&limit={months * 31}"  # ~daily observations for N months
    )
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        obs = data.get("observations", [])
        # Filter out missing values (".")
        valid = [o for o in obs if o.get("value") != "."]
        if not valid:
            return None
        latest_val = float(valid[0]["value"])
        # Get previous month value for change calculation
        prev = None
        for o in valid:
            if o["date"][:7] != valid[0]["date"][:7]:  # Different month
                prev = float(o["value"])
                break
        return {
            "latest": latest_val,
            "latest_date": valid[0]["date"],
            "previous": prev,
            "change": round(latest_val - prev, 4) if prev else None,
            "unit": None,  # Filled from SERIES metadata
        }
    except Exception as e:
        print(f"  {series_id}: ERROR — {e}")
        return None

def main():
    if not API_KEY:
        print("ERROR: Set FRED_API_KEY environment variable")
        print("Get free key: https://fred.stlouisfed.org/docs/api/api_key.html")
        sys.exit(1)

    out_dir = Path(__file__).parent.parent / "data" / "market_data"
    out_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "FRED (Federal Reserve Economic Data)",
        "series": {},
    }

    print("Fetching FRED series...")
    for series_id, meta in SERIES.items():
        s = fetch_series(series_id)
        if s:
            s["unit"] = meta["unit"]
            s["name"] = meta["name"]
            s["category"] = meta["category"]
            result["series"][series_id] = s
            change_str = f" (Δ {s['change']})" if s['change'] is not None else ""
            print(f"  {meta['name']}: {s['latest']}{s['unit']}{change_str}")
        else:
            print(f"  {meta['name']}: FAILED")
        time.sleep(0.3)  # FRED allows 120/min, be polite

    # Compute yield curve status
    dgs10 = result["series"].get("DGS10", {}).get("latest")
    dgs2 = result["series"].get("DGS2", {}).get("latest")
    spread = result["series"].get("T10Y2Y", {}).get("latest")
    if dgs10 and dgs2:
        spread_calc = round(dgs10 - dgs2, 2)
        result["yield_curve"] = {
            "spread": spread or spread_calc,
            "status": "inverted" if (spread or spread_calc) < 0 else "normal",
            "10y": dgs10,
            "2y": dgs2,
        }
        print(f"\n  Yield curve: {result['yield_curve']['spread']}% ({result['yield_curve']['status']})")

    out_path = out_dir / "fred.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    count = len(result["series"])
    print(f"\n✓ Fetched {count} FRED series → {out_path}")

if __name__ == "__main__":
    main()
