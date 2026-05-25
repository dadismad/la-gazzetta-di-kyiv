# Gazzetta di Kyiv — Organization Audit + Multi-Team Integration Prompt (V1)

## Executive Audit (Current -> Required)

### What exists
- Working static site + API JSON surfaces.
- Working Telegram delivery pipeline (3x/day) via cron.
- Story cards now present on homepage with claim/transmission/repricing blocks.
- Build provenance and production smoke checks are in place.

### Core gaps
1. Semantic specificity gap: too few named actors/subject-object relations in published outputs.
2. Political anchor gap: insufficient handling of power actors, policy conflict, propaganda/misrepresentation framing.
3. Newsroom language gap: still partly template-like vs professional editorial rhythm.
4. Cross-surface consistency gap: homepage, data desk, and Telegram not fully isomorphic in schema.
5. Team-operating gap: no formalized role choreography across AI engineering, editorial HQ, researchers, and investment desk.

## Target Operating Model (Institutional)

### Team A — AI Engineering (Reliability + Product)
- Owns ingestion reliability, schema validation, rendering contracts, CI gates, and observability.
- KPI: zero silent failures, deterministic output structure, deploy truth guaranteed.

### Team B — Newspaper HQ (Editorial)
- Owns headline quality, narrative continuity, contradiction framing, manipulation detection language standards.
- KPI: readability, distinctiveness, retention, clarity under time pressure.

### Team C — Research Bureau (Semantics + Verification)
- Owns entity extraction, claim typing, source triangulation, contradiction matrix.
- KPI: named-entity coverage, factual density, contradiction recall.

### Team D — Investment Desk (Decision Layer)
- Owns cause->effect mapping, asset transmission, repricing probabilities, invalidation precision.
- KPI: actionable quality and calibration quality.

## Unified Semantic Schema (apply everywhere)
Each story must contain:
- Actors: PERSON / ORG / COUNTRY / ASSET / POLICY OBJECT
- Proposition: subject-verb-object sentence
- Claim: thesis sentence
- Evidence: numeric + timestamped facts
- Contradiction: strongest opposing thesis
- Manipulation risk: likely media framing distortion or omission
- Transmission: first-order and second-order effects
- Repricing: instrument, direction, probability %, projection %, invalidation
- Continuity: relation to 2h / 24h / 3d progression

## Institutional Story Prompt (Master)
You are an integrated institutional newsroom + research + investment desk.
Write as a human newspaper professional under decision-time constraints.
No generic abstractions. No one-word narratives.

For each top story, output these sections:
1) Headline (event -> consequence)
2) Actors
3) Core proposition (SVO)
4) Claim/Thesis
5) Evidence (3-5 hard facts)
6) Contradictions & media misrepresentation/manipulation risk
7) Cause -> effect transmission (macro -> asset)
8) Repricing thesis (24-72h)
9) Invalidation trigger

Then output portfolio layer:
- 3 bet snippets
- winners/losers basket
- regime flip trigger
- continuity link

## Integration Rules
- Homepage cards: compact semantic fields.
- Data Desk: full semantic table + contradiction/manipulation columns.
- Telegram: concise but names-first with politics anchors and contradiction blocks.
- CI gate: reject if required fields missing.

## Acceptance Criteria
- Every story includes named actors + SVO + contradiction + manipulation note.
- Every story includes numeric evidence and repricing projection.
- Homepage/Data/Telegram share the same semantic backbone.
- Production smoke confirms presence of semantic labels on live site.
