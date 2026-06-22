#!/usr/bin/env python3
"""
La Gazzetta di Kyiv — Phase 6
Module: fetch_macro_baselines.py
Purpose: Maintain macro_baselines.json — the denominator layer for
         Relative Capital Intensity (RCI) calculations.
Schedule: Weekly cron (Saturday 03:00 UTC)
"""

import json, os, sys, urllib.request
from pathlib import Path
from datetime import timezone, datetime

DATA_DIR = Path("/opt/gazzetta-di-kyiv/data")
OUTPUT = DATA_DIR / "macro_baselines.json"

# ── Hardcoded baselines (updated weekly via cron) ──
# These are reference denominators — not fetched from APIs because
# there's no free, reliable single source for global equity market cap
BASELINES = {
    "global_equities_usd":     100_000_000_000_000,   # ~$100T global equities
    "us_m2_usd":                22_800_000_000_000,   # ~$22.8T US M2 money supply
    "total_crypto_mcap_usd":    2_400_000_000_000,   # ~$2.4T total crypto market cap
}

# ── Narrative-to-segment mapping ──
# Which denominator should each narrative's capital be measured against?
NARRATIVE_SEGMENTS = {
    "dollar_decline":        "us_m2_usd",
    "rate_cycle":            "us_m2_usd",
    "crypto_reserve":        "total_crypto_mcap_usd",
    "tech_convergence":      "global_equities_usd",
    "ai_chips":              "global_equities_usd",
    "space_economy":         "global_equities_usd",
    "china_ascent":         "global_equities_usd",
    "deglobalization":       "global_equities_usd",
    "energy_sovereignty":    "global_equities_usd",
    "gene_editing":          "global_equities_usd",
    "wealthy_sports":        "global_equities_usd",
    "commodity_supercycle":  "global_equities_usd",
}

# ── Saturation thresholds ──
# If total narrative capital exceeds this fraction of its segment,
# flag as "overheated / crowded trade"
SATURATION_THRESHOLD = 0.15  # 15%


def fetch_live_crypto_mcap():
    """Try to get live total crypto market cap from CoinGecko free API."""
    try:
        url = "https://api.coingecko.com/api/v3/global"
        req = urllib.request.Request(url, headers={"User-Agent": "GazzettaDiKyiv/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            mcap = data.get("data", {}).get("total_market_cap", {}).get("usd")
            if mcap:
                return int(mcap)
    except Exception as e:
        print(f"  [warn] CoinGecko global fetch failed: {e}")
    return None


def main():
    print("[fetch_macro_baselines] Running...")

    # Try live crypto mcap
    live_crypto = fetch_live_crypto_mcap()
    if live_crypto:
        BASELINES["total_crypto_mcap_usd"] = live_crypto
        print(f"  Live crypto mcap: ${live_crypto:,.0f}")

    now = datetime.now(timezone.utc).isoformat()

    output = {
        "updated": now,
        "baselines": BASELINES,
        "narrative_segments": NARRATIVE_SEGMENTS,
        "saturation_threshold": SATURATION_THRESHOLD,
    }

    # Atomic write
    tmp = OUTPUT.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    os.replace(tmp, OUTPUT)

    # POSIX: ensure gazzetta daemon can read
    try:
        import pwd, grp
        uid = pwd.getpwnam("gazzetta").pw_uid
        gid = grp.getgrnam("gazzetta").gr_gid
        os.chown(str(OUTPUT), uid, gid)
    except (KeyError, OSError):
        pass

    print(f"[fetch_macro_baselines] Wrote {OUTPUT} ({len(json.dumps(output))} bytes)")


if __name__ == "__main__":
    main()
