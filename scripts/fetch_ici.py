#!/usr/bin/env python3
"""fetch_ici.py — Pull weekly mutual fund / ETF flow estimates from ICI.

Sources (3 XLS files updated weekly by ICI):
  1) Combined ETF + Long-Term Fund Flows
  2) Long-Term Mutual Fund Net New Cash Flow (detailed breakdown)
  3) Money Market Fund Assets

ICI is the best free source for retirement flow tracking (401k, pension flows).

Output: data/market_data/ici_flows.json

Dependencies: xlrd (pip install xlrd)
"""

import json, os, sys, urllib.request, re
from datetime import datetime, timezone
from pathlib import Path

try:
    import xlrd
except ImportError:
    print("ERROR: xlrd is required. Run: pip install xlrd")
    sys.exit(1)

BASE_URL = "https://www.ici.org"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

# NOTE: The year suffix changes annually (e.g., _2026.xls becomes _2027.xls in Jan).
# We try the current year first, fall back to previous year.
CURRENT_YEAR = datetime.now().year
PREVIOUS_YEAR = CURRENT_YEAR - 1

FILES = {
    "combined_flows": {
        "path": "/combined_flows_data_{year}.xls",
        "page": "/research/statistics/etfs/weekly-combined-estimated-etf-and-longterm-flows",
        "description": "Weekly Combined ETF and Long-Term Fund Flows",
    },
    "mf_flows": {
        "path": "/flows_data_{year}.xls",
        "page": "/research/statistics/mutual-funds/weekly-estimated-longterm-mutual-fund-flows",
        "description": "Weekly Estimated Long-Term Mutual Fund Flows",
    },
    "mm_assets": {
        "path": "/mm_summary_data_{year}.xls",
        "page": "/weekly-money-market-mutual-fund-assets",
        "description": "Weekly Money Market Fund Assets",
    },
}


def download_xls(file_key: str) -> bytes | None:
    """Try to download an ICI XLS file, falling back to previous year."""
    info = FILES[file_key]
    for year in (CURRENT_YEAR, PREVIOUS_YEAR):
        url = BASE_URL + info["path"].format(year=year)
        print(f"  Trying {url}...")
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            if len(data) > 1000:
                print(f"  ✓ Downloaded ({len(data)} bytes)")
                return data
        except Exception as e:
            print(f"  ✗ {e}")
    print(f"  ✗ Failed to download {file_key}")
    return None


def parse_combined_flows(data: bytes) -> dict:
    """Parse the Combined ETF + Long-Term Fund Flows XLS."""
    wb = xlrd.open_workbook(file_contents=data)
    sh = wb.sheet_by_index(0)

    result = {
        "source": "ICI - Combined ETF and Long-Term Fund Flows",
        "unit": "millions_USD",
        "monthly": [],
        "weekly": [],
    }

    section = "monthly"
    for r in range(sh.nrows):
        date_val = str(sh.cell_value(r, 0)).strip()
        # Skip header rows
        if not date_val or not re.match(r"\d{1,2}/\d{1,2}/\d{4}", date_val):
            label = date_val.lower()
            if "estimated weekly" in label:
                section = "weekly"
            continue

        total = _safe_float(sh.cell_value(r, 1))
        equity_total = _safe_float(sh.cell_value(r, 3))
        equity_domestic = _safe_float(sh.cell_value(r, 5))
        equity_world = _safe_float(sh.cell_value(r, 7))
        hybrid = _safe_float(sh.cell_value(r, 9))
        bond_total = _safe_float(sh.cell_value(r, 11))
        bond_taxable = _safe_float(sh.cell_value(r, 13))
        bond_municipal = _safe_float(sh.cell_value(r, 15))
        commodity = _safe_float(sh.cell_value(r, 17))

        entry = {
            "date": date_val,
            "total_flows": total,
            "equity": {
                "total": equity_total,
                "domestic": equity_domestic,
                "world": equity_world,
            },
            "hybrid": hybrid,
            "bond": {
                "total": bond_total,
                "taxable": bond_taxable,
                "municipal": bond_municipal,
            },
            "commodity": commodity,
        }
        result[section].append(entry)

    return result


