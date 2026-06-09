# Capital Flow Decomposition — Full Top-Down Hierarchy

> Research-backed integration spec for Gazzetta's capital flows pipeline.
> Extends flows.json, flow_nodes.json, and market_regime.json with macro regime context,
> layered decomposition, and product-level security flows.

## Overview

The current pipeline tracks flat directional flows (inflow/outflow, amount, sector, confidence).
This spec adds **5 hierarchical layers** that decompose capital flows from the most macro
(secular regime) down to the most micro (specific product/security financing).

```
                    ┌─────────────────────────┐
                    │  L1: SECULAR / REGIME    │  ← Dominant multi-decade trends
                    │  (20-50 year cycles)     │
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────────┐
                    │  L2: CYCLICAL / LIQUIDITY│  ← Credit cycle, central bank
                    │  (1-10 year cycles)      │    balance sheets, global M2
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────────┐
                    │  L3: ASSET CLASS ROTATION│  ← Equities ↔ Bonds ↔ Commodities
                    │  (months to years)       │    ↔ Crypto ↔ Private ↔ Real Estate
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────────┐
                    │  L4: SECTOR FLOWS        │  ← Tech vs Energy vs Defense
                    │  (weeks to months)       │    vs Healthcare vs Financials
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────────┐
                    │  L5: PRODUCT / SECURITY  │  ← BCI chips, rocket engines,
                    │  FLOWS                   │    quantum computing, biotech
                    │  (daily to weekly)       │    trial financing, drone mfrs
                    └─────────────────────────┘
```

**Two display modes:**
- **Mike Green (top-down):** Layer-to-layer drill-down starting at L1 secular regime
- **Degen (bottom-up):** Start at L5 product flows with the highest heat/velocity, show
  the macro context that explains WHY those flows exist

---

## LAYER 1 — SECULAR / REGIME

### Dominant Multi-Decade Regimes (2024-2029+)

| Regime | Time Horizon | Magnitude | Key Characteristic |
|--------|-------------|-----------|--------------------|
| **Passive Index Dominance** | 2010-2030+ | $15T+ in passive vehicles | Concentration risk, reduced price discovery, auto-buy-the-dip mechanics |
| **AI Capex Supercycle** | 2023-2032 | $1T+ cumulative capex (BofA: $500B/yr by 2027) | Semis, hyperscaler data centers, energy infrastructure |
| **Deglobalization / Reshoring** | 2018-2035+ | $3T+/yr trade reconfiguration | CHIPS Act, IRA, friendshoring, supply chain security premium |
| **Energy Transition** | 2020-2050 | $4T+/yr (IEA NZE scenario) | Grid buildout, electrification, critical minerals demand |
| **Demographic Inversion** | 2020-2080 | 2:1+ dependency ratio in developed markets | Labor scarcity → automation capex, housing demand shift, pension flow structural deficits |
| **Fiscal Dominance** | 2020-? | US debt/GDP >120% | Crowding out, higher neutral rate (R*), persistent inflation risk |

### Key Metrics & Data Sources

#### Passive Index Dominance
| Metric | Source | Freemium | Update | How to Track |
|--------|--------|----------|--------|-------------|
| Global passive AUM / total AUM ratio | BCG Global Asset Management, McKinsey | Paid ($5K-$15K) | Annual | BCG report PDF, extract ratio |
| U.S. passive % equity fund AUM | ICI Factbook | Free | Annual | ici.org/research/statistics/factbook |
| S&P 500 top-10 weight % | Bloomberg `SPX Index WEIGHT` | Bloomberg Terminal | Daily | Free: SlickCharts, S&P Dow Jones Indices |
| ETF as % of daily volume | Bloomberg, NYSE data | Paid | Daily | CBOE market data, NYSE TAQ |
| Vanguard/BlackRock combined % of S&P 500 | SEC 13F filings | Free | Quarterly | web.archive.org, WhaleWisdom, Fintel |
| Passive flow as % of total equity flow | ICI weekly + Bloomberg | Free/Paid | Weekly | Compute: ICI ETF flows / total flows |

#### AI Capex Supercycle
| Metric | Source | Freemium | Update | How to Track |
|--------|--------|----------|--------|-------------|
| Hyperscaler capex (MSFT, GOOGL, AMZN, META) | Earnings reports (10-Q/10-K) | Free | Quarterly | SEC EDGAR, extract "Capital Expenditures" line |
| Total AI-related construction spending | US Census Bureau (VALUE series) | Free | Monthly | Census.gov "Construction Spending" → manufacturing |
| GPU shipments (NVIDIA DC revenue) | NVIDIA 10-K | Free | Quarterly | NVIDIA IR page |
| Data center REIT % of REIT index | BGSIM / S&P / FTSE Russell | Paid | Quarterly | Bloomberg `DATA Index WEIGHT` |
| AI startup VC flows | PitchBook, CB Insights | Paid ($10K+) | Quarterly | PitchBook-NVCA Venture Monitor |
| Stargate/Project-related commitments | Press releases, DoC CHIPS tracker | Free | As announced | CHIPS.gov, company IR |

#### Deglobalization / Reshoring
| Metric | Source | Freemium | Update | How to Track |
|--------|--------|----------|--------|-------------|
| US manufacturing construction spending | US Census Bureau `MANUF` | Free | Monthly | Census.gov, FRED `CONSMNTSAMUCDMEI` |
| CHIPS Act disbursements | CHIPS.gov | Free | Monthly | CHIPS.gov/awards, extract award amounts |
| IRA clean energy manufacturing tax credits | IRS Forms, DOE | Free | Quarterly | DOE's Qualified Advanced Energy Project portal |
| US imports from China as % of total | US Census FT900 | Free | Monthly | Census.gov → Trade Data |
| Nearshoring index (Mexico imports / China imports) | US Census, INEGI | Free | Monthly | US Census FT900, INEGI trade data |
| Supply chain concentration (HHI per sector) | BIS working papers, research | Free | Ad-hoc | BIS.org, academic papers |

#### Energy Transition
| Metric | Source | Freemium | Update | How to Track |
|--------|--------|----------|--------|-------------|
| Global renewable energy investment | IEA WEO, BNEF | Paid ($2K-$20K) | Annual | IEA.org, BNEF (NEO summary free) |
| US clean energy tax credit monetization | IRS, DOE | Free | Quarterly | DOE portal |
| Global EV penetration rate | BNEF, IEA | Free summary | Monthly | IEA Global EV Outlook |
| Critical mineral (copper, lithium) supply gap | CRU Group, S&P Global | Paid | Annual | Free: USGS Mineral Commodity Summaries |

### Integration Spec

#### New JSON fields in flows.json

Add a top-level `layers` object:

```jsonc
{
  // ... existing fields
  
  "layers": {
    "secular": {
      "regime": "passive_dominance",
      "sub_regime": "ai_supercycle",
      "confidence": 88,
      "narrative": "Passive index dominance continues to auto-buy dips, but AI capex supercycle is creating a parallel thematic flow layer that traditional passive vehicles underweight.",
      "regimes": [
        {
          "id": "passive_dominance",
          "name": "Passive Index Dominance",
          "weight": 0.35,
          "direction": "bullish",
          "velocity": "persistent",
          "conviction": "high",
          "metrics": {
            "passive_pct_equity": 0.55,
            "passive_pct_equity_change": 0.02,
            "sp500_top10_weight": 35.2,
            "etf_pct_volume": 0.42,
            "data_source": "ICI Factbook 2025",
            "data_updated": "2025-12-15"
          },
          "leading_indicators": [
            {
              "name": "Passive Flow Ratio",
              "value": 0.68,
              "signal": "regime_confirmed",
              "source": "ICI Weekly + Bloomberg"
            },
            {
              "name": "Concentration Heat",
              "value": 35.2,
              "percentile": 95,
              "signal": "extreme",
              "source": "S&P DJI"
            }
          ],
          "edge_to_layer2": "Passive dominance suppresses vol, encouraging more leverage/credit extension in L2",
          "relevance": 95
        },
        {
          "id": "ai_supercycle",
          "name": "AI Capex Supercycle",
          "weight": 0.30,
          "direction": "bullish",
          "velocity": "accelerating",
          "conviction": "high",
          "metrics": {
            "hyperscaler_capex_quarterly_b": 75.4,
            "ai_gpu_revenue_b": 39.5,
            "data_center_construction_b": 45.0,
            "chips_act_disbursed_b": 33.2,
            "data_source": "10-K filings + CHIPS.gov",
            "data_updated": "2026-03-01"
          },
          "leading_indicators": [
            {
              "name": "Hyperscaler Capex Growth YoY",
              "value": 0.62,
              "signal": "accelerating",
              "source": "Earnings Transcripts"
            },
            {
              "name": "NVIDIA DC Revenue Growth YoY",
              "value": 1.12,
              "signal": "accelerating",
              "source": "NVIDIA 10-K"
            }
          ],
          "edge_to_layer2": "AI capex is funded by debt issuance (L2 corporate bond market), creating tight coupling",
          "relevance": 90
        },
        {
          "id": "reshoring",
          "name": "Deglobalization / Reshoring",
          "weight": 0.20,
          "direction": "bullish",
          "velocity": "moderate",
          "conviction": "medium",
          "metrics": {
            "us_mfg_construction_b": 230.0,
            "china_import_share": 0.137,
            "chips_act_authorized_b": 52.7,
            "data_source": "Census FT900 + CHIPS.gov",
            "data_updated": "2026-04-01"
          },
          "leading_indicators": [
            {
              "name": "US Manufacturing Construction Spend YoY",
              "value": 0.38,
              "signal": "accelerating",
              "source": "Census Bureau"
            },
            {
              "name": "Import Share from China",
              "value": 0.137,
              "percentile": 15,
              "signal": "regime_change",
              "source": "Census FT900"
            }
          ],
          "edge_to_layer2": "Fiscal stimulus from CHIPS/IRA increases supply of Treasuries, impacting L2 bond supply",
          "relevance": 65
        }
      ],
      "dominant_narrative": {
        "headline": "The AI capex supercycle is creating a parallel asset class in semiconductors/ compute that sits outside traditional equity-beta frameworks",
        "thesis": "Traditional passive vehicles (market-cap weighted) underweight this regime. Active money flows into AI are creating a structural bid that the market-regime-normalization trades (small-cap value, international) cannot match until the passive indexing regime peaks.",
        "contradiction": "Every prior tech capex cycle (1999, 2007, 2017) ended in a bust. The difference is this one has explicit government backing (CHIPS, IRA) and is driven by a general-purpose technology with measurable productivity ROI.",
        "key_data_gaps": [
          "Real-time AI startup financing flows (PitchBook lags by 1-3 months)",
          "Supply chain concentration HHI by end market"
        ]
      }
    }
  }
}
```

