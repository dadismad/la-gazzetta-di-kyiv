# CFTC Public SODA Endpoint — Correct vs Wrong

## The Pitfall

The CFTC has TWO different API domains. They are NOT interchangeable:

| Domain | Type | Key Required | Works? |
|--------|------|-------------|--------|
| `api.cftc.gov` | Legacy API | YES — requires `CFTC_API_KEY` | **NO — returns 401 without key, broken even with key** |
| `publicreporting.cftc.gov` | Socrata SODA API | NO — completely public | **YES — works immediately** |

## Correct Endpoint

```
https://publicreporting.cftc.gov/resource/kh3c-gbw2.json
```

This is the **Disaggregated Futures+Options Combined** dataset. It contains 187,243 rows across all commodities, all time, with 40+ columns per row.

### Query Syntax (Socrata SODA)

```
# Filter by commodity name
?commodity_name=GOLD

# Order and limit
&$order=report_date_as_yyyy_mm_dd+DESC
&$limit=5

# Select specific columns
&$select=commodity_name,report_date_as_yyyy_mm_dd,m_money_positions_long_all

# Group by
&$select=commodity_name&$group=commodity_name
```

### Key Column Names

| Column | Meaning |
|--------|---------|
| `commodity_name` | CFTC commodity name (GOLD, SILVER, CRUDE OIL, NATURAL GAS, COPPER, CORN, etc.) |
| `report_date_as_yyyy_mm_dd` | Report date (weekly, released Fridays) |
| `m_money_positions_long_all` | Managed Money (hedge funds, CTAs) long positions |
| `m_money_positions_short_all` | Managed Money short positions |
| `prod_merc_positions_long` | Producer/Merchant (commercial hedgers) long |
| `prod_merc_positions_short` | Producer/Merchant short |
| `swap_positions_long_all` | Swap Dealer long |
| `swap__positions_short_all` | Swap Dealer short (note double underscore!) |
| `open_interest_all` | Total open interest |
| `contract_market_name` | Full exchange+contract name |

### Values Are Strings

All numeric columns in the SODA API return **strings**, not numbers. Must cast with `int(float(val))` in Python.

### Rate Limits

- 1,000 requests/day without app token
- Our usage: 19 commodities × 1 request each = 19 requests/cycle × 144 cycles/day = 2,736 — **requires app token for full-scale**
- Alternative: batch query without per-commodity filter, parse client-side

### App Token (For Scale)

Register at `https://publicreporting.cftc.gov/signup` for a free app token. Add as `X-App-Token` header. Raises limit to 1,000 requests/hour.

## Other CFTC SODA Datasets (Not Currently Used)

These were discovered but are non-tabular (Socrata "chart" views — cannot be queried via API):

- TFF Combined: `dw8z-x6ih` — financial futures (currencies, rates, equity indices). Would provide rate_cycle and dollar_decline financial positioning.
- Legacy Futures Only: `yjak-hhbj` 
- Legacy Combined: `8jj7-5vf4`

The TFF dataset would be valuable but its SODA endpoint is non-tabular. Alternative: scrape the CFTC website directly or use a paid API for financial futures data.

## Contract Notionals for Dollar-Value Conversion

CFTC data gives contract counts. Multiply by these to get USD exposure:

| Ticker | Contract Size | Approx Notional (June 2026) |
|--------|--------------|---------------------------|
| GC (Gold) | 100 troy oz | $330,000 |
| SI (Silver) | 5,000 troy oz | $165,000 |
| PL (Platinum) | 50 troy oz | $50,000 |
| CL (WTI Crude) | 1,000 barrels | $68,000 |
| NG (Natural Gas) | 10,000 MMBtu | $35,000 |
| HG (Copper) | 25,000 lbs | $115,000 |
| ZC (Corn) | 5,000 bushels | $22,500 |
| ZW (Wheat) | 5,000 bushels | $27,500 |
| ZS (Soybeans) | 5,000 bushels | $52,500 |
| KC (Coffee) | 37,500 lbs | $101,250 |
| CC (Cocoa) | 10 metric tons | $65,000 |
| SB (Sugar) | 112,000 lbs | $21,280 |
