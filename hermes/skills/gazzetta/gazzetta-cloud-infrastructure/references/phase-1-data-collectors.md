# Phase 1 Data Collectors — Verified Schemas (June 2026)

## CFTC Legacy COT (`fetch_cftc_cot.py`)

### Source
- URL: `https://www.cftc.gov/files/dea/history/deacot{year}.zip` (Legacy COT, NOT Disaggregated)
- Inner file: `annual.txt`
- Format: CSV, comma-delimited, quoted fields

### Verified Column Names
```
[0] Market and Exchange Names
[2] As of Date in Form YYYY-MM-DD
[7] Open Interest (All)
[8] Noncommercial Positions-Long (All)
[9] Noncommercial Positions-Short (All)
[11] Commercial Positions-Long (All)
[12] Commercial Positions-Short (All)
```

### Verified Market Names
```
BITCOIN - CHICAGO MERCANTILE EXCHANGE
E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE
GOLD - COMMODITY EXCHANGE INC.
SILVER - COMMODITY EXCHANGE INC.
WTI FINANCIAL CRUDE OIL - NEW YORK MERCANTILE EXCHANGE
UST BOND - CHICAGO BOARD OF TRADE
```

### Pitfalls
- Do NOT use Disaggregated report column names (M_Money_Positions_Long_All) — those are in `fut_disagg_txt_2026.zip`, which lacks Bitcoin and S&P 500
- Do NOT use `Market_and_Market_Type` — actual column is `Market and Exchange Names`
- Do NOT use `Asset_Mgr_Positions_Long_All` — this column doesn't exist in either report
- The `deacot2026.zip` URL returns 404 for Disaggregated; `fut_disagg_txt_2026.zip` has `f_year.txt` not `annual.txt`
- 10-Year Treasury Notes are NOT in Legacy COT; only `UST BOND - CHICAGO BOARD OF TRADE` (30-year)

## FRED Macro (`fetch_fred_data.py`)

### Source
- URL: `https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}`
- No API key required
- Format: CSV, two columns (DATE, VALUE)
- Missing data sentinel: `.` (dot)

### Verified Series
```
WALCL      — Fed Total Assets (millions) — rate_cycle narrative
RRPONTSYD  — Overnight Reverse Repo (billions) — rate_cycle narrative
DGS10      — 10-Year Treasury Yield (percent) — rate_cycle narrative
```

### Pitfalls
- ICI mutual fund flow data is NOT accessible via CSV (ici.org returns 404 for CSV paths)
- The analyst's proposed URL `ici.org/stats/weekly_mutual_fund_flows.csv` returns 404
- FRED data uses `.` for missing values — must skip those rows

## CoinGecko Crypto (`fetch_coingecko.py`)

### Source
- URL: `https://api.coingecko.com/api/v3/simple/price?ids={csv}&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true`
- Free tier: 30 calls/minute
- Batch: comma-separated IDs in single call (up to 250)

### Verified Response Format
```json
{"bitcoin": {"usd": 64231, "usd_market_cap": 1286600000000, "usd_24h_vol": 15639000000}}
```

### Pitfalls
- 429 rate limit — script exits cleanly without crashing pipeline
- Bulk endpoint `/simple/price` accepts comma-separated IDs — always batch, never iterate

## RSS Feed Expansion (June 2026)

### Verified Working Feeds (200 response, valid XML)
```
https://feeds.bloomberg.com/markets/news.rss          — Bloomberg Markets
https://www.ft.com/markets?format=rss                  — FT Markets
https://www.coindesk.com/arc/outboundfeeds/rss/        — CoinDesk (redirect 308→200)
https://www.al-monitor.com/feed                        — Al-Monitor (redirect 301→200)
https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147 — CNBC
```

### Verified Dead Feeds
```
https://www.reuters.com/arc/outboundfeeds/v3/all/?outputType=xml — 404 (Reuters retired RSS 2020)
https://kyivindependent.com/feed/                                — HTML error page (Next.js SSR)
https://www.cnbc.com/id/10001147/device/rss/rss.html             — 403 Forbidden
```

### Ingestion Starvation Diagnosis
- `+0 dupes:70` = feeds working, all items already seen. Add more sources.
- `+0 dupes:0` = feed URL may be dead. Test with curl.
- 5-10 feeds usually saturate a 10-minute cycle.