### Display — Flows Page

**Mike Green mode (top-down):**
- Show L1 as a **regime banner** across the top of the flows page
- Color: gold/orange background if regime-confident, grey if uncertain
- Each active regime gets a pill-badge with weight (35% passive dominance, etc.)
- Hover to see leading indicators and edge_to_layer2 arrows
- `LAYER 1 → LAYER 2` connector shows: "Passive dominance → low vol → more credit" or "AI capex → debt issuance → bond supply"

**Degen mode (bottom-up):**
- L1 appears as a **"macro context" collapsible section** at the bottom of each product flow
- Example: A TSMC Arizona construction flow shows: "🔼 Reshoring regime (+38% YoY mfg construction)"
- Single-line regime label with sparkline indicator of directional change

---

## LAYER 2 — CYCLICAL / LIQUIDITY

### Key Metrics & Data Sources

#### Credit Cycle
| Metric | Source | Freemium | Update | How to Track |
|--------|--------|----------|--------|-------------|
| Fed Balance Sheet ($B) | FRED `WALCL` | Free | Weekly | api.stlouisfed.org WALCL series |
| Fed RRP Facility ($B) | FRED `RRPONTSYD` | Free | Daily | api.stlouisfed.org |
| TGA (Treasury General Account) | FRED `WTREGEN` | Free | Daily | api.stlouisfed.org |
| Bank Lending Standards (SLOOS) | FRED `DRTSCILM` (C&I) | Free | Quarterly | Fed SLOOS data |
| HY Credit Spread (OAS) | FRED `BAMLH0A0HYM2` | Free | Daily | api.stlouisfed.org |
| IG Credit Spread (OAS) | FRED `BAMLC0A0CM` | Free | Daily | api.stlouisfed.org |
| US High Yield Default Rate | FRED `DRTSCILM`, Moody's | Free/Paid | Monthly | Moody's default report |
| Loan Growth (C&I Loans) | FRED `BUSLOANS` | Free | Weekly | api.stlouisfed.org |
| Commercial Paper Outstanding | FRED `CP` | Free | Weekly | api.stlouisfed.org |
| Leveraged Loan Index price | S&P/LSTA LLI (Bloomberg) | Paid | Daily | WSJ Markets (free summary) |
| Bank reserves total | FRED `TOTRESNS` | Free | Weekly | api.stlouisfed.org |

#### Global Liquidity
| Metric | Source | Freemium | Update | How to Track |
|--------|--------|----------|--------|-------------|
| Global M2 (GDP-weighted) | CrossAsset, Bloomberg | Paid | Monthly | Bloomberg `GLM2GDP Index` |
| US M2 (% YoY) | FRED `M2SL` | Free | Monthly | api.stlouisfed.org |
| Eurozone M3 (% YoY) | ECB SDW | Free | Monthly | sdw.ecb.europa.eu |
| China Total Social Financing | People's Bank of China | Free | Monthly | PBOC.gov.cn |
| Japan M3 (% YoY) | BOJ | Free | Monthly | BOJ stats |
| Global Central Bank Balance Sheet | Bloomberg `CENBALANCE Index` | Paid | Weekly | Bloomberg Terminal |
| Central Bank Swap Lines outstanding | NY Fed | Free | Weekly | newyorkfed.org |
| EM FX reserves (China, etc.) | IMF IFS | Free | Monthly | IMF Data, PBOC |

#### Fed Trajectory
| Metric | Source | Freemium | Update | How to Track |
|--------|--------|----------|--------|-------------|
| Fed Funds Rate | FRED `DFEDTARU` | Free | Daily | api.stlouisfed.org |
| QT Pace (monthly cap) | NY Fed | Free | Monthly | newyorkfed.org/markets |
| SEP Dot Plot | Fed | Free | Quarterly | federalreserve.gov |
| Fed Funds Futures | CME FedWatch | Free | Daily | cmegroup.com/market-data |
| OIS 1Y forward | Bloomberg `OIS` | Paid | Daily | Bloomberg terminal |
| Balance sheet runoff (monthly) | FRED `WALCL` diff | Free | Monthly | Compute WALCL change |

### Integration Spec

New `layers.cyclical` section in flows.json:

```jsonc
{
  "layers": {
    "cyclical": {
      "credit_cycle": {
        "phase": "tightening_ending",
        "phase_label": "Late cycle — credit tightening peaking",
        "phase_confidence": 82,
        "core_metrics": {
          "fed_balance_sheet_b": 7200,
          "rrp_b": 85,
          "tga_b": 650,
          "hy_oas": 3.45,
          "ig_oas": 1.12,
          "bank_loan_standards_net_pct_tightening": 15.7,
          "ci_loan_growth_yoy_pct": 2.1,
          "default_rate_hy_pct": 2.3,
          "fed_funds_rate": 4.25,
          "qt_monthly_cap_b": 25
        },
        "signal": {
          "overall": "neutral_bearish",
          "score": 38,
          "components": {
            "liquidity": {
              "score": 42,
              "label": "Moderate — RRP drain nearly complete, TGA normalizing",
              "leading": "rrp_b < 100, tga_b normalizing"
            },
            "credit": {
              "score": 35,
              "label": "Tightening — bank lending standards still restrictive",
              "leading": "sloos_net_pct > 10"
            },
            "rates": {
              "score": 38,
              "label": "Restrictive — real rates still positive across all tenors",
              "leading": "fed_funds > cpi_core"
            }
          }
        },
        "global_liquidity": {
          "us_m2_yoy_pct": 2.8,
          "ecb_m3_yoy_pct": 3.2,
          "china_tsf_yoy_pct": 8.5,
          "japan_m3_yoy_pct": 1.8,
          "global_m2_yoy_pct": 3.4,
          "global_central_bank_balance_sheets_b": 32000,
          "source": "FRED, ECB, PBOC, BOJ, Bloomberg",
          "updated": "2026-06-01"
        },
        "flow_source_mapping": {
          "description": "L2 liquidity conditions determine the overall capital available for L3-L5 flows",
          "current_regime": "Liquidity is recovering from 2022-2023 tightening peak but remains restrictive. Global M2 positive but decelerating. Corporate bond supply heavy as companies pre-refinance before election uncertainty.",
          "edge_to_layer3": "If credit conditions ease further (SLOOS below 10), capex-heavy sectors (AI, reshoring) see accelerated L3 rotation from bonds to equities",
          "data_gaps": [
            "Real-time corporate bond issuance by purpose (capex vs refi vs buyback)",
            "Private credit market total AUM changes (Preqin/PitchBook data lags)"
          ]
        }
      }
    }
  }
}
```

### Display — Flows Page

**Mike Green mode (top-down):**
- **2-row regime strip** under L1 banner
- Row 1: Liquidity dashboard — Fed Balance Sheet (numeric + direction arrow), RRP, TGA, Global M2 YoY sparklines
- Row 2: Credit dashboard — HY OAS (color bar: green <3, yellow 3-5, red >5), Bank Lending Standards bar, Corp Bond Issuance running total
- Each metric: show value + 13-week change direction
- "Credit Cycle Phase" badge: Early / Mid / Late / Recession (with confidence %)
- Click any metric → opens FRED chart overlay

**Degen mode (bottom-up):**
- Per-product flow gets a **"macro overlay" tag**: 
  - "🔴 HY OAS 345bp — credit tightening active" (for rocket engine supplier debt financing)
  - "🟢 Global M2 +3.4% — liquidity supportive" (for AI startup VC flow)
- **"What's driving this"** microcard on each L5 flow shows relevant L2 metrics
- Center column: L2 aggregate "Liquidity Score" as a percent gauge

---

## LAYER 3 — ASSET CLASS ROTATION

### Key Metrics & Data Sources

