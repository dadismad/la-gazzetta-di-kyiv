#!/usr/bin/env python3
"""
La Gazzetta di Kyiv — Phase 2, Task 2.0
Module: fetch_cftc_cot.py (expanded — Legacy + Disaggregated)
Purpose: TIER_1 Data Stream — unified CFTC institutional positioning.
Sources:
  - Legacy COT (deacotYYYY.zip / annual.txt) — Financials, Metals, Crypto
  - Disaggregated COT (fut_disagg_txt_YYYY.zip / f_year.txt) — Physical Commodities
Normalizes both schemas into a single cftc_cot.json.
"""

import os, sys, json, csv, zipfile, io, requests
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("/opt/gazzetta-di-kyiv/data")
OUTPUT_FILE = OUTPUT_DIR / "cftc_cot.json"

# ── Legacy COT markets (Financials, Metals, Crypto) ──
LEGACY_MARKETS = {
    "BITCOIN - CHICAGO MERCANTILE EXCHANGE":             "crypto_reserve",
    "E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE":      "rate_cycle",
    "GOLD - COMMODITY EXCHANGE INC.":                    "commodity_supercycle",
    "SILVER - COMMODITY EXCHANGE INC.":                  "commodity_supercycle",
    "WTI FINANCIAL CRUDE OIL - NEW YORK MERCANTILE EXCHANGE": "commodity_supercycle",
    "UST BOND - CHICAGO BOARD OF TRADE":                 "rate_cycle",
}

# ── Disaggregated COT markets (Physical Commodities) ──
DISAGG_MARKETS = {
    # Energy
    "GASOLINE RBOB - NEW YORK MERCANTILE EXCHANGE":      "commodity_supercycle",
    # Metals
    "COPPER- #1 - COMMODITY EXCHANGE INC.":              "commodity_supercycle",
    "PALLADIUM - NEW YORK MERCANTILE EXCHANGE":           "commodity_supercycle",
    "PLATINUM - NEW YORK MERCANTILE EXCHANGE":            "commodity_supercycle",
    # Grains
    "CORN - CHICAGO BOARD OF TRADE":                     "commodity_supercycle",
    "SOYBEANS - CHICAGO BOARD OF TRADE":                 "commodity_supercycle",
    "SOYBEAN MEAL - CHICAGO BOARD OF TRADE":             "commodity_supercycle",
    "WHEAT-SRW - CHICAGO BOARD OF TRADE":                "commodity_supercycle",
    # Softs
    "COFFEE C - ICE FUTURES U.S.":                       "commodity_supercycle",
    "SUGAR NO. 11 - ICE FUTURES U.S.":                   "commodity_supercycle",
    "COTTON NO. 2 - ICE FUTURES U.S.":                   "commodity_supercycle",
    "COCOA - ICE FUTURES U.S.":                          "commodity_supercycle",
    # Livestock
    "LIVE CATTLE - CHICAGO MERCANTILE EXCHANGE":         "commodity_supercycle",
    "LEAN HOGS - CHICAGO MERCANTILE EXCHANGE":           "commodity_supercycle",
    "FEEDER CATTLE - CHICAGO MERCANTILE EXCHANGE":       "commodity_supercycle",
}

