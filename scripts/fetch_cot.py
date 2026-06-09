#!/usr/bin/env python3
"""fetch_cot.py — Download CFTC Commitment of Traders data for key markets.

Downloads both the Financial Futures (fut_fin) and Disaggregated (fut_disagg)
COT files from the CFTC. Extracts positioning data for:
  - S&P 500, VIX, US Treasuries (2Y, 5Y, 10Y, Ultra Bond) from Financial file
  - Gold, WTI Crude Oil from Disaggregated file

Computes net positioning (Long - Short) per trader category and week-over-week
changes. Output: data/market_data/cot.json

Key trader categories for CTA/institutional analysis:
  Financial file: Lev_Money (Leveraged Money = Hedge Funds/CTAs)
                  Asset_Mgr (Asset Managers = Pensions/Endowments)
  Disaggr file:   M_Money (Managed Money = CTAs, Commodity Pools)

Usage: python fetch_cot.py [--year 2026]
"""

import csv, io, json, os, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

# ── Paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "market_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CFTC_BASE = "https://www.cftc.gov/files/dea/history"

# ── Key Markets to Track ───────────────────────────────────────────────
# Markets from the Financial Futures file (fut_fin_txt_YYYY.zip)
# Trader types: Dealer, Asset_Mgr, Lev_Money, Other_Rept, NonRept
FINANCIAL_MARKETS = {
    "S&P_500":   "S&P 500 Consolidated - CHICAGO MERCANTILE EXCHANGE",
    "VIX":       "VIX FUTURES - CBOE FUTURES EXCHANGE",
    "UST_10Y":   "UST 10Y NOTE - CHICAGO BOARD OF TRADE",
    "UST_2Y":    "UST 2Y NOTE - CHICAGO BOARD OF TRADE",
    "UST_5Y":    "UST 5Y NOTE - CHICAGO BOARD OF TRADE",
    "UST_BOND":  "UST BOND - CHICAGO BOARD OF TRADE",
    "ULTRA_BOND":"ULTRA UST BOND - CHICAGO BOARD OF TRADE",
    "FED_FUNDS": "FED FUNDS - CHICAGO BOARD OF TRADE",
}

# Markets from the Disaggregated file (fut_disagg_txt_YYYY.zip)
# Trader types: Prod_Merc, Swap, M_Money, Other_Rept, NonRept
COMMODITY_MARKETS = {
    "GOLD":      "GOLD - COMMODITY EXCHANGE INC.",
    "WTI_CRUDE": "CRUDE OIL, LIGHT SWEET-WTI - ICE FUTURES EUROPE",
    "NAT_GAS":   "NAT GAS NYME - NEW YORK MERCANTILE EXCHANGE",
}


def fetch_zip(url: str) -> bytes | None:
    """Download a zip file from CFTC, with retries and SSL handling."""
    import ssl, time
    from urllib.request import Request
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/125.0.0.0 Safari/537.36",
        "Accept": "application/zip,application/octet-stream,*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm",
    }
    for attempt in range(3):
        try:
            req = Request(url, headers=headers)
            resp = urlopen(req, timeout=60, context=ctx)
            return resp.read()
        except Exception as e:
            if attempt == 2:
                print(f"[cot] ERROR downloading {url}: {e}")
                return None
            time.sleep(2)


