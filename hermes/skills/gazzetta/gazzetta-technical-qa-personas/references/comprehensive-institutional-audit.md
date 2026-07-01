# Comprehensive Institutional Audit Framework v1.0

Seven independent audit streams, each with a dedicated persona, structured checklist, and hard pass/fail criteria. Run in parallel batches of 3 (max concurrency).

## Streams

1. **SRE (Infrastructure & DevOps)** — DNS, TLS, CDN, GCS, data files, SPA routes, VM/pipeline, security headers. 43 checks across sections 1.1-1.8.
2. **QA (Frontend Engineering)** — JS health, CSS rendering, DOM integrity, trade thesis rendering, source attribution. 39 checks across sections 2.1-2.5.
3. **UX Writer** — First impression, core metric clarity, data labeling, zero states, trust signals, jargon audit, PM trust scorecard. 7 dimensions rated 1-10.
4. **Mobile Designer** — Layout integrity, readability, scrolling/navigation at 390px/480px/768px. 17 checks across sections 4.1-4.3.
5. **Data Engineer (Pipeline)** — Data freshness, data integrity, trade thesis quality, capital volume accuracy, ingestion pipeline health. 24 checks across sections 5.1-5.5.
6. **A11y Specialist** — Automated audit, keyboard navigation, screen reader readiness. 17 checks across sections 6.1-6.3.
7. **Product Manager (Synthesis)** — Completeness, performance, cross-browser, documentation, client-ready checklist. Weighted composite of streams 1-6.

## Execution Protocol

- **Phase 1:** Spawn streams 1-3 in parallel (batch 1), then 4-6 (batch 2). Stream 7 synthesized from 1-6 results.
- **Phase 2:** Triage every finding: P0 (blocks trust), P1 (degrades appearance), P2 (best practice), P3 (nice-to-have).
- **Phase 3:** Execute P0 fixes immediately, P1 in priority order. File P2/P3 as GitHub issues.
- **Phase 4:** Re-audit streams 2, 3, 7 after P0/P1 remediation.

## Key Pitfall: Diagnose with Data Before Rewriting Prompts

When a field is missing from LLM output (e.g., trade_thesis in stories.json), check the actual CDN data first before assuming a prompt logic error. `curl -sk URL/data/stories.json | python3 -c "..."`. The data distribution tells you whether the problem is token starvation (field entirely absent from most responses), prompt logic (field set to NEUTRAL), or JSON parsing (field dropped in assembly). Rewriting prompts without checking data causes destructive surgery on functioning prompt logic.
