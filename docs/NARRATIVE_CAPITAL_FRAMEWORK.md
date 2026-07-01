# Narrative Market Capitalization (NMC) Framework

## 1. Objective

To ground structural narrative themes in auditable macroeconomic weights. NMC provides a deterministic denominator to our analytical engine, allowing the platform to contrast *dynamic tactical flows* against the *static strategic universe*.

Without NMC, a narrative showing "$4.2B inflow" could be a 0.3% shift in a $1.4T universe or a 42% flood into a $10B niche. The user cannot distinguish signal from noise. NMC makes that distinction quantitative.

---

## 2. The Graph Model

Economic assets are fundamentally cross-cutting; a single commodity or technology player can belong to multiple tectonic narrative shifts simultaneously. This platform explicitly **rejects siloed mapping** in favor of a graph-based representation (`data/narrative_graph.json`).

### Mathematical Formulations

For any given narrative segment $n$, the platform computes total market capitalization and average daily dollar volume using an explicit Theme Purity Weight ($w$):

$$NMC_n = \sum_{i \in A_n} (\text{Cap}_i \times w_{i,n})$$

$$\text{Liquidity}_n = \sum_{i \in A_n} (\text{AvgVolume}_i \times \text{Price}_i \times w_{i,n})$$

Where:
- $A_n$ is the array of constituent assets mapped to the narrative node.
- $\text{Cap}_i$ evaluates to `marketCap` for Equities, and `totalAssets` or `netAssets` for ETFs.
- $w_{i,n}$ is an explicit weight ($0 < w \le 1$) denoting structural thematic exposure.

---

## 3. Data Provenance & Governance

To ensure audit stability, all purity weights are mapped with an explicit `weight_source`:

| Source | Description | Example |
|--------|-------------|---------|
| `editorial_v1` | Manual baseline from qualitative prospectus review | NVDA at 1.0 for Compute Hegemony |
| `observed_revenue` | Segmented corporate revenue attribution | XOM at 0.7 if 30% revenue is non-energy |
| `statistical_correlation` | Rolling factor-loading regressions | Correlation to narrative basket returns |

**Principle**: Weights start as editorial estimates and improve over time with observed data. No weight is permanent — all are versioned and auditable. Changes to weights require updating the `weight_source` field.

---

## 4. Phase 1 Implementation (Current)

**Scope**: Strictly limited to Developed Markets (DM) liquid Equities and ETFs.

**Included**:
- Single-name equities with observable market cap
- Thematic and sector ETFs with disclosed holdings
- Daily updates via yfinance (free tier)

**Excluded** (deferred to Phase 2+):
- Cryptocurrencies (no standard "market cap" — circulating supply × price is not analogous)
- Physical commodities without distinct corporate equities (requires futures notional modeling)
- Futures contracts (notional vs open interest distinction needed)
- Private assets (no observable market price)
- Fixed income instruments

### File Structure

```
data/
├── narrative_graph.json     # Master graph: all narratives with assets, weights, computed caps
└── narrative_cap.json       # Lightweight frontend cache: narrative_id → {narrative_cap_usd, narrative_liquidity_usd, as_of}
```

### Computation Cadence

Daily at 07:00 Kyiv (04:00 UTC). Market capitalizations do not move enough intraday to justify per-cycle updates. The daily snapshot is sufficient for narrative-level analysis.

---

## 5. Phase 1b (Next)

- **Narrative Liquidity**: Aggregate average daily dollar volume per narrative.
- **Historical snapshots**: Store daily NMC values to enable momentum and rotation tracking.

## 6. Phase 2 (This Month)

- **Narrative Breadth**: Number of constituent assets.
- **Narrative Concentration**: Top-N assets as % of total NMC.
- **Cross-narrative asset references**: Assets belonging to multiple narratives with partial weights.

## 7. Phase 3 (Future)

- **Narrative GDP**: Sum of all narrative capitalizations.
- **Narrative Share**: Each narrative's % of GDP.
- **Narrative Rotation**: Month-over-month capital migration between narratives.
- **Narrative Momentum**: 30-day NMC change.

---

## 8. Frontend Integration

The GAP Leaderboard card gains one additional line:

```
Energy Sovereignty
GAP 73 · ↑8 · CL=F
Capital in Play: $1.42T  ← NEW
Active Flow: +$4.2B
```

The `Capital in Play` line sources from `data/narrative_cap.json`, updated daily. The `Active Flow` line sources from the existing pipeline (improving hourly via re-synthesis).

---

*Last updated: 2026-06-25. This document governs the NMC product line. Phase boundaries are guidelines, not contracts. Scope expands only when current phase is validated.*
