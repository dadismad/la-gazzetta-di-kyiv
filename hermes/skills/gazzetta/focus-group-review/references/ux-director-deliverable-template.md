# UX Director Deliverable Template

A standardized output structure for Senior UX Director (Bloomberg/FT level) reviews. Use when the user asks for a professional UX audit, Phase 1/2 review, or comprehensive product evaluation. This is the deliverable format — pair with the `focus-group-review` skill's 5-phase pipeline for the *process*, use this template for the *output*.

## When to Use

- User asks for "UX review," "audit through professional eyes," "comprehensive evaluation"
- After running a multi-persona focus group (or synthesizing existing findings)
- Before significant design/IA changes to establish baseline

## Deliverable Structure

### 1. UX SWOT Analysis
Four-quadrant assessment. Strengths and Weaknesses are internal (your control). Opportunities and Threats are external (market/competitive).

**Strengths:** What genuinely works. Name specific elements (`#divergenceHero`, `.teaser-card`) and why they succeed. Back with persona evidence: "5/5 personas praised X."

**Weaknesses (RANKED):** Critical first. Each entry needs: severity label (CRITICAL/HIGH/MEDIUM/LOW), personas flagging it, citation evidence. Use a table format:

| Rank | Weakness | Severity | Personas | Evidence |
|------|----------|----------|----------|----------|
| 1 | ... | CRITICAL | 5/5 | ... |

**Opportunities:** What's the growth vector? Where's the untapped audience segment? Name the transformation path ("Closing the 55yo gap from 5.8→7.5 doubles addressable audience").

**Threats:** Competitive, regulatory, reputational. Be specific — "Zero settled track record is existential — if competitor X launches with verifiable track record."

### 2. Information Architecture Audit

Include two things:

**A) Current IA Map (ASCII or structured outline)**
```
┌─ MASTHEAD ─────────┐
│ [section] [section] │
├─ HERO ─────────────┤
│ stat | stat         │
├─ MAIN (2-col) ─────┤
│ LEFT         │ RIGHT│
│ INTEL        │ Sent │
│ Teaser ×184  │ SNAP │
│ ALPHA        │ NAV  │
└─────────────────────┘
```

**B) What's Broken**
Numbered list of specific IA failures. Focus on:
- **Comprehension cliffs** — where a user goes from "I understand" to "I'm lost" without a bridge
- **Dead zones** — sections that promise content but deliver empty/Loading/Absent
- **Mislabeled sections** — label says one thing, content says another
- **No cross-page state** — "where am I?" disorientation
- **Invisible taxonomies** — INTEL vs ALPHA has no visual differentiation

### 3. TOP 5 UX Bottlenecks

Ranked by user impact. Each needs:
- **What** — specific CSS selectors/classes/pages
- **Where** — exact element location (`.teaser-headline`, `#colAlpha`, `/about`)
- **WCAG/best practice violation** if applicable ("10px fails AA minimum of 16px")
- **User impact** — persona-specific: "55yo Retail scored 5.8 — primary driver was illegibility"
- **Fix cost** — honest time estimate: "Changing 4 CSS classes = 10 minutes"

### 4. Fix Priority Matrix

Four quadrants:

| Quadrant | Issue | Effort | Impact |
|----------|-------|--------|--------|
| **URGENT (today)** | Remove broken Loading states | 20 min | Trust restored on 100% of loads |
| **HIGH (this week)** | ... | 2 hours | ... |
| **MEDIUM (this sprint)** | ... | 4 hours | ... |
| **LOW (backlog)** | ... | 8 hours | ... |

Rule: every URGENT item must be fixable in <1 hour. If it takes longer, it's HIGH.

### 5. Quick Wins

3 changes, <1 hour each, maximum perceived improvement per minute.

Each quick win gets:
- **Title** (e.g., "Font Size Bump")
- **Time estimate** (e.g., "15 minutes")
- **What to change** — exact CSS selectors, file paths, or text content
- **Impact** — quantified score improvement estimate (e.g., "55yo Retail jumps 5.8 → 6.8")

### 6. Long-term UX Roadmap

6-month vision. Month-by-month with:
- Specific deliverables (not vague "improve UX")
- Target scores after each phase
- One North Star metric (e.g., "when 55yo Retail = Busy Pro, the product is ready")

Structure:
- **Month 1** — Trust Foundation: fix broken/Loading/empty pages, WCAG compliance
- **Month 2** — Comprehension Layer: glossary, TL;DR bars, label simplification
- **Month 3** — IA Consolidation: unified nav, visual taxonomy, cross-page state
- **Month 4** — Credibility: track record milestones, server-side persistence
- **Month 5** — Daily Habit: morning scan, alerts, personalization
- **Month 6** — Scale & Monetize: freemium, API, performance

## Tone & Stance

- **No diplomacy.** This is a Bloomberg/FT-level review, not a friendly suggestion. Use "this is broken," "this is a trust killer," "this must be fixed today."
- **Cite specific elements.** Never say "the font is too small." Say "`.teaser-headline` at 12px fails WCAG AA."
- **Score everything.** Every component gets a number. The gap between segment scores is your argument.
- **The Busy Pro vs 55yo Retail delta IS your thesis.** A site that works for insiders but not newcomers is halfway there — the rest is comprehensibility.

## Known Pitfalls

- Don't produce a UX report without visiting the live site. Focus group findings alone are historical artifacts — current state may differ.
- Don't recommend "make it better." Every recommendation must have: what to change + where it lives + how long it takes.
- Don't skip Quick Wins. A roadmap with no "fix this in 20 minutes" section signals the team has no quick momentum.
- Don't underestimate the trust impact of dead pages. A single `/about` page with no content can undo $100K of design work.
