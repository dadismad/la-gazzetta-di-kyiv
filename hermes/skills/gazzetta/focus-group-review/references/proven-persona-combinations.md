# Proven Persona Combinations — Gazzetta di Kyiv Focus Groups

Derived from 9-persona, 4-round focus group audit (June 2026).

## Full Persona Roster Used

| Persona | Round | Best For | Key Insight |
|---------|-------|----------|-------------|
| **Skeptical Journalist** | R1 | Content audit, jargon detection, credibility | "Only show capital flow when it contradicts consensus" |
| **Design-Sensitive Reader** | R1 | Typography, layout, visual hierarchy | "Same palette, serif values + Inter labels, gold-left-border" |
| **Competitive Reader** | R1 | Differentiation, competitive positioning | "PDR gauge — one metric no competitor publishes" |
| **Retail Trader (CFA fail)** | R2 | Bet&Benefit audit, actionable signal | "2/10 — decoration with potential. Kill narrative-driven %" |
| **Crypto Trader** | R3 | Crypto-native signals, headline aggression | "Zero crypto content. Add stablecoin supply, funding rate, netflow" |
| **Impatient Retail Trader** | R3 | Mobile-first, scan-ability, trade extraction | "6/10. Move THE PLAY to top of card" |
| **Sarcastic Copywriter** | R3 | Headlines, voice, language | "5.6/10 headlines. Embed projection IN headline text, not separate pill" |
| **Simple Idiot $15K** | R4 | Accessibility, FOMO triggers, dopamine | "4/10. Needs BUY NOW button, Bitcoin at top, no jargon" |
| **Chief Editor Bitch** | R4 | Quality gate, design shredding, trust | "Kill Bet&Benefit name. Kill 2h projections. Kill filter bar." |
| **Logic Professor** | R5 | Container integrity, logical coherence, taxonomy consistency, fallacy detection, information architecture | "The flows container is showing story narratives — container boundary violation. Hero story count doesn't match the DOM. These are logical leaks, not just design bugs." |

## Proven Combinations by Task Type

### Container Integrity / Architecture Audit (use when containers bleed)
1. **Logic Professor** — maps every container, checks for cross-contamination, traces premise→conclusion chain, audits taxonomy consistency across containers, scores architecture coherence 1-10
2. **Skeptical Journalist** — validates content placement: does each container hold what its title promises?
3. **Senior Web Designer** — inspects DOM structure: are data attributes scoped correctly? Are there selector collisions?

### Complete Site Audit (use all 9 in rounds of 3)
R1: Skeptical Journalist + Design-Sensitive Reader + Competitive Reader
R2: Retail Trader (CFA fail) — solo deep-dive on sidebar
R3: Crypto Trader + Impatient Retail Trader + Sarcastic Copywriter
R4: Simple Idiot $15K + Chief Editor Bitch — final gate

### Palette / Design System Change
1. **Metallic Design Specialist** — metallic finishes, hex values, contrast ratios
2. **Information Density Specialist** — measurements, compression targets, readability safeguards
3. **Design-Sensitive Reader** — visual hierarchy, typography coherence

### Voice / Language Audit
1. **Sarcastic Copywriter** — headline scoring, register calibration
2. **Skeptical Journalist** — jargon hunting, banned phrases
3. **Chief Editor Bitch** — final shred, "would you hire this editor?"

### Feature Integration (e.g., capital flow reporting)
1. **Skeptical Journalist** — content placement, trust evaluation
2. **Design-Sensitive Reader** — visual fit, CSS-level detail
3. **Competitive Reader** — differentiation from Bloomberg/FT/Economist

### Retail Trader Readiness
1. **Impatient Retail Trader** — mobile-first, 5-second trade extraction
2. **Simple Idiot $15K** — accessibility, FOMO, dopamine
3. **Crypto Trader** — crypto-native signals, degen language

### Hero Stat / Confidence Label Audit (proven June 2026)
When a stat label confuses retail users — especially percentages like "model confidence" or "directional alignment" — use this three-persona pack. Proven in the Gazzetta v22.7 confidence overhaul where all 3 unanimously agreed the old label was incomprehensible.

1. **Degen Retail Crypto Trader** — 30-second attention span, trades meme coins, needs actionable signals FAST. Key questions: What do you understand in 10 seconds? What does the confidence number tell you to DO? Which hero stats matter vs are useless? Rate trade-extraction speed 1-10.

2. **55-Year-Old Retail Investor** — Started during COVID, understands basics but gets confused by institutional jargon and complex percentages. Not stupid — wants clear explanations. Key questions: What's immediately confusing? What do you THINK the metric means? Would you understand PDR/ATR/velocity without a glossary? Rate comprehensibility 1-10.

3. **UX Designer for Retail Financial Products** — Specializes in dashboards for non-professionals (Robinhood, eToro, Coinbase). Key questions: What's the BEST label for this stat? Is the expandable format intuitive? What's the single highest-impact UX fix? Are we showing the right metrics? Rate retail UX readiness 1-10.

