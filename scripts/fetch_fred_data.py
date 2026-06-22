#!/usr/bin/env python3
"""
La Gazzetta di Kyiv — Phase 1, Task 1.3
Module: fetch_fred_data.py
Purpose: TIER_3 Data Stream — FRED macro indicators (no API key required).
"""

import os, sys, json, requests
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("/opt/gazzetta-di-kyiv/data")
OUTPUT_FILE = OUTPUT_DIR / "fred_macro.json"

FRED_SERIES = {
    "WALCL":      "rate_cycle",       # Fed Total Assets (balance sheet)
    "RRPONTSYD":  "rate_cycle",       # Overnight Reverse Repo (liquidity drain)
    "DGS10":      "rate_cycle",        # 10-Year Treasury Constant Maturity
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

def fetch_fred_series(series_id: str) -> list:
    """Pull CSV from FRED public endpoint. No API token needed."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            print(f"[-] FRED {series_id}: HTTP {resp.status_code}")
            return []

        lines = [l.strip() for l in resp.text.split("\n") if l.strip()]
        if len(lines) < 2:
            return []

        points = []
        for line in lines[1:]:  # skip header
            parts = line.split(",")
            if len(parts) == 2:
                date_str, val_str = parts[0], parts[1]
                if val_str == ".":  # FRED missing-data sentinel
                    continue
                try:
                    points.append({"date": date_str, "value": float(val_str)})
                except ValueError:
                    continue
        return points
    except Exception as e:
        print(f"[-] FRED {series_id} error: {e}")
        return []

def main():
    print("[Task 1.3] Pulling FRED macro indicators...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    metrics = {}
    for series_id, narrative in FRED_SERIES.items():
        points = fetch_fred_series(series_id)
        if not points:
            print(f"[-] Series {series_id} empty — aborting to preserve state.")
            sys.exit(1)

        latest = points[-1]
        metrics[series_id] = {
            "narrative_assignment": narrative,
            "last_updated_date": latest["date"],
            "current_value": latest["value"],
            "history_sample_count": len(points),
        }

    output = {
        "metadata": {
            "source": "St. Louis Fed (FRED)",
            "extracted_at": datetime.utcnow().isoformat() + "Z",
            "data_fidelity": "TIER_3",
        },
        "metrics": metrics,
    }

    tmp_path = OUTPUT_FILE.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, OUTPUT_FILE)

    print(f"[+] FRED cache: {OUTPUT_FILE}")
    fix_ownership(str(OUTPUT_FILE))

if __name__ == "__main__":
    main()
