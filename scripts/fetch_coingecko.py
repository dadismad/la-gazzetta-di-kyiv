#!/usr/bin/env python3
"""
La Gazzetta di Kyiv — Phase 1, Task 1.4
Module: fetch_coingecko.py
Purpose: TIER_2 Data Stream — Crypto market caps, volumes, prices.
Source: CoinGecko API v3 (free tier, bulk endpoint).
"""

import os, sys, json, requests
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("/opt/gazzetta-di-kyiv/data")
OUTPUT_FILE = OUTPUT_DIR / "coingecko_data.json"

# Bulk endpoint: comma-separated IDs in a single call
COINGECKO_IDS = [
    "bitcoin", "ethereum", "solana", "ripple", "cardano",
    "dogecoin", "avalanche-2", "polkadot", "chainlink", "litecoin",
    "bitcoin-cash", "uniswap", "stellar", "monero", "near",
    "aptos", "sui", "arbitrum", "optimism", "polygon-ecosystem-token",
]

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

def fetch_crypto_data() -> dict:
    """Single bulk call to CoinGecko /simple/price with all 20 IDs."""
    ids_csv = ",".join(COINGECKO_IDS)
    url = (
        f"https://api.coingecko.com/api/v3/simple/price"
        f"?ids={ids_csv}"
        f"&vs_currencies=usd"
        f"&include_market_cap=true"
        f"&include_24hr_vol=true"
    )
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 429:
            print("[-] CoinGecko rate limited (429). Skipping cycle.")
            return {}
        if resp.status_code != 200:
            print(f"[-] CoinGecko returned {resp.status_code}")
            return {}
        raw = resp.json()

        data = {}
        for cg_id, metrics in raw.items():
            data[cg_id] = {
                "price_usd": metrics.get("usd", 0),
                "market_cap_usd": metrics.get("usd_market_cap", 0),
                "volume_24h_usd": metrics.get("usd_24h_vol", 0),
            }
        return data
    except Exception as e:
        print(f"[-] CoinGecko error: {e}")
        return {}

def main():
    print("[Task 1.4] Fetching crypto market data (bulk endpoint)...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    crypto_data = fetch_crypto_data()
    if not crypto_data:
        print("[-] Empty crypto payload. Preserving previous state.")
        sys.exit(1)

    output = {
        "metadata": {
            "source": "CoinGecko API v3",
            "extracted_at": datetime.utcnow().isoformat() + "Z",
            "data_fidelity": "TIER_2",
            "assets_tracked": len(crypto_data),
        },
        "assets": crypto_data,
    }

    tmp_path = OUTPUT_FILE.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, OUTPUT_FILE)

    print(f"[+] CoinGecko cache: {OUTPUT_FILE} ({len(crypto_data)} assets)")
    fix_ownership(str(OUTPUT_FILE))

if __name__ == "__main__":
    main()