| From | To | Key Metric | Source | Freemium | Update |
|------|----|-----------|--------|----------|--------|
| Equities | Fixed Income | Corp Bond / Equity fund flow ratio | ICI, EPFR | Free | Weekly |
| Equities | Commodities | DJCI vs SPX relative flow | EPFR, Bloomberg | Paid | Weekly |
| Equities | Crypto | GBTC premium/discount + ETHE flows | CoinMetrics, Bloomberg | Free | Daily |
| Active Funds | Passive ETFs | Passive as % of total equity flows | ICI, Morningstar | Free | Weekly |
| Public Markets | Private Markets | Corp Bond Buyback / PE Buyout ratio | Dealogic, S&P | Paid | Quarterly |
| Domestic | International | US ex-US equity flow ratio | EPFR | Free/Paid | Weekly |
| Growth | Value | Growth ETF / Value ETF flow ratio | Bloomberg CF-FLOW | Paid | Weekly |
| Large Cap | Small Cap | S&P 600 / S&P 500 ETF flow ratio | Bloomberg | Paid | Weekly |
| US | EM | EM equity fund flows (weekly) | EPFR, IIF | Free | Weekly |

### Programmatic Tracking

```python
# ICI data already fetched → compute rotation ratios weekly
def compute_rotation_signals(ici_data):
    """Compute asset class rotation indicators from ICI weekly data."""
    e = ici_data['data']['combined_flows']['weekly'][-1]
    return {
        'stock_bond_ratio': e['equity']['total'] / abs(e['bond']['total']) if e['bond']['total'] else None,
        'domestic_international_ratio': e['equity']['domestic'] / abs(e['equity']['world']) if e['equity']['world'] else None,
        'growth_value_ratio': ...,  # From sector-level detail
        'rotation_direction': 'risk_on' if e['equity']['total'] > 0 and e['bond']['total'] < 0 else 'risk_off',
        'rotation_speed': ...
    }
```

### Integration Spec

```jsonc
{
  "layers": {
    "rotation": {
      "current_regime": {
        "overall": "risk_on_uneven",
        "label": "Risk-on but concentrated — all-time highs driven by AI/tech megacaps, broad market participation weak",
        "score": 62,
        "divergence_score": 78,  // High = narrow leadership
        "rotations": [
          {
            "id": "equities_to_bonds",
            "from": "equities",
            "to": "bonds",
            "net_weekly_b": -4.2,
            "direction": "equities_preferred",
            "ratio": 7.3,
            "3m_change_pct": -15,
            "signal": "no_rotation",
            "source": "ICI Weekly"
          },
          {
            "id": "active_to_passive",
            "from": "active_mutual_funds",
            "to": "passive_etfs",
            "net_weekly_b": 12.8,
            "direction": "passive_preferred",
            "ratio": 2.1,
            "3m_change_pct": 8,
            "signal": "rotation_active",
            "source": "ICI + Morningstar"
          },
          {
            "id": "public_to_private",
            "from": "public_equities",
            "to": "private_markets",
            "net_quarterly_b": 45.0,
            "direction": "private_preferred",
            "ratio": 0.15,
            "signal": "rotation_active",
            "source": "Preqin, Dealogic",
            "note": "Private market flows are quarterly, not weekly. Estimated from PE/VC fund closes."
          },
          {
            "id": "us_to_international",
            "from": "us_equities",
            "to": "international_equities",
            "net_weekly_b": -2.1,
            "direction": "us_preferred",
            "ratio": 0.85,
            "3m_change_pct": 12,
            "signal": "rotation_starting",
            "source": "EPFR"
          },
          {
            "id": "equities_to_commodities",
            "from": "equities",
            "to": "commodities",
            "net_weekly_b": 3.8,
            "direction": "commodities_preferred",
            "ratio": 0.3,
            "3m_change_pct": 45,
            "signal": "rotation_active",
            "source": "EPFR",
            "driver": "Geopolitical risk premium + energy transition metals demand"
          },
          {
            "id": "growth_to_value",
            "from": "growth",
            "to": "value",
            "net_weekly_b": -25.3,
            "direction": "growth_preferred",
            "ratio": 0.3,
            "signal": "no_rotation",
            "source": "Bloomberg CF-FLOW"
          },
          {
            "id": "traditional_to_crypto",
            "from": "traditional_markets",
            "to": "crypto",
            "net_weekly_b": -0.8,
            "direction": "traditional_preferred",
            "ratio": 0.02,
            "signal": "rotation_stalled",
            "source": "CoinMetrics, Glassnode"
          }
        ],
        "source_destination_map": [
          {
            "id": "private_credit",
            "source": ["banks", "institutional_insurance"],
            "intermediary": ["private_credit_funds", "bdcs"],
            "destination": ["middle_market_lending", "direct_lending"],
            "quarterly_b": 65.0,
            "trend": "accelerating",
            "note": "Banks retreating from C&I → private credit fills gap at 150-300bp premium"
          },
          {
            "id": "buyback_to_passive",
            "source": ["corporate_treasuries"],
            "intermediary": ["share_buybacks"],
            "destination": ["index_etfs", "passive_flow"],
            "quarterly_b": 280.0,
            "trend": "secular",
            "note": "Corporate buybacks → rise in stock → rebalancing sells into index funds → buys the whole market symmetrically"
          }
        ]
      }
    }
  }
}
```

### Display — Flows Page

**Mike Green mode (top-down):**
- **Chord diagram** or **Sankey flow** below L1/L2 showing capital moving between asset classes
- Source columns (left): Equities, Bonds, Commodities, Crypto, Private Markets, Real Estate
- Destination columns (right): the same, with ribbon widths proportional to flow magnitude
- Color: green ribbons = net inflow, red = outflow, amber = mixed
- Right panel: "Dominant Rotation" card — e.g., "Active→Passive: $12.8B/week (2.1x)"
- **Divergence score badge**: "Narrow — 78/100" when growth/value ratio extreme

**Degen mode (bottom-up):**
- Per-product flow shows its place in the rotation:
  - "This Neuralink Series E funding is part of the broader Private←Public rotation (+$45B/q)"
- **"Rotation Chain"** widget: From → Through → To
  - Example: "Corp Buybacks → Passive Index Funds → NVDA (7th rebalance weight)"
- For pure plays: show the rotation ratio and where it ranks (e.g., "AI is the #1 destination of Growth rotation")

---

## LAYER 4 — SECTOR FLOWS

### Key Metrics & Data Sources

| Sector | Metric | Source | Freemium | Update |
|--------|--------|--------|----------|--------|
| Tech (AI/Semis) | SMH, SOXX, IYW ETF flows | Bloomberg, EPFR | Free/Paid | Daily |
| Tech | NVDA, AVGO, AMD institutional positioning | SEC 13F | Free | Quarterly |
| Energy | XLE, OIH ETF flows | Bloomberg, EPFR | Free/Paid | Daily |
| Energy | E&P sector capex plans | Earnings calls transcripts | Free | Quarterly |
| Defense | ITA, PPA ETF flows + DoD budget | Bloomberg, USASpending.gov | Free | Daily/Annual |
| Healthcare | XLV, IBB, XBI ETF flows | Bloomberg, EPFR | Free/Paid | Daily |
| Healthcare | Biotech IPO/SPAC pipeline | BioPharma Dive, PitchBook | Free/Paid | Weekly |
| Financials | XLF, KRE ETF flows | Bloomberg, EPFR | Free/Paid | Daily |
| Financials | Bank deposit flows (FDIC) | FDIC H8 | Free | Weekly |
| Real Estate | XLRE, IYR ETF flows | Bloomberg, EPFR | Free/Paid | Daily |
| Industrials | XLI ETF flows | Bloomberg, EPFR | Free/Paid | Daily |
| Materials | XLB ETF flows | Bloomberg, EPFR | Free/Paid | Daily |
| Consumer Disc | XLY ETF flows | Bloomberg, EPFR | Free/Paid | Daily |
| Consumer Staples | XLP ETF flows | Bloomberg, EPFR | Free/Paid | Daily |
| Utilities | XLU ETF flows | Bloomberg, EPFR | Free/Paid | Daily |
| Dividends | SCHD, VYM, SDY flows | Bloomberg | Free/Paid | Daily |

### Programmatic Tracking

Two approaches:

**Approach 1 — ETF flow proxy (Python, daily):**
```python
# fetch_sector_flows.py
# Scrape Bloomberg EPFR sector ETF flow data (or SEC filings)
# Uses the sector-ticker mapping above to compute:
# - Net sector flow ($B/week)
# - Sector flow vs market cap weight (overweight/underweight)
# - 4-week accumulation/distribution signal

import json
from datetime import datetime
from urllib.request import urlopen

SECTOR_ETFS = {
    'tech': ['SMH', 'SOXX', 'IYW', 'QQQ'],
    'defense': ['ITA', 'PPA'],
    'energy': ['XLE', 'OIH'],
    'healthcare': ['XLV', 'IBB', 'XBI'],
    'financials': ['XLF', 'KRE'],
    'real_estate': ['XLRE', 'IYR'],
    'industrials': ['XLI'],
    'materials': ['XLB'],
    'consumer_disc': ['XLY'],
    'consumer_staples': ['XLP'],
    'utilities': ['XLU'],
    'semiconductors': ['SMH', 'SOXX'],
    'ai': ['BOTZ', 'AIQ', 'ROBT', 'QQQ'],
}

def compute_sector_positioning(cot_data, ici_data):
    """Compute sector-level accumulation/distribution from COT + ICI."""
    # ...
```

