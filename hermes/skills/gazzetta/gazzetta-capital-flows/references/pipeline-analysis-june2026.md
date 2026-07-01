# Gazzetta Publishing Pipeline — Analysis & Competitor Landscape (June 2026)

Condensed from full pipeline analysis mission. Covers Mike Green methodology, competitor matrix, platform recommendations, and capital flow integration plan.

## Mike Green's Capital Flow Methodology (7 Indicators)

| # | Indicator | Formula / Signal | Data Source | Frequency |
|---|-----------|-----------------|-------------|-----------|
| 1 | **PDR** (Passive Dominance Ratio) | (Passive flows × AUM) / (Active flows × AUM) | ICI weekly + Morningstar | Weekly |
| 2 | **22x Multiplier** | $1 passive inflow → ~$22 market cap appreciation | S&P 500 market cap / passive inflows | Continuous |
| 3 | **√2 Levered ETF Multiplier** | Levered products have 1.41x impact on flows | ETF.com creation/redemption | Daily |
| 4 | **401k Diminishment Signal** | 55+ hiring rate / under-29 hiring rate > 2.0 = warning | BLS age-cohort employment | Monthly |
| 5 | **Flow-Price Divergence** | Price ↑ + money out = distribution ⚠️ | ICI flows vs S&P price | Weekly |
| 6 | **65% Threshold** | Above 65% passive share, vol event mathematically guaranteed | Aggregate passive AUM tracking | Quarterly |
| 7 | **15%/yr Passive Factor** | S&P returns attributable to mechanical flows, not fundamentals | Regression analysis | Annual |

**Green's channels:** Substack "Yes, I Give a Fig" (weekly), Simplify blog (monthly), X @ProfPlum99 (daily). Book "The Greatest Story Ever Sold" (Oct 2026).

## Competitor Landscape

| Competitor | Flow Analysis? | Retail-Native? | Aggressive? | Free? | Trade Ideas? | Telegram? |
|------------|:---:|:---:|:---:|:---:|:---:|:---:|
| ZeroHedge | No | Yes | Yes | Freemium | No | Yes |
| Kobeissi Letter | No | Yes | Medium | Paid | Yes | No |
| Mike Green (Simplify) | **Best** | No | No | Paid | Institutional | No |
| Bianco Research | Excellent | No | No | Paid | No | No |
| Macro Compass (Alf) | Partial | Yes | Medium | Paid | Yes | Yes |
| Game of Trades | No | Yes | **High** | Paid | Yes | Yes |
| Daily Shot | Excellent | No | No | Paid | No | No |
| **Gazzetta di Kyiv** | **Green framework** | **Yes** | **High** | **Free** | **Yes** | **Yes** |

**Gazzetta's edge:** Only competitor combining Green's flow methodology + retail-native + free + trade-specific + multi-platform. Nobody else does structured capital flow claims with 70% confidence intervals.

## Publishing Formats

### THE BRIEF (Telegram) — 500-1000 chars
```
🇮🇷 [EVENT HEADLINE WITH EMOJI]
THE BRIEF: 1-sentence claim
THE DATA: specific flow number
THE TRADE: ticker + position + size + stop
THE EDGE: 22x multiplier or framework reference
70% confidence. Contra (30%): ...
```

### THE DISPATCH (Reddit self-post) — 1500-3000 chars
```
# [Bold claim headline]
## THE SETUP — 2 sentences
## THE DATA — specific flow numbers with sources
## THE FRAMEWORK — Green's model applied
## THE PAYOUT — Entry, Target, Stop, R/R
## WHAT GREEN WOULD SAY
---
Sources: ICI Weekly, Simplify Tier 1 Alpha, CFTC COT
```

### THE CLAIM (X.com thread) — 4-6 tweets, 280 chars each
```
1/ [Claim + $ amount + 70% confidence]
2/ THE DATA: [specific flow number + source]
3/ THE FRAMEWORK: [Green's indicator applied]
4/ THE TRADE: [ticker + direction + stop]
5/ Contra (30%): [bear case]
6/ Follow the flows, not the headlines. /end 🧵
```

## Platform Status (June 2026)

- **Telegram:** ✅ Live. Cron `gazzetta-hourly-narrative-review` runs 06:30/18:30 EET. Delivers to @GazzettadiKyiv.
- **Reddit:** ❌ PAUSED. Cron `gazzetta-devvit-only-pipeline` paused May 28 (model quota). Devvit project at ~/lagazzettadikyiv. Needs: switch model to deepseek-v4-flash + re-enable.
- **X.com:** ⚠️ Outbound only (free tier ~100 req/mo). Script `x_post_from_file.py` exists. Data collection frozen.

## Capital Flow Integration Plan

### Data Sources (all free tier)
1. ICI.org — Weekly mutual fund/ETF flows
2. BLS.gov — Age-cohort employment
3. CFTC COT — Futures positioning
4. ETF.com — Daily ETF AUM and flow data
5. Simplify.us/blog — Green's research notes

### Derived Indicators (compute daily)
1. PDR = passive AUM flow ratio
2. 22x market impact = passive inflows × 22 vs actual market cap change
3. 401k Heat Index = 55+ hiring / under-29 hiring (ratio > 2.0 = yellow)
4. Flow-Price Divergence Score: +1 aligned, -1 divergence (per sector)
5. Levered ETF Amplification = creation/redemption × leverage × √2

### Output Schedule
- Daily flow snapshot → Telegram (08:00 EET)
- Divergence signal → Telegram + X (T/W/Th 14:00 EET)
- THE DISPATCH → Reddit (every 48h)
- X thread → X.com (daily 07:30 EET)
- Weekly flow report → All 3 (Sunday 10:00 EET)
