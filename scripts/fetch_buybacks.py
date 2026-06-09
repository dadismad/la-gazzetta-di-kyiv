#!/usr/bin/env python3
"""fetch_buybacks.py — Pull S&P 500 corporate buyback data from SEC EDGAR XBRL API.

Corporate buybacks are a critical capital flow component that Gazzetta was missing.
This script fetches structured buyback data (PaymentsForRepurchaseOfCommonStock)
directly from the SEC's XBRL API — the ONLY free, reliable source for buyback data.

How it works:
  1. Fetches the S&P 500 constituents list (with CIKs) from a well-known GitHub dataset
  2. For each company, queries the SEC XBRL API for us-gaap:PaymentsForRepurchaseOfCommonStock
  3. Finds the most recent non-zero value (annual 10-K or quarterly 10-Q)
  4. Aggregates by sector, computes trends, and outputs structured data

Data latency: SEC XBRL data lags by ~45-90 days (the 10-Q/10-K filing window).
This is normal — Birinyi, GS, and Bloomberg all have similar or worse latency.

Rate limits: SEC requests ≤10/sec. We add 0.3s delay between requests (~3/sec, well under).

Output: data/market_data/buybacks.json + data/market_data/buybacks_signal.json

SEC XBRL API docs: https://www.sec.gov/edgar/sec-api-documentation
XBRL concepts used:
  - us-gaap:PaymentsForRepurchaseOfCommonStock (cash flow from financing)
  - us-gaap:StockRepurchasedDuringPeriodValue (fallback, equity section)

Set SEC_USER_AGENT env var for your email (required by SEC).
"""

import csv, json, os, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

# ── Configuration ───────────────────────────────────────────────────────────

USER_AGENT = os.environ.get(
    "SEC_USER_AGENT",
    "GazzettaDiKyiv/1.0 (research@gazzetta.com; +https://gazzetta-di-kyiv.com)"
)

# Where to get the S&P 500 constituent list (includes CIK numbers!)
SP500_URL = (
    "https://raw.githubusercontent.com/datasets/"
    "s-and-p-500-companies/main/data/constituents.csv"
)

# SEC EDGAR XBRL API endpoints
SEC_TICKER_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_XBRL_CONCEPT = (
    "https://data.sec.gov/api/xbrl/companyconcept/"
    "CIK{cik_padded}/us-gaap/{concept}.json"
)

# XBRL concepts to try, in priority order
XBRL_CONCEPTS = [
    "PaymentsForRepurchaseOfCommonStock",  # Cash flow statement (most common)
    "StockRepurchasedDuringPeriodValue",   # Equity/balance sheet approach (fallback)
]

# Request delay (seconds) — SEC says ≤10 req/sec; we use ~3/sec
REQUEST_DELAY = 0.35

PROJ = Path(__file__).resolve().parent.parent
OUT_DIR = PROJ / "data" / "market_data"
OUT_PATH = OUT_DIR / "buybacks.json"
SIGNAL_PATH = OUT_DIR / "buybacks_signal.json"
TEMPLATE_PATH = OUT_DIR / "buybacks_template.json"

# Cache for SEC company_tickers to avoid re-fetching
_ticker_cache = None


# ── Data Fetching ───────────────────────────────────────────────────────────

def _fetch_json(url, timeout=20):
    """Fetch JSON from a URL with proper headers."""
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None  # Concept not found for this company
        print(f"  HTTP {e.code} fetching {url}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  Error: {e}", file=sys.stderr)
        return None