**Approach 2 — COT sector positioning (weekly, already fetched):**
Leverage the existing COT data — the disaggregated report already has sector-level commodity positioning that can be mapped to equity sectors through cross-asset correlation.

**Approach 3 — Reuters/EPFR API (paid, best signal):**
EPFR Global offers sector-level equity fund flow data via API. Free tier includes limited weekly data.

### Integration Spec

Extend existing `sector_summary` in flows.json:

```jsonc
{
  // existing structure
  "sector_summary": {
    "equities": { /* existing */ },
    "tech": { /* existing */ },
    // ADD:
    "sectors_detailed": {
      "timestamp": "2026-06-07T13:26:00Z",
      "confidence": 85,
      "positions": [
        {
          "id": "sector_tech",
          "name": "Technology (AI / Semis)",
          "etf_proxies": ["QQQ", "SMH", "SOXX", "IYW"],
          "weekly_net_flow_b": 8.2,
          "direction": "accumulating",
          "pace": "accelerating",
          "conviction": "high",
          "total_aum_tracked_b": 4560,
          "relative_weight_vs_sp500": {
            "sector_weight_pct": 32.5,
            "neutral_weight_pct": 28.0,
            "status": "overweight",
            "gap_pct": 4.5
          },
          "positioning_data": {
            "cftc_cot_signal": "net_long",
            "cftc_net_pct_oi": 23.4,
            "institutional_sentiment": "bullish",
            "retail_sentiment": "very_bullish",
            "divergence": "signals_aligned"
          },
          "flow_velocity": {
            "weekly": 8.2,
            "monthly": 32.1,
            "quarterly": 95.4,
            "yoy": 280.0
          },
          "dominant_flow_type": "passive_dominant",
          "source": "ICI + Bloomberg ETF flows + COT"
        },
        {
          "id": "sector_semis",
          "name": "Semiconductors (narrow tech)",
          "etf_proxies": ["SMH", "SOXX"],
          "weekly_net_flow_b": 5.4,
          "direction": "accumulating",
          "pace": "accelerating",
          "conviction": "high",
          "total_aum_tracked_b": 850,
          "relative_weight_vs_sp500": {
            "sector_weight_pct": 8.2,
            "neutral_weight_pct": 4.5,
            "status": "overweight",
            "gap_pct": 3.7
          },
          "dominant_flow_type": "active_rotation",
          "source": "Bloomberg + EPFR"
        },
        {
          "id": "sector_energy",
          "name": "Energy (Oil & Gas)",
          "etf_proxies": ["XLE", "OIH"],
          "weekly_net_flow_b": -1.2,
          "direction": "distributing",
          "pace": "moderate",
          "conviction": "medium",
          "total_aum_tracked_b": 320,
          "relative_weight_vs_sp500": {
            "sector_weight_pct": 3.8,
            "neutral_weight_pct": 4.2,
            "status": "underweight",
            "gap_pct": -0.4
          },
          "positioning_data": {
            "cftc_cot_signal": "net_short",
            "cftc_net_pct_oi": -12.1,
            "institutional_sentiment": "bearish",
            "retail_sentiment": "neutral",
            "divergence": "institutions_vs_retail"
          },
          "flow_velocity": { "weekly": -1.2, "monthly": -4.8, "quarterly": -12.5, "yoy": -35.0 },
          "dominant_flow_type": "active_distribution",
          "source": "ICI + Bloomberg ETF flows + COT"
        },
        {
          "id": "sector_defense",
          "name": "Defense / Aerospace",
          "etf_proxies": ["ITA", "PPA"],
          "weekly_net_flow_b": 2.8,
          "direction": "accumulating",
          "pace": "accelerating",
          "conviction": "high",
          "total_aum_tracked_b": 210,
          "relative_weight_vs_sp500": {
            "sector_weight_pct": 2.1,
            "neutral_weight_pct": 1.5,
            "status": "overweight",
            "gap_pct": 0.6
          },
          "dominant_flow_type": "geopolitical_premium",
          "source": "EPFR + DoD budget tracker"
        },
        {
          "id": "sector_healthcare",
          "name": "Healthcare / Biotech",
          "etf_proxies": ["XLV", "XBI", "IBB"],
          "weekly_net_flow_b": 0.8,
          "direction": "accumulating",
          "pace": "moderate",
          "conviction": "medium",
          "total_aum_tracked_b": 980,
          "dominant_flow_type": "defensive_rotation",
          "source": "ICI + EPFR"
        }
      ],
      "accumulation_distribution_ratio": 1.8,
      "breadth_score": 42,
      "breadth_label": "narrow"
    }
  }
}
```

### Display — Flows Page

