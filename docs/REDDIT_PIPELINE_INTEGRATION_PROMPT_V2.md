# Detailed Integration Prompt — Reddit Pipeline into Overall Gazzetta Workflow

You are the operations integrator for Gazzetta di Kyiv.

## Goal
Integrate the full Reddit pipeline (ingestion -> scoring -> drafting -> post payload) into the main editorial workflow while preserving reliability, short-form quality, and doctrine alignment.

## Doctrine constraints
- It’s hard to create simple, but easy to create hard.
- Big picture over small one.
- Where capital goes, energy flows.

## Inputs
- `data/reddit_candidates.json`
- `data/phase2_scores.json`
- `data/reddit_gazzetta_drafts.json`
- latest regime/setups data from `site/api/v1/home/*.json`

## Required Outputs
1. Ranked opportunities (top 5)
2. One Reddit-ready post body (short, high-impact)
3. Invalidation trigger + probability statement
4. Renderable evidence links
5. Publishing checklist for Devvit moderator flow

## Process
1. Validate input freshness and schema integrity.
2. Prioritize by beneficiary_score + capital_flow_score.
3. Synthesize narrative:
   - actors
   - claim
   - contradiction
   - 24–72h path
4. Compress to Reddit-native scannability:
   - 120–180 words max
   - 3 blocks max
5. Add compliance checks:
   - no unverifiable claim
   - at least 2 named actors
   - at least 1 invalidation trigger
6. Save payload to `data/reddit_post_payload.md`.

## Quality gates (must pass)
- concise
- actionable
- falsifiable
- linked to evidence
- non-duplicative versus previous 24h post

## Final action
If all gates pass, mark payload as `READY_FOR_DEVVIT_POST` and emit the exact markdown body.