def parse_mf_flows(data: bytes) -> dict:
    """Parse the Long-Term Mutual Fund Flows XLS (detailed breakdown)."""
    wb = xlrd.open_workbook(file_contents=data)
    sh = wb.sheet_by_index(0)

    result = {
        "source": "ICI - Long-Term Mutual Fund Net New Cash Flow",
        "unit": "millions_USD",
        "monthly": [],
        "weekly": [],
    }

    # Column mapping (0-indexed based on the XLS layout)
    # R4: Date(0), Total(1), (2), Equity(3) ...
    # R5: ..., Equity Total(3), Domestic(5), World(17)
    # R6: ..., Domestic: Total Domestic(5), Large cap(7), Mid cap(9), Small cap(11), Multi cap(13), Other(15)
    #     ..., World: Total World(17), Developed(19), Emerging(21)
    #     ..., Hybrid(23)
    #     ..., Bond: Total Bond(25), Taxable(27), Municipal(39)
    #     ..., Taxable: Investment grade(29), High yield(31), Government(33), Multisector(35), Global(37)

    section = "monthly"
    for r in range(sh.nrows):
        date_val = str(sh.cell_value(r, 0)).strip()
        if not date_val or not re.match(r"\d{1,2}/\d{1,2}/\d{4}", date_val):
            label = date_val.lower()
            if "estimated weekly" in label or "weekly net new cash flow" in label:
                section = "weekly"
            continue

        entry = {
            "date": date_val,
            "total_long_term": _safe_float(sh.cell_value(r, 1)),
            "equity": {
                "total": _safe_float(sh.cell_value(r, 3)),
                "domestic": {
                    "total": _safe_float(sh.cell_value(r, 5)),
                    "large_cap": _safe_float(sh.cell_value(r, 7)),
                    "mid_cap": _safe_float(sh.cell_value(r, 9)),
                    "small_cap": _safe_float(sh.cell_value(r, 11)),
                    "multi_cap": _safe_float(sh.cell_value(r, 13)),
                    "other": _safe_float(sh.cell_value(r, 15)),
                },
                "world": {
                    "total": _safe_float(sh.cell_value(r, 17)),
                    "developed_markets": _safe_float(sh.cell_value(r, 19)),
                    "emerging_markets": _safe_float(sh.cell_value(r, 21)),
                },
            },
            "hybrid": _safe_float(sh.cell_value(r, 23)),
            "bond": {
                "total": _safe_float(sh.cell_value(r, 25)),
                "taxable": {
                    "total": _safe_float(sh.cell_value(r, 27)),
                    "investment_grade": _safe_float(sh.cell_value(r, 29)),
                    "high_yield": _safe_float(sh.cell_value(r, 31)),
                    "government": _safe_float(sh.cell_value(r, 33)),
                    "multisector": _safe_float(sh.cell_value(r, 35)),
                    "global": _safe_float(sh.cell_value(r, 37)),
                },
                "municipal": _safe_float(sh.cell_value(r, 39)),
            },
        }
        result[section].append(entry)

    return result


