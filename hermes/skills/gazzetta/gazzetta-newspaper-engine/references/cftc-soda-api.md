# CFTC SODA API — Public Endpoint Knowledge Bank

Discovered June 20, 2026. Deployed to production June 22, 2026.

## Key Insight

The CFTC hosts two separate APIs:
- `api.cftc.gov` — requires API key, different structure
- `publicreporting.cftc.gov` — Socrata SODA API, COMPLETELY PUBLIC, no key needed

**Always use the public SODA endpoint.** The key-requiring one is the wrong target.

## Working Endpoint

```
https://publicreporting.cftc.gov/resource/kh3c-gbw2.json
```

**Dataset:** Disaggregated Futures+Options Combined
**Update cadence:** Weekly (Friday release, available Wednesday evening)
**Rate limit:** None for reasonable use (<1000 req/day)
**Authentication:** NONE

## Query Syntax (Socrata SODA)

All queries use URL parameters:

| Parameter | Syntax | Example |
|-----------|--------|---------|
| Filter by commodity | `?commodity_name=GOLD` | Exact match on commodity_name field |
| Order by | `&$order=report_date_as_yyyy_mm_dd+DESC` | Latest first |
| Limit | `&$limit=5` | Rows to return |
| Select fields | `&$select=commodity_name,m_money_positions_long_all` | Subset of columns |
| Group by | `&$group=commodity_name` | Distinct values |
| Where clause | `&$where=commodity_name='GOLD'` | Cannot combine with simple `commodity_name=` filter |

## Critical: simple filter beats $where

The Socrata parser rejects `$where` clauses when combined with `$select`. Use the simple field-name filter instead:

```bash
# WRONG (rejected):
?$select=commodity_name,m_money_positions_long_all&$where=commodity_name='GOLD'&$order=report_date_as_yyyy_mm_dd+DESC&$limit=1

# CORRECT:
?commodity_name=GOLD&$order=report_date_as_yyyy_mm_dd+DESC&$limit=1
```

## Column Reference (Key Fields)

All position values are stored as strings in SODA. Must convert with `int(float(...))`.

| Field | Meaning | Use |
|-------|---------|-----|
| `commodity_name` | CFTC commodity name (e.g., "GOLD", "CRUDE OIL") | Filter key |
| `report_date_as_yyyy_mm_dd` | Report date (calendar_date type) | Freshness check |
| `contract_market_name` | Specific contract (e.g., "GOLD - COMMODITY EXCHANGE INC.") | Disambiguation |
| `m_money_positions_long_all` | Managed Money (specs) long | Speculative bullish conviction |
| `m_money_positions_short_all` | Managed Money (specs) short | Speculative bearish conviction |
| `prod_merc_positions_long` | Producer/Merchant long | Commercial hedging (bullish bias) |
| `prod_merc_positions_short` | Producer/Merchant short | Commercial hedging (bearish bias) |
| `swap_positions_long_all` | Swap dealer long | Intermediary positioning |
| `swap__positions_short_all` | Swap dealer short | Intermediary positioning (note: double underscore) |
| `open_interest_all` | Total open interest | Market size / liquidity |

## Sentiment Derivation

```
if MM net > 0 AND Producer net < 0 → BULLISH (specs long, hedgers short)
if MM net < 0 AND Producer net > 0 → BEARISH (specs short, hedgers long)
if both near zero → NEUTRAL
if both same direction → DIVERGENT (unusual — investigate)
```

## 57 Commodities Available

Full list from distinct query: ALUMINUM, BIODIESEL/HEATING OIL, BUTTER, CANOLA, CHEESE, COAL, COBALT, COCOA, COFFEE, COPPER, CORN, COTTON, CRUDE OIL, DIESEL/CRUDE OIL, DIESEL/HEATING OIL, ELECTRICITY, ETHANOL, ETHYLENE, FEEDER CATTLE, FERTILIZER, FREIGHT RATE, FROZEN CONCENTRATED ORANGE JUICE, FUEL OIL, FUEL OIL/CRUDE OIL, GASOLINE, GOLD, HEATING OIL/CRUDE OIL SPREADS, HEATING OIL-DIESEL-GASOIL, IRON ORE, JET FUEL, JET FUEL/HEATING OIL, LEAN HOGS, LITHIUM, LIVE CATTLE, LUMBER, MILK, NAPHTHA, NAPHTHA/CRUDE OIL, NATURAL GAS, NATURAL GAS LIQUIDS, OATS, PALLADIUM, PALM OIL, PLATINUM, POLLUTION, PORK BELLIES, PROPYLENE, RICE, SCRAP METAL, SILVER, SOYBEAN MEAL, SOYBEAN OIL, SOYBEANS, STEEL, SUGAR, UNLEADED GAS/CRUDE OIL SPREADS, WEATHER, WHEAT

## TFF (Financial Futures) — NOT Available via SODA

The TFF dataset (`dw8z-x6ih`) and Legacy datasets return `"no row or column access to non-tabular tables"`. These are Socrata "chart" or "map" visualizations, not queryable tables. For currencies, rates, and equity index futures positioning, use FRED for macro context + market_reality.py for price data instead.

## Production Script

`scripts/fetch_cftc.py` in the Gazzetta repo. Maps 19 physical commodities to 3 narratives (dollar_decline, energy_sovereignty, commodity_supercycle). Fetches sequentially with 0.3s courtesy pause between calls. 19 calls = ~6 seconds per cycle.

Output: `data/cftc_positions.json` with per-contract and per-narrative aggregation.
