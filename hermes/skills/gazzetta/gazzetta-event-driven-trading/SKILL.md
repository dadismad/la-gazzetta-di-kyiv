---
name: gazzetta-event-driven-trading
description: Event-driven trading strategies for retail traders — economic releases, news/catalyst plays, prediction market signals. Used by Gazzetta di Kyiv editorial writer to add Bet&Benefit trading context to stories.
version: 1.0.0
author: Hermes Agent
created_by: agent
---

# Event-Driven Trading — Retail Strategies for Bet&Benefit

Reference: `gazzetta-di-kyiv/docs/RETAIL_EVENT_DRIVEN_STRATEGIES_V1.md` (full 462-line playbook)
Supplementary: `gazzetta-di-kyiv/docs/PREDICTION_MARKET_STRATEGIES_V1.md` (prediction market signal analysis)

## When to Use

Load this skill when:
- Writing Bet&Benefit asset-claim pills for Gazzetta di Kyiv stories
- Analyzing an event's tradable implications for retail audience
- User asks about trading strategies, event catalysts, or "how to play" a news event
- Producing Telegram or Reddit content that includes a trading angle
- Cross-referencing prediction market odds against asset price movements

## Core Principles

1. **Edge comes from structure, not alpha.** Retail traders don't have better information — they have better discipline and pre-positioning.
2. **The crowd is almost always right about direction, wrong about magnitude.** Mean reversion after events is the highest-probability trade.
3. **Volatility crush is the invisible tax.** Most event-driven premium-buying strategies lose to IV crush — sell vol, don't buy it.
4. **Time stops matter more than price stops.** 90% of geopolitical flash moves revert within 2 hours. Don't hold through the overnight gap.

## Strategy Categories (prioritized for editorial use)

### Tier 1: Editorial-Grade (actionable in a 90-word pill)
- **Vol Crush Post-Event:** Sell strangles/iron condors 30 min after event. Win rate: 75–85%. Simplest execution, most consistent returns.
- **Fade-the-Initial-Move:** Enter counter-directional 15–60 min post-release, target 61.8% retracement. Best on FX pairs and commodities.
- **Earnings Gap-and-Go:** Screen for >5% gaps with <50% fill in 60 min. Enter on continuation, hold 1–5 sessions.

### Tier 2: Context-Grade (mention in long-form)
- **FOMC Powell Play:** Statement (2PM) vs. presser (2:30PM) as separate trades.
- **FDA Calendar Spread:** Sell near-term, buy next-month straddle on biotech catalysts.
- **Unusual Options Flow:** Track OTM block trades >$250K after 3:30 PM — the last 30 minutes carry maximum information asymmetry.

### Tier 3: Reference-Grade (don't push, offer if asked)
- **M&A Arbitrage:** Only all-cash small-caps (<$500M). 4% annualized spread minimum.
- **GDP Pre-Positioning:** Whisper numbers vs. live indicators (ADP before NFP, regional Fed before CPI).

## Event-Strategy Mapping (for quick editorial lookup)

| Event Type | Best Strategy | Asset | Hold Time | Win Rate |
|-----------|--------------|-------|-----------|----------|
| NFP / CPI release | Fade-the-Move (reversion) | FX pairs (EUR/USD) | 2–24h | 65% |
| FOMC rate decision | Powell Play (statement + presser) | ES, ZN, 0DTE strangles | Intraday | 60% |
| Earnings surprise | Gap-and-Go momentum | Individual stocks | 1–5 sessions | 55% |
| FDA PDUFA date | OTM call spread | Biotech >$300M | 1–2 weeks | 50% |
| Geopolitical flash | Buy crude/gold, exit in 2h | CL, GC futures | 30 min–2h | 55% (if disciplined) |
| M&A announcement | Cash arb | Small-cap targets | Until close/break | 70% (but rare) |
| Unusual options flow | Buy underlying stock | Liquid names | 1–5 sessions | 50% |
| Pre-market gapper | Benzinga Squeeze Play | Stocks gapping >3% | Intraday | 55% |

## The Contradiction Lens (editorial voice)

For every story with a tradable event, surface the contradiction:
- **"What traders think:"** how the initial spike prices the event
- **"What the data says:"** the historical edge of the counter-trade
- **"The Bet&Benefit:"** specific asset + direction + % narrative-driven

Example: "NFP beats by 180K, EUR/USD spikes 75 pips. Traders buy dollars. But the volatility crush post-NFP has won 68% of the time since 2020 — fading the spike to 1.0850 (61.8% retrace) is the structured play."

## Retail Trader Pitfalls (editorial guardrails)

Never recommend strategies that rely on:
- **Slippage immunity:** Options spreads widen 5–15x post-release. Limit orders fail.
- **Dark pool access:** Unusual options flow without Bloomberg terminal-level detail is noise.
- **Speed edge:** Headline momentum plays require <30-second reaction. Retail is always behind.
- **Unlimited capital:** Straddles cost 3–5% of notional — no more than 2 plays at once.
- **Overnight hold on geopolitics:** 50/50 direction on next-day gap. Close intraday.

## Platform-Specific Content Rules

### Telegram (90–120 words)
- One event, one strategy, one asset, one price level
- Include: "Historical win rate: X%" for credibility
- Format: Signal → Contradiction → Bet&Benefit level → edge stat

### Reddit (140–260 words)
- Full strategy breakdown with decision rules
- Include pitfall section
- End with: "What are you fading this week?"

### Website (Bet&Benefit pill)
- Asset ticker + predicted direction + narrative-driven % of move
- Cross-reference with prediction market odds (if available)
- Format: `BTC ⬆ $78,500 | 62% narrative-driven | Polymarket: 68% odds aligned`

## Integration Points

- **`gazzetta-prediction-market-trading`** — for polymarket odds cross-reference. The X.com macro consensus vs. Polymarket betting crowd divergence IS the signal.
- **`gazzetta-editorial-writer`** — for asset-claim pill generation (Step 5.5).
- **`polymarket`** (research skill) — for live API queries.
- **X.com Macro Intelligence Feed** (`gazzetta-di-kyiv/data/xcom_intel/latest.json`) — 33 accounts spanning macro consensus, geopolitics, crypto, and abundance tech. This is the PRIMARY event-catalyst detection layer. When `@BRICSinfo` drops a "JUST IN:" on Iran, or `@biancoresearch` flags a Fed governance crisis, or `@novogratz` announces institutional prediction market trading — these ARE the events that trigger the strategies in this playbook. The collector script lives at `scripts/xcom_collector.py` (under `gazzetta-paradigm-and-strategy` skill).
