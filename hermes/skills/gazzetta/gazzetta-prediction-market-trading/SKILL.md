---
name: gazzetta-prediction-market-trading
description: Prediction market dynamics as trading signals — Polymarket/Kalshi odds, betting society mechanics, cross-asset lead analysis. Used by Gazzetta di Kyiv editorial writer for contradiction-first "what the crowd believes vs. reality" framing.
version: 1.0.0
author: Hermes Agent
created_by: agent
---

# Prediction Market Trading — Betting Society Dynamics

Reference: `gazzetta-di-kyiv/docs/PREDICTION_MARKET_STRATEGIES_V1.md` (full research synthesis)
Sibling skill: `gazzetta-event-driven-trading` (retail event strategies)
Polymarket API: loaded from `polymarket` research skill (free, read-only, no auth)

## When to Use

Load this skill when:
- Cross-referencing prediction market odds against asset price movements for Bet&Benefit
- Writing Gazzetta di Kyiv content that uses "what the crowd believes vs. reality" framing
- Detecting market mispricing: when prediction odds diverge from actual asset prices
- Analyzing the "betting society" dimension of an event (gamification of news, information asymmetry)
- Generating editorial claims about what's "priced in" vs. structural reality

## Core Principle: Prediction Markets as Leading Indicators

Prediction market prices ARE probabilities — a 65¢ contract means the crowd believes 65% probability. These probabilities update in real-time as information arrives, often **leading** traditional financial markets by minutes to days.

**The editorial edge:** When Polymarket odds move sharply but the related asset hasn't moved yet → that's a signal. When the asset has moved but odds haven't → that's also a signal (crowd is sleeping on something).

## Key Relationships (for editorial reference)

| Polymarket Event | Traditional Asset | Lag | Correlation |
|-----------------|-------------------|-----|-------------|
| Fed rate decision odds | SOFR futures, 2Y Treasury | 30 min | 0.85 |
| Election outcome odds | Energy/Clean Energy ETFs | 15–30 min | 0.6–0.7 |
| Middle East conflict odds | Crude oil futures (CL) | 1–2 hours | 0.7 |
| Company milestone odds | Stock price (small-caps only) | Hours–days | 0.3–0.5 |
| CPI inflation odds | 5Y breakeven rate | ~4 hours | 0.55 |
| Recession probability odds | VIX, credit spreads | Days | 0.5–0.6 |

## Signal Types (editorial-grade)

### 1. Whale Alert
$50K+ USDC volume on a single contract in <10 minutes. Signals non-public information or large conviction.
**Editorial use:** "Polymarket whale drops $85K on 'Fed holds rates in June' — odds move from 72% to 89% in 8 minutes."

### 2. Odds Velocity Reversal
Sharp spike (e.g., 50¢ → 85¢ in 1 hour) that fades back to 70¢ within 4 hours = sell-the-news event.
**Editorial use:** "Market overreacts to Iran headline — Polymarket conflict odds spike to 88%, then fade to 65% within three hours. Classic knee-jerk premium."

### 3. Cross-Asset Divergence
Polymarket odds moving, asset not yet responding. The prediction market is faster.
**Editorial use:** "Polymarket puts Carney win at 71%, probability up 9 points in 48 hours — but CAD hasn't moved. The FX market is behind the betting market by ~2 days."

### 4. Herd Fade Signal
>75% of volume on one side, price >85¢. The herd is right about direction, wrong about magnitude. Mean reversion is the play.
**Editorial use:** "The crowd is 85% certain the ECB cuts in July. History says: when >75% of Polymarket volume clusters on one side above 85¢, the reversal trade wins 65% of the time."

### 5. OI Divergence
Price rising but open interest falling = trend weakening. Price flat but OI surging = accumulation before a move.
**Editorial use:** "BRICS currency basket odds are flat at 15% — but open interest is up 40% this week. Someone is quietly building a position."

## Betting Society Lens (editorial voice)

Every prediction market story should surface one of these dynamics:

