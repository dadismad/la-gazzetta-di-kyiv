# Retail/Degen UX Audit — Proven Persona Combo

**Proven:** v25.11, June 2026  
**Context:** Full UX audit of Gazzetta di Kyiv across all 8 nav-linked pages  
**Result:** 10 consensus issues found, 4 critical bugs fixed, 6 pending

## Persona Roster (5 personas, Batch 1)

| # | Persona | Role | Key Questions |
|---|---------|------|---------------|
| 1 | **Degen Crypto Trader** | Phone-trader UX, actionable signals | "Can I trade on this in 15 seconds?" |
| 2 | **55-Year-Old Retail Investor** | Credibility, readability, over-50 UX | "Would my broker recommend this? Are fonts readable?" |
| 3 | **UX Designer (Robinhood/Public.com)** | Grandma-test label audit | "Does every label pass the grandma test?" |
| 4 | **Busy Professional** | 10-second value test, scannability | "What concrete fact did I learn in 10 seconds?" |
| 5 | **Design-Sensitive Reader** | Pixel-level design audit, typography | "Is the design system consistent? What's off-brand?" |

## Batch 2 (supplementary, run after Batch 1)

| # | Persona | Focus |
|---|---------|-------|
| 6 | **Mobile-First Reader** | Responsive at 390px, tap targets |
| 7 | **Skeptical Journalist** | Jargon hunt, straw-man detection |
| 8 | **Logic Professor** | Container integrity, taxonomy consistency |

## Spawn Pattern

```js
delegate_task(tasks=[
  {goal: "Degen Crypto Trader: audit all 8 pages for phone-trader UX...", toolsets: ["browser"]},
  {goal: "55yo Retail Investor: audit all 8 pages for credibility, readability...", toolsets: ["browser"]},
  {goal: "Retail UX Designer: grandma-test audit of all 8 pages...", toolsets: ["browser"]},
])
// Wait for results, then run Batch 2
delegate_task(tasks=[
  {goal: "Busy Professional: 10-second value test on all 8 pages...", toolsets: ["browser"]},
  {goal: "Design-Sensitive Reader: pixel-level audit...", toolsets: ["browser"]},
])
```

## Key Findings from June 2026 Audit

### Consensus Issues (3+ personas)
- PDR acronym unexplained (30+ occurrences) — all 5
- Track page: 0 settled positions — all 5
- Font sizes too small (H1=16px, nav=11px) — 4/5
- FIXED_INCOME raw DB key leaked — 3/5
- LONG/SHORT instead of BUY/SELL — 3/5
- EN/RU buttons 1998 HTML styling — 3/5

### Pages Ranked by Quality
1. Signal (9.3/10) — "Stories: 0 / Flows: 3 ↑ / Trades: ↓" format
2. Trades (9.0/10) — entry/stop/target at a glance
3. Horizon (8.7/10) — They Say/Reality + THE PLAY format
4. Stories (7.7/10)
5. Homepage (7.3/10)
6. Flow Nodes (5.3/10) — phone-unfriendly SVG
7. Flows (4.3/10) — empty containers
8. Track (3.0/10) — premature launch

### Top Praise
"They Say vs Reality" format is the site's secret weapon — every persona praised it.

### Top Complaint
The Flows page promises data but delivers empty containers and dash placeholders.

## When to Use
- User says "review the site," "UX audit," "look through different lenses"
- After major design/content changes
- When user expresses dissatisfaction with how the site "feels"
- Before launching to retail/degen audience
