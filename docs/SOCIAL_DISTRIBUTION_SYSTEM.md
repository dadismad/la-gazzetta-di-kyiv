# Social Distribution System — Narrative Distribution Architecture

## Purpose
Social channels are narrative acquisition funnels, not mirrors. All distribution must reinforce institutional identity, drive website conversion, and preserve narrative continuity across X, Telegram, and Reddit.

## Canonical Narrative Object (required input for all platforms)
Every social post must be derived from a single narrative object.

### Social narrative fields (required)
1. narrative_hook
2. dominant_consensus
3. hidden_contradiction
4. strategic_implication
5. market_asset_implication
6. verified_human_detail (with citation id + source URL)
7. website_cta

### Core mandatory fields (from Unified Media Policy)
- claim
- contradiction
- implications (industry + asset)
- invalidation_trigger
- confidence_score + confidence_label
- capital_flow_3d_estimate

### Required supporting metadata
- narrative_id
- actors
- sectors
- evidence_urls
- continuity_link (prior update + next trigger)
- narrative_stage (spark | validate | deepen | update)
- platform_post_type
- website_url
- publish_window (morning / evening)

## Platform roles & daily narrative arc
- **X = detonation:** curiosity spike and authority framing.
- **Telegram = reinforcement:** real-time intelligence wire.
- **Reddit = laboratory:** hypothesis testing and community signal capture.

### Narrative intensity ladder (daily)
| Stage | Goal | Primary platform | Window |
| --- | --- | --- | --- |
| Spark | Trigger curiosity + contradiction | X | Morning cycle 06:30 |
| Validate | Reinforce signal + actionable interpretation | Telegram | Morning cycle 06:30–10:00 |
| Deepen | Hypothesis testing + discussion | Reddit | Midday 12:00–15:00 |
| Update | Continuity + new trigger | Telegram (+ X follow-up if needed) | Evening cycle 18:30 |

Rules:
- One narrative advances through stages; no duplicate sparks in the same cycle.
- Updates require new evidence or a measurable trigger shift.
- All platforms must reference continuity link and avoid verbatim reuse.

## Universal post rules
- No copy-paste across platforms.
- Each post includes a continuity reference and a “what to watch next” trigger.
- Each post includes exactly one website CTA.
- Evidence links required for claims or projections.
- Verified human detail is mandatory and must cite the ledger entry.

## Platform blueprints

### X.com (Detonation Layer)
**Structure (6-step):**
1) Hook
2) Consensus
3) Contradiction
4) Market implication
5) Human detail (verified)
6) CTA

Guardrails:
- Max 275 characters for single-post automation.
- Evidence link in a reply or follow-up post.
- No near-duplicate of last 3 posts.

CTA micro-phrases (rotate):
- "Full contradiction map: {website_url}"
- "Full narrative breakdown on La Gazzetta di Kyiv: {website_url}"
- "Positioning framework updated here: {website_url}"
- "Full cross-asset exposure map: {website_url}"
- "Complete narrative dossier: {website_url}"

### Telegram (Rapid Intelligence Terminal)
Post types: Breaking Narrative | Strategic Brief | Signal Alert

Structure:
1) Opening signal (1 line)
2) Immediate implication
3) Actionable interpretation (1–3 bullets)
4) Verified human detail (with citation)
5) Continuity link + next trigger
6) CTA

Guardrails:
- Target 90–160 words.
- Evidence links required for projections.

CTA micro-phrases (rotate):
- "Full briefing and positioning map: {website_url}"
- "Narrative exposure dashboard: {website_url}"
- "Detailed contradiction map: {website_url}"
- "Full 24–72h positioning note: {website_url}"
- "Complete intelligence brief: {website_url}"

### Reddit (Narrative Laboratory)
**Narrative Lab format (long-form):**
1) Context
2) Dominant narrative
3) Contradiction
4) Second-order implications
5) Strategic interpretation (24–72h + invalidation)
6) Verified human detail (with citation)
7) Discussion prompt
8) CTA

Guardrails:
- Target 180–260 words for narrative lab posts.
- Evidence links + invalidation trigger required.
- Maintain subreddit brand voice: concise, analytical, falsifiable.

CTA micro-phrases (rotate):
- "Full narrative dossier and data links: {website_url}"
- "Complete contradiction map: {website_url}"
- "Full cross-asset breakdown: {website_url}"
- "Detailed positioning framework: {website_url}"
- "Full intelligence brief and sources: {website_url}"

## Retention loops & continuity
Each post must include:
- Continuity link to the prior update (timestamp or narrative_id).
- “What to watch next” trigger (explicit condition or event).

Format example:
- "Continuity: {prior_update} | Next trigger: {trigger}."

## Verified human-detail process
Checklist (must pass):
1. Publicly verifiable source (primary or two reputable secondary sources).
2. Non-defamatory, non-sensational, and relevant to the narrative.
3. Time-anchored (date or period stated).
4. Stored in the ledger with an ID + source URL.
5. Ledger ID cited in the post body.

Ledger location:
- `data/human_detail_ledger.md`

Compliance gate:
- Block any post lacking a ledger ID + source URL.

## CTA architecture
- CTA library is stored in `data/cta_library.json`.
- Rotate phrases; avoid reuse within the last 7 posts per platform.
- One CTA per post; must point to the website narrative thread.

## Knowledge storage & feedback loops
Log each post to `data/social_distribution_log.jsonl` using `data/social_distribution_log_schema.json`.

Required log fields:
- narrative_id, narrative_stage, platform, post_type
- actors, sectors, framing_pattern
- CTA phrase used + website_url
- engagement metrics + CTR
- evidence_urls, continuity_link, human_detail_id

Use logs to update:
- `data/nios/memory_log.jsonl`
- `data/nios/pattern_library.json`

Weekly review:
- identify top framing patterns
- refresh CTA library
- adjust pacing by platform

## Governance & QA gates
Block publish if any fail:
- Narrative object incomplete
- Missing evidence links
- Missing verified human detail (ledger ID)
- Missing continuity link + next trigger
- CTA missing or multiple CTAs
- Length or tone guardrail breach
- Cross-platform duplication

## Integration
Distribution adaptation and QA gates are enforced in `docs/CROSS_CHANNEL_EDITORIAL_SOP.md`.
