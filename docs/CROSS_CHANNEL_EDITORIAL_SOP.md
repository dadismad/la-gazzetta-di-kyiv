# Cross-Channel Editorial SOP

## Workflow
1. Scout: ingest source narratives.
2. Analyst: produce structured narrative objects.
3. Editor: rewrite in plain investment language.
4. Distribution Adapter: map narrative object to platform blueprints, assign narrative stage, and select CTA.
5. Risk: attach invalidation and confidence.
6. Publisher: format for Website/X/ChiefEditorX/Subreddit.
7. Verifier: quality gates + endpoint/renderability checks.
8. Governor: approve or block with remediation.

## Distribution Adaptation Requirements
- Canonical narrative object required for all social outputs.
- Enforce platform-native blueprints (X/Telegram/Reddit).
- Attach continuity link and “what to watch next” trigger.
- Use a single website CTA from the approved library.
- No copy-paste reuse across platforms.

Reference: `docs/SOCIAL_DISTRIBUTION_SYSTEM.md`.

## Platform QA Gates (pre-publish)
- Length guardrails (X 275 chars; Telegram 90–160 words; Reddit 180–260 words).
- Tone: concise, analytical, non-hype.
- Evidence links required where claims or projections appear.
- Verified human detail required (ledger ID + source URL).
- Non-duplication across platforms within the same cycle.

## Cadence
- Morning cycle 06:30
- Evening cycle 18:30
- Reliability loop every 2h

## Publish States
- draft
- reviewed
- approved
- published
- verified

## Block Conditions
- missing mandatory narrative fields
- duplicate wording across left-right panels
- no claims on front page
- renderability failed
- missing verified human detail (ledger ID + source URL)
- missing continuity link or next-trigger statement
- missing CTA or multiple CTAs
- evidence links missing where claims or projections are present
- cross-platform near-duplication within the same cycle
