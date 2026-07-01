# Narrative Market Cap — Methodology & VC Defense

**Version:** 1.0.0
**Date:** 2026-06-27
**Prepared for:** Institutional due diligence

---

## Executive Summary

La Gazzetta di Kyiv tracks capital flows through 12 macro narratives. Our Narrative Market Cap (NMC) methodology measures the investable capital pool crystallized around each narrative — not through aspirational total addressable market estimates, but through **Representational Proxy Portfolios** of highly liquid, publicly traded instruments whose price action is causally linked to narrative development.

This document defends our methodology for venture capital and institutional due diligence.

---

## The Problem We Solve

Traditional financial media describes narratives in words. We quantify them in dollars. The challenge: a narrative like "deglobalization" is not a single asset class. It spans defense contractors (ITA), industrial ETFs (XLI), metals and mining (XME), and currency pairs (DXY). Summing the total market cap of all global industrials ($8T+) would be mathematically dishonest — most of that cap is driven by factors unrelated to deglobalization.

We needed a methodology that:
1. Measures what is actually measurable
2. Is defensible under due diligence
3. Produces numbers that drive tradable signals (not vanity metrics)

---

## Methodology: Representational Proxy Portfolios (RPP)

### Definition

A **Representational Proxy Portfolio** is a curated set of 5–15 highly liquid, publicly traded instruments selected for **causal relevance** to a specific macro narrative — not for convenience, coverage, or availability.

### Selection Criteria

Every instrument in a proxy portfolio must satisfy ALL of:

| Criterion | Requirement | Verification |
|-----------|------------|-------------|
| **Causal Link** | The narrative's development must have a demonstrable, directional impact on the instrument's price | Correlation analysis over 6-month rolling window |
| **Liquidity** | Average daily volume ≥ $50M | Exchange data |
| **Institutional Accessibility** | Tradable via standard brokerage, no accredited-investor restrictions | Exchange listing verification |
| **Narrative Beta** | Instrument must show statistically significant excess sensitivity to narrative-specific catalysts vs. broad market | Event study methodology |
| **Single-Name Preference** | Prefer individual equities over sector ETFs where causal attribution is clearer | Entity grounding analysis |

### Per-Narrative Proxy Portfolios

| Narrative | Proxy Assets | Rationale |
|-----------|-------------|-----------|
| **Sovereign Liquidity Migration** (dollar_decline) | GLD, SLV, UUP, DX=F, EURUSD=X | Gold/silver as anti-dollar hedges; DXY and EURUSD as direct currency vectors |
| **Energy Sovereignty** (critical_resource_control) | CL=F, NG=F, XLE, URA, NLR | Crude + natural gas futures; uranium as energy independence play |
| **Industrial Reshoring** (deglobalization) | XLI, ITA, PPA, XME, FDX, CAT | Defense + industrial metals + logistics |
| **Eurasia Capital Architecture** (china_ascent) | FXI, KWEB, MCHI, BABA, CNY=X | China equity ETFs + currency |
| **Orbital Industrialization** (space_economy) | ARKX, UFO, ROKT, LMT, NOC | Space + defense primes |
| **Longevity & Bioreality** (gene_editing) | ARKG, XBI, IBB, CRSP, NTLA | Biotech + gene editing pure-plays |
| **Enterprise Intelligence** (tech_convergence) | MSFT, AMZN, GOOGL, QQQ, CLOU | Cloud + enterprise tech |
| **Trophy Asset Financialization** (wealthy_sports) | DKNG, MANU, BATRK, DIS | Sports betting + franchise ownership |
| **Compute Hegemony** (ai_chips) | NVDA, SMH, AMD, ASML, TSM | Semiconductor + AI infrastructure |
| **Decentralized Capital** (crypto_reserve) | BTC-USD, COIN, MSTR, ETH-USD | Crypto + institutional on-ramps |
| **Liquidity Regime Transition** (rate_cycle) | TLT, SHY, IEF, ZN=F, ZB=F | Treasury ETFs + bond futures |
| **Physical Resource Revaluation** (commodity_supercycle) | DBC, GLD, COPX, XME, WEAT | Broad commodities + industrial metals |

---

## Capital-at-Stake Calculation

```
Capital_at_Stake = Σ (|Net_Speculative_Position| × Contract_Notional) per narrative
                 × Contradiction_Gap / 100
                 × Data_Fidelity_Multiplier
```

### Data Fidelity Tiers

| Tier | Source | Multiplier | Description |
|------|--------|:----------:|-------------|
| TIER_1 | CFTC COT | 1.0 | Live institutional futures positioning — highest fidelity |
| TIER_2 | FRED macro series | 0.8 | Macro-economic indicators with causal linkage |
| TIER_3 | ETF AUM proxy | 0.5 | Inferred positioning from fund flows |

---

## Why This Methodology Is VC-Defensible

### 1. Falsifiability
Every proxy asset selection can be challenged and revised. A critic can argue "copper futures (HG=F) have stronger causal linkage to deglobalization than steel (ST=F)." That's a productive debate — and we can swap the asset.

### 2. Audit Trail
Every capital-at-stake number traces back to: (a) a specific CFTC position report or ETF flow data, (b) a specific contradiction score from editorial analysis, (c) a specific data fidelity tier. There are no black-box numbers.

### 3. Bounded Scope
We do not claim to measure "all global capital affected by AI." We claim to measure "capital positioned in NVDA, SMH, AMD, ASML, and TSM — five instruments with well-understood causal links to AI infrastructure spending." The bounded scope makes the claim testable.

### 4. Signal, Not Vanity
The NMC number is not displayed as a badge of authority. It is a **signal input** to the Contradiction Gap scoring system. When NMC rises while Δ Edge remains low, the platform detects an emerging divergence — a trade signal.

---

## What We Explicitly Do NOT Claim

- ❌ That our proxy portfolios capture 100% of narrative-driven capital flows
- ❌ That NMC = total addressable market for the narrative
- ❌ That our numbers are comparable to Bloomberg or MSCI aggregate estimates
- ❌ That NMC is an investable index (though it is the foundation for future thematic portfolio products)

---

## Future Product Path: Thematic Narrative Portfolios

The proxy portfolios defined above are the natural foundation for investable products:

1. **Narrative ETN/Basket:** A weighted basket of the proxy assets, rebalanced weekly based on Δ Edge scores
2. **Narrative Options Strategies:** Selling volatility on low-Δ-Edge narratives, buying convexity on high-Δ-Edge narratives
3. **Narrative Hedge Fund Benchmark:** A composite index of all 12 narrative baskets for performance attribution

Each of these products is built on the same RPP methodology — the methodology scales from signal to product without architectural change.

---

*For institutional inquiries: alexander.solianin@lagazzettadikyiv.com*