# Notionals per contract
CONTRACT_NOTIONALS = {
    "GOLD - COMMODITY EXCHANGE INC.": 100 * 3300,
    "SILVER - COMMODITY EXCHANGE INC.": 5000 * 33,
    "WTI FINANCIAL CRUDE OIL - NEW YORK MERCANTILE EXCHANGE": 1000 * 68,
    "UST BOND - CHICAGO BOARD OF TRADE": 1000 * 115,
    "E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE": 50 * 5900,
    "BITCOIN - CHICAGO MERCANTILE EXCHANGE": 5 * 64000,
    "COPPER- #1 - COMMODITY EXCHANGE INC.": 25000 * 5,
    "CORN - CHICAGO BOARD OF TRADE": 5000 * 5,
    "SOYBEANS - CHICAGO BOARD OF TRADE": 5000 * 12,
    "SOYBEAN MEAL - CHICAGO BOARD OF TRADE": 100 * 400,
    "WHEAT-SRW - CHICAGO BOARD OF TRADE": 5000 * 6,
    "COFFEE C - ICE FUTURES U.S.": 37500 * 3,
    "SUGAR NO. 11 - ICE FUTURES U.S.": 112000 * 0.20,
    "COTTON NO. 2 - ICE FUTURES U.S.": 50000 * 0.80,
    "COCOA - ICE FUTURES U.S.": 10 * 8000,
    "LIVE CATTLE - CHICAGO MERCANTILE EXCHANGE": 40000 * 2,
    "LEAN HOGS - CHICAGO MERCANTILE EXCHANGE": 40000 * 1,
    "FEEDER CATTLE - CHICAGO MERCANTILE EXCHANGE": 50000 * 2.50,
    "GASOLINE RBOB - NEW YORK MERCANTILE EXCHANGE": 42000 * 2.50,
    "PALLADIUM - NEW YORK MERCANTILE EXCHANGE": 100 * 1300,
    "PLATINUM - NEW YORK MERCANTILE EXCHANGE": 50 * 1100,
}


def fix_ownership(path_str: str):
    if sys.platform != "linux":
        return
    try:
        import pwd, grp
        uid = pwd.getpwnam("gazzetta").pw_uid
        gid = grp.getgrnam("gazzetta").gr_gid
        os.chown(path_str, uid, gid)
    except (KeyError, OSError):
        pass


# ═══════════════════════════════════════════════════════════════
#  LEGACY COT PARSER
# ═══════════════════════════════════════════════════════════════

def fetch_legacy_cot() -> dict:
    """Legacy COT: deacotYYYY.zip → annual.txt"""
    url = f"https://www.cftc.gov/files/dea/history/deacot{datetime.now().year}.zip"
    try:
        resp = requests.get(url, timeout=20)
        if resp.status_code != 200:
            print(f"  [-] Legacy COT: HTTP {resp.status_code}")
            return {}
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            if "annual.txt" not in z.namelist():
                print("  [-] Legacy COT: annual.txt missing")
                return {}
            raw = z.read("annual.txt").decode("utf-8", errors="replace")
        return _parse_legacy(raw)
    except Exception as e:
        print(f"  [-] Legacy COT error: {e}")
        return {}


