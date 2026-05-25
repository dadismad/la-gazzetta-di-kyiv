# Gazzetta di Kyiv — Full Audit, Competitor Cross-Reference, Gap Matrix, and Agentic Integration Plan (V1)

## 1) Main goals cross-reference (ground truth)
Reference doctrine: `docs/OPERATING_MANDATE.md`

Core goals checked:
- European narrative-intelligence newspaper identity
- high-signal, decision-grade storytelling
- cross-asset transmission and repricing clarity
- reliability + deployment truth + continuity
- semantic specificity (actors, claims, contradiction, invalidation)

Status:
- Reliability stack: strong (build stamp, CI checks, smoke checks)
- Identity direction: mostly aligned
- Story quality and specificity: partially aligned
- Cross-surface schema consistency: improving but not fully complete

## 2) Website audit (UX + content + architecture)

### Strengths
- Live deploy evidence visible (build + generated timestamp)
- Clear hero promise and direct Telegram CTA
- Story cards include claim/transmission/repricing/invalidation
- Search and frame navigation exist

### Mismatches vs desired state
1. **Actor quality mismatch**: extracted actors can be generic/noisy.
2. **Narrative depth mismatch**: some cards still read as model-template copy.
3. **Continuity mismatch**: weak explicit 2h/24h/3d continuity markers on homepage.
4. **Contradiction/misrepresentation mismatch**: visible but not deeply contextualized per story card.
5. **Data Desk mismatch**: schema visible, but semantic fields not yet fully generated from first-party structured extraction pipeline.

## 3) Competitor research (accessible evidence)

### Bridgewater Research & Insights (directly observed)
Patterns to copy:
- named-author authority
- thesis headline + concise consequence framing
- regime/topic taxonomy
- date and context always visible

### FT World RSS (directly observed)
Patterns to copy:
- event-driven, named actors, high recency
- strong headline specificity
- short, high-information summary line

### Reuters World (partially blocked by device verification)
Known benchmark pattern:
- speed + factual clarity + actor-first lead sentence

## 4) Improvement opportunities (priority order)
P0 (immediate):
- deterministic actor mapping by narrative domain (avoid generic actor artifacts)
- enforce contradiction + manipulation note quality in Telegram output prompt
- add continuity sentence in each homepage story block where data permits

P1 (next):
- move Data Desk semantic fields from static enrichment to structured API-driven extraction
- add source citation anchors per story card
- add per-story politics anchor chip set

P2 (later):
- narrative thread pages (entity timelines)
- confidence calibration dashboard

## 5) Agentic integration prompt (execute across org)
Use this as the controlling prompt for newsroom/engineering loops:

"You are the integrated Gazzetta operating stack: AI Engineering + Newspaper HQ + Research Bureau + Investment Desk.

Mission: produce newspaper-grade, actor-specific, contradiction-aware, investment-decision intelligence without breaking reliability.

For every cycle:
1) Ingest + rank top narratives.
2) Extract entities (person/org/country/asset/policy object).
3) Build SVO proposition and claim/counter-claim pair.
4) Tag manipulation risk (selection bias, omission, framing distortion, timing amplification).
5) Build cause->effect macro transmission and cross-asset repricing map.
6) Publish synchronized outputs to homepage, data desk, telegram.
7) Validate schema + deployment truth + quality gates.

Hard output requirements per story:
- Headline (event -> consequence)
- Actors (named)
- Proposition (SVO)
- Claim/Thesis
- Evidence (numeric + timestamped)
- Contradiction + manipulation risk
- Repricing (asset, direction, probability %, projection %)
- Invalidation
- Continuity link (2h/24h/3d)

Failure policy:
- If any required field missing, block publish or mark confidence degraded explicitly.
- Never output one-word summaries.
- Never claim completion without production proof."

## 6) Execution changes performed now
- Improved homepage actor quality via deterministic narrative->actor map fallback in `site/app.js`.
- Prepared this master audit and integration directive document.

## 7) Acceptance criteria for next cycle
- No story card displays generic actors like "Narrative"/"Second"
- Telegram output includes explicit politics anchors + contradiction + manipulation vectors
- Data Desk semantic columns become API-driven (not static placeholders)
- Homepage and Telegram share same semantic contract.
