# Canonical Platform Intelligence Definitions

> **Rule**: Every variable, metric, or pipeline step using these terms must adhere to these operational definitions. Vocabulary drift between modules is a silent tax on execution quality.

---

## 1. Primary Metrics

### Capital Volume USD (`capital_volume_usd`)

- **Definition**: Estimated tactical capital exposure associated with a specific narrative-contradiction, derived from observable market positioning or price action.
- **Type**: Integer USD.
- **Source Hierarchy**:
  1. **HIGH CONFIDENCE**: CFTC net positioning change × standard contract notional value.
  2. **MEDIUM CONFIDENCE**: Asset price velocity × thematic ETF total net assets or market cap proxy.
  3. **LOW CONFIDENCE**: LLM text-to-exposure narrative inference.
  4. **NONE**: Set to 0 if zero quantifiable basis exists.
- **Guardrails**: Scaled to billions on frontend; absolute pipeline ceiling capped at $500B.
- **Display**: Frontend divides by 1e9 for billions display. Confidence marker shown alongside.

### Narrative Market Capitalization (`narrative_cap_usd` / NMC)

- **Definition**: The total static pool of capital over which a core economic narrative exerts structural gravity. Calculated deterministically as the sum of float-adjusted market capitalizations (Equities) or Total Net Assets (ETFs) of its constituent graph nodes, scaled by theme purity weights.
- **Type**: Integer USD.
- **Cadence**: Computed daily at 07:00 Kyiv time via `scripts/fetch_narrative_cap.py`.
- **Source**: yfinance (`marketCap` for equities, `totalAssets` for ETFs).

### Narrative Liquidity (`narrative_liquidity_usd`)

- **Definition**: The thematic aggregate average daily dollar volume of a narrative segment, tracking real-time trade execution capacity of underlying assets.
- **Type**: Integer USD.
- **Calculation**: `Σ(averageVolume × currentPrice × purity_weight)` for all constituent assets.

---

## 2. Confidence & Audit Fields

### Capital Flow Confidence (`capital_flow_confidence`)

System tag mapping extraction fidelity of dynamic flow estimates:

| Value | Source |
|-------|--------|
| `HIGH` | CFTC positioning, actual flow data |
| `MEDIUM` | Price/volume proxy inference |
| `LOW` | Narrative text inference only |
| `NONE` | Zero quantifiable basis |

### Estimation Method (`estimation_method`)

Explicit audit tag tracking the algorithmic path used to derive exposure metrics:

| Value | Meaning |
|-------|---------|
| `cftc_notional` | CFTC contract × notional value |
| `price_proxy` | Ticker price move × ETF AUM / market cap proxy |
| `llm_inference` | Narrative text estimation |
| `none` | No basis for estimation |

---

## 3. Core Intelligence Concepts

### Intelligence

A falsifiable claim about future capital allocation, backed by verifiable evidence, with a measurable outcome. Content lacking falsifiability or measurable outcome is classified as **inventory**, not intelligence.

### Narrative

A structured, widespread belief system driving capital flows, capable of being quantified, tracked, and measured against market reality.

### Signal

A measurable divergence (contradiction) between a prevailing media narrative and actual capital movement.

### Claim

A falsifiable statement extracted from one or more sources, with explicit confidence, source, timestamp, and supporting evidence.

### Conviction

Confidence score assigned to a signal or trade thesis based on evidence quality and agreement across sources. Values: `HIGH`, `ELEVATED`, `SPECULATIVE`, `HOLD`.

### Reality Payload (`reality`)

Pure quantitative market data (CFTC data feeds, asset prices, FRED macro indices) used strictly as ground truth to validate or falsify narrative claims.

---

## 4. Trust Layer Concepts

### Recommendation

A published trade proposal recorded in the Recommendation Ledger. Must include: ticker, direction, conviction, entry/stop/target, and publish timestamp.

### Outcome

Measured result of a recommendation after publication. Includes exit price, realized P&L, and benchmark comparison.

### Trust

Accumulated evidence that the platform's intelligence improves decision quality. Measured via the Recommendation Ledger.

---

## 5. North Star Metrics

### Intelligence Yield

```
Useful Decisions Enabled ÷ Information Consumed
```

The primary organizational metric. Every collector, pipeline step, and product must justify its existence against this ratio.

### Intelligence Quality Score (IQS)

Composite score based on:
- Prediction Accuracy
- Timeliness
- Novelty
- Decision Utility
- Risk-Adjusted Outcome
- User Engagement

*Formal specification deferred to Phase 2. Operational proxy: Recommendation Ledger win rate.*

---

## 6. Theme Purity Weight

- **Definition**: A coefficient (0 < w ≤ 1) representing an asset's direct exposure to a specific narrative.
- **Governance**: All weights carry a `weight_source` tag:
  - `editorial_v1`: Manual baseline from qualitative review.
  - `observed_revenue`: Segmented corporate revenue attribution.
  - `statistical_correlation`: Factor-loading regression models.
- **Principle**: Weights start as editorial estimates and improve over time with observed data. No weight is permanent — all are versioned and auditable.

---

*Last updated: 2026-06-25. This document governs all platform terminology. Amendments require corresponding updates to code comments, schema definitions, and downstream documentation.*
