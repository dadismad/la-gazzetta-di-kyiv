#!/usr/bin/env python3
"""
fetch_fred.py -- FRED Macro Baseline via St. Louis Fed API
==========================================================
Daily fetch of key Federal Reserve Economic Data series. Provides the
macro regime baseline (rates, inflation, employment, trade) used by
calculate_capital.py and the contradiction_synthesizer market context.

API:      https://api.stlouisfed.org/fred/
Docs:     https://fred.stlouisfed.org/docs/api/fred/
Key:      FRED_API_KEY (free -- register at https://fred.stlouisfed.org/docs/api/api_key.html)

Schedule: Daily at 06:00 UTC. Governor runs this as step 2.6.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

# -- config ----------------------------------------------------------
PROJECT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = DATA_DIR / "fred_series.json"

FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
if not FRED_API_KEY:
    # Fallback: GCP Secret Manager
    try:
        import subprocess as _sp
        _r = _sp.run(
            ["gcloud", "secrets", "versions", "access", "latest",
             "--secret=gazzetta-fred-key"],
            capture_output=True, text=True, timeout=10
        )
        if _r.returncode == 0 and _r.stdout.strip():
            FRED_API_KEY = _r.stdout.strip()
    except Exception:
        pass
FRED_BASE = "https://api.stlouisfed.org/fred"
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3

# -- Series definitions ----------------------------------------------
# Each entry: fred series ID, human label, narrative association, unit
SERIES = [
    # --- Interest Rates (rate_cycle, dollar_decline) ---
    {"id": "DGS10",    "label": "10Y Treasury Yield",           "narrative": "rate_cycle",   "unit": "%"},
    {"id": "DGS2",     "label": "2Y Treasury Yield",            "narrative": "rate_cycle",   "unit": "%"},
    {"id": "DFEDTARU", "label": "Fed Funds Target (Upper)",     "narrative": "rate_cycle",   "unit": "%"},
    {"id": "T10Y2Y",   "label": "10Y-2Y Spread",                "narrative": "rate_cycle",   "unit": "bp"},
    {"id": "T10YIE",   "label": "10Y Breakeven Inflation",      "narrative": "rate_cycle",   "unit": "%"},
    {"id": "DFII10",   "label": "10Y TIPS Real Yield",          "narrative": "rate_cycle",   "unit": "%"},

    # --- Dollar & Currency (dollar_decline) ---
    {"id": "DTWEXBGS", "label": "Trade-Weighted Dollar (Broad)", "narrative": "dollar_decline", "unit": "idx"},
    {"id": "DEXUSEU",  "label": "USD/EUR Exchange Rate",        "narrative": "dollar_decline", "unit": "USD"},
    {"id": "DEXJPUS",  "label": "JPY/USD Exchange Rate",        "narrative": "dollar_decline", "unit": "JPY"},
    {"id": "DEXCHUS",  "label": "CNY/USD Exchange Rate",        "narrative": "china_ascent",   "unit": "CNY"},

    # --- Inflation (commodity_supercycle, rate_cycle) ---
    {"id": "CPIAUCSL", "label": "CPI All Urban Consumers",      "narrative": "commodity_supercycle", "unit": "idx"},
    {"id": "CPILFESL", "label": "CPI Core (ex-Food/Energy)",    "narrative": "commodity_supercycle", "unit": "idx"},
    {"id": "PPIACO",   "label": "PPI All Commodities",          "narrative": "commodity_supercycle", "unit": "idx"},
    {"id": "PCEPI",    "label": "PCE Price Index",              "narrative": "commodity_supercycle", "unit": "idx"},

    # --- Employment (rate_cycle) ---
    {"id": "UNRATE",   "label": "Unemployment Rate",            "narrative": "rate_cycle",   "unit": "%"},
    {"id": "PAYEMS",   "label": "Nonfarm Payrolls",             "narrative": "rate_cycle",   "unit": "M"},
    {"id": "ICSA",     "label": "Initial Jobless Claims",       "narrative": "rate_cycle",   "unit": "K"},

    # --- Industrial / Trade (deglobalization, china_ascent) ---
    {"id": "INDPRO",   "label": "Industrial Production Index",  "narrative": "deglobalization", "unit": "idx"},
    {"id": "BOPGSTB",  "label": "Trade Balance: Goods & Svcs",  "narrative": "deglobalization", "unit": "M USD"},
    {"id": "GPDI",     "label": "Gross Private Domestic Invest", "narrative": "deglobalization", "unit": "B USD"},

    # --- GDP (deglobalization) ---
    {"id": "GDP",      "label": "Gross Domestic Product",       "narrative": "deglobalization", "unit": "B USD"},
    {"id": "GDPC1",    "label": "Real GDP",                     "narrative": "deglobalization", "unit": "B USD"},

    # --- Energy (critical_resource_control) ---
    {"id": "DCOILWTICO", "label": "WTI Crude Oil Spot",         "narrative": "critical_resource_control", "unit": "USD"},
    {"id": "DHHNGSP",    "label": "Henry Hub Natural Gas Spot", "narrative": "critical_resource_control", "unit": "USD"},

    # --- Financial Conditions (all narratives) ---
    {"id": "VIXCLS",   "label": "VIX Close",                    "narrative": "rate_cycle",   "unit": "idx"},
    {"id": "NFCI",     "label": "Chicago Fed Financial Cond.",   "narrative": "rate_cycle",   "unit": "idx"},
    {"id": "TEDRATE",  "label": "TED Spread",                   "narrative": "rate_cycle",   "unit": "bp"},

    # --- Credit Spreads (rate_cycle) ---
    {"id": "BAA10Y",   "label": "Baa Corp Spread vs 10Y Trsy",  "narrative": "rate_cycle",   "unit": "%"},
    {"id": "AAA10Y",   "label": "Aaa Corp Spread vs 10Y Trsy",  "narrative": "rate_cycle",   "unit": "%"},
]


# -- Fetch helpers ---------------------------------------------------
def _ts():
    return datetime.now(timezone.utc).isoformat()


def fetch_series(series_id, retries=MAX_RETRIES):
    """Fetch the most recent observation for a FRED series."""
    if not FRED_API_KEY:
        print(
            f"[fred] WARNING: FRED_API_KEY not set -- skipping {series_id}",
            file=sys.stderr,
        )
        return None

    url = f"{FRED_BASE}/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1,
    }
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                obs = data.get("observations", [])
                if obs:
                    return obs[0]
                print(f"[fred] No observations for {series_id}", file=sys.stderr)
                return None
            elif resp.status_code == 400:
                print(
                    f"[fred] Bad request for {series_id}: {resp.text[:200]}",
                    file=sys.stderr,
                )
                return None
            elif resp.status_code == 429:
                wait = 2 ** attempt
                print(f"[fred] Rate limited, waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            else:
                print(
                    f"[fred] HTTP {resp.status_code} for {series_id}",
                    file=sys.stderr,
                )
                if attempt < retries - 1:
                    time.sleep(2)
        except requests.exceptions.Timeout:
            print(
                f"[fred] Timeout for {series_id} (attempt {attempt+1})",
                file=sys.stderr,
            )
            if attempt < retries - 1:
                time.sleep(5)
        except Exception as e:
            print(f"[fred] Error fetching {series_id}: {e}", file=sys.stderr)
            if attempt < retries - 1:
                time.sleep(3)
    return None


def compute_changes(series_id, current_val):
    """Compute 30-day and 90-day percent changes if data is available."""
    if not FRED_API_KEY or current_val is None:
        return {"value": current_val, "change_30d": None, "change_90d": None}

    changes = {"value": current_val, "change_30d": None, "change_90d": None}
    url = f"{FRED_BASE}/series/observations"
    base_params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
    }

    for window, key in [(30, "change_30d"), (90, "change_90d")]:
        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=window)).strftime(
                "%Y-%m-%d"
            )
            params = {
                **base_params,
                "observation_start": cutoff,
                "limit": 1,
                "sort_order": "asc",
            }
            resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                obs = data.get("observations", [])
                if obs and obs[0].get("value") not in (".", None):
                    prev = float(obs[0]["value"])
                    if current_val != 0:
                        changes[key] = round(
                            ((current_val - prev) / abs(prev)) * 100, 2
                        )
        except Exception:
            pass
    return changes


def classify_regime(series_output):
    """Multi-dimensional macro regime classifier using FRED series.
    
    Primary axis: 10Y nominal yield (DGS10).
    Secondary axis: yield curve (T10Y2Y), real rates (DFII10), financial conditions (NFCI).
    Overlay: VIX stress, unemployment.
    
    Regimes (in order of restrictiveness):
      INVERSION       — yield curve inverted (2Y > 10Y by >30bp)
      RESTRICTIVE     — nominal >5.0%, tight financial conditions
      TIGHTENING      — nominal >4.0% with elevated real rates or flattening curve
      NEUTRAL-TIGHT   — nominal 3.5–4.5% with modest real rates, curve normalising
      STRESS          — financial stress (VIX > 28 or NFCI > 0) regardless of rate level
      NEUTRAL         — nominal 2.5–3.5%, no stress signals
      EASING          — nominal <3.0% with accommodative posture
      ACCOMMODATIVE   — nominal <2.5% with low unemployment
      UNKNOWN         — insufficient data
    """
    dgs10 = series_output.get("DGS10", {}).get("value")       # 10Y nominal yield
    spread = series_output.get("T10Y2Y", {}).get("value")     # 10Y-2Y spread (bp)
    dfii10 = series_output.get("DFII10", {}).get("value")     # 10Y TIPS real yield
    nfci = series_output.get("NFCI", {}).get("value")         # Chicago Fed Financial Conditions
    unrate = series_output.get("UNRATE", {}).get("value")     # Unemployment rate
    vix = series_output.get("VIXCLS", {}).get("value")        # VIX close

    if dgs10 is None:
        return "UNKNOWN"

    # ── Yield curve inversion — strongest structural signal ──
    if spread is not None and spread < -0.3:
        return "INVERSION"

    # ── Financial stress overlay (can co-occur with any regime) ──
    stress = False
    if vix is not None and vix > 28:
        stress = True
    if nfci is not None and nfci > 0:
        stress = True

    # ── Real rate estimate (use TIPS if available, else approximate) ──
    real_rate = dfii10 if dfii10 is not None else (dgs10 - 3.0)

    # ── Multi-dimensional regime classification ──
    if dgs10 > 5.0:
        return "RESTRICTIVE"
    elif dgs10 > 4.0:
        if real_rate is not None and real_rate > 1.5:
            return "TIGHTENING"
        elif stress:
            return "STRESS"
        else:
            return "NEUTRAL-TIGHT"
    elif dgs10 > 3.0:
        if stress:
            return "STRESS"
        elif real_rate is not None and real_rate < 0:
            return "EASING"
        else:
            return "NEUTRAL"
    elif dgs10 > 2.0:
        if stress:
            return "STRESS"
        return "EASING"
    else:
        if unrate is not None and unrate < 4.0:
            return "ACCOMMODATIVE"
        return "EASING"


# -- Main ------------------------------------------------------------
def main():
    if not FRED_API_KEY:
        print(
            "[fred] ERROR: FRED_API_KEY not set. Cannot fetch any series.",
            file=sys.stderr,
        )
        empty = {
            "generated_at": _ts(),
            "source": "FRED (Federal Reserve Economic Data)",
            "api_key_configured": False,
            "series_fetched": 0,
            "total_series_defined": len(SERIES),
            "macro_regime": "UNKNOWN",
            "series": {},
            "status": "missing_api_key",
            "error": "FRED_API_KEY not set. Register at https://fred.stlouisfed.org/docs/api/api_key.html",
        }
        tmp = str(OUTPUT_FILE) + ".tmp"
        with open(tmp, "w") as f:
            json.dump(empty, f, indent=2)
        os.replace(tmp, OUTPUT_FILE)
        print("[fred] Degraded output written (missing API key)")
        return 1

    fetched = 0
    failed = 0
    series_output = {}

    for cfg in SERIES:
        sid = cfg["id"]
        obs = fetch_series(sid)
        if obs is None:
            failed += 1
            series_output[sid] = {
                "label": cfg["label"],
                "narrative": cfg["narrative"],
                "unit": cfg["unit"],
                "status": "error",
                "value": None,
                "date": None,
                "change_30d": None,
                "change_90d": None,
            }
            time.sleep(0.3)
            continue

        try:
            val = float(obs["value"]) if obs.get("value") not in (".", None) else None
        except (ValueError, TypeError):
            val = None

        changes = compute_changes(sid, val)
        series_output[sid] = {
            "label": cfg["label"],
            "narrative": cfg["narrative"],
            "unit": cfg["unit"],
            "status": "ok" if val is not None else "no_data",
            "value": val,
            "date": obs.get("date"),
            "change_30d": changes.get("change_30d"),
            "change_90d": changes.get("change_90d"),
        }
        fetched += 1 if val is not None else 0
        time.sleep(0.3)  # FRED free tier: 120 req/min

    regime = classify_regime(series_output)

    output = {
        "generated_at": _ts(),
        "source": "FRED (Federal Reserve Economic Data)",
        "api_key_configured": True,
        "series_fetched": fetched,
        "series_failed": failed,
        "total_series_defined": len(SERIES),
        "macro_regime": regime,
        "series": series_output,
        "status": "ok" if fetched > 0 else "error",
    }

    tmp = str(OUTPUT_FILE) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(output, f, indent=2)
    os.replace(tmp, OUTPUT_FILE)

    print(
        f"[fred] {fetched}/{len(SERIES)} series written to {OUTPUT_FILE} (regime: {regime})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