def _parse_legacy(raw: str) -> dict:
    reader = csv.DictReader(io.StringIO(raw))
    snapshots = {}
    for row in reader:
        name = row.get("Market and Exchange Names", "").strip()
        if name not in LEGACY_MARKETS:
            continue
        date_str = row.get("As of Date in Form YYYY-MM-DD", "").strip()
        if not date_str:
            continue
        try:
            oi   = int(row.get("Open Interest (All)", "0"))
            spec_l = int(row.get("Noncommercial Positions-Long (All)", "0"))
            spec_s = int(row.get("Noncommercial Positions-Short (All)", "0"))
            comm_l = int(row.get("Commercial Positions-Long (All)", "0"))
            comm_s = int(row.get("Commercial Positions-Short (All)", "0"))
        except ValueError:
            continue

        snap = {
            "report_date": date_str,
            "narrative_assignment": LEGACY_MARKETS[name],
            "open_interest": oi,
            "noncommercial_long": spec_l,
            "noncommercial_short": spec_s,
            "noncommercial_net": spec_l - spec_s,
            "commercial_long": comm_l,
            "commercial_short": comm_s,
            "commercial_net": comm_l - comm_s,
            "source": "legacy",
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        prev = snapshots.get(name)
        if not prev or date_str >= prev["report_date"]:
            snapshots[name] = snap
    return snapshots


# ═══════════════════════════════════════════════════════════════
#  DISAGGREGATED COT PARSER
# ═══════════════════════════════════════════════════════════════

def fetch_disagg_cot() -> dict:
    """Disaggregated COT: fut_disagg_txt_YYYY.zip → f_year.txt"""
    url = f"https://www.cftc.gov/files/dea/history/fut_disagg_txt_{datetime.now().year}.zip"
    try:
        resp = requests.get(url, timeout=20)
        if resp.status_code != 200:
            print(f"  [-] Disagg COT: HTTP {resp.status_code}")
            return {}
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            if "f_year.txt" not in z.namelist():
                print("  [-] Disagg COT: f_year.txt missing")
                return {}
            raw = z.read("f_year.txt").decode("utf-8", errors="replace")
        return _parse_disagg(raw)
    except Exception as e:
        print(f"  [-] Disagg COT error: {e}")
        return {}


def _parse_disagg(raw: str) -> dict:
    """Map Disaggregated schema to unified format:
    spec = Managed Money (hedge funds)
    hedge = Producer/Merchant + Swap Dealers (commercials)
    """
    reader = csv.DictReader(io.StringIO(raw))
    snapshots = {}
    for row in reader:
        name = row.get("Market_and_Exchange_Names", "").strip()
        if name not in DISAGG_MARKETS:
            continue
        date_str = row.get("Report_Date_as_YYYY-MM-DD", "").strip()
        if not date_str:
            continue
        try:
            oi = int(row.get("Open_Interest_All", "0"))
            spec_l = int(row.get("M_Money_Positions_Long_All", "0"))
            spec_s = int(row.get("M_Money_Positions_Short_All", "0"))
            prod_l = int(row.get("Prod_Merc_Positions_Long_All", "0"))
            prod_s = int(row.get("Prod_Merc_Positions_Short_All", "0"))
            swap_l = int(row.get("Swap_Positions_Long_All", "0"))
            swap_s = int(row.get("Swap__Positions_Short_All", "0"))  # double underscore is real
        except ValueError:
            continue

        hedge_l = prod_l + swap_l
        hedge_s = prod_s + swap_s

        snap = {
            "report_date": date_str,
            "narrative_assignment": DISAGG_MARKETS[name],
            "open_interest": oi,
            "noncommercial_long": spec_l,
            "noncommercial_short": spec_s,
            "noncommercial_net": spec_l - spec_s,
            "commercial_long": hedge_l,
            "commercial_short": hedge_s,
            "commercial_net": hedge_l - hedge_s,
            "source": "disaggregated",
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        prev = snapshots.get(name)
        if not prev or date_str >= prev["report_date"]:
            snapshots[name] = snap
    return snapshots


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("[Task 1.2] Fetching unified CFTC positioning (Legacy + Disaggregated)...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    legacy = fetch_legacy_cot()
    print(f"  Legacy: {len(legacy)} markets")

    disagg = fetch_disagg_cot()
    print(f"  Disaggregated: {len(disagg)} markets")

    # Merge — Legacy takes priority on overlapping markets (e.g. WTI Crude)
    merged = {**disagg, **legacy}

    if not merged:
        print("[-] CRITICAL: No CFTC data extracted. Preserving previous state.")
        sys.exit(1)

    output = {
        "metadata": {
            "source": "CFTC Legacy + Disaggregated COT",
            "extracted_at": datetime.utcnow().isoformat() + "Z",
            "data_fidelity": "TIER_1",
            "markets_total": len(merged),
            "legacy_count": len(legacy),
            "disaggregated_count": len(disagg),
        },
        "data": merged,
    }

    tmp_path = OUTPUT_FILE.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, OUTPUT_FILE)

    print(f"[+] CFTC cache: {OUTPUT_FILE} ({len(merged)} total markets)")
    fix_ownership(str(OUTPUT_FILE))


if __name__ == "__main__":
    main()
