# Trust & Data Integrity Architecture

## 1. Core Philosophy

La Gazzetta di Kyiv exists to measure the divergence between media consensus and institutional capital flow. The platform's primary asset is **trust** — every number displayed must carry verifiable provenance.

**Principle**: Trust the capital ledger. Verify the media narrative. Never fabricate.

---

## 2. Data Lineage Requirements

Every quantitative output must carry:

| Field | Required | Example |
|-------|----------|---------|
| `source` | Yes | `CFTC COT Report 2026-06-09` |
| `timestamp` | Yes | `2026-06-25T10:00:00+03:00` |
| `confidence` | Yes | `HIGH` / `MEDIUM` / `LOW` / `NONE` |
| `estimation_method` | Yes | `cftc_notional` / `price_proxy` / `llm_inference` / `none` |
| `validation_status` | Yes | `VERIFIED` / `UNVERIFIED` / `FLAGGED_ANOMALY` |

If any element is missing, the value must not be displayed.

---

## 3. Ingestion Defense Layers

### Source Provenance & Noise Filtration

Raw data streams are inherently dirty. Before reaching `all_stories`, the ingestion pipeline enforces:

- **The "T" Filter Protocol**: Anomalous single-character source artifacts (`"t"` → `"T"` via `.upper()`), `"UNKNOWN"`, or null references are intercepted and stripped at the synthesizer level. A signal without valid provenance is discarded.
- **Source Deduplication**: SHA-256 hashing prevents duplicate entries across ingestion cycles.
- **Capital Floor**: Assets must map to the Narrative Market Capitalization (NMC) graph to qualify for trade-level signals.

### Ticker Normalization & Domain Bounding

Asset tickers undergo rigorous sanitization in `contradiction_synthesizer.py`:

- **Sanitization**: Strip `$`, `#`, whitespace. Force uppercase. Validate format.
- **Cross-Domain Hallucination Prevention**: Tickers are validated against canonical sets per narrative (e.g., energy narratives cannot produce SMH/QQQ). The LLM's `affected_tickers` output is post-processed with an intersection check against `CANONICAL_TICKERS[narrative_id]`.

---

## 4. The GAP Score: Deterministic Spread

The `contradiction_gap` (0-100) is NOT an arbitrary rating. It is a deterministic calculation:

```
GAP = floor(10 × sum of absolute percentage moves of all contradictory tickers)
```

**Numeric anchoring**:
- 0-15: No tracked ticker moved >0.5% contrary to narrative
- 16-30: Minor tension (0.5-1.5% moves)
- 31-50: Moderate contradiction (1.5-3% moves)
- 51-75: Significant (3-5% or 2+ tickers at 2%+)
- 76-100: Extreme (broad index 2%+ or sector ETF 5%+ opposing narrative)

A GAP ≥ 70 with `capital_flow_confidence` of HIGH or ELEVATED triggers an automated trade thesis (THE PLAY).

---

## 5. Confidence Provenance Matrix

| Confidence | Source Requirement |
|-----------|-------------------|
| **HIGH** | Observable CFTC positioning, ETF flow data, or measured capital allocation |
| **MEDIUM** | Market cap proxy, price action inference, or liquidity proxy |
| **LOW** | Narrative-derived estimate, LLM interpretation, no direct quantitative source |
| **NONE** | No defensible basis for estimation; value set to 0 |

---

## 6. The System of Record

Telegram is the presentation layer. The broadcast engine is the gatekeeper.

- Only signals that pass `send_telegram()` are etched into `recommendation_ledger.jsonl`.
- The ledger is append-only. No deletion. No retroactive modification.
- Ledger schema:
  ```json
  {
    "ledger_id": "uuid4",
    "published_at": "ISO 8601 Europe/Kyiv",
    "story_id": "X",
    "narrative_id": "energy_sovereignty",
    "ticker": "CL=F",
    "direction": "LONG",
    "conviction": "HIGH",
    "entry_price": 72.00,
    "stop_loss": 68.00,
    "take_profit": 82.00,
    "status": "OPEN"
  }
  ```
- Status lifecycle: `OPEN` → `TRIGGERED` → `CLOSED` (with exit_price + realized_pnl_pct)

---

## 7. Validation Gates

Before any deploy, the pipeline must pass:
- **Syntax check**: `py_compile` on all modified scripts
- **Test suite**: `test_platform.py` — 147 assertions on built HTML
- **Pipeline audit**: `governor.py` end-of-cycle diagnosis
- **Brand enforcement**: No regressions in editorial voice or visual standards

If the pipeline cannot say *"I verified this"*, the terminal must not say *"this is true"*.

---

*Last updated: 2026-06-25. This document governs all trust-layer decisions. Amendments require ADR sign-off.*
