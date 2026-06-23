# Info Product Quality Audit Methodology
## Lessons from Phase 9 (June 2026)

### Audit Structure

The audit scored the Gazzetta di Kyiv platform **58/100** using 3 institutional personas reviewing the live site + raw story/flow data. This methodology is reusable for any intelligence product audit.

### Persona Selection

| Persona | Role | Key Questions | Score Weight |
|---------|------|---------------|-------------|
| **HF Manager** ($2B AUM) | Would they allocate? | Edge identification, conviction framing, risk/reward, stops | 40% |
| **PE Associate** (Tech/Growth) | Would they use for decks? | Structural depth, supply-chain insight, regulatory awareness, moat analysis | 30% |
| **HFT** (Quant) | Would they pipe to feed? | Data freshness, signal-to-noise, velocity metrics, API suitability | 30% |

### Audit Methodology

1. **Fetch ALL data from live endpoints** — stories.json, flows.json, signal.json, trades.json
2. **Parse each story** for: capital_flow dict completeness, trade_signal presence, contradiction_score, source quality, sector tagging accuracy
3. **Cross-reference claims against data** — does the asymmetry score exist in the schema? Are stops uniform or asset-specific?
4. **Generate Strategic Recommendations** for each story as a value-add test
5. **Score 0-100** on: depth × actionability × uniqueness × contradiction clarity

### Key Findings (Phase 9)

- 4/35 stories were unvetted OSINT placeholders (source=osint_reuters_business, trade_signal=N/A)
- Asymmetry Score (the flagship metric) was absent from the data schema
- 20/35 stories shared the same $88B capital_flow amount (copy-paste from flow JOIN)
- Sector tagging was broken: Home Sales→crypto, Stock Market→defense, European Tech→defense
- All stops were uniform -5% (audit flagged this; ANCHOR_ASSETS were actually ATR-calibrated — the stories lacked trade signals entirely)
- Subscription readiness: LOW-MEDIUM. Recommended $79/mo individual, $499/mo institutional

### Post-Audit Fixes (Phase 10)

- OSINT stories filtered at DB query level in db_to_json.py
- Asymmetry Score computed from narrative-vs-price divergence, injected into signal.json
- Capital flow JOIN changed from unconditional-overwrite to default-override-only
- Sector tags corrected: Home Sales→macro, ADP→macro, Stock Selling→equities
- Strategic Recommendations auto-generated for stories with contradiction_score ≥ 55

### Scoring Rubric

| Score | Tier | Meaning |
|-------|------|---------|
| 90-100 | LAUNCH-READY | Institutional investors would pay. All critical gaps closed. |
| 70-89 | BETA | Genuine edge on specific verticals. Needs 1-2 months hardening. |
| 50-69 | PROTOTYPE | Differentiated but inconsistent. 6 months to launch-ready. |
| 30-49 | PRE-SEED | Conceptual value. Needs fundamental rebuild. |
| 0-29 | NON-VIABLE | Would not pass any investor's due diligence. |

### Persona Sub-Scores

For the HF Manager:
- Edge identification (can I trade this?)
- Conviction framing (how confident? why?)
- Risk/reward clarity (where's my stop? what's the target?)
- Contradiction depth (how big is the narrative-vs-reality gap?)
- Actionability (can I execute this right now?)

For the PE Associate:
- Structural depth (do they understand the industry?)
- Supply-chain insight (do they know how things connect?)
- Regulatory awareness (do they track policy impact?)
- Competitive moat analysis (can they identify durable advantages?)
- Multi-year trends (do they see beyond the 24h news cycle?)

For the HFT:
- Data freshness (how stale is the signal?)
- Signal-to-noise ratio (how much is actionable vs filler?)
- Velocity metrics (is there a pace indicator? is it reliable?)
- Asymmetry mathematical rigor (is the score actually derived or hardcoded?)
- API suitability (can I pipe this into a trading system?)
