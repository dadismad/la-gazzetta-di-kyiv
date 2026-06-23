# Tier 1 Data Integration: CFTC COT + FRED

Added June 22, 2026. Two institutional-grade data sources integrated into the
governor pipeline with a shared graceful-degradation contract.

## Data Sources

### CFTC Commitments of Traders (SODA API)

- **API:** https://api.cftc.gov/api/cot/v1/CommodityFuturesTraders
- **Key:** `CFTC_API_KEY` (free, register at https://api.cftc.gov/)
- **Cadence:** Weekly (Wednesday after 15:30 ET). Governor step: `cftc_data`, timeout=60s, critical=False.
- **Script:** `scripts/fetch_cftc.py`
- **Output:** `data/cftc_positions.json`
- **Contract mapping:** 14 CME futures contracts mapped to 7 of 12 Gazzetta narratives:
  - dollar_decline: DX, 6E, 6J
  - energy_sovereignty: CL, NG
  - deglobalization: GC, SI
  - china_ascent: CNH
  - tech_convergence: NQ
  - commodity_supercycle: SI, HG, ZC, PL
  - rate_cycle: ZN, ZB
- **Narratives without direct CME futures:** space_economy, gene_editing, wealthy_sports, ai_chips, crypto_reserve

### FRED Macro Baseline (St. Louis Fed)

- **API:** https://api.stlouisfed.org/fred/
- **Key:** `FRED_API_KEY` (free, register at https://fred.stlouisfed.org/docs/api/api_key.html)
- **Cadence:** Daily (06:00 UTC). Governor step: `fred_data`, timeout=120s, critical=False.
- **Script:** `scripts/fetch_fred.py`
- **Output:** `data/fred_series.json`
- **27 series across 5 narratives:**
  - rate_cycle: DGS10, DGS2, DFEDTARU, T10Y2Y, T10YIE, DFII10, UNRATE, PAYEMS, ICSA, VIXCLS, NFCI, TEDRATE
  - dollar_decline: DTWEXBGS, DEXUSEU, DEXJPUS
  - china_ascent: DEXCHUS
  - commodity_supercycle: CPIAUCSL, CPILFESL, PPIACO, PCEPI
  - deglobalization: INDPRO, BOPGSTB, GPDI, GDP, GDPC1
  - energy_sovereignty: DCOILWTICO, DHHNGSP
- **Macro regime classifier:** INVERSION (spread < -0.5), TIGHTENING (10Y > 5.5), ACCOMMODATIVE (10Y < 2.5 + unemployment < 4.5), EASING (10Y < 2.5), NEUTRAL, UNKNOWN

## JSON Schemas

### cftc_positions.json

```json
{
  "generated_at": "ISO8601",
  "source": "CFTC Commitments of Traders (SODA API)",
  "api_key_configured": true,
  "contracts_fetched": 13,
  "narratives_populated": 7,
  "positions_by_contract": {
    "DX": {
      "commercial_net": 12500, "commercial_long": 45000, "commercial_short": 32500,
      "speculative_net": -8400, "speculative_long": 12000, "speculative_short": 20400,
      "total_open_interest": 98000, "contract_size": 1000.0,
      "contract_unit": "USD", "report_date": "2026-06-16",
      "contract_name": "Dollar Index", "cftc_code": "098662"
    }
  },
  "positions_by_narrative": {
    "dollar_decline": {
      "contracts": ["DX", "6E", "6J"],
      "total_speculative_net": -15200,
      "total_commercial_net": 28100,
      "total_open_interest_lots": 245000
    }
  },
  "status": "ok"
}
```

### fred_series.json

```json
{
  "generated_at": "ISO8601",
  "source": "FRED (Federal Reserve Economic Data)",
  "api_key_configured": true,
  "series_fetched": 26,
  "series_failed": 1,
  "total_series_defined": 27,
  "macro_regime": "TIGHTENING",
  "series": {
    "DGS10": {
      "label": "10Y Treasury Yield",
      "narrative": "rate_cycle",
      "unit": "%",
      "status": "ok",
      "value": 4.85,
      "date": "2026-06-19",
      "change_30d": 0.12,
      "change_90d": -0.35
    }
  },
  "status": "ok"
}
```

## Graceful Degradation Contract

ALL pipeline data-fetching scripts MUST follow this pattern:

1. **Read API key from environment only:** `CFTC_API_KEY=os.env...Y", "")` — no hardcoded secrets, no file reads.
2. **If key is absent:** Print a single WARNING to stderr, then write a degraded JSON file with `status: "missing_api_key"` and an `error` field with the registration URL. Return exit code 1 so the governor knows it failed, but produce a valid file so downstream scripts can still parse it.
3. **If API fails (timeout, 429, 500):** Retry up to 3 times with exponential backoff. If all fail, write degraded JSON with `status: "error"` and the failure reason. Return exit code 1.
4. **Atomic writes:** Write to `.tmp` then `os.replace()` — never write partial JSON.
5. **Downstream resilience:** `calculate_capital.py` and `build_frontend.py` must handle `status != "ok"` by falling back to existing data (market_prices.json AUM for capital, no CFTC/FRED fields in context). Never crash because a non-critical data file is degraded.

## Three-Point Wiring (Governor Integration)

When adding a new pipeline script, three changes in `governor.py` are required:

1. **Load the env var at module level:**
   ```python
   CFTC_API_KEY=os.env...Y", "")
   FRED_API_KEY=os.env...Y", "")
   ```

2. **Add to STEPS array** (position matters — CFTC/FRED run after market_data, before synthesis):
   ```python
   ("cftc_data", [str(VENV), str(SCRIPTS/"fetch_cftc.py")], 60, False),
   ("fred_data", [str(VENV), str(SCRIPTS/"fetch_fred.py")], 120, False),
   ```

3. **Add to run_cmd() env dict** (the most commonly forgotten):
   ```python
   env={**os.environ, "PYTHONUNBUFFERED":"1",
        "DEEPSEEK_API_KEY": DEEPSEEK_KEY or "",
        "CFTC_API_KEY": CFTC_API_KEY or "",
        "FRED_API_KEY": FRED_API_KEY or "",
        "TELEGRAM_BOT_TOKEN": TELEGRAM_TOKEN or "",
        "TELEGRAM_CHAT_ID": TELEGRAM_CHAT or ""}
   ```

Missing step 3 is the silent failure mode — the script runs but never sees its key, even though the key is loaded in the governor process.

## Deployment Pattern

```
scp scripts/fetch_cftc.py scripts/fetch_fred.py scripts/governor.py gazzetta-prod:/tmp/
ssh gazzetta-prod "sudo mv /tmp/fetch_cftc.py /tmp/fetch_fred.py /tmp/governor.py /opt/gazzetta-di-kyiv/scripts/"
```

Add API keys to VM `.env`:
```
CFTC_API_KEY=<value>
FRED_API_KEY=<value>
```

The systemd timer picks up the new governor.py on the next cycle. No restart needed.