**Consensus they produced:** "Directional alignment across N tracked flows: X%" → incomprehensible to all 3 → renamed "Flow conviction: X% ↑". "Total at stake" → confusing/scary → replaced with "Track record". Flow positioning all "hedging" → credibility destroyed → fixed by deriving from direction+magnitude. This combination catches jargon barriers that professional personas skim past.

## Key Learnings

- **Never fewer than 3 personas per round** — 2 produces groupthink, 4 is dilutive
- **Always include a hostile persona** — the Chief Editor Bitch or Skeptical Journalist who will say "this is shit"
- **The Simple Idiot persona catches things no one else does** — if they can't use it in 3 seconds, it's broken regardless of what the pros say
- **Parallel spawn, sequential review** — all personas hit the live URL simultaneously, then findings are synthesized for consensus/contradiction
- **Independent convergence is the gold standard** — when 3+ personas independently recommend the same thing, it's law
- **Fix critical bugs immediately** — if the focus group finds a rendering bug (JS error, empty container, broken feature), fix and deploy it before writing the report. Don't document a broken site.

---

## Full Site Audit — Professional Lenses (proven June 2026)

This combination covers execution, rigor, UX, and product viability in one pass. Use when the user says "review through different professional lenses" or "audit everything."

1. **Time-Pressed Degen Trader** — visits live URL with browser tools. Evaluates: (1) Concrete tradeable insight in first 15 seconds, (2) Scroll vs bounce factors, (3) Whether cross-container signals help decide fade/follow, (4) What's missing vs CT/ZeroHedge/FinTwit, (5) Overall 1-10 as daily trading resource. Requires browser console inspection of JS functions and DOM structure.

2. **Hedge Fund Macro Analyst** — visits live URL with browser tools. Evaluates: (1) Is capital flow data actionable or decorative — cite specific amounts from page, (2) Does cross-container triangulation add genuine analytical value or just remix data, (3) Weakest analytical link in the chain, (4) What's needed before forwarding to PM, (5) Analytical rigor 1-10 vs sell-side research. Must use browser_console to inspect scoring algorithms.

3. **UX Director (Bloomberg/Stripe/Linear experience)** — visits live URL with browser tools. Evaluates: (1) Visual hierarchy — eye path 1st/2nd/3rd, is it right for financial intelligence, (2) Does layout work at current container count, (3) Is synthesis container visually distinct, (4) Icon correctness per Lucide spec, (5) 3 specific CSS/design fixes ranked by impact. Must use browser_snapshot(full=true) and browser_console.

4. **Senior Web Designer (Goldman Sachs/Bloomberg/Economist level)** — visits live URL with browser tools. Evaluates: (1) CSS execution quality — gradient opacities, shadow weights, border rendering, (2) Responsive breakpoints — does layout hold at 390px/768px/1200px, (3) Color application — are gold/green/red used correctly or garishly, (4) Information density balance, (5) DOM rendering bugs — NaN values, empty containers, selector mismatches, sizing inconsistencies, (6) 3 specific CSS fixes ranked by impact. Must use browser_snapshot(full=true), browser_console to inspect rendering, and browser_scroll to check all containers. This persona inspects the actual code, not just the design concept.

## Divergent Persona Pack (high-conflict review, proven June 2026)

When the user wants fresh eyes or says "different peculiar personas," use this pack instead of the standard professional lenses. These personas have STRONG conflicting values — they will produce non-correlated feedback:

1. **Machiavellian Strategist** — evaluates everything through power, perception, and information asymmetry. Believes media's purpose is making the reader feel smarter than everyone else. Key questions: Does the site make you feel you have information others don't? What's the most cunning design choice? What would a rival steal? Does the fox/Machiavelli symbolism feel earned? This persona catches strategic positioning issues the professional personas miss.

2. **Aesthetic Purist / Minimalist** — believes every pixel must justify its existence. Hates visual clutter, unnecessary frames, decorative fluff, and excessive micro-icons. Rates minimalism 1-10 (10 = Apple-level restraint). Key questions: Does the frameless design hold? Is every SVG justified? What's the most visually offensive element? This persona catches CSS leaks that break design contracts (e.g., gold box-shadow on a "frameless" section).

3. **Proud Italian Diaspora Reader** — cares deeply about Italian cultural representation. Suspicious of brands using Italian names without earning them. Rates cultural authenticity 1-10. Key questions: Does the site feel Italian or is the name the only Italian thing? Is the design language Italian (Bodoni, warm carta tones, architectural proportion) or generic? Would you share this proudly with your Italian community? This persona catches superficial branding that other personas ignore.

These three produce HIGH conflict feedback — the Machiavellian values cunning, the Purist hates decoration, the Italian demands cultural depth. Use when the user says "different personas" or "fresh perspectives." They will find things the standard professional roster misses.

**Aggregation template for the report:**

```markdown
## Aggregate Scores
| Persona | Score | Biggest Praise | Biggest Complaint |

## Critical Bugs Found
- [bug]: root cause + fix applied + deployed status

## Consensus Issues (2+ personas)
| # | Issue | Personas | Fix |

## Contradictions Across Lenses
- [persona A] says X; [persona B] says Y → resolution:

## Priority Fix List
1. [critical bug fix — deploy immediately]
2. [high-impact consensus item]
3. ...
```
