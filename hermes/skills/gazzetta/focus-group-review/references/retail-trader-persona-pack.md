# Retail Trader Persona Pack — Retail UX Audit

Proven combination for evaluating a financial intelligence site through retail/non-professional eyes. Used June 2026 for Gazzetta di Kyiv v22.7 hero stat overhaul.

## The Three Personas

### 1. Degen Retail Crypto Trader
**Profile:** Trades meme coins, watches on-chain flows, 30-second attention span. Needs actionable signals FAST. Judges everything by "can I trade on this in 5 seconds?"

**Key questions:**
- What do you understand in the first 10 seconds?
- What does the confidence indicator tell you to DO?
- Which hero stat matters most? Least?
- What's the biggest blocker to daily use?
- Rate trade-idea extraction speed: 1-10

**Typical findings:** Flags jargon-heavy labels, slow UX, lack of one-click action. Praises direct trade ideas. Hates editorial volume metrics ("who cares how many articles?").

### 2. 55-Year-Old Retail Investor
**Profile:** Started trading during COVID. Understands basic concepts but gets confused by institutional jargon, ratios, complex percentages. Not stupid — just wants clear explanations.

**Key questions:**
- What's immediately confusing? Point to specific elements.
- What do you THINK "Directional alignment across N flows: X%" means?
- Would you understand "PDR gauge," "ATR-based stops," or "+2.3× velocity" without a glossary?
- What would make you feel smart using this site instead of confused?
- Rate overall comprehensibility for non-professional: 1-10

**Typical findings:** Identifies specific jargon walls, catches contradictory signals (inflow + SELL), demands plain-English annotations. Praises THEY SAY/REALITY format and concrete trade ideas. Finds methodology links hidden/buried.

### 3. UX Designer for Retail Financial Products
**Profile:** Product/UX designer specializing in financial dashboards for retail users (Robinhood, Public.com level). Judges information architecture, labeling, onboarding.

**Key questions:**
- Is the confidence indicator label better or worse after the change? What's the BEST label?
- Are expandable flow items (click to see linked story + position bet) intuitive for retail?
- What's the single highest-impact UX fix for retail usability?
- Are the 5 hero stats the RIGHT 5 for retail? Which would you replace/rename?
- Rate retail UX readiness: 1-10

**Typical findings:** Proposes specific label rewrites, identifies onboarding gaps, suggests information architecture fixes. Evaluates visual hierarchy. Proposes "signal bar + plain-English label" combos.

## When to Use
- User says "review through simple people's eyes" or "dead gen traders"
- Evaluating hero stats, confidence indicators, or data labels for retail comprehension
- Before any label/text change that affects first-time visitor understanding
- When user complains "this site is only for pros"

## Spawn Pattern
```python
delegate_task(tasks=[
  {"goal": "Degen trader evaluation of {URL}...", "context": "...", "toolsets": ["browser"]},
  {"goal": "55-year-old retail investor evaluation of {URL}...", "context": "...", "toolsets": ["browser"]},
  {"goal": "UX designer for retail financial products evaluating {URL}...", "context": "...", "toolsets": ["browser"]},
])
```

## Expected Output
All three will converge on:
- Unclear labels that need simplification
- Jargon that needs explanation
- Information overload areas
- Missing onboarding/education
- The trade-idea flow (does it work in seconds?)

They will diverge on:
- Which stats matter most (degen wants signal, 55yo wants clarity, UX wants information architecture)
- How much jargon is acceptable
- What the "right" label should be

## Key Finding from June 2026 Session
All three personas independently flagged the "Directional alignment across N tracked flows: X%" label as incomprehensible. The UX designer proposed "Flow conviction: X% ↑" with directional arrow — implemented as v22.7. All three flagged "Total at stake" as useless/confusing — replaced with "Track record."
