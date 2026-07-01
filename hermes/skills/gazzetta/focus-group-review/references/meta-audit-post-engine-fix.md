# Meta-Audit Pattern — Post-Engine-Fix Review (June 2026)

## When to use
After a major data engine rebuild or pipeline architecture change. This is a comprehensive 5-phase review that validates the fix was real, the data is genuine, and the editorial output matches the new data quality.

## Phase A: Visual Sweep (15 min)
- Navigate ALL tabs with fresh cache-bust URL (`?_v=N`)
- `browser_console` for JS errors, gold heading color, story count, body length
- Verify GCS file matches VM build (timestamp, size, gold heading override)
- Check: sidebar capital values changed, GAP distribution is diverse, story count matches

## Phase B: Content/Writing Audit (3 personas, browser tools)
- **Chief Editor**: Headline grading A-F (20 random), They Say/Reality sharpness, straw-man detection, editorial voice score
- **Skeptical Journalist**: Hunt for straw-men, GPT-isms, template rot, source attribution quality, banned phrase detection
- **First-Time Reader (50+, non-finance)**: Comprehensibility, jargon density, trust signals, likelihood to return

## Phase C: Publishing Strategy (2 personas, context-fed)
- **Growth PM**: Conversion funnel, trust signals, competitive positioning, OG tags, CTAs, shareability
- **Portfolio Manager (Mike Green)**: Data integrity, capital flow accuracy, would-I-allocate-capital test

## Phase D: Technical Verification
- Pipeline: 10/10 steps, test gate 156/156
- Capital variance: unique values > 3 across >10 stories
- GAP distribution: no single value accounts for >50% of stories
- Deploy: GCS file fresh, gold headings at #8C7123
- Banned phrase check: 0/20 most recent headlines contain banned patterns

## Phase E: Consolidation
- Aggregate all persona findings into: Review Report, Suggestions Report, Implementation Plan
- Map every finding to a specific file and line number
- Prioritize: P0 (data/trust) → P1 (editorial/accessibility) → P2 (growth/UX)

## Proven persona prompts

### Skeptical Journalist (straw-man hunter)
"Find 3 words or phrases that could mean anything. What's the most concrete sentence? Does the 'They Say' quote actual media narratives verbatim or invent an opponent? Hunt for GPT-isms and template rot. Count identical headline patterns."

### Chief Editor (post-engine-fix)
"Grade 20 headlines A-F. Check if They Say/Reality pairs are differentiated. Check if editorial quality matches the new data quality. Are high-GAP stories getting better headlines than low-GAP stories? Rate editorial voice 1-10."

### First-Time Reader (50+, non-finance)
"Can a smart non-finance person find value? Count unexplained terms per card. Check sentence length. What makes you trust/distrust this? Would you return?"

## Key metrics to extract
| Metric | Pre-fix baseline | Post-fix target |
|--------|-----------------|-----------------|
| GAP distribution | 98.9% at single value | Natural variance across 0-85 range |
| Capital values | All identical ($100M) | Multiple unique values, TIER_1/2/3 differentiation |
| Banned headlines | 55+/200 | <5/20 |
| They-Say quality | Vague paraphrase | Source-attributed with specific claim |
| Deploy freshness | Stale (days old) | <10 min |
| Gold heading contrast | #D4AF37 (1.99:1 fail) | #8C7123 (3.0+:1 pass) |
| Test assertions | 155 | 156 (capital variance check) |
| Pipeline steps | 8 (classify/calc_capital missing) | 10 (all active) |