def fetch_sp500_constituents():
    """Fetch the S&P 500 constituent list with CIK numbers."""
    print("Fetching S&P 500 constituent list...")
    req = urllib.request.Request(SP500_URL, headers={
        "User-Agent": USER_AGENT,
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            reader = csv.DictReader(resp.read().decode("utf-8").splitlines())
            companies = []
            for row in reader:
                cik_raw = row.get("CIK", "").strip()
                companies.append({
                    "ticker": row.get("Symbol", "").strip(),
                    "name": row.get("Security", "").strip(),
                    "sector": row.get("GICS Sector", "").strip(),
                    "sub_industry": row.get("GICS Sub-Industry", "").strip(),
                    "cik": int(cik_raw) if cik_raw.isdigit() else None,
                })
            print(f"  Found {len(companies)} constituents")
            return companies
    except Exception as e:
        print(f"  ERROR fetching S&P 500 list: {e}", file=sys.stderr)
        return []


def fetch_company_tickers():
    """Fetch the SEC master company_tickers.json for CIK→ticker mapping."""
    global _ticker_cache
    if _ticker_cache:
        return _ticker_cache
    data = _fetch_json(SEC_TICKER_URL)
    if not data:
        return {}
    mapping = {}
    for item in data.values():
        ticker = item.get("ticker", "").upper()
        cik = item.get("cik_str")
        if ticker and cik:
            mapping[ticker] = cik
    _ticker_cache = mapping
    print(f"  Loaded {len(mapping)} ticker→CIK mappings from SEC")
    return mapping


def fetch_buyback_concept(cik, concept):
    """Fetch a single XBRL concept for a company.

    Returns the most recent non-zero annual value, or None.
    """
    if not cik:
        return None
    cik_padded = str(cik).zfill(10)
    url = SEC_XBRL_CONCEPT.format(cik_padded=cik_padded, concept=concept)
    data = _fetch_json(url)
    if not data:
        return None

    units = data.get("units", {})
    for unit_key, points in units.items():
        if not points:
            continue
        # Filter to non-zero values, preferring annual (10-K) over quarterly (10-Q)
        # First find the most recent non-zero annual value
        non_zero = [p for p in points if p.get("val", 0) != 0]
        if not non_zero:
            continue

        # Prefer 10-K annual values
        annual_vals = [p for p in non_zero if p.get("form") == "10-K"]
        if annual_vals:
            best = annual_vals[-1]  # Most recent 10-K
        else:
            # Fall back to most recent non-zero (could be 10-Q)
            best = non_zero[-1]

        return {
            "value": best.get("val", 0),
            "date": best.get("end"),
            "form": best.get("form"),
            "fy": f"FY{best.get('fy', '')}",
            "unit": unit_key,
        }
    return None


def fetch_company_buyback(cik):
    """Fetch buyback data for a single company across all fallback concepts."""
    for concept in XBRL_CONCEPTS:
        result = fetch_buyback_concept(cik, concept)
        if result and result.get("value", 0) > 0:
            result["concept"] = concept
            return result
    return None


# ── Aggregation ─────────────────────────────────────────────────────────────

def aggregate_buybacks(results):
    """Compute sector and aggregate totals from individual company results."""
    sector_data: dict = defaultdict(lambda: {
        "total_b": 0.0,
        "count": 0,
        "companies": [],
        "top_5": [],
    })
    total = 0.0
    count = 0

    for r in results:
        val_b = r["value_b"]
        sector = r.get("sector", "Unknown")
        sector_data[sector]["total_b"] += val_b
        sector_data[sector]["count"] += 1
        sector_data[sector]["companies"].append({
            "ticker": r["ticker"],
            "value_b": val_b,
            "date": r["date"],
        })
        total += val_b
        count += 1

    # Sort sectors by total
    sorted_sectors = sorted(
        sector_data.items(), key=lambda x: x[1]["total_b"], reverse=True
    )

    # Compute top 5 companies per sector
    for sector, data in sorted_sectors:
        data["companies"].sort(key=lambda x: x["value_b"], reverse=True)
        data["top_5"] = data["companies"][:5]
        # Remove full companies list from sector level (keep in detail)
        del data["companies"]

    # Sort companies overall for detail
    results.sort(key=lambda x: x["value_b"], reverse=True)

    return {
        "total_b": round(total, 1),
        "count": count,
        "sectors": {
            sector: {
                "total_b": round(data["total_b"], 1),
                "count": data["count"],
                "top_5": data["top_5"],
            }
            for sector, data in sorted_sectors
        },
        "detail": results,
    }


# ── Signal Generation ──────────────────────────────────────────────────────

def compute_signal(aggregated, previous_total_b=None):
    """Generate a buyback flow signal for the Gazzetta pipeline."""
    total_b = aggregated["total_b"]
    count = aggregated["count"]

    # Determine pace
    if total_b > 250:
        pace = "very_high"
        level = "critical"
        message = f"$S&P 500 buybacks at ~${total_b:.0f}B annualized — massive corporate inflow."
    elif total_b > 150:
        pace = "high"
        level = "warning"
        message = f"S&P 500 buybacks ~${total_b:.0f}B/yr — significant corporate demand."
    elif total_b > 80:
        pace = "moderate"
        level = "info"
        message = f"S&P 500 buybacks ~${total_b:.0f}B/yr — normal corporate activity."
    else:
        pace = "low"
        level = "warning"
        message = f"S&P 500 buybacks ~${total_b:.0f}B/yr — below trend, watch for pullback."

    if previous_total_b and total_b:
        pct_change = round((total_b - previous_total_b) / previous_total_b * 100, 1)
        if abs(pct_change) > 5:
            direction = "accelerating" if pct_change > 0 else "decelerating"
            message += f" YoY buyback pace {direction} ({pct_change:+.1f}%)."

    signal = {
        "type": "corporate_buybacks",
        "level": level,
        "pace": pace,
        "message": message,
        "data": {
            "total_annual_b": total_b,
            "reporting_companies": count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "SEC EDGAR XBRL (PaymentsForRepurchaseOfCommonStock)",
        },
    }

    # Top sectors
    top_sectors = sorted(
        aggregated["sectors"].items(),
        key=lambda x: x[1]["total_b"],
        reverse=True,
    )[:5]
    signal["data"]["top_sectors_b"] = {
        s: round(d["total_b"], 1) for s, d in top_sectors
    }

    return signal


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Get S&P 500 constituents
    companies = fetch_sp500_constituents()
    if not companies:
        print("ERROR: Could not fetch S&P 500 constituent list")
        print("The manual template is available for manual updates.")
        sys.exit(1)

    # 2. Process each company
    print(f"\nFetching buyback data for {len(companies)} S&P 500 companies...")
    results = []
    errors = []
    start = time.time()

    for i, company in enumerate(companies):
        ticker = company["ticker"]
        cik = company.get("cik")

        if not cik:
            errors.append({"ticker": ticker, "reason": "no CIK"})
            continue

        data = fetch_company_buyback(cik)
        if data and data.get("value", 0) > 0:
            value_b = round(data["value"] / 1_000_000_000, 2)  # Convert to billions
            results.append({
                "ticker": ticker,
                "name": company["name"],
                "sector": company.get("sector", "Unknown"),
                "sub_industry": company.get("sub_industry", ""),
                "cik": cik,
                "value_b": value_b,
                "value_raw": data["value"],
                "date": data["date"],
                "form": data["form"],
                "fy": data["fy"],
                "source_concept": data["concept"],
            })
            print(f"  [{i+1}/{len(companies)}] {ticker} ({company['name'][:30]}): "
                  f"${value_b}B on {data['date']} ({data['form']})")
        else:
            errors.append({"ticker": ticker, "reason": "no buyback data in SEC XBRL"})
            print(f"  [{i+1}/{len(companies)}] {ticker}: No buyback data found")

        time.sleep(REQUEST_DELAY)

    elapsed = time.time() - start
    print(f"\nProcessed {len(companies)} companies in {elapsed:.0f}s")

    # 3. Aggregate
    aggregated = aggregate_buybacks(results)
    total_b = aggregated["total_b"]
    count = aggregated["count"]

    # 4. Build output
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "fetch_buybacks.py",
        "source": "SEC EDGAR XBRL (us-gaap:PaymentsForRepurchaseOfCommonStock)",
        "data_lag_days": "~45-90 (10-Q/10-K filing window)",
        "confidence": "medium — based on reported GAAP data, not real-time execution",
        "notes": [
            "Data is from the most recent fiscal period (10-K annual or 10-Q quarterly).",
            "SEC XBRL data lags by 45-90 days from the reporting date.",
            "Not all S&P 500 companies report buybacks via XBRL — ~85-95% coverage expected.",
            "Birinyi/GS/Bloomberg all derive from similar SEC data with proprietary adjustments.",
            "For real-time buyback estimates, Goldman Sachs buyback desk or Bloomberg BQ needed.",
        ],
        "summary": {
            "total_annual_b": total_b,
            "reporting_companies": count,
            "sp500_total_companies": len(companies),
            "coverage_pct": round(count / len(companies) * 100, 1) if companies else 0,
            "data_date_range": f"Latest data as of most recent filings through ~{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        },
        "sectors": aggregated["sectors"],
        "companies": aggregated["detail"],
        "errors": errors,
    }

    # Save buybacks.json
    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Buyback data → {OUT_PATH}")
    print(f"  Aggregated: ${total_b}B annualized across {count} companies")

    # 5. Generate market signal for the pipeline
    signal = compute_signal(aggregated, previous_total_b=None)
    signal_output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "SEC EDGAR XBRL (via fetch_buybacks.py)",
        "buybacks_signal": signal,
    }
    with open(SIGNAL_PATH, "w") as f:
        json.dump(signal_output, f, indent=2, ensure_ascii=False)
    print(f"✓ Buyback signal → {SIGNAL_PATH}")

    # 6. Error summary
    if errors:
        print(f"\n⚠ {len(errors)} companies had no buyback data in SEC XBRL:")
        for e in errors[:10]:
            print(f"  {e['ticker']}: {e['reason']}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")

    # 7. Update template with latest run
    template = build_template()
    template["last_updated"] = output["generated_at"]
    template["summary"]["last_reported_total_b"] = total_b
    template["summary"]["last_reported_companies"] = count
    with open(TEMPLATE_PATH, "w") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    print(f"✓ Updated template → {TEMPLATE_PATH}")

    return output


def build_template():
    """Build the manual-update JSON template with all the right fields.

    This template serves as:
    1. Documentation of the buyback data schema
    2. Fallback for manual updates when the scraper can't run
    3. Reference for integration with the flows pipeline
    """
    return {
        "_meta": {
            "description": "S&P 500 Corporate Buyback Data — Manual Update Template",
            "purpose": "Track corporate buyback flows for Gazzetta capital flows pipeline",
            "update_frequency": "weekly or after each earnings season (quarterly)",
            "source_options": {
                "primary": "SEC EDGAR XBRL (free) — fetch_buybacks.py auto-populates",
                "paid_alternatives": {
                    "goldman_sachs": "GS US Weekly Buyback Brief (institutional clients only)",
                    "bloomberg": "BQ function on Bloomberg Terminal (~$2K/mo)",
                    "birinyi": "Birinyi Associates enterprise subscription (~$15-25K/yr)",
                    "compustat": "S&P Global Compustat via WRDS (academic) or enterprise",
                    "factset": "FactSet screening module (enterprise license)",
                    "refinitiv": "Refinitiv Eikon buyback screening (terminal required)",
                },
                "notes": [
                    "All paid sources ultimately derive from the same SEC filings.",
                    "The edge of paid sources is: (a) timeliness, (b) normalization across GAAP differences, (c) execution estimates vs. announced programs.",
                    "Goldman Sachs also provides real-time buyback execution estimates from their prime brokerage desk (proprietary).",
                    "Birinyi manually tracks announced programs vs. actual execution — useful for completion rates.",
                ],
            },
        },
        "last_updated": "",
        "generated_by": "fetch_buybacks.py or manual entry",
        "summary": {
            "last_reported_total_b": 0.0,
            "last_reported_companies": 0,
            "data_date": "YYYY-MM-DD",
            "annualized_pace_b": 0.0,
            "yoy_change_pct": 0.0,
            "confidence_pct": 0,
            "coverage_note": "Top ~100 companies account for ~80% of total buyback volume",
        },
        "signal": {
            "type": "corporate_buybacks",
            "direction": "inflow",
            "level": "info | warning | critical",
            "pace": "low | moderate | high | very_high",
            "message": "Describe the current buyback environment",
            "data": {
                "total_annual_b": 0.0,
                "reporting_companies": 0,
                "timestamp": "",
                "source": "Manual update or SEC EDGAR XBRL",
            },
        },
        "sectors": {
            "Information Technology": {
                "total_b": 0.0,
                "count": 0,
                "top_5": [
                    {"ticker": "AAPL", "value_b": 0.0},
                ],
            },
            "Financials": {
                "total_b": 0.0,
                "count": 0,
                "top_5": [],
            },
            "Health Care": {
                "total_b": 0.0,
                "count": 0,
                "top_5": [],
            },
            "Consumer Discretionary": {
                "total_b": 0.0,
                "count": 0,
                "top_5": [],
            },
            "Energy": {
                "total_b": 0.0,
                "count": 0,
                "top_5": [],
            },
            "Communication Services": {
                "total_b": 0.0,
                "count": 0,
                "top_5": [],
            },
            "Industrials": {
                "total_b": 0.0,
                "count": 0,
                "top_5": [],
            },
            "Consumer Staples": {
                "total_b": 0.0,
                "count": 0,
                "top_5": [],
            },
            "Utilities": {
                "total_b": 0.0,
                "count": 0,
                "top_5": [],
            },
            "Materials": {
                "total_b": 0.0,
                "count": 0,
                "top_5": [],
            },
            "Real Estate": {
                "total_b": 0.0,
                "count": 0,
                "top_5": [],
            },
        },
        "companies": [
            {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "sector": "Information Technology",
                "value_b": 90.7,
                "date": "2025-09-27",
                "form": "10-K",
                "fy": "FY2025",
                "notes": "Apple is consistently the largest S&P 500 buyback company",
            },
        ],
        "flow_integration": {
            "pipeline_stage": "enrich_market_data.py reads buybacks_signal.json",
            "flows_impact": {
                "direction": "inflow",
                "asset_class": "equities",
                "anchor_symbol": "SPX",
                "flow_type": "corporate_buybacks",
                "default_confidence_pct": 75,
                "notes": [
                    "Buybacks are a persistent, systematic inflow into equities.",
                    "Unlike fund flows, buybacks are price-insensitive (executed via 10b5-1 plans).",
                    "Buybacks accelerate during blackout periods (post-earnings).",
                    "They are the single largest source of equity demand, exceeding all other sources combined in most years.",
                    "GS estimates S&P 500 buybacks at ~$1.1T for 2025.",
                    "SEC-reported values lag 45-90 days; use as a trend indicator, not real-time.",
                ],
            },
        },
    }


if __name__ == "__main__":
    main()
