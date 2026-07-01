# Phase 1 — Verified External Data Schemas (June 2026)

Every field name, column header, market name, and URL in this document was
verified against live data — not assumed from documentation.

## CFTC Legacy COT

- Archive: `https://www.cftc.gov/files/dea/history/deacot{year}.zip`
- Inner file: `annual.txt`
- Delimiter: comma
- Key columns: `Market and Exchange Names`, `As of Date in Form YYYY-MM-DD`,
  `Open Interest (All)`, `Noncommercial Positions-Long (All)`,
  `Noncommercial Positions-Short (All)`, `Commercial Positions-Long (All)`,
  `Commercial Positions-Short (All)`

### Verified Market Names
| Name | Narrative |
|---|---|
| BITCOIN - CHICAGO MERCANTILE EXCHANGE | crypto_reserve |
| E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE | rate_cycle |
| GOLD - COMMODITY EXCHANGE INC. | commodity_supercycle |
| SILVER - COMMODITY EXCHANGE INC. | commodity_supercycle |
| WTI FINANCIAL CRUDE OIL - NEW YORK MERCANTILE EXCHANGE | commodity_supercycle |
| UST BOND - CHICAGO BOARD OF TRADE | rate_cycle |

## CFTC Disaggregated COT

- Archive: `https://www.cftc.gov/files/dea/history/fut_disagg_txt_{year}.zip`
- Inner file: `f_year.txt`
- Delimiter: comma
- Key columns: `Market_and_Exchange_Names`, `Report_Date_as_YYYY-MM-DD`,
  `Open_Interest_All`, `M_Money_Positions_Long_All`,
  `M_Money_Positions_Short_All`, `Prod_Merc_Positions_Long_All`,
  `Prod_Merc_Positions_Short_All`, `Swap_Positions_Long_All`,
  `Swap__Positions_Short_All` (double underscore is real — CFTC format)

### Verified Market Names (15 physical commodities)
| Name | Narrative |
|---|---|
| GASOLINE RBOB - NEW YORK MERCANTILE EXCHANGE | commodity_supercycle |
| COPPER- #1 - COMMODITY EXCHANGE INC. | commodity_supercycle |
| PALLADIUM - NEW YORK MERCANTILE EXCHANGE | commodity_supercycle |
| PLATINUM - NEW YORK MERCANTILE EXCHANGE | commodity_supercycle |
| CORN - CHICAGO BOARD OF TRADE | commodity_supercycle |
| SOYBEANS - CHICAGO BOARD OF TRADE | commodity_supercycle |
| SOYBEAN MEAL - CHICAGO BOARD OF TRADE | commodity_supercycle |
| WHEAT-SRW - CHICAGO BOARD OF TRADE | commodity_supercycle |
| COFFEE C - ICE FUTURES U.S. | commodity_supercycle |
| SUGAR NO. 11 - ICE FUTURES U.S. | commodity_supercycle |
| COTTON NO. 2 - ICE FUTURES U.S. | commodity_supercycle |
| COCOA - ICE FUTURES U.S. | commodity_supercycle |
| LIVE CATTLE - CHICAGO MERCANTILE EXCHANGE | commodity_supercycle |
| LEAN HOGS - CHICAGO MERCANTILE EXCHANGE | commodity_supercycle |
| FEEDER CATTLE - CHICAGO MERCANTILE EXCHANGE | commodity_supercycle |

## FRED Macro

- Endpoint: `https://fred.stlouisfed.org/graph/fredgraph.csv?id={SERIES_ID}`
- No API key required
- Format: CSV with header `DATE,VALUE`
- Missing data sentinel: `.` (single dot) — skip these rows

### Verified Series
| Series ID | Description | Current Value (June 2026) |
|---|---|---|
| WALCL | Fed Total Assets | ~$6.7T (millions) |
| RRPONTSYD | Overnight Reverse Repo | ~$0.25B |
| DGS10 | 10-Year Treasury Yield | ~4.49% |

## CoinGecko

- Endpoint: `https://api.coingecko.com/api/v3/simple/price`
- Bulk pattern: `?ids=bitcoin,ethereum,solana,...&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true`
- Free tier: 30 calls/minute — ONE call for all 20 assets
- Response: `{"bitcoin": {"usd": ..., "usd_market_cap": ..., "usd_24h_vol": ...}, ...}`

## Verified RSS Feeds (June 2026)

| Feed | URL | Status |
|---|---|---|
| ECB Press | ecb.europa.eu/rss/press.html | 200 |
| IMF News | imf.org/en/News/RSS | 200 |
| FT Markets | ft.com/markets?format=rss | 200 (likely truncated paywall) |
| Bloomberg Markets | feeds.bloomberg.com/markets/news.rss | 200 |
| World Nuclear News | world-nuclear-news.org/feed | 200 |
| OilPrice | oilprice.com/rss/main | 200 |
| SCMP | scmp.com/rss/91/feed | 200 |
| Al-Monitor | al-monitor.com/feed | 301→200 |
| SpaceNews | spacenews.com/feed/ | 200 |
| FierceBiotech | fiercebiotech.com/feed | 200 |
| STAT News | statnews.com/feed/ | 200 |
| MIT Tech Review | technologyreview.com/feed/ | 200 |
| Sportico | sportico.com/feed/ | 200 |
| CoinDesk | coindesk.com/arc/outboundfeeds/rss/ | 308→200 |
| CNBC Markets | search.cnbc.com/rs/search/combinedcms/view.xml?... | 200 |
| Reuters (all) | reuters.com/arc/outboundfeeds/v3/all/?outputType=xml | 404 — DEAD |

## ICI Flow Data

- `https://www.ici.org/stats/weekly_mutual_fund_flows.csv` — 404
- ICI does NOT offer machine-readable CSV downloads
- Skip this data source — use CFTC COT + FRED + CoinGecko instead
