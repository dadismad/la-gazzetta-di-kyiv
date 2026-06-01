# NIOS Architecture v1 — Gazzetta di Kyiv

## Mission Layer
La Gazzetta di Kyiv operates as a Narrative Intelligence Operating System (NIOS):
- detect dominant narratives,
- map actors + incentives + contradictions,
- translate to cross-asset implications,
- provide retail-accessible positioning guidance,
- retain institutional memory for compounding accuracy.

## Core Pipelines
1. Signal Detection
   - Source registry + event ingestion (multi-source headlines, transcripts, social discourse).
2. Narrative Structuring
   - Claim extraction, taxonomy tagging, actor/incentive graph updates.
3. Interpretation Engine
   - Contradiction mapping, regime classification, cross-asset transmission, invalidation logic.
4. Distribution Engine
   - Website terminal cards, Telegram compact brief, Reddit long-form hypothesis posts.
5. Memory + Feedback
   - Store outputs, confidence, invalidation outcomes, and pattern success/failure.

## Data Contracts
- `site/api/v1/home/regime.json` — macro regime state.
- `site/api/v1/home/setups.json` — thesis + probabilities + invalidation.
- `site/api/v1/home/contradictions.json` — conflict claims and urgency.
- `data/contracts/article_contract_v1.json` — editorial structure contract.
- `data/nios/actor_graph_v1.json` — actor/incentive relationship map.

## Reliability Requirements
- Every publish cycle must include: thesis, actor list, incentive map, invalidation, confidence.
- Probabilities must sum to 100 for each setup.
- Missing invalidation or citations blocks publishing.

## Scale Risks
- Taxonomy drift (same narrative tagged under different labels).
- Generic output regression under sparse data conditions.
- Pipeline desync between website cards and social distribution.

## Mitigations
- Deterministic taxonomy map.
- Contract validator in CI/publish scripts.
- One-source-of-truth JSON payloads feeding all channels.