def parse_mm_assets(data: bytes) -> dict:
    """Parse the Money Market Fund Assets XLS."""
    wb = xlrd.open_workbook(file_contents=data)
    sh = wb.sheet_by_index(0)

    result = {
        "source": "ICI - Weekly Money Market Fund Assets",
        "unit": "millions_USD",
        "weekly": [],
    }

    # Column mapping based on header analysis:
    # Each section (Total/Institutional/Retail) has 6 categories, each with (#Classes, TNA) = 12 cols each
    # Total: 1 + 3*12 = 37 cols (0-36)
    # Col 0: Date
    #
    # TOTAL ALL (cols 1-12):
    #   1: TOTAL.classes, 2: TOTAL.tna, 3: TAX-EXEMPT.classes, 4: TAX-EXEMPT.tna
    #   5: GOVERNMENT.classes, 6: GOVERNMENT.tna, 7: TREASURY_REPO.classes, 8: TREASURY_REPO.tna
    #   9: TREASURY_AGENCY.classes, 10: TREASURY_AGENCY.tna, 11: PRIME.classes, 12: PRIME.tna
    #
    # INSTITUTIONAL (cols 13-24): same pattern
    # RETAIL (cols 25-36): same pattern

    for r in range(sh.nrows):
        date_val = str(sh.cell_value(r, 0)).strip()
        if not date_val or not re.match(r"\d{1,2}/\d{1,2}/\d{4}", date_val):
            continue

        entry = {
            "date": date_val,
            "total_all": {
                "total": _mk_mm_cat(sh, r, 1, 2),
                "tax_exempt": _mk_mm_cat(sh, r, 3, 4),
                "government": {
                    "total": _mk_mm_cat(sh, r, 5, 6),
                    "treasury_repo": _mk_mm_cat(sh, r, 7, 8),
                    "treasury_agency": _mk_mm_cat(sh, r, 9, 10),
                },
                "prime": _mk_mm_cat(sh, r, 11, 12),
            },
            "institutional": {
                "total": _mk_mm_cat(sh, r, 13, 14),
                "tax_exempt": _mk_mm_cat(sh, r, 15, 16),
                "government": {
                    "total": _mk_mm_cat(sh, r, 17, 18),
                    "treasury_repo": _mk_mm_cat(sh, r, 19, 20),
                    "treasury_agency": _mk_mm_cat(sh, r, 21, 22),
                },
                "prime": _mk_mm_cat(sh, r, 23, 24),
            },
            "retail": {
                "total": _mk_mm_cat(sh, r, 25, 26),
                "tax_exempt": _mk_mm_cat(sh, r, 27, 28),
                "government": {
                    "total": _mk_mm_cat(sh, r, 29, 30),
                    "treasury_repo": _mk_mm_cat(sh, r, 31, 32),
                    "treasury_agency": _mk_mm_cat(sh, r, 33, 34),
                },
                "prime": _mk_mm_cat(sh, r, 35, 36),
            },
        }
        result["weekly"].append(entry)

    return result


def _safe_float(val) -> float | None:
    """Convert cell value to float, return None if empty/invalid."""
    if val == "" or val is None:
        return None
    try:
        return round(float(val), 2)
    except (ValueError, TypeError):
        return None


def _safe_int(val) -> int | None:
    """Convert cell value to int, return None if empty/invalid."""
    if val == "" or val is None:
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def _mk_mm_cat(sh, r: int, col_classes: int, col_tna: int) -> dict:
    """Build a {'classes': ..., 'tna': ...} dict from two adjacent columns."""
    return {
        "classes": _safe_int(sh.cell_value(r, col_classes)),
        "tna": _safe_float(sh.cell_value(r, col_tna)),
    }


def _normalize_date(d: str) -> str:
    """Normalize date to YYYY-MM-DD for cross-file matching."""
    parts = d.strip().split("/")
    if len(parts) == 3:
        m, day, y = parts
        return f"{y}-{int(m):02d}-{int(day):02d}"
    return d.strip()


def compute_etf_flows(combined: dict, mf: dict) -> list:
    """
    Compute ETF-only flows by subtracting mutual fund flows from combined flows.

    The combined report includes both mutual funds + ETFs.
    The MF report includes only mutual funds.
    ETF flows = Combined flows - MF flows.

    Returns a list of weekly entries with ETF flows added.
    """
    # Build lookup dicts keyed by normalized date
    mf_weekly = {_normalize_date(w["date"]): w for w in mf.get("weekly", [])}

    etf_entries = []
    for cw in combined.get("weekly", []):
        date = cw["date"]
        ndate = _normalize_date(date)
        mw = mf_weekly.get(ndate, {})
        mf_total = mw.get("total_long_term")
        combined_total = cw.get("total_flows")

        etf_total = None
        if combined_total is not None and mf_total is not None:
            etf_total = round(combined_total - mf_total, 2)

        # Estimations for equity and bond by category
        etf_entry = {
            "date": date,
            "etf_estimated_flows": etf_total,
            "combined_flows": combined_total,
            "mutual_fund_flows": mf_total,
        }
        etf_entries.append(etf_entry)

    return etf_entries


