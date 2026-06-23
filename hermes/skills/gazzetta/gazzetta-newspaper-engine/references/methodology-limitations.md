# Known Methodology Limitations & Risks
**Added June 22, 2026 — Skeptical Journalist Audit**
**Source:** Full audit at `gazzetta-knowledge-base/references/skeptical-journalist-audit-june2026.md`

Read this before operating or defending the pipeline. The Gazzetta presents itself as a quantitative contradiction-measurement system. In practice, these limitations mean the GAP score and capital flow numbers are NOT independently verifiable by readers.

---

## 1. GAP Score Is LLM-Generated, Not Deterministic

The `contradiction_synthesizer.py` SYSTEM_PROMPT instructs DeepSeek to output a `contradiction_gap` integer (0-100) using a suggested formula: `GAP = floor(10 × sum of absolute % moves of contradictory tickers)`. This formula is an **LLM instruction**, not code. DeepSeek decides:

- Which tickers are "contradictory" to the narrative
- What those tickers' percentage moves actually are
- Whether to follow the formula or diverge

There is zero code-level enforcement. A reader cannot trace any single GAP score back to the specific market data snapshot it was computed from. No audit trail exists.

**Mitigation (partial):** The prompt says "Never invent ticker data. Only reference the market data provided." A snapshot timestamp should be stored alongside each story.

## 2. Capital Flow Numbers Have Zero Provenance

Every capital number on the site ($28.8B into QQQ, $13.2B into ROKT, $7.9B into BATRK) displays without source attribution. A reader cannot:

- Determine whether it's AUM, daily volume, net inflow, or an LLM estimate
- Find the source API call or timestamp
- Distinguish between a legitimate data point and an LLM hallucination

The data pipeline DOES fetch real prices (yfinance), real crypto data (CoinGecko), real CFTC positioning, and real FRED macro data. But none of these are surfaced as provenance in the UI.

**Mitigation:** Display `(source: {provider}, {timestamp})` next to every capital number.

## 3. Majority of Stories Use a Flat $100M Default

189 of 191 active pipeline stories carry `capital_volume_usd: 100000000` — exactly $100M. This is not organic diversity. It's the fallback value from `calculate_capital.py` when no specific AUM or CFTC positioning data is triggered for a narrative.

The "49 unique values for 371 stories" observed in the old container structure has been replaced by near-uniform $100M in the new pipeline. Narrative-level capital aggregates (sidebar $XB values) are essentially `story_count × $100M` divided across narratives, not genuine market data.

**Mitigation:** Ensure `calculate_capital.py` runs correctly per-narrative, or accept the $100M floor as documented "TIER_3 baseline capital estimate" displayed in the UI as such.

## 4. "DISCREPANCIES: N" Is a Count of High-GAP Stories

The discrepancy counter (`build_frontend.py` line 199) counts stories with `contradiction_gap ≥ 40`. It is NOT a bug count, error count, or freshness warning. It's the system working as designed.

The term is misleading — it sounds like an operational alert when it's just a category filter.

**Fix:** Rename to "Divergences" or "High-GAP Stories" with a UI tooltip explaining what it counts.

## 5. Low-GAP Stories Use Template Frames

The `contradiction_synthesizer.py` prompt explicitly instructs DeepSeek to choose from a rotating set of frames for GAP 0-15 stories (market indifference, market efficiency, price alignment, normal noise). The prompt bans the word "Unmoved" and provides 8 substitutes.

This produces correct journalism (GAP 0-15 = no contradiction) but can read as template filler. "Hong Kong doctor firing leaves market pricing unchanged for tracked assets" is technically honest but visibly templated.

**Verdict:** Acceptable — the journalism is correct. The template-rot risk is aesthetic, not factual.

## 6. THEY SAY/REALITY Format Has Moderate Straw-Man Risk

Most high-GAP stories pass the straw-man test: the THEY SAY passage matches a real news article (verified by URL), and the market data contradicts it. But the format structurally incentivizes finding contradiction. The prompt instructs DeepSeek: "identify the contradiction between what the media says and what the market data shows." The product exists to find gaps — so it finds them.

**Highest-risk patterns:**
- "Ukraine war escalates but markets rally" — implying markets SHOULD sell off on Ukraine news (a 2022-era frame possibly no longer held by any credible analyst).
- "Stablecoin run fears clash with risk-on rally" — attributing a fringe fear as the consensus narrative.
- "Heat wave narrative vs market" — implying heat waves should uniformly move energy stocks.

**Mitigation:** Every THEY SAY should cite a specific named source. The prompt already requires this. Verify that high-GAP stories with GAP 50+ always include a named actor or publication.

---

## Summary Table

| Limitation | Severity | Fixability |
|-----------|----------|------------|
| GAP = LLM judgment | HIGH | Snapshot timestamps, deterministic fallback |
| Capital provenance missing | HIGH | Render provider + timestamp in UI |
| Flat $100M defaults | MEDIUM | Fix calculate_capital.py per-narrative routing |
| "DISCREPANCIES" misleading | LOW | Rename, add tooltip |
| Template frames for low-GAP | LOW | Expand frame pool |
| Straw-man structural risk | MODERATE | Enforce named-source THEY SAY on high-GAP |