def parse_csv_from_zip(zip_bytes: bytes, filename: str, encoding: str = "utf-8-sig") -> list[dict]:
    """Extract a CSV from inside a zip and return list of dicts."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        with z.open(filename) as f:
            raw = f.read()
            # Handle BOM and decode
            text = raw.decode(encoding)
            reader = csv.DictReader(io.StringIO(text))
            return [row for row in reader]


def safe_int(val: str) -> int:
    """Convert CSV value to int, handling '.' (missing data)."""
    v = val.strip().strip('"')
    if v == '.' or v == '' or v == '..':
        return 0
    try:
        return int(v)
    except ValueError:
        return 0


def extract_market_rows(rows: list[dict], market_name: str) -> list[dict]:
    """Extract all rows for a given market name (multiple weeks)."""
    return [r for r in rows if r.get("Market_and_Exchange_Names", "").strip('"') == market_name]


def compute_net_positioning(data_rows: list[dict], fin_file: bool = True) -> dict | None:
    """
    From the time series of a single market, extract the latest 2 weeks
    and compute net positioning + changes.
    
    For financial file categories: Dealer, Asset_Mgr, Lev_Money, Other_Rept, NonRept
    For disaggregated: Prod_Merc, Swap, M_Money, Other_Rept, NonRept
    """
    if not data_rows:
        return None
    
    # Sort by report date descending
    data_rows.sort(key=lambda r: r.get("Report_Date_as_YYYY-MM-DD", ""), reverse=True)
    
    latest = data_rows[0]
    prev = data_rows[1] if len(data_rows) > 1 else None
    
    report_date = latest.get("Report_Date_as_YYYY-MM-DD", "").strip('"')
    as_of = latest.get("As_of_Date_In_Form_YYMMDD", "").strip('"')
    
    # Determine column prefixes based on file type
    if fin_file:
        cats = ["Dealer", "Asset_Mgr", "Lev_Money", "Other_Rept", "NonRept"]
    else:
        cats = ["Prod_Merc", "Swap", "M_Money", "Other_Rept", "NonRept"]
    
    open_interest = safe_int(latest.get("Open_Interest_All", "0"))
    
    result = {
        "market": data_rows[0].get("Market_and_Exchange_Names", "").strip('"'),
        "report_date": report_date,
        "as_of": as_of,
        "open_interest": open_interest,
        "categories": {},
    }
    
    for cat in cats:
        long_col = f"{cat}_Positions_Long_All"
        short_col = f"{cat}_Positions_Short_All"
        
        long_val = safe_int(latest.get(long_col, "0"))
        short_val = safe_int(latest.get(short_col, "0"))
        net = long_val - short_val
        
        entry = {
            "long": long_val,
            "short": short_val,
            "net": net,
            "net_pct_oi": round(net / open_interest * 100, 2) if open_interest > 0 else 0.0,
        }
        
        if prev:
            prev_long = safe_int(prev.get(long_col, "0"))
            prev_short = safe_int(prev.get(short_col, "0"))
            prev_net = prev_long - prev_short
            entry["net_change_1w"] = net - prev_net
        else:
            entry["net_change_1w"] = 0
        
        result["categories"][cat] = entry
    
    # Compute combined 'smart money' indicators for key categories
    if fin_file:
        # For financial: Leveraged Money (CTAs) + Asset Managers (Institutional)
        lm_net = result["categories"]["Lev_Money"]["net"]
        am_net = result["categories"]["Asset_Mgr"]["net"]
        result["smart_money_net"] = lm_net + am_net
        
        if prev:
            prev_lm = (safe_int(prev.get("Lev_Money_Positions_Long_All", "0")) -
                       safe_int(prev.get("Lev_Money_Positions_Short_All", "0")))
            prev_am = (safe_int(prev.get("Asset_Mgr_Positions_Long_All", "0")) -
                       safe_int(prev.get("Asset_Mgr_Positions_Short_All", "0")))
            result["smart_money_change_1w"] = (lm_net + am_net) - (prev_lm + prev_am)
        else:
            result["smart_money_change_1w"] = 0
    else:
        # For commodities: Managed Money (CTAs/funds) + Swap Dealers (commercial hedgers)
        mm_net = result["categories"]["M_Money"]["net"]
        result["smart_money_net"] = mm_net
        
        if prev:
            prev_mm = (safe_int(prev.get("M_Money_Positions_Long_All", "0")) -
                       safe_int(prev.get("M_Money_Positions_Short_All", "0")))
            result["smart_money_change_1w"] = mm_net - prev_mm
        else:
            result["smart_money_change_1w"] = 0
    
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fetch CFTC COT data")
    parser.add_argument("--year", type=int, default=datetime.now().year, help="Year to fetch")
    args = parser.parse_args()
    
    year = args.year
    generated_at = datetime.now(timezone.utc).isoformat()
    
    print(f"[cot] Fetching CFTC COT data for {year}...")
    
    # ── 1. Download Financial Futures file ──────────────────────────
    fin_url = f"{CFTC_BASE}/fut_fin_txt_{year}.zip"
    print(f"[cot] Downloading {fin_url}...")
    fin_zip = fetch_zip(fin_url)
    if fin_zip is None:
        print(f"[cot] FATAL: Could not download {fin_url}")
        sys.exit(1)
    
    fin_rows = parse_csv_from_zip(fin_zip, "FinFutYY.txt")
    print(f"[cot]   Parsed {len(fin_rows)} financial futures data rows")
    
    # ── 2. Download Disaggregated (commodities) file ────────────────
    dis_url = f"{CFTC_BASE}/fut_disagg_txt_{year}.zip"
    print(f"[cot] Downloading {dis_url}...")
    dis_zip = fetch_zip(dis_url)
    if dis_zip is None:
        print(f"[cot] FATAL: Could not download {dis_url}")
        sys.exit(1)
    
    dis_rows = parse_csv_from_zip(dis_zip, "f_year.txt")
    print(f"[cot]   Parsed {len(dis_rows)} disaggregated data rows")
    
    # ── 3. Extract key markets ──────────────────────────────────────
    markets_data = {}
    
    # Financial markets
    for key, name in FINANCIAL_MARKETS.items():
        rows = extract_market_rows(fin_rows, name)
        if rows:
            result = compute_net_positioning(rows, fin_file=True)
            if result:
                markets_data[key] = result
                print(f"[cot]   {key}: {result['report_date']} — "
                      f"LevMoney net={result['categories']['Lev_Money']['net']:+,d} "
                      f"(Δ1w={result['categories']['Lev_Money']['net_change_1w']:+,d})")
        else:
            print(f"[cot]   {key}: NOT FOUND in financial file")
    
    # Commodity markets (only unique — skip if already found as financial)
    for key, name in COMMODITY_MARKETS.items():
        if key in markets_data:
            continue
        rows = extract_market_rows(dis_rows, name)
        if rows:
            result = compute_net_positioning(rows, fin_file=False)
            if result:
                markets_data[key] = result
                print(f"[cot]   {key}: {result['report_date']} — "
                      f"MMoney net={result['categories']['M_Money']['net']:+,d} "
                      f"(Δ1w={result['categories']['M_Money']['net_change_1w']:+,d})")
        else:
            print(f"[cot]   {key}: NOT FOUND in disaggregated file")
    
    # ── 4. Build output ─────────────────────────────────────────────
    output = {
        "generated_at": generated_at,
        "source": f"CFTC COT ({year})",
        "base_url_fin": fin_url,
        "base_url_dis": dis_url,
        "markets": markets_data,
        "summary": {
            "count": len(markets_data),
        }
    }
    
    # Generate a text summary signal
    signals = []
    for key, m in markets_data.items():
        cats = m.get("categories", {})
        # Find the best directional signal
        for cat_name in ["Lev_Money", "M_Money", "Asset_Mgr"]:
            if cat_name in cats:
                cat = cats[cat_name]
                change = cat.get("net_change_1w", 0)
                net = cat.get("net", 0)
                if abs(change) > 100:
                    direction = "BULLISH" if change > 0 else "BEARISH"
                    signals.append({
                        "market": key,
                        "trader_type": cat_name,
                        "signal": direction,
                        "net_position": net,
                        "weekly_change": change,
                    })
                break
    
    output["signals"] = signals
    
    # ── 5. Write output ─────────────────────────────────────────────
    out_path = DATA_DIR / "cot.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n[cot] ✓ Written {len(markets_data)} markets to {out_path}")
    print(f"[cot]   {len(signals)} directional signals generated")


if __name__ == "__main__":
    main()
