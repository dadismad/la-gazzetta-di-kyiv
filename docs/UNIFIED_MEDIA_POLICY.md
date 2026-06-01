# Unified Media Policy — Gazzetta di Kyiv

## Scope
Applies to: Website, Newspaper X account, Chief Editor X account, Newspaper Subreddit.

## Editorial North Star
Narratives first, actionability second, certainty never overstated.

## Mandatory Output Rules
1. Every narrative must include: claim, description, controversial angle, implications, action-now, invalidation, projection 3d (%), confidence score/label, capital flow 3d.
2. Left panel and right panel must not repeat wording verbatim.
3. Short-term lens required: 24h–3d tactical applicability.
4. Professional tone: concise, non-hype, plain investment language.

## Canonical Narrative Object (All Channels)
All channels (website + X + Telegram + Reddit) must use the same narrative object input. Required fields include:
- narrative_hook
- dominant_consensus
- hidden_contradiction
- strategic_implication
- market_asset_implication
- verified_human_detail (ledger ID + source URL)
- website_cta
- claim, contradiction, implications, invalidation_trigger
- confidence_score + confidence_label
- capital_flow_3d_estimate
- actors, sectors, evidence_urls, continuity_link

See `docs/SOCIAL_DISTRIBUTION_SYSTEM.md` for platform-specific blueprints and pacing rules.

## Social Distribution Rules
- Platform roles are distinct: X (detonation), Telegram (reinforcement), Reddit (laboratory).
- No copy-paste reuse across platforms; adapt tone and pacing.
- Every social post must include a continuity link + next trigger.
- Each post must include a single website CTA from the approved library.
- Verified human detail is mandatory and must cite the ledger entry.

## Risk & Compliance Rules
- Declare confidence + uncertainty on every tactical recommendation.
- Explicit invalidation triggers required.
- No publish if mandatory fields are missing.

## Design Rules
- Brand palette and compact typography must pass gates.
- Renderability check required (content-type html + DOM markers).

## Incident Rules
- If primary endpoint degraded, switch status to degraded and surface fallback message.
- Auto-redeploy permitted only after consecutive failures.
