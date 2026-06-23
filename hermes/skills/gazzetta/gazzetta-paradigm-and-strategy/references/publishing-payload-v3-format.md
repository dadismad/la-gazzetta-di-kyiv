# Gazzetta Publishing Payloads — v3.0 Format Specs

Derived from `docs/SOCIAL_DISTRIBUTION_SYSTEM.md` and `docs/CROSS_CHANNEL_EDITORIAL_SOP.md`.
Implemented in `scripts/prepare_publish_payloads_v2.py` (v3.0).

---

## Telegram — Rapid Intelligence Terminal

> **⚠️ SUPERSEDED for top-2 stories (June 22, 2026):** The Chief Editor evaluation prescribed a new GapFire Dispatch format for the top 2 Telegram stories. See `gazzetta-newspaper-engine` skill, reference `editorial-quality-gates-v3.md`. This 6-block format may still serve lower-priority stories.

**Target:** 50–160 words.
**Cadence:** 2x/day (06:30, 18:30) via `gazzetta-hourly-narrative-review` cron.

### Structure (6 blocks):
```
1. OPENING SIGNAL (1 line)
   — What changed. Direct claim from the lead setup's thesis.

2. IMMEDIATE IMPLICATION
   — Regime label + risk state. What this means for positioning now.

3. ACTIONABLE INTERPRETATION (1–3 bullets)
   — Top 3 setups, each: title + thesis in ~90 chars.
   — If no setups: "Monitor {regime_label} for signal evolution."

4. VERIFIED HUMAN DETAIL
   — From `data/human_detail_ledger.md`.
   — Format: "¹ {detail} (ledger: {id}, source: {url})"

5. CONTINUITY LINK + NEXT TRIGGER
   — "Continuity: via {homepage} | {window} invalidation: {trigger}"
   — Window from top contradiction's `invalidation_window`.

6. CTA
   — Single CTA from `data/cta_library.json` (random, avoid last 7).
   — Falls back to: "Full briefing and positioning map: {homepage}"
```

### Guardrails:
- No copy-paste between platforms in same cycle.
- Evidence links required where claims/projections appear.
- Must not exceed 160 words; under 50 warns.
- Post logged to `data/social_distribution_log.jsonl`.

---

## Reddit — Narrative Laboratory

**Target:** 140–260 words.
**Cadence:** 2x/day (06:45, 18:45) via `gazzetta-agentic-nlp-guarded-autopost-8h` cron.

### Structure (8 blocks):
```
1. CONTEXT
   — "**Regime:** {label} ({risk_state})"
   — Data provenance: timestamp, source count, setup/contradiction counts.

2. DOMINANT NARRATIVE
   — Lead thesis + key actors (max 4) + incentives (max 3).

3. CONTRADICTION (explicit — key differentiator)
   — "Consensus says *{claim_a}*, but *{claim_b}*."
   — Urgency level. If no contradiction: "Monitor for divergence signal."

4. SECOND-ORDER IMPLICATIONS
   — Retail execution tips (max 2 from setup).
   — Cross-asset: historical pattern for this regime.

5. STRATEGIC INTERPRETATION (24–72h + invalidation)
   — Base/Bull/Bear probabilities.
   — Invalidation trigger (primary + secondary if available).

6. VERIFIED HUMAN DETAIL
   — Same format as Telegram.

7. DISCUSSION PROMPT
   — "What signals would falsify or strengthen this {title} thesis in your framework?"

8. EVIDENCE + CTA
   — 3 links: Homepage, Setups API, Contradictions API.
   — CTA from library (random, avoid last 7).
   — MUST end with: READY_FOR_DEVVIT_POST
```

### Guardrails:
- Post as r/LaGazzettadiKyiv subreddit.
- Devvit app deploys: `tools/autopost_publish_install.sh`.
- Must not exceed 260 words; under 140 warns.
- Post logged to `data/social_distribution_log.jsonl`.

---

## CTA Library

Location: `data/cta_library.json`

Rotation rule: track last 7 posts per platform in `social_distribution_log.jsonl`.
Pick random from available pool. If all exhausted, reset.

Telegram pool:
- "Full briefing and positioning map: {website_url}"
- "Narrative exposure dashboard: {website_url}"
- "Detailed contradiction map: {website_url}"
- "Full 24–72h positioning note: {website_url}"
- "Complete intelligence brief: {website_url}"

Reddit pool:
- "Full narrative dossier and data links: {website_url}"
- "Complete contradiction map: {website_url}"
- "Full cross-asset breakdown: {website_url}"
- "Detailed positioning framework: {website_url}"
- "Full intelligence brief and sources: {website_url}"

---

## Human Detail Ledger

Location: `data/human_detail_ledger.md`

Table format with columns: id | subject | verified_detail | source_url | verified_at | relevance_to_narrative | usage_notes

5 seed entries as of 2026-06-02: HD-001 through HD-005 covering OpenAI, ECB, Ukraine Reconstruction, Oil Markets, BRICS Summit.

All entries must be: publicly verifiable, non-defamatory, time-anchored, relevant to narrative.
