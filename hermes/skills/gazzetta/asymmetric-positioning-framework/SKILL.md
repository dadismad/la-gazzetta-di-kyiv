---
name: asymmetric-positioning-framework
description: 5-step asymmetric positioning framework for evaluating trades and narratives through convexity, Kelly sizing, and tail-risk lens. Integrate into editorial and data pipelines.
version: 1.0.0
category: gazzetta
---

# Asymmetric Positioning Framework

Derived from Taleb (Antifragile), Spitznagel (Universa), Cole (Artemis), Dalio (Bridgewater), and Soros (reflexivity). Applied to Gazzetta di Kyiv narrative-driven capital flow analysis.

## 5-Step Evaluation Checklist

### Step 1: Define the Asymmetric Win Zone
- Binary payoff structure: what must happen for 10x+ win? Max loss in % portfolio.
- Accept only if gain/loss ratio > 3:1.
- Set hard stop-loss at max risk. Use defined-risk spreads.

### Step 2: Assess the Volatility Regime
- Compare implied vs realized volatility. Is vol cheap (IV < RV) or expensive?
- Check put/call skew (25-delta). Rising skew = fear; falling = complacency (cheap insurance).
- Only enter if tail hedge cost below 2-year median.

### Step 3: Identify the Narrative Feedback Loop
- Map capital flows: who is buying? Why? Reflexive loop present?
- Estimate narrative duration (days/weeks/months) and saturation (% of potential capital deployed).
- If flow exhausted + narrative at peak saturation → asymmetric short signal.

### Step 4: Calculate the Kelly Fraction
- P = probability of positive outcome. b = odds (gain/max loss).
- f* = (P × b - q) / b. If f* < 0, no edge.
- Size at 25% of Kelly (fractional). Example: 20% chance of 5x → f* = 0.04 → bet 1% capital.

### Step 5: Establish Exit/Rebalance Triggers
- Invalidation conditions: thesis loss, stop-loss hit, vol regime shift, time decay.
- Rolling re-evaluation cycle. Add to position if risk/reward improved.

## Asymmetry Detection Metrics

| Metric | Threshold | Signal |
|--------|-----------|--------|
| Risk/Reward Ratio | > 3:1 | Minimum entry |
| Put/Call Skew (10-delta) | < 15th percentile | Cheap tail hedges |
| Passive Flow Dominance | > 40% | Fragility → buy puts (Mike Green) |
| Concentration (HHI top 5) | > 25% of index | Tail risk of unwind |
| Implied vs Realized Vol | IV < RV by 2σ | Cheap vol → buy options |

## Pipeline Integration

### Editorial
- Every story scored through 5-step checklist → Asymmetry Score (1-10)
- Score 7+ → dedicated analysis with payoff diagram, Kelly sizing table
- Template fields: Binary scenario, max loss/gain, vol regime, narrative saturation, Kelly fraction, rebalance conditions

### Data
- Scrape: VIX term structure, SPX skew, put/call ratios, ETF flows, concentration metrics (HHI)
- Alert triggers: 10-delta skew < 15th percentile, PDR > 40%, HHI > 25%
- Dashboard: Green/Yellow/Red asymmetry scores per asset class

### Hedge Fund Gold Standards
1. Source validation — audit trail, SLA, bias detection
2. Cross-verification — multi-source triangulation, outlier flagging
3. Confidence quantification — SNR, Information Coefficient, Bayesian updating
4. Position sizing — Kelly-informed, risk budget parity, volatility targeting
5. Performance attribution — source-level P&L, interpretation attribution, decay tracking

## Validation Gates (Institutional Pipeline)
1. Schema conformance → 2. Distributional stability → 3. Look-ahead integrity → 4. Survivorship bias → 5. Correlation matrix → 6. Walk-forward P&L → 7. Stress test → 8. Operational redundancy
