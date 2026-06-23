# Developer Indicator (Contradiction Score) Audit — June 2026

## Issue
User called DEVELOPING indicator "incomprehensible." Focus group (Financial Product Reviewer + UX Writer) confirmed:
- "DEVELOPING 50" reads as story status, not contradiction strength
- All 10 scores cluster 45-60 — fake distribution, no card scores above 60 or below 40
- Tooltip invisible on mobile, no scale context
- Zero color differentiation between tiers (CSS existed but badges hidden on collapsed cards)

## Fix Applied (v22.12)

### Labels Changed
| Old | New | Color | Meaning |
|-----|-----|-------|---------|
| CONTRADICTED 67 | MAX TENSION 67/100 | Red `#DC2626` | Narrative inverts reality |
| DIVERGENT 55 | HIGH TENSION 55/100 | Amber `#B45309` | Material gap — opportunity |
| DEVELOPING 50 | BUILDING 50/100 | Blue-gray `#4B6B8A` | Early tension forming |
| ALIGNED 25 | CONSENSUS 25/100 | Muted | Low edge, narrative matches |

### Code Locations Changed
- `site/app.js` line 834-840: `tierLabel` and `tierTitle` strings
- `site/app.js` line 862: score display `${cs}` → `${cs}/100`
- `site/app.js` line 1390-1401: patchStoryCard equivalent updates

### Remaining Issue
Scores still cluster 45-60. The contradiction scoring algorithm (`calcContradictionScore`) needs recalibration to produce a genuine spread. Root cause: the algorithm relies on regex word-matching that produces similar results for most stories. Fix: increase divergence bonus weight when flow direction contradicts narrative tone, widen the contrast-marker scoring range.

## Audit Persona Combination (proven June 2026)
For contradiction score / indicator audits:
1. **UX Writer** — catches ambiguous labels, missing scale context
2. **Financial Product Reviewer** — catches fake distributions, rates insight value
3. **55-Year-Old Retail Investor** — catches incomprehensibility for non-pros