1. **Gamification:** "Traders are now betting on the betting — Polymarket screenshots are content. The line between information and entertainment has collapsed."
2. **Information asymmetry:** "The biggest trades are happening in the last 30 minutes before Polymarket closes, when US East Coast insiders have the freshest information and Asian retail is asleep."
3. **Crowd as contrarian indicator:** "When the betting crowd is unanimous, the structured trade is the other side. The crowd is always right about direction and always wrong about magnitude."
4. **Regulatory arbitrage:** "Polymarket is offshore crypto. Kalshi is CFTC-regulated. PredictIt has an academic exemption. Three different rulebooks, one probability — the spread between them IS the regulatory uncertainty premium."

## Contradiction-First Framing Template

For Gazzetta editorial output, use this structure:

```
WHAT THE CROWD BELIEVES: [Polymarket odds + interpretation]
WHAT'S ACTUALLY HAPPENING: [Structural reality / data / historical edge]
THE BET&BENEFIT: [Asset + direction + narrative-driven % + time horizon]
```

## Polymarket API Quick Reference

Load the `polymarket` research skill for full endpoint docs. Quick access:

- **Search markets:** `https://gamma-api.polymarket.com/markets?tag=geopolitics&active=true&order=volume`
- **Event browse:** `https://gamma-api.polymarket.com/events?active=true&tag=politics,macro`
- **Price history:** `https://clob.polymarket.com/prices-history?market=<conditionId>`
- **Orderbook:** `https://clob.polymarket.com/orderbook?token_id=<clobTokenId>`

No authentication required — all endpoints are read-only and public.

## Integration with Editorial Pipeline

### X.com Macro Intelligence Feed (Companion Signal)
The Gazzetta di Kyiv data pipeline now includes a live X.com intelligence layer (33 accounts, polled via `scripts/xcom_collector.py`). This is the PRIMARY companion signal to Polymarket odds — the X.com macro consensus tells you **what the experts believe**, while Polymarket tells you **what the betting crowd believes**. The gap between these two is the editorial edge.

**Key accounts cross-referenced with prediction markets:**
- `@RaoulGMI`, `@BittelJulien` → crypto/global liquidity cycle vs. Polymarket crypto resolution odds
- `@biancoresearch` → Fed policy, Treasury market structure vs. Polymarket Fed decision odds (0.85 correlation with SOFR)
- `@elerianm` → institutional macro consensus vs. Polymarket recession probability odds
- `@LukeGromen` → dollar architecture thesis vs. Polymarket geopolitical odds (0.7 correlation with crude)
- `@SantiagoAuFund` → contrarian dollar bull (Dollar Milkshake Theory) — gives the OTHER side of the Gazzetta de-dollarization thesis
- `@novogratz` → institutional crypto positioning, Galaxy OTC prediction market trading ($10M day-one trade)

**Workflow for cross-referencing:**
1. Pull `data/xcom_intel/latest.json` for current macro consensus
2. Query Polymarket for active geopolitical/macro contracts
3. Compare: which narrative direction has more conviction — the betting crowd or the expert class?
4. The divergence IS the story. When `@LukeGromen` shows retail at 75% of Treasury demand and Polymarket hasn't moved on USD reserve status odds → that's a signal the betting market is sleeping on a structural shift.

**Data paths:**
- X.com intel: `gazzetta-di-kyiv/data/xcom_intel/latest.json`
- Account map: `gazzetta-di-kyiv/data/xcom_intel/account_map.json`

### For gazzetta-editorial-writer
When generating Bet&Benefit asset-claim pills, cross-reference:
1. Check Polymarket for any active contracts on the story's event type
2. Compare odds direction vs. asset price direction
3. If they agree → "68% of the move is narrative-driven" (the crowd is aligned with the asset)
4. If they diverge → that IS the story — the crowd believes X but the asset says Y

### For cron jobs
Suggested `gazzetta-prediction-market-monitor` (every 60 min, deepseek-v4-flash):
- Track top 5 geopolitical/macro contracts by 24h volume
- Flag any odds velocity >15% in 4 hours
- Cross-reference flagged events against related asset prices
- Output: 3–5 sentence brief for editorial writer consumption

### Data storage
- Raw: `gazzetta-di-kyiv/data/prediction_markets/latest.json`
- Processed: `gazzetta-di-kyiv/data/prediction_markets/signals_latest.json` (velocity, divergence, whale alerts)
