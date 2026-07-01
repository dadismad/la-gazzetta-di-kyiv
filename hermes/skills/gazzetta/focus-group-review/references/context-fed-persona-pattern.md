# Context-Fed Persona Pattern (Proven June 2026)

## When to Use Browser Tools vs Context-Fed

This session confirmed the pattern from the v3.0 skill spec: analytical personas
(Logic Professor, Portfolio Manager doing data-only review, Machiavellian Strategist,
Chief Editor) MUST NOT receive browser tools. They iterate endlessly on
`browser_console` calls, burn 971K-1.28M tokens, and hit `max_iterations` with
no result (2 of 3 failed in June 2026 baseline).

## Proven Pattern (Phase C Design Audit, June 2026)

**Batch: 3 personas, all context-fed, no browser tools**
- Degen Crypto Trader: context-fed, completed in 88s, 184K input tokens
- Portfolio Manager ($5B AUM): context-fed, completed in 87s, 286K input tokens
- Machiavellian Strategist: context-fed, completed in 104s, 113K input tokens

All 3 returned structured, specific, actionable design recommendations.
Zero iteration loops. Total cost: ~584K input tokens for the batch.

## Pre-Extraction Checklist
Before spawning an analytical focus group, extract:

1. **Site capabilities** — narrative taxonomy, data sources, current UX problems
2. **Current metrics** — story count, GAP range, capital coverage, sidebar state
3. **Product output** — a real GapFire dispatch example, trade thesis format
4. **Known issues** — from previous audits/bug reports
5. **Target user profile** — explicit persona description with behavioral traits

Feed all as structured `context` in the `delegate_task` call. Give `toolsets: []`.

## When Browser Tools ARE Necessary
Only for visual-inspection personas: Senior Web Designer (needs `getComputedStyle`),
UX Director (needs `browser_snapshot`), Design-Sensitive Reader (needs visual audit).
These personas MUST have `toolsets: ["browser"]`.