**Mike Green mode (top-down):**
- **Sector grid** (already partially implemented) with enhancement:
  - Each sector card shows: ETF icon, weekly net flow ($B), direction arrow, relative weight badge (overweight/underweight), COT signal
  - Card color intensity scales with conviction (faded green = low, bright green = accumulating, red = distributing)
  - **Breadth score gauge**: 0-100, where >70 = broad participation, <30 = narrow (only tech)
  - **Sector rotation map**: Heat map of all 11 S&P sectors with weekly flow ranking (#1 = most inflow)
  - Click sector → expand to show sub-sector (tech → semis, software, hardware)

**Degen mode (bottom-up):**
- Each L5 product flow shows its parent sector and the sector-level context:
  - "This is the #1 sector by weekly flows (+$8.2B tech)"
- **"Sector context bar"**: miniature version of the full sector grid, highlighting the relevant sector
- **"Flow ranking"**: "SMH is the #1 ETF for inflows this week, +$5.4B"
- Per-flow: "Sector relative weight: Tech is 4.5% overweight vs S&P — extreme"

---

## LAYER 5 — PRODUCT / SECURITY FLOWS

This is the deepest, most granular layer. It tracks capital flows into **specific products,
technologies, and securities** — the actual projects, companies, and instruments that
represent the frontier of capital deployment.

### 5A — Brain-Computer Interfaces (BCI)

#### Key Entities & Flow Sources

| Company | Latest Round | Amount Raised | Lead Investors | Status | Data Source |
|---------|-------------|---------------|----------------|--------|-------------|
| Neuralink | Series E (2025) | ~$680M total | Founders Fund, Vy Capital, Google Ventures | Human trials approved (FDA 2023) | SEC filings, PitchBook, press releases |
| Synchron | Series C (2024) | ~$145M total | Bezos Expeditions, ARCH Venture, Gates Frontier | 6 human patients implanted | Synchron.com, clinicaltrials.gov |
| Precision Neuroscience | Series C (2025) | ~$155M total | Baird Capital, Ducera | 1,000+ microelectrode arrays in human brain | PrecisionNeuro.com |
| Blackrock Neurotech | Series A (2024) | ~$50M | Various | Oldest BCI company, 29 patients implanted | BlackrockNeurotech.com |
| Motif Neurotech | Seed (2025) | ~$20M | | Incubated at Rice | MotifNeuro.com |
| Paradromics | Series A (2024) | ~$63M | Westcott LLC, Broadscale | NMP (Next-Gen BCI) program | Paradromics.com |

#### How to Track Programmatically

```python
# fetch_bci_flows.py — Track BCI company financing + clinical trial progress

SOURCES = [
    # 1. SEC EDGAR: Form D (Regulation D Exempt Offerings)
    #    https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=neuralink
    # 2. Crunchbase/PitchBook API (paid, $10K+/yr)
    # 3. ClinicalTrials.gov API (free, for BCI trial registrations)
    # 4. FDA device approvals (free, fda.gov/medical-devices)
    # 5. Press releases (Google News RSS for each company)
]

def track_bci_flows():
    # SEC EDGAR search for each company's funding rounds
    # ClinicalTrials.gov → count BCI-related trials
    # Aggregate: total $B flowing into BCI per quarter/year
    return {
        "sector": "bci",
        "total_raised_b": 1.1,
        "companies_tracked": 15,
        "quarterly_b": 0.15,
        "trend": "accelerating",
        "key_events": [
            {"company": "Neuralink", "event": "Series E close", "amount_b": 0.28, "date": "2025-11-15", "investors": ["Founders Fund", "Vy Capital"]},
            {"company": "Synchron", "event": "5th patient implanted", "date": "2026-03-01"},
        ]
    }
```

### 5B — Advanced Semiconductors

#### Key Flow Map

| Project | Company | Location | Total Commitment | Financing Source | Status | Source |
|---------|---------|----------|-----------------|-----------------|--------|--------|
| Fab 21 Phase 1-4 | TSMC | Phoenix, AZ | $100B+ | CHIPS Act ($6.6B grant + $5B loan), TSMC operating cash, equipment financing | Phase 1 operational (4nm), Phase 2 2026 (3nm), Phase 3-4 2028+ (2nm) | CHIPS.gov, TSMC IR |
| Fab 62 (Intel Ohio) | Intel | New Albany, OH | ~$100B total | CHIPS Act ($8.5B grant + $11B loan), Intel cash flow, equipment leases | Construction underway, 2027-2028 production | CHIPS.gov, Intel IR |
| Samsung Taylor | Samsung | Taylor, TX | ~$44B | CHIPS Act ($6.4B grant), Samsung corp cash | Delayed, production expected 2027 | CHIPS.gov, Samsung IR |
| Micron Boise | Micron | Boise, ID | $15B | CHIPS Act ($6.1B grant), Micron cash | Construction underway | CHIPS.gov |
| SK Hynix West Lafayette | SK Hynix | West Lafayette, IN | $3.87B | CHIPS Act ($450M grant), SK Hynix | R&D facility | CHIPS.gov |
| Texas Instruments | TI | Sherman, TX | $30B | TI cash, CHIPS Act ($1.6B grant) | Under construction | TI IR |
| GlobalFoundries Malta | GF | Malta, NY | $11.6B | CHIPS Act ($1.5B grant), GF | Expansion underway | CHIPS.gov |

#### Metrics to Track

| Metric | Source | Freemium | Update |
|--------|--------|----------|--------|
| CHIPS Act total disbursed | CHIPS.gov/awards | Free | Monthly |
| CHIPS Act by company (grant + loan) | CHIPS.gov | Free | Monthly |
| Equipment CAPEX (ASML orders) | ASML 10-K, IR | Free | Quarterly |
| Semicon equipment billings (SEMI) | SEMI.org | Free/Paid | Monthly |
| Fab construction progress (% complete) | State/local permits, press | Free | As announced |
| ASML EUV tool orders (number x $350M) | ASML IR | Free | Quarterly |
| Semiconductor equipment leasing volume | DLL, banks | Paid | Quarterly |
| SOX/SMH ETF flows (proxies for semis positioning) | Bloomberg, EPFR | Free/Paid | Daily |

#### How to Track

```python
# fetch_semiconductor_flows.py

# 1. CHIPS Act awards: scrape CHIPS.gov/awards
import requests, re, json
from pathlib import Path

CHIPS_AWARDS_URL = "https://www.chips.gov/awards"
DATA_DIR = Path("/path/to/data/market_data")

def fetch_chips_awards():
    """Scrape CHIPS Act awards page for latest disbursements."""
    resp = requests.get(CHIPS_AWARDS_URL)
    # Parse table of awards: company, amount, type (grant/loan), date, status
    # Output: list of award dicts
    return awards

# 2. ASML equipment orders (from earnings transcript)
# ASML reports net system bookings quarterly
# Extract: EUV count, DUV count, EUV ASP (~€350M)

# 3. SEMI equipment billings (North America)
# SEMI posts monthly: https://www.semi.org/en/market-data/equipment-statistics
def fetch_semi_billings():
    """Download SEMI monthly billings data."""
    pass
```

### 5C — Rocket Engines / Space

#### Key Flow Map

| Project | Company | Engine | Total Contract Value | Customer | Financing | Source |
|---------|---------|--------|---------------------|----------|-----------|--------|
| Starship / Super Heavy | SpaceX | Raptor 3 | >$4B (NASA HLS) | NASA HLS, DoD launch | SpaceX private funding ($350M 2024 raise) | NASA.gov, SEC Form D |
| New Glenn | Blue Origin | BE-4 (x7) | >$3.4B (NSSL Phase 3 Lane 2) | DoD NSSL, Amazon Kuiper | Bezos-funded (~$2B/yr), ULA engine sales | DoD.gov |
| Neutron | Rocket Lab | Rutherford (Archimedes) | ~$500M (DoD) | DoD HASTE launch contract | Public (RKLB) + $50M DoD | RKLB IR, DoD |
| Vulcan Centaur | ULA | BE-4 (x2) | >$5B (NSSL Phase 3) | DoD NSSL, Amazon Kuiper | Joint venture Boeing/Lockheed | DoD.gov, ULA |
| Terran R | Relativity Space | Aeon R | ~$60M | NASA/DoD launch contracts | $1.3B total raised, public via SPAC | Relativity IR |
| Ariane 6 | ArianeGroup | Vulcain 2.1 | >€4B (EU institutional) | EU, ESA | ESA/government funding | ESA.int |
| Miranda | Stoke Space | Full-flow staged combustion | ~$20M (NASA Tipping Point) | NASA, DoD | $175M total raised | NASA.gov |

#### Supply Chain Financing

| Component | Key Suppliers | Financing Mechanism | Scale | Source |
|-----------|---------------|-------------------|-------|--------|
| Raptor nozzles | Calspan, ATI | Supplier PO financing | $50M+/yr | SpaceX 10-K (as Black OpCo) |
| BE-4 turbopumps | Honeywell, Barber-Nichols | ULA advanced payments | $100M+/yr | ULA contracts |
| Rutherford pumps | Rocket Lab in-house | Internal R&D | $20M/yr | RKLB 10-K |
| Carbon composites | Toray, Hexcel | Long-term supply agreements | $200M+/yr across space industry | Hexcel/Toray IR |
| Avionics | L3Harris, Honeywell | Defense contracts | $500M/yr govt procurement | DoD contracts |

#### How to Track

```python
# fetch_space_flows.py

# 1. NASA/DoD contract awards (USASpending.gov API)
# 2. SEC filings for public companies (RKLB, LUNR, etc.)
# 3. SpaceNews / Payload newsletters for private company updates
# 4. FAA launch licenses (launch frequency proxy)
# 5. Private company SPAC/IPO pipeline

SPACE_SOURCES = {
    'gov_contracts': 'https://api.usaspending.gov/api/v2/search/spending_by_category/',
    'launch_manifest': 'https://spaceflightnow.com/launch-schedule/',
    'spacex_valuation': 'https://www.forbes.com/companies/spacex/',
}
```

### 5D — Quantum Computing

#### Key Flow Map

| Company | Approach | Total Raised | Government Grants | Recent Round | Source |
|---------|---------|-------------|-------------------|-------------|--------|
| IBM | Superconducting | $30B+ (corporate R&D + acquisitions) | DARPA, DOE, EU | In-house | IBM IR |
| Google (Sycamore/Willow) | Superconducting | $10B+ (Alphabet R&D) | DARPA, DOE | In-house | Alphabet 10-K |
| IonQ | Trapped Ion | $1.1B (post-SPAC merger) | DARPA, AFRL | Public (IONQ) | IONQ IR |
| Rigetti | Superconducting | $500M (post-SPAC) | DARPA, DOE, NASA | Public (RGTI) | RGTI IR |
| D-Wave | Quantum Annealing | $400M (public via SPAC) | NASA, LCN, DARPA | Public (QBTS) | QBTS IR |
| Quantinuum (Honeywell) | Trapped Ion | $1.5B (Honeywell spin-out) | DARPA, DOE, UK Gov | $300M equity round | Quantinuum IR |
| PsiQuantum | Photonic | $1.5B | DARPA ($), $1B Australian gov | Series D | PsiQ.com |
| Alice & Bob | Cat Qubit | $100M | French gov, Bpifrance | Series B | AliceBob.com |
| Xanadu | Photonic | $250M | Canadian gov, DARPA | Public bond/private | Xanadu.ca |
| Quandela | Photonic | $120M | French gov, EU Quantum Flagship | Series B | Quandela.com |

#### Programmatic Tracking

```python
# fetch_quantum_flows.py

# Sources:
# 1. DARPA Quantum Benchmarking program contracts (DARPA.gov/procurement)
# 2. DOE/National QIS Research Center appropriations (DOE.gov)
# 3. Public company 10-Ks (IONQ, RGTI, QBTS)
# 4. PitchBook/Crunchbase quantum VC tracking
# 5. EU Quantum Flagship funding (€1B+ total)

QUANTUM_TRACKERS = {
    'darpa_contracts': 'https://www.darpa.mil/program/quantum-benchmarking',
    'doe_qis': 'https://www.energy.gov/science/quantum-information-science',
    'nsf_quantum': 'https://new.nsf.gov/funding/opportunities/quantum-leap',
}
```

### 5E — Biotech / Pharma (Gene Therapy, mRNA)

#### Key Flow Map

| Category | Flow Type | Volume ($B/yr) | Source |
|----------|-----------|---------------|--------|
| mRNA platform R&D | Corporate + VC | $15-20B | BioPharma Dive |
| Gene therapy trials | VC + pharma M&A | $10-15B | Alliance for Regenerative Medicine |
| ADC (antibody-drug conjugate) | M&A + licensing | $25-30B | EvaluatePharma |
| GLP-1/GIP (obesity) | Revenue + R&D | $50B+ (revenue) | Company 10-Ks (NVO, LLY) |
| CRISPR/Cas9 | VC + licensing | $5-8B | Vertex/CRISPR Tx IR |
| Cell therapy (CAR-T) | Revenue + trials | $8-12B | Legend/J&J, BMS 10-Ks |
| Radiopharmaceuticals | M&A + development | $8-10B | Novartis, Lantheus |

### 5F — Defense Tech

#### Key Flow Map

| Category | Key Companies | Flow Source | Volume | Track Via |
|----------|--------------|-------------|-------|-----------|
| Drones/UAS | Anduril, Skydio, Shield AI, AeroVironment | DoD budget, VC | $20B+/yr | USASpending.gov, Anduril SEC filing |
| Hypersonics | RTX, Boeing, Lockheed, Dynetics | DoD RDT&E budget | $15B/yr (FY26 request) | DoD budget docs, USASpending |
| Autonomous Systems | Anduril (Lattice), Palantir (AIP), Shield AI (Hivemind) | DoD + VC | $10B+/yr | SEC filings, DoD contracts |
| Space Defense | SpaceX (Starshield), Rocket Lab, Sierra Space | DoD/NASA | $25B+/yr | DoD Space Force budget |
| EW/Cyber | L3Harris, BAE, Palantir | DoD + intel budgets | $15B+/yr | National Defense Strategy docs |
| Directed Energy | Lockheed, Raytheon, nLight | DoD S&T | $2-3B/yr | DoD S&T budget line items |

#### Anduril/Palmer Luckey Ecosystem VC Flows

| Company | Latest Raise | Total | Investors | Product |
|---------|-------------|-------|-----------|---------|
| Anduril | Series F $1.5B (2024) | $4.5B+ total | a16z, Founders Fund, Baillie Gifford | Lattice, Fury, Ghost, Roadrunner, Dive-LD |
| Palmer Luckey personal ventures | $2B (2025 funding vehicle) | $2B | Own capital | Defense tech ecosystem |
| Shield AI | Series F $300M+ (2024) | $1.2B+ | Disruptive, Point72, Riot | Hivemind AI pilot |
| Skydio | Series E $170M (2023) | $700M+ | a16z, IVP, Linse Capital | Autonomous drones |
| Saronic | Series B $175M (2025) | $250M+ | a16z, Caffeinated Capital | Autonomous surface vessels |
| Rebellion Defense | Series C $150M+ (2023) | $250M+ | L Catterton, 1984 Ventures | AI for defense intel |
| Aalyria (Google spinout) | $300M+ in contracts | — | Govt contracts | Optical mesh networking for DoD |

#### DoD Budget Tracker (Key Line Items)

```python
# fetch_dod_flows.py — Track key DoD budget line items

DOD_BUDGET_PROGRAMS = {
    'hypersonics': {
        'FY26_request_b': 15.0,
        'programs': [
            'LRHW (Dark Eagle) — Army hypersonic missile',
            'C-HGB — Common hypersonic glide body',
            'HAWC — Hypersonic air-breathing weapon concept',
        ]
    },
    'drones_uas': {
        'FY26_request_b': 8.5,
        'programs': ['Replicator initiative', 'CCA (Collaborative Combat Aircraft)', 'MUM-T'],
    },
    'space_force': {
        'FY26_request_b': 30.0,
        'programs': ['NSSL Phase 3', 'Starshield procurement', 'GPS III', 'SBIRS/NGP'],
    }
}

def fetch_dod_budget():
    """Scrape DoD budget press releases and USASpending contract awards."""
    # Source: https://comptroller.defense.gov/Budget-Materials/
    pass
```

### Integration Spec

New `layers.product` section in flows.json:

```jsonc
{
  "layers": {
    "product": {
      "timestamp": "2026-06-07T13:26:00Z",
      "categories": [
        {
          "id": "product_bci",
          "name": "Brain-Computer Interfaces",
          "total_flow_b": 1.1,
          "quarterly_b": 0.15,
          "pace": "accelerating",
          "confidence": 80,
          "direction": "inflow",
          "heat_score": 65,
          "companies": [
            {
              "id": "neuralink",
              "name": "Neuralink",
              "total_raised_b": 0.68,
              "latest_round": "Series E",
              "latest_round_b": 0.28,
              "latest_date": "2025-11-15",
              "lead_investors": ["Founders Fund", "Vy Capital", "Google Ventures"],
              "valuation_b": 5.0,
              "status": "active_human_trials",
              "flow_source_type": ["venture_capital", "corporate"],
              "confidence": 85,
              "positioning": "accumulating"
            },
            {
              "id": "synchron",
              "name": "Synchron",
              "total_raised_b": 0.145,
              "latest_round_b": 0.05,
              "latest_date": "2024-06-01",
              "lead_investors": ["Bezos Expeditions", "ARCH Venture", "Gates Frontier"],
              "status": "human_implanted",
              "flow_source_type": ["venture_capital", "family_office"]
            }
          ],
          "data_sources": ["SEC EDGAR", "ClinicalTrials.gov", "Crunchbase", "PitchBook"],
          "macro_context": "BCI is a ~L4 Healthcare sector flow that correlates with AI compute democratization",
          "derived_signal": {
            "overall": "early_stage_accumulation",
            "flag": "watch",
            "explanation": "Total BCI VC is ~$1.1B cumulative — insignificant vs semis ($100B+) but the trend is accelerating (4x year-on-year)"
          }
        },
        {
          "id": "product_semiconductors",
          "name": "Advanced Semiconductors",
          "total_flow_b": 320.0,
          "quarterly_b": 35.0,
          "pace": "accelerating",
          "confidence": 90,
          "direction": "inflow",
          "heat_score": 95,
          "projects": [
            {
              "id": "tsmc_arizona",
              "name": "TSMC Arizona (Fab 21)",
              "total_commitment_b": 100.0,
              "chips_act_grant_b": 6.6,
              "chips_act_loan_b": 5.0,
              "equipment_financing_b": 25.0,
              "phase_1_status": "operational_4nm",
              "phase_2_expected": "2026 (3nm)",
              "phase_3_expected": "2028 (2nm)",
              "equipment_suppliers": ["ASML", "Applied Materials", "Lam Research", "KLA"],
              "job_commitment": 6000,
              "financing_notes": "$100B = private investment in TSMC's largest single-site commitment; CHIPS Act $11.6B is <12%",
              "confidence": 95,
              "flow_sources": ["government", "corporate", "equipment_financing"]
            },
            {
              "id": "intel_ohio",
              "name": "Intel Ohio (Fab 62)",
              "total_commitment_b": 100.0,
              "chips_act_grant_b": 8.5,
              "chips_act_loan_b": 11.0,
              "equipment_financing_b": 20.0,
              "phase_1_status": "construction",
              "phase_1_expected": "2027-2028",
              "equipment_suppliers": ["ASML", "Applied Materials"],
              "confidence": 85,
              "flow_sources": ["government", "corporate", "equipment_financing"]
            },
            {
              "id": "samsung_taylor",
              "name": "Samsung Taylor",
              "total_commitment_b": 44.0,
              "chips_act_grant_b": 6.4,
              "status": "delayed",
              "confidence": 75,
              "flow_sources": ["government", "corporate"]
            }
          ],
          "data_sources": ["CHIPS.gov", "company IR", "SEMI", "ASML IR"],
          "macro_context": "The biggest capex project in US history. Semis construction is the physical manifestation of the AI supercycle + reshoring regime.",
          "supply_chain_financing": {
            "equipment_leasing_b": 35.0,
            "supplier_po_financing_b": 8.0,
            "total_supply_chain_flow_b": 320.0,
            "key_equipment_cycles": {
              "asml_euv_orders": 42,
              "asml_euv_backlog_b": 38.0,
              "lam_research_deposits_b": 3.5
            }
          },
          "derived_signal": {
            "overall": "structural_mega_flow",
            "flag": "conviction_long",
            "explanation": "Semiconductor fab capex is the single largest flow in the Gazzetta system. The $100B+ TSMC Arizona and $100B Intel Ohio commitments alone exceed the total AUM of most hedge funds. This is a structural multi-year flow, not a tactical position.",
            "edge_to_flows_page": "Should appear as its own flow card: '$320B long-term flow into semis fab construction' with projected quarterly pace and CHIPS Act milestone tracker"
          }
        },
        {
          "id": "product_rocket_engines",
          "name": "Rocket Engines / Space Launch Infrastructure",
          "total_flow_b": 45.0,
          "quarterly_b": 3.2,
          "pace": "accelerating",
          "confidence": 85,
          "direction": "inflow",
          "heat_score": 88,
          "systems": [
            {
              "id": "raptor",
              "name": "SpaceX Raptor 3",
              "engine_count": 3,
              "per_engine_cost_m": 0.25,
              "annual_production_rate": 1000,
              "total_contract_value_b": 4.0,
              "customer": "NASA HLS, DoD",
              "flow_sources": ["government", "corporate"]
            },
            {
              "id": "be4",
              "name": "Blue Origin BE-4",
              "engine_count": 2,
              "per_engine_cost_m": 8.0,
              "total_contract_value_b": 3.4,
              "customer": "DoD NSSL, ULA (engine customer)",
              "flow_sources": ["government", "corporate", "family_office"]
            },
            {
              "id": "rutherford",
              "name": "Rocket Lab Rutherford / Archimedes",
              "total_contract_value_b": 0.5,
              "customer": "DoD HASTE",
              "flow_sources": ["government", "public_market"]
            }
          ],
          "launch_contracts_b": {
            "nssl_phase3": 5.6,
            "starshield_procurement": 2.0,
            "science_missions": 1.5,
            "commercial_kuiper": 3.0
          },
          "macro_context": "Rocket engine supply chains are the bottleneck for the entire space launch market. Raptor demand is pulling through a ~$200M/yr supply chain financing requirement for nozzles, turbopumps, and composites.",
          "derived_signal": {
            "overall": "structural_flow",
            "flag": "bullish_space",
            "explanation": "Space launch contracts are shifting from cost-plus to fixed-price (competition-driven). This is creating a financing gap that private capital (Bezos, SpaceX raises, SPAC pipeline) is filling."
          }
        },
        {
          "id": "product_quantum",
          "name": "Quantum Computing",
          "total_flow_b": 8.5,
          "quarterly_b": 0.8,
          "pace": "accelerating",
          "confidence": 80,
          "direction": "inflow",
          "heat_score": 72,
          "companies": [
            {
              "id": "ionq",
              "name": "IonQ",
              "total_raised_b": 1.1,
              "market_cap_b": 3.5,
              "govt_contracts_b": 0.15,
              "govt_contract_sources": ["DARPA", "AFRL"],
              "flow_sources": ["public_market", "government"]
            },
            {
              "id": "rigetti",
              "name": "Rigetti",
              "total_raised_b": 0.5,
              "market_cap_b": 1.2,
              "govt_contracts_b": 0.08,
              "govt_contract_sources": ["DARPA", "DOE", "NASA"],
              "flow_sources": ["public_market", "government"]
            },
            {
              "id": "psiquantum",
              "name": "PsiQuantum",
              "total_raised_b": 1.5,
              "largest_grant_b": 1.0,
              "grant_source": "Australian Government",
              "flow_sources": ["government", "venture_capital"]
            },
            {
              "id": "quantinuum",
              "name": "Quantinuum (Honeywell)",
              "total_raised_b": 1.5,
              "latest_round_b": 0.3,
              "investors": ["Honeywell", "JPMorgan", "Mitsui"],
              "flow_sources": ["corporate", "venture_capital"]
            }
          ],
          "govt_funding_tracker": {
            "darpa_quantum_benchmarking_b": 0.5,
            "doe_qis_b": 0.8,
            "nsf_quantum_leap_b": 0.3,
            "eu_quantum_flagship_b": 1.2,
            "total_annual_govt_b": 2.8
          },
          "derived_signal": {
            "overall": "nascent_accumulation",
            "flag": "watch_early",
            "explanation": "Quantum is where AI was in 2017 — massive government investment ($2.8B/yr globally), private capital beginning to flow, but no killer app yet. IonQ and Quantinuum lead in trapped-ion approach."
          }
        },
        {
          "id": "product_biotech",
          "name": "Biotech / Pharma Frontier",
          "total_flow_b": 85.0,
          "quarterly_b": 22.0,
          "pace": "moderate",
          "confidence": 82,
          "direction": "inflow",
          "heat_score": 70,
          "sub_sectors": [
            {
              "id": "gene_therapy",
              "name": "Gene Therapy",
              "annual_b": 12.0,
              "top_players": ["Vertex", "Sarepta", "Bluebird Bio", "Pfizer (hemophilia)"],
              "trial_count": 2000,
              "m_a_volume_b": 15.0,
              "flow_sources": ["venture_capital", "pharma_m_and_a", "public_market"]
            },
            {
              "id": "mrna",
              "name": "mRNA Platforms",
              "annual_b": 18.0,
              "top_players": ["Moderna", "BioNTech", "CureVac", "Arcturus"],
              "pipeline_count": 50,
              "m_a_volume_b": 5.0,
              "flow_sources": ["venture_capital", "government", "public_market"]
            },
            {
              "id": "glp1",
              "name": "GLP-1 / Obesity",
              "annual_revenue_b": 50.0,
              "top_players": ["Novo Nordisk (NVO)", "Eli Lilly (LLY)"],
              "r_and_d_b": 8.0,
              "capex_b": 12.0,
              "flow_sources": ["corporate_revenue", "public_market"]
            }
          ],
          "derived_signal": {
            "overall": "accelerating_growth",
            "flag": "bullish",
            "explanation": "Gene therapy is approaching an inflection point (FDA approvals accelerating), GLP-1 is already a mega-blockbuster (LLY +$400B market cap added), and mRNA is expanding beyond COVID into RSV, flu, cancer."
          }
        },
        {
          "id": "product_defense",
          "name": "Defense Tech",
          "total_flow_b": 100.0,
          "quarterly_b": 25.0,
          "pace": "accelerating",
          "confidence": 92,
          "direction": "inflow",
          "heat_score": 92,
          "categories": [
            {
              "id": "defense_autonomous",
              "name": "Autonomous Systems / Drones",
              "annual_b": 20.0,
              "top_companies": {
                "anduril": {
                  "total_raised_b": 4.5,
                  "latest_round": "Series F $1.5B (2024)",
                  "investors": ["a16z", "Founders Fund", "Baillie Gifford"],
                  "valuation_b": 14.0,
                  "products": ["Lattice", "Fury (autonomous fighter)", "Ghost (UAS)", "Roadrunner", "Dive-LD"],
                  "contracts_b": 3.0
                },
                "shield_ai": {
                  "total_raised_b": 1.2,
                  "latest_round_b": 0.3,
                  "investors": ["Disruptive", "Point72", "Riot Ventures"],
                  "products": ["Hivemind (AI pilot)", "V-BAT drone"],
                  "contracts_b": 1.0
                }
              },
              "vc_ecosystem_b": 8.0,
              "flow_sources": ["venture_capital", "government", "corporate"]
            },
            {
              "id": "defense_hypersonics",
              "name": "Hypersonics",
              "annual_b": 15.0,
              "programs": {
                "LRHW_Dark_Eagle": 3.5,
                "C_HGB": 2.0,
                "HAWC": 1.5,
                "ARRW": 1.0
              },
              "flow_sources": ["government_rdte"]
            },
            {
              "id": "defense_ew",
              "name": "Electronic Warfare / Cyber",
              "annual_b": 15.0,
              "flow_sources": ["government"]
            }
          ],
          "macro_context": "Defense tech VC flows are the fastest-growing category of VC globally. Anduril's $14B valuation on $3B in contracts implies a massive discount to traditional primes (LMT: 2.5x P/S). The Replicator initiative alone is $8B+ for autonomous systems.",
          "derived_signal": {
            "overall": "structural_mega_flow",
            "flag": "conviction_long",
            "explanation": "Defense tech is the intersection of AI capex supercycle + deglobalization regime. The shift from cost-plus to fixed-price procurement creates demand for agile, VC-funded startups. Anduril's $1.5B Series F is the largest single defense tech raise ever.",
            "edge_to_flows_page": "Should generate a dedicated flow card: '$4.5B VC flow into defense tech ecosystem' with contract value ($3B Anduril) and Replicator initiative tracker"
          }
        }
      ],
      "aggregate": {
        "total_product_flows_tracked_b": 559.6,
        "total_categories": 6,
        "highest_heat": "semiconductors (95), defense_tech (92), rocket_engines (88)",
        "largest_dollar": "semiconductors ($320B), defense_tech ($100B), biotech ($85B)",
        "fastest_growth": "bci (4x YoY), quantum (3x YoY), defense_tech (2.5x YoY)",
        "data_quality_grade": "B+",
        "data_gaps": [
          "Real-time venture flow tracking (PitchBook/Crunchbase lag 1-3 months)",
          "Private company valuations post-raise (secondary market data needed)",
          "Supply chain financing breakdowns (PO financing, equipment leasing terms)"
        ]
      }
    }
  }
}
```

### Display — Flows Page

**Mike Green mode (top-down):**
- **"Deep Flow Decomposition" section** at the bottom of the page, after L1-L4
- Each product category is an expandable card with:
  - Heat score badge (0-100, color scale)
  - Total flow tracked ($B)
  - Key companies as pill badges
  - Click → expand to show company-level detail with confidence, investors, status
- **"Derived Signal" card** for each product: conviction_long / watch / nascent_accumulation with explanation
- **"Macro Context" connector**: shows which L1 regime and L4 sector this product flow belongs to
- Sankey diagram showing: L1 Regime → L4 Sector → L5 Product → $B amount

**Degen mode (bottom-up):**
- **Product flows ARE the default view** — show L5 first, because these are the most actionable
- **"Flow Heat Map"**: Sort all 6 product categories by heat_score descending
- Each product flow has:
  - Company logos/icons (if available)
  - Amount raised + latest round
  - Speed dial: "🔥 accelerating" / "→ steady" / "🪦 slowing"
  - **"Macro overlay"**: small pill showing L1 context (e.g., "Reshoring regime" for TSMC)
  - **"Sector context"**: X% of L4 sector flow (e.g., "Semis = 85% of Tech sector flows")
- **"Get the trade"**: For each L5 product, a degen-level thesis on how to trade it:
  - "Long SMH / short XLE = semis capex rotation play"
  - "Long Anduril pre-IPO via secondary market (3.5x revenue multiple vs LMT at 2.5x)"
  - "Long IONQ: DARPA contract + trapped-ion moat, but watch dilution"
- **"Flow chain"**: For each L5 flow, show the capital journey:
  ```
  US Treasury (L2 QE) → CHIPS Act Grant (L2 govt) → TSMC Arizona (L5 product)
           ↘ Corporate Bond Issuance (L2 credit) → ASML EUV Orders (supply chain)
  ```

---

## Pipeline Integration

### New Scripts to Create

```
scripts/
  fetch_sector_flows.py      ← L4 sector-level ETF flow aggregation (daily)
  fetch_bci_flows.py         ← L5 BCI company financing tracker (weekly)
  fetch_semiconductor_flows.py ← L5 CHIPS Act + fab construction tracker (weekly)
  fetch_space_flows.py       ← L5 space/rocket engine financing (weekly)
  fetch_quantum_flows.py     ← L5 quantum VC + govt grant tracker (weekly)
  fetch_biotech_flows.py     ← L5 biotech trial financing + M&A (weekly)
  fetch_defense_flows.py     ← L5 defense tech VC + DoD budget (weekly)
  generate_flow_layers.py    ← NEW MASTER SCRIPT: produces the layers section in flows.json
```

### Pipeline (cron) Changes

Add these to the cron schedule (see `docs/architecture/cron-registry.md`):

| Job | Script | Frequency | Priority |
|-----|--------|-----------|----------|
| L1-L2 regime updater | `generate_flow_layers.py` | 60m | P1 |
| L3 rotation tracker | Compute from existing ICI data + new sector flow data | 60m | P1 |
| L4 sector flows | `fetch_sector_flows.py` | Daily | P1 |
| L5 product flows | 6 x fetch scripts | Weekly | P2 |
| L5 master aggregator | `generate_flow_layers.py` (consolidates all L5 into flows.json) | 60m | P1 |

### flows.json Schema Changes

Add the new `layers` top-level key:

```jsonc
{
  // Existing fields: generated_at, generated_by, next_update, update_frequency,
  //                  summary, aggregate_confidence, aggregate_confidence_label,
  //                  aggregate_direction, total_flows_tracked, lead_insight,
  //                  sector_summary, flows
  // NEW:
  "layers": {
    "secular": { /* L1: regime array, dominant_narrative */ },
    "cyclical": { /* L2: credit_cycle, global_liquidity, flow_source_mapping */ },
    "rotation": { /* L3: current_regime, rotations[], source_destination_map[] */ },
    "sectors_detailed": { /* L4: positions[], breadth_score, accumulation_distribution_ratio */ },
    "product": { /* L5: categories[], aggregate */ }
  }
}
```

### flow_nodes.json Schema Changes

Add `regime_context` to both nodes and edges:

```jsonc
{
  // Existing fields
  "nodes": [
    {
      // Existing fields
      "regime_context": {
        "primary_regime": "ai_supercycle",
        "secular_weight": 0.30,
        "credit_cycle_phase": "tightening_ending"
      }
    }
  ],
  "edges": [
    {
      // Existing fields
      "layer": 4,  // Which layer this belongs to (1-5)
      "parent_flow_id": "flow_n21_chips_act_tsmc",
      "regime_context": {
        "driving_regime": "reshoring",
        "rotations_active": ["active_to_passive", "public_to_private"]
      }
    }
  ]
}
```

### market_regime.json Schema Changes

Extend the existing market regime file:

```jsonc
{
  // Existing: generated_at, source, indicators[3]
  // ADD:
  "secular_regime": {
    "dominant": "passive_dominance",
    "regimes": [
      { "id": "passive_dominance", "weight": 0.35, "direction": "bullish" },
      { "id": "ai_supercycle", "weight": 0.30, "direction": "bullish" },
      { "id": "reshoring", "weight": 0.20, "direction": "bullish" }
    ]
  },
  "credit_cycle": {
    "phase": "tightening_ending",
    "phase_confidence": 82,
    "fed_balance_sheet_b": 7200,
    "hy_oas": 3.45,
    "global_m2_yoy_pct": 3.4
  },
  "rotation": {
    "stock_bond_ratio": 7.3,
    "active_passive_ratio": 2.1,
    "domestic_international_ratio": 0.85,
    "breadth_score": 42,
    "divergence_score": 78
  },
  "product_flows": {
    "total_tracked_b": 559.6,
    "highest_heat_category": "semiconductors",
    "top_flows": [
      { "id": "tsmc_arizona", "name": "TSMC Arizona", "amount_b": 100.0, "heat": 95 },
      { "id": "anduril", "name": "Anduril Defense Tech", "amount_b": 4.5, "heat": 92 }
    ]
  }
}
```

---

## Display Summary

### Mike Green Mode (Top-Down)

```
┌──────────────────────────────────────────────────────────────┐
│  L1 REGIME BANNER   [Passive Dominance 35% | AI 30% | Reshore 20%]  │
│  Narrative: The AI capex supercycle is creating...                  │
├──────────────────────────────────────────────────────────────┤
│  L2 LIQUIDITY DASHBOARD   Fed: $7.2T ↓  RRP: $85B ↓  TGA: $650B │
│  CREDIT CYCLE: [TIGHTENING ENDING]  HY OAS: 345bp ████░░    │
│  Global M2: +3.4% YoY                                          │
├──────────────────────────────────────────────────────────────┤
│  L3 ROTATION SANKEY     Equities → Bonds $4.2B  Active→Passive $12.8B  │
│  Divergence Score: 78 (Narrow)  Breadth: 42/100               │
├──────────────────────────────────────────────────────────────┤
│  L4 SECTOR GRID                                           │
│  [TECH +$8.2B ████████]  [SEMIS +$5.4B ██████]  [ENERGY -$1.2B ░░]  │
│  [DEFENSE +$2.8B ████]   [HEALTHCARE +$0.8B ░]               │
├──────────────────────────────────────────────────────────────┤
│  L5 PRODUCT DECOMPOSITION                                    │
│  [🔥 Semis $320B]  [🔥 Defense Tech $100B]  [🔥 Rocket Engines $45B]  │
│  [👁 Biotech $85B]  [🔬 Quantum $8.5B]  [🧠 BCI $1.1B]       │
│  Click to expand → company-level detail + derived signal     │
└──────────────────────────────────────────────────────────────┘
```

### Degen Mode (Bottom-Up)

```
┌──────────────────────────────────────────────────────────────┐
│  🔥 FLOW HEAT MAP — Sorted by heat score                     │
│                                                            │
│  1. SEMIS $320B  [🔥🔥🔥🔥🔥 95]  ← Reshoring + AI Capex         │
│     → TSMC AZ $100B · Intel OH $100B · Samsung TX $44B      │
│     → CHIPS Act disbursed: $33.2B                           │
│     → TRADE: Long SMH, Short XLE (capex rotation)           │
│                                                            │
│  2. DEFENSE TECH $100B  [🔥🔥🔥🔥 92]  ← Deglobalization        │
│     → Anduril $4.5B (Series F $1.5B @ $14B val)            │
│     → Shield AI $1.2B · Skydio $700M                        │
│     → TRADE: Anduril pre-IPO secondary at 3.5x rev          │
│                                                            │
│  3. ROCKET ENGINES $45B  [🔥🔥🔥🔥 88]  ← AI Compute Demand     │
│     → Raptor: $4B · BE-4: $3.4B · Archimedes: $0.5B         │
│     → NSSL Phase 3 contracts: $5.6B                         │
│     → MACRO: Every Raptor engine needs ~$200K supply chain  │
│                                                            │
│  4. BIOTECH $85B  [🔥🔥🔥 70]  ← Demographics Inversion        │
│  5. QUANTUM $8.5B  [🔥🔥 72]  ← AI Supercycle spillover      │
│  6. BCI $1.1B  [🔥 65]  ← AI + Healthcare convergence       │
│                                                            │
│  ──────────────────────────────────────────────────        │
│  L2 MACRO CONTEXT:                                          │
│  Credit Cycle: Tightening Ending = supportive for          │
│  capex-heavy flows (semis, defense)                        │
│  Global M2: +3.4% = moderate liquidity                     │
└──────────────────────────────────────────────────────────────┘
```

---

## Data Quality & Limitations

| Limitation | Impact | Mitigation |
|------------|--------|-----------|
| L1 regime confidence is subjective | Regime weights are ±10pp uncertain | Display confidence score, allow manual override by editor |
| L5 venture flows lag 1-3 months | Real-time picture incomplete | Supplement with press releases + SEC Form D filings (same-day) |
| L3 private market data is quarterly | Rotation signal delays | Use public market flows as leading indicator (weekly) |
| Supply chain financing is opaque | Equipment leasing terms not public | Estimate from ASML/Lam Research backlog + financing arm disclosures |
| BCI/Quantum are young sectors | Total flows are small vs semis | Display both absolute ($B) and relative (YoY growth rate) |

## Implementation Priority

1. **P0 (immediate):** L2 cyclical/liquidity section — all data already available from FRED/ICI/COT
2. **P0:** L4 sector detail with relative weight — ETF proxy mapping is straightforward
3. **P1 (next sprint):** L3 rotation section — compute from existing ICI + new ETF sector flows
4. **P1:** L5 semiconductor flows — CHIPS Act tracker is free machine-readable data
5. **P1:** L5 defense tech flows — Anduril/Shield AI via press + SEC Form D
6. **P2 (backlog):** L1 secular regime narrative — requires editorial judgment; build scoring framework first
7. **P2:** L5 BCI, quantum, biotech — niche, small absolute flows, lower priority for initial launch
8. **P2:** Flow nodes regime_context integration — requires schema update + flow-nodes.html update

---

*Document generated by Hermes Agent — Capital Flow Decomposition Research.*
*Integrates with flows.json, flow_nodes.json, market_regime.json, and flows.html / flow-nodes.html.*