def main():
    out_dir = Path(__file__).parent.parent / "data" / "market_data"
    out_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "ICI (Investment Company Institute) — Weekly Fund Flow Estimates",
        "urls": {
            "combined_flows": BASE_URL + FILES["combined_flows"]["page"],
            "mf_flows": BASE_URL + FILES["mf_flows"]["page"],
            "mm_assets": BASE_URL + FILES["mm_assets"]["page"],
        },
        "note_etf_vs_mf": (
            "ETF flows are estimated as Combined flows minus Mutual Fund flows. "
            "ICI does not publish ETF-only flows directly."
        ),
        "note_domestic_vs_world": (
            "Both equity (domestic/world) and detailed style/sector breakdowns are available "
            "in the mutual fund flows data."
        ),
        "data": {},
    }

    print("=" * 60)
    print("ICI Weekly Fund Flow Data Fetcher")
    print("=" * 60)

    # 1. Combined ETF + Long-Term Flows
    print("\n[1/3] Combined ETF + Long-Term Fund Flows...")
    raw_combined = download_xls("combined_flows")
    if raw_combined:
        result["data"]["combined_flows"] = parse_combined_flows(raw_combined)
        n_weekly = len(result["data"]["combined_flows"]["weekly"])
        print(f"  → {n_weekly} weekly data points")

    # 2. Long-Term Mutual Fund Flows
    print("\n[2/3] Long-Term Mutual Fund Flows...")
    raw_mf = download_xls("mf_flows")
    if raw_mf:
        result["data"]["mf_flows"] = parse_mf_flows(raw_mf)
        n_weekly = len(result["data"]["mf_flows"]["weekly"])
        print(f"  → {n_weekly} weekly data points")

    # 3. Money Market Fund Assets
    print("\n[3/3] Money Market Fund Assets...")
    raw_mm = download_xls("mm_assets")
    if raw_mm:
        result["data"]["mm_assets"] = parse_mm_assets(raw_mm)
        n_weekly = len(result["data"]["mm_assets"]["weekly"])
        print(f"  → {n_weekly} weekly data points")

    # 4. Compute ETF-only flows (where both datasets available)
    if "combined_flows" in result["data"] and "mf_flows" in result["data"]:
        print("\n  Computing ETF-only flows (Combined − MF)...")
        result["data"]["etf_estimated_flows"] = compute_etf_flows(
            result["data"]["combined_flows"],
            result["data"]["mf_flows"],
        )
        print(f"  → {len(result['data']['etf_estimated_flows'])} weekly ETF estimates")

    # Write output
    out_path = out_dir / "ici_flows.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"✓ Written to {out_path}")
    print(f"  Generated: {result['generated_at']}")

    # Quick summary of latest weekly data
    datasets = ["combined_flows", "mf_flows", "mm_assets"]
    for key in datasets:
        dset = result["data"].get(key, {})
        weekly = dset.get("weekly", [])
        if weekly:
            latest = weekly[-1]
            print(f"\n  Latest {key}: {latest['date']}")
            if "total_flows" in latest:
                print(f"    Total flows: {latest['total_flows']}M USD")
            if "total_all" in latest:
                tna = latest["total_all"].get("total", {}).get("tna")
                if tna is not None:
                    print(f"    Total MM assets: {tna:,.0f}M USD ({tna/1000:,.1f}B)")

    if "etf_estimated_flows" in result["data"]:
        etf = result["data"]["etf_estimated_flows"]
        if etf:
            print(f"  Latest estimated ETF flows: {etf[-1]['etf_estimated_flows']}M USD")


if __name__ == "__main__":
    main()
