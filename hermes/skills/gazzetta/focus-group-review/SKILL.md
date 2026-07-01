---
name: focus-group-review
description: Multi-industry focus group for reviewing design, content, and user experience. Spawns reader-persona agents from 14 industries (35+ personas) who audit a live URL through 4 lenses (top-down, bottom-up, source trust, competitive threat) and return structured feedback with combined scoring. Use before any design/content decision that affects user perception.
version: 3.1.0
author: Hermes Agent
created_by: agent
---

# Focus Group Review — Multi-Industry Pipeline v3.0.0

A repeatable workflow for user-perspective design and content audits. Spawns multiple reader-persona agents from **14 industries (35+ personas)** who visit a live URL and evaluate it through **4 lenses** (top-down, bottom-up, source trust, competitive threat). Aggregate their findings into actionable changes with **weighted combined scoring** (40% top-down / 60% bottom-up).

## Multi-Industry Focus Group Pipeline (v3.0.0)

Every focus group now flows through a **5-phase pipeline** with **35+ personas across 14 industries** and **weighted top-down/bottom-up evaluation**. No ad-hoc reviews. See full spec at `docs/focus-group-pipeline-spec.md`.

### Phase 1: PRE-REVIEW — Data Freshness & Readiness
- **VISUAL-FIRST SWEEP (MANDATORY v24.0+):** Before ANY code inspection, use `browser_navigate` + `browser_vision` on ALL nav-linked pages (homepage + every page in the navigation bar). Code-only debugging misses: debug grid numbers rendered as visible text, keyboard hints in production, stuck loading states, truncated text, duplicate elements. Curl 200 ≠ page works. See `references/corrupted-html-line-numbers.md` for detection pattern.
- Check `stories.json` / `flows.json` mtime → must be < 2h old
- Verify source attribution for every story and flow
- Verify live site returns HTTP 200 (`curl -sI "https://storage.googleapis.com/www.lagazzettadikyiv.com/index.html"`)
- Verify CDN has fresh content, not cached stale version (`gsutil cp gs://www.lagazzettadikyiv.com/index.html - | grep '<date-marker>'`)
- Select 10 personas max (5 per batch) from 35+ roster — mix finance/industry/generalist/contrarian
- Record selection rationale

### Phase 2: REVIEW — Multi-Persona Focus Group (2 Batches)

**Batch 1: Initial Scan (5 personas)** — Finance core + industry specialists + contrarian. Spawn in 2 parallel delegate_task calls (max_concurrent_children is typically 3, so split 3+2). Each evaluates through 4 lenses: Top-Down, Bottom-Up, Source Trust, Competitive Threat. **PITFALL:** Attempting all 5 in one delegate_task call fails with 'Too many tasks: 5 provided, but max_concurrent_children is 3'. Always check your effective max_concurrent_children before spawning and split batches accordingly.

**Batch 2: Targeted Investigation (5 personas)** — Fresh perspectives + technical deep-dives + UX. Run AFTER Batch 1 output is collected. If Batch 1 showed strong consensus, deliberately select contrarian personas to maximize contradiction.

### Phase 3: POST-REVIEW — Aggregate & Prioritize
- **Consensus Catalog** — issues flagged by 3+ personas (non-negotiable fixes)
- **Contradiction Map** — where personas disagree (especially interesting: industry splits)
- **Critical Bugs** — rendering errors, broken functionality → MUST fix immediately
- **Combined Scoring** — Top-Down (avg of all persona Top-Down scores) × 0.40 + Bottom-Up (avg of all persona Bottom-Up scores) × 0.60 → PASS (≥8.0) / CONDITIONAL PASS (6.0-7.99) / FAIL (<6.0)
- **Priority-Ordered Fix List** — ranked by severity × consensus count × fix effort (inverse)

### Phase 4: INTEGRATION — Update & Deploy
- Fix critical bugs immediately (do NOT wait for full cycle)
- Apply priority fixes in order
- Update skill knowledge: add new persona combinations, pitfalls, quality gate thresholds
- Update data: fix label quality, stale data, missing sources
- Deploy: `bash /Users/alexstocchi/.hermes/scripts/gazzetta_deploy_to_gcs.sh`
- Verify deploy: check fresh content on GCS

### Phase 5: QUALITY GATE — Verify & Close
- Spawn 2-3 Fresh Eyes personas (NOT used in Phase 2)
- For each fix: is it live? Score 1-10. All ≥ 8/10 → PASS
- Regression scan: any NEW issues introduced by fixes?
- Save pipeline results to `data/quality_gates/history.jsonl`
- If any fix < 7/10 or regression found → loop back to Phase 4
- Archive full pipeline output

**Non-negotiable:** Every focus group MUST complete all 5 phases. Skipping Pre-Review = stale data evaluation. Skipping Quality Gate = regressions reach users. Skipping Post-Review = intelligence lost.

- Before committing a design change that affects the homepage
- When the user expresses dissatisfaction with how the site "feels" or "reads"
- When evaluating typography, color, layout, or attention-capture
- When the user asks about content quality, photo fit, design feel, or "how does this look"— spawn the focus group BEFORE implementing changes, not after. The user's judgment is the instruction; the focus group's judgment is the implementation guide.
- When evaluating image/photo relevance, visual identity, or whether a photo "fits" a story — use the Photo Quality Review combination below. Generic Unsplash pools are not enough; every photo must pass the test: "If you swapped it with another story in the same sector, would it still make sense? If yes, it's too generic."
- **When the user asks for a full site/product audit through multiple professional lenses** — use the Full Product Improvement Cycle below. This is the reusable meta-workflow that covers interpret → review → report → upgrade → execute so the user never has to describe the sequence again.

---

## Full Product Improvement Cycle (Meta-Workflow)

When the user says anything like "review the site through different lenses," "run a focus group and fix what you find," or "audit everything and integrate changes," do NOT just run the focus group — run the full 6-phase cycle:

### Phase 1: Multi-Perspective Interpretation
Before any action, interpret the user's request through 3-4 distinct lenses. Example for "look at the site through different professionals' eyes":
- **Trade execution lens**: what does a degen trader need?
- **Analytical rigor lens**: what would a hedge fund analyst demand?
- **UX/product lens**: what would a design director notice?
- **Adoption/growth lens**: what would a PM building a DAU-based product ship?

### Phase 2: Parallel Focus Group (2 Batches, 10 Personas Max)
Spawn 5 personas in **Batch 1** via `delegate_task` with `browser` toolsets, all pointing at the live URL. Each gets a 4-lens industry-specific prompt. Run in parallel. Collect output, then spawn **Batch 2** (5 more personas) targeting issues from Batch 1 + blind spots.

### Phase 3: Aggregate & Brief Report
Collect all responses. Produce a structured report with:
1. **Aggregate scores** (per persona, with biggest praise + biggest complaint + top-down/bottom-up scores)
2. **Consensus issues** (flagged by 3+ personas — non-negotiable fixes)
3. **Contradictions** (personas disagree — especially note industry splits)
4. **Critical bugs found** (must fix immediately, don't wait for full cycle)
5. **Combined score** (Top-Down × 0.40 + Bottom-Up × 0.60 + PASS/CONDITIONAL/FAIL verdict)
6. **Priority-ordered fix list** (#1 = most critical)

### Phase 4: Fix Critical Bugs Immediately
If the focus group found a rendering bug (empty containers, broken features, JS errors), fix and deploy it BEFORE completing the report. Do not wait for the full cycle.

**Frameless design contracts must be absolute** — if the design language says "frameless" (no shadows, no borders, no radius), every element must comply. A single box-shadow on a "frameless" section breaks the entire contract. The Aesthetic Purist persona catches these leaks. Check every container, card, and section against the design contract before claiming frameless.

**Dynamic data is non-negotiable** — user frustration is guaranteed when a hardcoded number (story count, asset count, confidence %) doesn't match actual data. All visible stats MUST be JS-updated from the data source. Never put a hardcoded digit in HTML that represents a dynamic quantity. Grep the HTML for any hardcoded digit — if it changes over time, make it dynamic.

### Phase 5: Identify Skill/Workflow Gaps
From the report, identify what needs to change at the skill/workflow level:
- New skills needed to prevent recurring issues
- Existing skills that need patching (wrong commands, missing pitfalls)
- Cron jobs that need new quality gates

### Phase 6: Execute Remaining Fixes
Apply fixes in priority order. Re-deploy. Run focus group again on updated URL to verify.

**Pitfall — DON'T skip Phase 4**: If a critical bug is found (empty loading state, broken feature, JS error), fix it immediately. Don't write a 3-page report while the site is broken. Fix → deploy → then report.

**Pitfall — Regex revolving-door in anti-rot guards (June 2026):** When the Chief Editor or Skeptical Journalist persona flags a phrase appearing 5+ times (e.g., "leaves market pricing unchanged"), check the anti-rot regex guard itself — not just the LLM output. In the June 2026 Gazzetta audit, the guard was replacing "fails to move" with "leaves market pricing unchanged" which was ALSO template rot. The guard was a revolving door swapping one rot phrase for another. Detection: grep the REPLACEMENT text in the sanitizer against the ban list. If a banned phrase appears as a replacement string, the guard is poisoning output and must be fixed.

**Pitfall — calcContradictionScore recalculates instead of using JSON field (v27.1, June 2026):** When all personas independently flag identical scores across every story (e.g., "CONSENSUS 30/100" on all 317 stories), the JS `calcContradictionScore()` function is likely recalculating from sparse fields (`they_say`, `reality`, `capital_flow.current_amount`) instead of using the pipeline-authored `story.contradiction_score` field from JSON. The JSON already has accurate scores (typically 47-75 range), but the JS function's baseline of 30 + missing fields = uniform fake output. Fix: add a guard at the top of `calcContradictionScore` to return `story.contradiction_score` directly when it's a valid number. Detection: `document.querySelector('.tier-badge')?.textContent?.trim()` — if all cards show identical tier + score, the JS is recalculating.

**Pitfall — Dual data structure in stories.json (v3.0, June 2026):** When `stories.json` contains both a legacy `containers` dict and an active `all_stories` array, different pipeline scripts may read different structures. `generate_flows.py` reads `containers` (stale, wrong counts). `build_frontend.py` reads `all_stories` (correct). The Capital Flows table and the Stream tab will show different story counts for the same narrative. Detection: compare `containers[<id>].stories.length` against `all_stories.filter(s => s.narrative_id === <id>).length` — any delta > 5 is a dual-structure divergence. Fix: delete the `containers` section or sync it to `all_stories` in `contradiction_synthesizer.py`. The live site uses `all_stories` as its source of truth — the `containers` section is dead legacy.

**Pitfall — story-app.js missing from story.html template (v27.1, June 2026):** Story detail pages (`/story.html?id=...`) may show "Loading intelligence report…" stuck permanently. Check: the story.html template MUST include `<script src="./story-app.HASH.js"></script>` alongside the i18n and app.js scripts. If missing, the story rendering logic (`buildHTML`, `init`, `getStoryId`) never executes. Also check for raw JS rendered as visible text — this means a `<script>` opening tag is missing before an inline IIFE.

**Font size minimum contract (v27.1, June 2026):** Tutorial font sizes are the #1 credibility destroyer for financial intelligence products. The Senior Web Designer persona MUST audit: body < 16px → FAIL, tier-badge < 12px → FAIL, con-score < 12px → FAIL, freshness-ago < 12px → FAIL. 10px text on metadata badges is an instant "amateur" signal — bump to 12px minimum. Body: 16px minimum. Gold (#D4AF37) on white (#FFFFFF) fails WCAG AA at 2.1:1 — flag when found.

## Workflow

### Step 0: Multi-Perspective Interpretation

Before spawning the focus group, interpret the user's request through 3-4 distinct perspectives. This prevents the focus group from reinforcing a single narrow reading.

Example for "the fonts feel plain":
- **Perspective 1 — Typography as Brand:** The font doesn't signal "premium newspaper" — it feels like a blog. Fix: distinctive display serif.
- **Perspective 2 — Attention Economics:** Plain fonts don't create visual hooks. The eye glides past without stopping. Fix: typographic hierarchy with varied weights/sizes.
- **Perspective 3 — Competitive Differentiation:** If the font looks like every other site, there's no reason to trust this one. Fix: distinctive, memorable type choices.

Present interpretations to the user OR bake them into the persona prompts. The focus group then validates which interpretation matters most.

### Step 1: Define the Review Target
A live URL. For local changes, deploy to the GCS bucket first (`bash /Users/alexstocchi/.hermes/scripts/gazzetta_deploy_to_gcs.sh`) so the focus group sees the real deployed page. Verify with `curl -sI "https://storage.googleapis.com/www.lagazzettadikyiv.com/index.html" | grep "200"`. For Gazzetta di Kyiv specifically, the canonical URLs are (in order of reliability):
1. `https://storage.googleapis.com/www.lagazzettadikyiv.com/index.html` (GCS direct — always works)
2. `https://www.lagazzettadikyiv.com/` (custom domain — may have SSL cert issues)
3. ⛔ `https://pureciclismo.github.io/gazzetta-di-kyiv/` (DEPRECATED — returns 404 since v22.7 migration)

### Step 2: Select Personas (5 minimum, 10 max — 2 batches)

Pick 5 personas for Batch 1 from the 35+ roster. Select from relevant industries + contrarian. Then pick 5 more for Batch 2 based on Batch 1 findings.

**14 Industries Covered:**

| # | Industry | Personas |
|---|----------|----------|
| 1 | **Finance & Investment** | Portfolio Manager, Degen Trader, 55yo Retail Investor, Hedge Fund Quant, PE/VC Principal, Derivatives Market Maker |
| 2 | **Energy** | Oil & Gas Trader, Renewables Analyst, Grid Operations Expert, Energy Policy Analyst |
| 3 | **Defense & Aerospace** | Defense Contractor Analyst, Military Logistics Analyst, Arms Trade Researcher |
| 4 | **Agriculture & Commodities** | Grain Trader, Softs Analyst, AgTech Supply Chain Analyst |
| 5 | **Shipping & Logistics** | Maritime Insurance Underwriter, Freight Forwarder, Port Operations Analyst |
| 6 | **Telecom & Infrastructure** | 5G/Spectrum Analyst, Data Center Analyst, Network Engineer |
| 7 | **Pharma & Biotech** | Clinical Trials Analyst, Market Access Analyst, Biotech Patent/IP Strategist |
| 8 | **Cybersecurity & INTEL** | Threat Intelligence Analyst, APT Researcher, Zero-Day Broker Analyst |
| 9 | **Real Estate & Property** | REIT Analyst, Cross-Border Property Analyst, Property Insurance/Cat Risk Analyst |
| 10 | **Luxury & Art Market** | Art Advisor, Auction House Specialist, Cultural Heritage/Provenance Researcher |
| 11 | **Legal & Regulatory** | Sanctions Lawyer, Trade Compliance Specialist, CFIUS/FDI Screener |
| 12 | **Academia & Research** | Political Scientist (IR), Econometrician, Game Theorist |
| 13 | **Retail & Consumer** | Consumer Sentiment Analyst, Supply Chain Retail Analyst, E-commerce Strategist |
| 14 | **Mining & Metals** | Rare Earths Analyst, Gold Trader, Base/Battery Metals Trader |

**Generalist / Cross-Cutting Personas (use in any review):**

| Persona | Use When | Key Questions | 4-Lens Prompt |
|---------|----------|---------------|--------------|
| **Busy Professional** | Evaluating first-impression, scannability, actionability | "What do I learn in 5 seconds? Would I come back?" | Top-Down: Does the architecture make me smarter in 5 seconds? Bottom-Up: What's the single most scannable vs. confusing element? Source: WSJ, Bloomberg Terminal. Threat: The 5-second bounce rate |
| **Skeptical Journalist** | Evaluating industry-specific language, jargon, credibility across all 14 sectors | "Does this feel like journalism or a consulting deck? What's hiding behind the words?" | Top-Down: Is the editorial voice consistent and authoritative? Bottom-Up: Find 3 words that could mean anything. Source: AP Stylebook, Nieman Lab. Threat: Straw-man constructions |
| **Design-Sensitive Reader** | Evaluating typography, layout, visual hierarchy | "Where does my eye go? What feels off?" | Top-Down: Does the design system reinforce or undermine the editorial mission? Bottom-Up: Rate typography/color/layout 1-10. Source: AIGA, design systems. Threat: Generic blog feel |
| **Conversion-Focused Reader** | Evaluating CTAs, funnel, action prompts | "What makes me want to click/subscribe/share? What blocks me?" | Top-Down: Is there a clear conversion path from arrival to action? Bottom-Up: Where are the friction points? Source: Growth metrics. Threat: The page is a dead end |
| **First-Time Regular Visitor** | Evaluating accessibility for non-finance audiences | "Do I understand this in 10 seconds? What's confusing?" | Top-Down: Is the site self-explanatory to someone outside this industry? Bottom-Up: Count unexplained terms. Source: General news. Threat: Jargon wall |
| **UX Writer / Content Designer** | Evaluating label clarity, jargon density, grammar | "Does every label pass the grandma test? Is every acronym explained?" | Top-Down: Is the taxonomy consistent across all containers? Bottom-Up: Find every label that fails the grandma test. Source: Content design standards. Threat: Internal language leaks |
| **Chief Editor** | Evaluating editorial quality, writing style, readability | "Is the writing style over-wordy? Where does reader attention drop?" | Top-Down: Does the editorial architecture serve the mission? Bottom-Up: Score each headline A-F. Source: AP, Reuters standards. Threat: LLM-template rot |
| **Senior Web Designer** | Evaluating CSS execution, color, typography, share UX | "Propose exact CSS for requested changes. Measure element sizes." | Top-Down: Is the design system internally consistent? Bottom-Up: Rate every CSS decision. Source: Design system docs. Threat: Leaky abstractions. **MUST audit:** color contrast (WCAG AA), font size minimums, touch targets (44px HIG), inline style count, dead fonts, frameless contract. See `references/design-qa-checklist.md`. |
| **Mobile-First Reader** | Evaluating responsive design | "What breaks on a phone? What's too small to tap?" | Top-Down: Is the mobile experience a first-class citizen? Bottom-Up: Check every interactive element at 390px. Source: Mobile UX best practices. Threat: Desktop-only thinking |
| **Logic Professor** | Evaluating container integrity, taxonomy, reasoning chains | "Does each container hold what it claims? Are premises connected to conclusions?" | Top-Down: Is the architecture a logical system or adjacent panels? Bottom-Up: Find cross-contamination and ambiguity. Source: Formal logic. Threat: Circular architecture |
| **Machiavellian Strategist** | Power dynamics, information asymmetry, competitive edge | "Does the site make you feel like you have info others don't?" | Top-Down: What's the power signal of this site? Bottom-Up: What single element would a rival steal? Source: Power dynamics. Threat: Pretentiousness |
| **Aesthetic Purist / Minimalist** | Every-pixel-must-justify visual review | "Is every SVG/icon justified? What's the most visually offensive element?" | Top-Down: Does the design language hold or are there leaks? Bottom-Up: Name 3 elements to remove. Source: Apple HIG. Threat: Visual clutter |
### Step 3: Spawn the Focus Group

**DEFAULT PATTERN (proven June 2026, 4/5 completion rate):**

Use a HYBRID approach — Batch 1 with browser tools for visual-inspection personas, Batch 2 with pre-extracted context for analytical personas.

**Batch 1 (3 personas, browser tools):** Give `toolsets: ["browser"]` to personas that MUST see the page visually: Senior Web Designer, UX Director, Design-Sensitive Reader. These personas need `getComputedStyle`, `browser_snapshot`, and visual inspection. Include the exact URL with cache-bust parameter (`?_v={rand}`). Include `bodyLen > 2000` + 3-second wait pItfalls in every prompt.

**Batch 2 (2-3 personas, NO browser tools):** Pre-extract all relevant site data yourself using `browser_console` JS evaluation or `terminal` + `curl` + Python. Feed the structured data as rich `context` to subagents. Give them `toolsets: []` or `toolsets: ["terminal"]` only. This prevents browser_console iteration loops, cuts token usage by ~60%, and produces consistent results. Analytical personas (Logic Professor, Systems Architect, McKinsey Partner, Portfolio Manager doing data-only review) MUST use this pattern.

**Why:** Browser-toolset subagents for analytical evaluation burned 971K-1.28M input tokens and hit max_iterations with no result (2 of 3 failed, June 2026). Context-fed subagents completed in 437K-921K tokens with detailed structured output (3 of 3 succeeded). Only visual-inspection personas justify browser tools.

**PITFALL:** Giving browser tools to Logic Professor or Systems Architect personas = guaranteed max_iterations failure. These personas try to inspect every DOM element via browser_console and never converge. Pre-extract the data they need.

**PITFALL: `toolsets: []` does not prevent skill_view or browser_navigate calls (June 2026).** Subagents with `toolsets: []` can still call skill_view (they loaded gazzetta skills unprompted) and browser_navigate (they tried to visit the live site despite having no browser tools). This is harmless but wastes tokens. Mitigation: in the `context` field, explicitly state "You have NO browser access. Do not attempt to navigate to any URL. Analyze the data provided below only." Also explicitly list the data provided so the subagent doesn't go looking for skills.

**Token-cost confirmation (June 22, 2026):** The 3-persona Batch 2 (Machiavellian + Chief Editor + Skeptical Journalist) with `toolsets: []` and pre-extracted context completed at 335K, 912K, and 1.59M input tokens respectively — all with detailed structured output. The 912K outlier loaded gazzetta skills via skill_view (unnecessary — all context was in the prompt). The 1.59M outlier did the same + made 30 tool calls despite `toolsets: []`. Lesson: pre-extraction works, but explicitly instruct subagents to NOT load skills when all needed context is already in the prompt.

### Step 4: Aggregate Findings with Combined Scoring

Collect all 10 persona responses. For each persona, extract their Top-Down and Bottom-Up scores.

**1. Consensus Catalog** — Issues flagged by 3+ personas (non-negotiable fixes). Per issue: element, count, severity.

**2. Contradiction Map** — Where personas disagree. Note industry splits (e.g., "finance loved it, energy hated it").

**3. Critical Bugs** — Must fix immediately, before proceeding.

**4. Combined Scoring** — The formal evaluation:
- **Top-Down Score** = average of all persona Top-Down scores (1-10)
- **Bottom-Up Score** = average of all persona Bottom-Up scores (1-10)
- **Combined Score** = Top-Down × 0.40 + Bottom-Up × 0.60
- **Verdict:** PASS (≥8.0) / CONDITIONAL PASS (6.0-7.99) / FAIL (<6.0)

**5. Priority-Ordered Fix List** — Ranked by severity × consensus count × (1/fix effort).

### Step 5: Apply Fixes
Prioritize: consensus items first, then contradictions (pick the high-impact side), then silence (leave alone).

### Step 6: Re-review
After applying fixes, run the focus group again on the updated URL. Confirm the original complaints are resolved and no new issues introduced.

## 4-Lens Evaluation Prompt Template

Every persona in a v3.0 focus group receives a 4-lens prompt. This is the canonical format:

```
You are [PERSONA NAME — INDUSTRY]. Visit {URL}.

Evaluate the site through FOUR specific lenses:

### Lens 1: TOP-DOWN (Systemic / Architecture View)
[Industry-specific question about the architecture, macro implications, paradigm consistency, or overall structure]

Score 1-10: ___

### Lens 2: BOTTOM-UP (Specific Element View)
[Industry-specific question about a specific label, number, container, or interaction]

Score 1-10: ___

### Lens 3: SOURCED ANALYSIS (Data Trust & Verification)
Where would I verify this data? What sources do I trust or distrust?
- Source I'd check first: ______
- Trust score for this site's data (1-10): ___
- What one source change would make me trust it more: ______

### Lens 4: COMPETITIVE THREAT (Information Asymmetry)
What information asymmetry does this create?
- Who wins if this data is real: ______
- Who loses: ______
- What trade can I execute right now based on this: ______

### Summary
Biggest praise (one sentence): ______
Biggest complaint (one sentence): ______
Combined verdict: PASS / CONDITIONAL PASS / FAIL
```

### Industry-Specific Prompt Injections

| Industry | Top-Down Injection | Bottom-Up Injection |
|----------|-------------------|---------------------|
| **Energy** | What does the capital flow data reveal about the oil-to-renewables rotation? | Is there a specific crude basis or power market dislocation? |
| **Defense** | Does the site capture the defense spending supercycle? | What specific contractor or subsystem supplier is positioned for identified conflicts? |
| **Agriculture** | Are weather, export policy, and supply chain risks modeled correctly? | Is there a specific soft or grain basis play? |
| **Shipping** | Is the trade lane disruption data leading or lagging price action? | What specific port or trade route shows congestion that consensus misses? |
| **Telecom** | Are infrastructure trends (data center buildout, 5G/6G) tracked as capital flows? | What specific data center market faces power constraints? |
| **Pharma** | Is the regulatory risk landscape (FDA, IRA, EU HTA) properly weighted? | What specific trial phase transition creates asymmetric upside? |
| **Cybersecurity** | Do cyber operations align with the geopolitical narrative? | What specific APT group TTP change reveals strategic intent? |
| **Real Estate** | Is the capital migration across property sectors tracked? | What specific market faces an uninsurability inflection? |
| **Luxury & Art** | Is art as an alternative asset class properly represented? | What specific artist segment has a pricing dislocation? |
| **Legal** | Are sanctions and trade control risks surfaced as capital flow drivers? | What specific jurisdiction faces elevated enforcement risk? |
| **Academia** | Does the narrative use correct IR theory and econometric modeling? | What specific model specification would identify a different regime signal? |
| **Retail & Consumer** | Is consumer sentiment vs. spending divergence captured? | What specific retail category shows inventory dislocation? |
| **Mining & Metals** | Is the critical mineral supply chain concentration risk modeled? | What specific metal market shows off-exchange stockpiling? |

## Drawbacks & Mitigations

| Drawback | Mitigation |
|----------|------------|
| **Agents may agree with each other** (groupthink) — if all agents use similar reasoning, they produce correlated feedback | Use diverse persona prompts with conflicting values (e.g., "you hate jargon" vs "you want technical depth") |
| **Agents may miss domain-specific issues** — LLMs lack real-world audience knowledge | Pair with competitive analysis: have one agent compare against a real competitor site |
| **Agents may over-index on language, miss visual design** | Include a persona specifically instructed to ignore text and evaluate only layout/typography/color |
| **Feedback may be too vague** — "feels off" without specifics | Require agents to cite specific elements by their text content or CSS selector |
| **Agents may hallucinate page content** | Require agents to use browser tools, not just describe from memory |
| **Subagents may fail with OpenAI quota errors** | Set delegation to DeepSeek: `hermes config set delegation.provider deepseek` + `hermes config set delegation.model deepseek-v4-flash` + `hermes config set delegation.base_url https://api.deepseek.com/v1`. **CRITICAL:** Also clear `delegation.api_key` if it holds an OpenAI key (`sk-pro...`) rather than the DeepSeek key — a stale api_key overrides the provider's env-var credential and causes the subagent to fall back to OpenAI, hitting quota. Fix: `hermes config set delegation.api_key ""` to inherit from `.env` DEEPSEEK_API_KEY. |
| **Subagents hit 404 on live site during CDN propagation** | GitHub Pages has a 600s (10 min) HTML cache. After deploying, the CDN serves stale 404s or old content. Wait 120-180s after any deploy before spawning a focus group. Verify with `curl -sI <url>` — look for `HTTP/2 200`. If `age` header shows > 60s and status is 404, the site may be disabled or the deploy workflow failed. See `gazzetta-website` skill `references/deployment-pitfalls.md` for full troubleshooting. |
| **SSL cert broken on custom domain** — GCS buckets do NOT serve SSL for custom domains without a Google Cloud Load Balancer. Browser returns `ERR_CERT_COMMON_NAME_INVALID`. | Always use GCS direct URL (`storage.googleapis.com/www.lagazzettadikyiv.com/index.html`) for focus groups when SSL is broken. Warn user that public visitors can't access the custom domain until SSL is configured via GCP LB + managed cert. |
| **Personas evaluate stale CDN-cached pages** | GCS CDN caches HTML for 3600s (1h). After deploying a change and immediately spawning a focus group, the subagents see the CACHED old version, not the fresh deploy. Fix: verify origin freshness before spawning — `gsutil cp gs://www.lagazzettadikyiv.com/index.html - | grep '<new-element>'`. Only proceed after confirming. |
| **Subagents evaluate stale CDN-cached pages** | GCS CDN caches HTML for 3600s (1h). When deploying a design change and immediately spawning a focus group, the subagents see the CACHED old version, not the fresh deploy. In v22.7, a masthead emblem focus group critiqued the old fox when the caduceus was already on GCS. Fix: verify origin freshness before spawning — `gsutil cp gs://www.lagazzettadikyiv.com/index.html - | grep '<new-element>'`. Only proceed after confirming. The subagent toolset should be `[\"browser\"]` only — browsers see the CDN-cached page. If the focus group is time-sensitive, wait 60-120s for propagation or force cache-bust with a query string. |
| **Immutable JS cache corrupts browser state across navigations (v22.38)** | Hashed JS files (`max-age=31536000, immutable`) persist in browser memory. When testing multiple deploys in one browser session, the browser's JS execution context becomes corrupted — old event listeners remain, global state leaks across navigations, `DOMContentLoaded` fires before new init code runs. Symptom: page stuck at "Loading…" despite loading correct JS hash. Fix: use fresh `_v=N` cache-bust parameter for each test, verify loaded hash via `document.querySelector('script[src*=\"story-app\"]')?.src`, and test JS logic directly via `browser_console` evaluation before debugging browser cache. |
| **Personas navigate to wrong repo or investigate wrong codebase** | Subagents lack context about which repo deploys the site. Always include the full live URL in the persona prompt and explicitly state "This is the live deployed site — evaluate what you SEE, not what you find in GitHub repos." The subagent toolset should be `["browser"]` only to prevent them from exploring repos. |
| **Subagents may hit GitHub Pages 404s** — intermittent CDN propagation windows cause navegation to return 404 even though the site is live at other times | **Always wait 120s after a deploy** before spawning focus group agents. If a subagent reports 404, wait 30s and retry the same URL. If the agent starts investigating wrong repos (common failure mode), kill it and re-spawn with explicit instruction: "Only visit this exact URL, do not search for alternatives." |
| **Subagent URL confusion — personas navigate to wrong/old URL (v26.7+)** — 2 of 3 personas in a June 2026 audit navigated to the OLD deprecated GitHub Pages URL (`pureciclismo.github.io`) instead of the current GCS deployment (`lagazzettadikyiv.com`). They wasted all 50 iterations on the wrong site and produced garbage findings. The Degen Trader checked 15+ localhost ports; the 55yo evaluated 7px fonts from the May 2026 codebase. Both were useless. | ALWAYS include the EXACT full URL in every persona prompt: `"Visit https://www.lagazzettadikyiv.com/?_v={rand}"` — do NOT assume the subagent knows the URL. Verify by checking the CSS hash the persona reports against the expected hash from the live deploy. If the persona reports a different CSS hash or mentions any URL other than the canonical one, kill and re-spawn. |
| **Data fetch timing false positive — persona reports "Failed to fetch" and "empty pages" (v26.7+)** — The UX Designer persona checked `browser_console` during the 1-2 second fetch retry window (`Gazzetta fetch retry 1/2 for ./data/flows.json in 1000ms`). They reported 5 pages as "empty data shells" and scored them 1/10. In reality, the data loads fine after the retry completes — stories.html had 424K chars and 246 cards. The persona was too fast. | Instruct personas to WAIT 3 seconds after page load before checking data population. Use `bodyLen > 2000` as the success indicator, NOT the absence of fetch retry messages. Add to persona prompt: `"After navigating to each page, wait 3 seconds for data to load. Check bodyLen > 2000 as the data-populated indicator. Do NOT mark a page as empty based on console fetch messages during the retry window."` |
| **Manufactured data detection — Story-Level Scaling / headline-hashing (v26.8, June 2026)** — When the Logic Professor or Portfolio Manager persona inspects the data pipeline, they may discover that dollar amounts displayed on stories are NOT sourced from actual capital flow tracking but are algorithmically generated from headline hashes (e.g., `Story Amount = Category Total × tier_fraction × pillar_bonus × (1 + jitter_pct/100)` with jitter derived from `hash(headline)`). This is a **fundamental data integrity failure** — the system manufactures the "contradictions" it claims to detect rather than measuring them from real data. Detection: identical flow mappings across unrelated stories (e.g., both a geopolitical story and a Father's Day gift guide → `1× NVDA BUY HIGH`), all stories showing identical confidence scores (CONSENSUS 30/100), uniform velocity (95% at exactly 1.0×). This class of finding is deeper than surface rendering bugs — it strikes at the editorial claim itself. Flag as CRITICAL when found. |\n| **Non-deterministic masthead rendering (v26.2, June 2026)** — Visual brand elements (caduceus, bulavas) may render correctly on index.html cold-load but be completely absent from sub-pages (/stories, /flows, /trades, /signal, /track, /flow-nodes, /event_horizon). Bulavas may appear on the LEFT side instead of RIGHT. The Senior Web Designer caught: caduceus present on homepage only, missing from all 7 sub-pages. | Instruct the Senior Web Designer to verify masthead symbols on ALL nav-linked pages with `browser_console`: `document.querySelector('.masthead-caduceus')` and `document.querySelector('.masthead-bulava')` on every page. Check element parent (`.masthead-left` vs `.masthead-right`). A cold-load vs warm-navigation difference signals JS-injected masthead — must be static HTML across all page templates. |
| **Placeholder price contamination in JS-hydrated SPAs (v26.2)** — Pre-hydration HTML may show stale/random placeholder prices that differ wildly from real data in JSON files. Degen Trader found BTC at $16,876 (homepage), $6,876 (/stories), $26,876 (/flows) — all different from real $61,876. Flow-by-sector units flip between B (billions) and M (millions) across pages (1,000× error). | Add to Degen Trader persona prompt: "Compare the first price/widget value you see on page load against the value after 3 seconds. If they differ by more than 1%, flag every inconsistent number with exact values and which page. Check for unit inconsistencies (B vs M, % vs raw)." |
| **CSS changes not visible after deploy — `build_site.py` does not hash CSS (v26.3)** — Editing `site/styles.css` and running `build_site.py` + `gsutil rsync` will NOT update the live site. `build_site.py` only syncs data JSON files; it does NOT hash CSS/JS or update HTML references. The browser loads `styles.OLDHASH.css` from cache while your edits sit in the unused `styles.css`. **Fix:** After any CSS edit, run `python3 scripts/build_hashed_assets.py` which hashes CSS/JS and rewrites all HTML `<link>` tags to point to the new hash. Then deploy. Verify with `grep "stylesheet.*styles\\." site/index.html` — the hash must match the latest file. | After editing CSS, always run `build_hashed_assets.py` BEFORE deploying. Symptom of missed step: `getComputedStyle()` returns old values despite `styles.css` being correct locally. |
| **`display: none` overridden by later CSS rule block (v26.3)** — When hiding an element with `.col-alpha { display: none; }`, if another `.col-alpha { display: flex; }` block exists later in the same CSS file, it wins due to equal specificity + cascade order. The browser renders the element despite your `display: none`. **Fix:** Delete the OLD rule block entirely, don't just add a new one above it. Verify with `grep -n "\.col-alpha" site/styles.css` — only ONE selector block should remain (your `display: none` one). Same pattern applies to any element you're hiding. | After any `display: none` addition, grep the CSS file for the same selector to ensure no later block re-enables it. |

## Hero Stat Label Consensus (Retail Focus Group, June 2026)

All 3 retail personas (Degen Crypto Trader, 55yo Retail Investor, UX Designer Retail) independently flagged the same hero stat labels. 100% consensus.

| Old | New | Complaint |
|-----|-----|-----------|
| Confidence | **Flow confidence** | "Confidence in WHAT?" — unsizable, ambiguous |
| Assets positioned | **Active positions** | "Where are they?" — passive, no container link |
| Track record | **Open exposure** | "$124K contradicts 'No settled predictions'" — trust-killing |

Pattern: retail users need labels that answer "what is this measuring?" in ≤2 words. Abstract nouns (Confidence, Alignment) fail. Concrete nouns with domain prefix (Flow confidence, Active positions) pass. Apply this test to any new hero stat label.

### Full Product Architecture Audit (proven June 2026)

Use when the user wants a comprehensive structural review — architecture sustainability, translation pipelines, UX coherence, competitive positioning, and monetization readiness.

1. **Portfolio Manager / Trader (Mike Green persona)** — evaluates data integrity per container. Flags truncation errors, duplicate flows, broken metrics (\"1× normal pace\" everywhere), wrong tickers (SPX vs SPY), contradictory stats (hero $124K vs track record $19.5K). Key question: \"Would I allocate capital based on this data?\" Output: per-container error catalog, numbers-first redesign spec.

2. **C-Level Digital Product Executive (ex-GS fintech CEO)** — evaluates architecture sustainability, build pipeline integrity, i18n maintainability, mobile readiness, competitive UVP. Key questions: \"Does the architecture prevent quality degradation with each update? Can this scale to 10K DAU? What's the migration path from static GCS to something maintainable?\" Output: architecture migration roadmap, i18n CI/CD spec, page-split proposal, competitive positioning matrix.

3. **Senior UX Director (Bloomberg/FT level)** — evaluates information architecture, visual hierarchy, comprehensibility cliff, density vs overwhelm, visual consistency. Key question: \"Can a 55-year-old retail investor understand this in 10 seconds?\" Output: wireframe concept, comprehension cliff catalog, font/color inconsistency list, density recommendations.

4. **Systems Architect (Bloomberg/Refinitiv)** — evaluates static→dynamic migration, container separation, error resilience, performance. Key questions: \"What breaks at scale? Are all JSON.parse calls guarded? What happens when data files are corrupt?\" Output: scaling limits, error resilience catalog, performance audit, container separation roadmap.

5. **White-Collar Professional (McKinsey/consultant)** — evaluates trust signals, would-pay assessment, jargon accessibility, competitive positioning. Key questions: \"Would I pay for this? How much? What destroys trust?\" Output: trust/bounce score, would-pay assessment, intel report feature list, jargon catalog.

**Proven results (June 2026):** This 5-persona audit found 22 C2 errors, 3 architecture anti-patterns, 16 missing data-i18n attributes, a contradictory hero/track record exposure, and a $0→$99-199/mo monetization path with 3 prerequisite trust fixes.

**Retail Trader Pack (v22.16 — proven for hero label/confidence audits):** Degen Crypto Trader + 55-Year-Old Retail Investor + UX Designer (Robinhood/Public.com). All 3 flagged "Flow confidence: 82% ↑" as incomprehensible. Redesigned to OUTLOOK: BULLISH/BEARISH badge. Hero stat labels changed: Capital tracked→Money tracked, Active positions→Open trades, Open exposure→At risk. Flow cards flattened: removed 80% and =1× from collapsed view — now shows direction + sector + play only.

### Proven Persona Combinations

### Design Audit (typography, layout, attention)
1. **Design-Sensitive Reader** — evaluates fonts, spacing, visual hierarchy, distinctiveness
2. **Busy Professional** — evaluates first-impression, scannability, actionability in 3 seconds
3. **Skeptical Journalist** — evaluates clarity, jargon, whether containers hold real content or decoration

### Capital Flow / Data Product Audit (proven June 2026)
1. **Portfolio Manager (Top-Down Macro)** — evaluates whether flow data supports allocation decisions: net exposure, dominant signal, sector rotations, institutional segmentation. Key questions: "What's the single-action implication?" "Which flows dominate and why?" "What data point would make this indispensable?"
2. **UX Designer (Retail Investment Apps)** — evaluates scannability, label effectiveness, visual hierarchy for non-pro users. Key questions: "Would a first-time visitor stay?" "What label system reduces repetition?" "What one change makes this feel alive?"
3. **Financial Data Journalist (Bloomberg/FT)** — evaluates editorial quality, narrative coherence, data integrity. Key questions: "What story does this tell?" "What's missing for cite-worthiness?" "Where are the contradictions?"

This combo was used for the v22.12 Container 2 ("Where the smart money is going") overhaul and produced: varied positioning labels (7 variants per direction), flow aggregation with catalyst badges, identification of duplicate-row credibility issues, and velocity data surfacing.

### Data Pipeline Audit (proven June 2026 — see `references/data-pipeline-audit-persona-pack.md`)

**Degen Trader + 55-Year-Old Retail Investor + Capital Flow Analyst.** Specifically designed for data integrity, confidence indicators, and pipeline audits. Catches fake precision, invisible indicators, source untraceability, and identical confidence traces. All 3 personas independently flagged the same issues.

### Wall Street Professional Audit (proven June 2026 — see `references/wall-street-audit-june2026.md`)

**Portfolio Manager ($5B AUM) + Quant/Structurer (GS/JPM) + S&T Desk (Equity Derivatives).** Full product audit across all products. PM: alpha generation + edge. Quant: model risk + data integrity. S&T: flow IQ + client-ready pitch. Contradictions ARE the signal. Spawn all 3 in parallel via delegate_task(browser).

### Product Interconnectivity Audit (proven June 2026 — see `references/product-interconnectivity-spec.md`)

**Product Architect (Bloomberg Terminal) + UX Architect (Bloomberg/FT).** Full cross-linking architecture audit. Product Architect: maps 21 missing cross-links between 6 products, designs ideal bidirectional architecture (Story↔Flow↔Trade↔Signal↔Track↔Horizon). UX Architect: cross-link pills (green=flow, gold=trade, blue=story), "The Nexus" FAB, Alpha Checklist single-page view. Use when user asks about "interconnectivity," "how products link," "alpha checklist."

### Crypto Representation Audit (proven June 2026 — see `references/crypto-representation-audit.md`)

**Crypto Market Structure Analyst (Tier 1 exchange) + Crypto-Native UX Designer.** Evaluates crypto coverage across all products: taxonomy accuracy (tickers, node labels), on-chain data gaps (Glassnode/Dune/CoinGecko), stablecoin/ETF flow tracking, crypto-native UX (dark mode, verification links, provenance). Use when user asks about "crypto representation," "crypto audit," "on-chain data."

### Flow Nodes Audit (proven June 2026 — see `references/flow-nodes-audit.md`)

**Macro PM (Bloomberg FFM) + Data Viz Designer.** Specific to flow-nodes.html: arrowhead CSS bugs, edge labels, mobile SVG breakage (min-width:900px), dark-theme disconnect, pace_multiplier field name mismatch in generate_flow_nodes.py. Use when user says "flow nodes," "review the nodes," "node-link diagram."

### Retail/Degen Trader UX Audit (proven June 2026 — see `references/retail-degen-ux-audit-combo.md`)

**Degen Crypto Trader + 55-Year-Old Retail Investor + Retail UX Designer (Robinhood) + Busy Professional + Design-Sensitive Reader.** Full UX audit across all 8 nav-linked pages. Found 10 consensus issues including unexplained PDR acronym (30+ occurrences), FIXED_INCOME raw DB key leak, missing spaces in Track stats, and LONG/SHORT jargon. Pages ranked: Signal (9.3), Trades (9.0), Horizon (8.7), Stories (7.7), Homepage (7.3), Flow Nodes (5.3), Flows (4.3), Track (3.0). Full reproduction: `references/retail-degen-ux-audit-combo.md`.

### Irrelevance / Insight Audit (proven June 2026)
**Mike Green (Portfolio Manager) + Degen Trader + Senior Web Designer.** Mike Green translates institutional capital flow products into degen-tradeable signals — PDR decomposition, passive/active regime detection, flow heat scoring. The Degen Trader validates what's actually tradeable from a phone in 15 seconds and demands one-tap UX. The Web Designer audits every pixel for comprehensibility to non-pros (color contrast, font sizes, label clarity). This combo produced the Market Regime panel (Money Flow, Top Heavy, Bond Fear) and the 13-fix design overhaul (v22.33). Use when user says "Mike Green lens," "degen traders," "review through their lens," or "simple people must understand."

### Institutional Betting Readiness Audit (proven June 22, 2026 — 6 personas, 6/6 completion)

Use when the user asks about "institutional grade," "betting/gambling usefulness," "geopolitics-first event-driven bet suggesting machine," "position ourselves for betting," or wants a comprehensive assessment of whether the product generates tradeable conviction. This combo spans concept validation (do people trust it?) and verification (can claims be independently verified?). The split between "concept people" (CONDITIONAL PASS) and "verification people" (FAIL) is the core signal.

**Batch 1 (3 browser personas — spawn in parallel):**
1. **Portfolio Manager ($5B AUM macro fund)** — evaluates alpha generation, institutional credibility, trade execution readiness. Catches: VIX discrepancy (14.2 vs 17.1 in same build), zero source attribution on capital numbers, no price targets/timeframes. Key question: "Would I put P&L behind any of these signals?"
2. **Degen Crypto Trader** — evaluates phone-first actionability, signal quality, mobile UX. Catches: $0M noise on sidebar, EQUILIBRIUM radar as useless, GAP scores don't tell direction. Key question: "Can I find a tradeable signal in under 15 seconds from my phone?"
3. **Senior Web Designer (Bloomberg/FT level)** — evaluates design system integrity, mobile responsiveness, institutional visual credibility. Catches: 10px badges, 12px filter pills (untappable on mobile), cream background as "blog" signal. Key question: "Does this look like something a hedge fund would pay for?"

**Batch 2 (3 context-fed personas — spawn AFTER Batch 1, NO browser tools):**
4. **Machiavellian Strategist** — evaluates power dynamics, information asymmetry, the "I know something others don't" sensation. Catches: framework is brilliant but execution betrays it — architecture promises power tool but pipeline delivers blog. Key question: "Does this create genuine information asymmetry or just rearrange public information?"
5. **Chief Editor (FT/Economist, 25yr)** — evaluates editorial-to-betting pipeline, headline quality (A-F grading), template rot detection, intellectual intrusion. Catches: systemic template rot ("leaves market pricing unchanged" 5+ uses, "as markets rally" 6+ uses), GAP-5 stories as brand poison, Telegram posts as headlines-only (zero trade thesis). Key question: "Does the editorial architecture lead the reader toward a betting intention or stop at 'here's an interesting contradiction'?"
6. **Skeptical Journalist (Reuters/AP, 20yr)** — evaluates methodology honesty, data provenance, straw-man detection. Catches: GAP score is LLM-instructed not deterministically computed, $100M default capital on 189/191 stories, "DISCREPANCIES: 143" is GAP≥40 count not bug count. Key question: "Can a reader independently verify a single GAP score?"

**Pre-extraction for Batch 2:** SSH to VM for stories.json stats (narrative distribution, capital value range, unique GAP scores), terminal for flows.json and derivatives.json, browser_console JS evaluation on all 5 tabs for DOM structure. Feed as structured `context` — this achieved 3/3 completion with zero iteration loops (83K-185K tokens each). See `references/gapfire-dispatch-format.md` for the Telegram format this combo produced.

**Proven results (June 22, 2026):** This 6-persona combo evaluated La Gazzetta di Kyiv for institutional betting readiness. Found 8 consensus issues: $0M capital on 9/12 narratives (CRITICAL), no trade thesis anywhere (CRITICAL), zero source provenance (HIGH), template rot in headlines (HIGH), Tactical Radar always EQUILIBRIUM (MEDIUM), mobile filter buttons unusable (MEDIUM), cream background feels like blog (MEDIUM), Telegram posts headlines-only (HIGH). Combined score: 4.4/10 FAIL. The core tension: 4 personas gave CONDITIONAL PASS (framework is brilliant), 2 gave FAIL (claims can't be verified). The contradiction IS the signal — the framework is genuinely differentiated but the pipeline stops at "here's the GAP" and never says what to do about it.

**The GapFire Dispatch:** The Chief Editor prescribed a 6-block Telegram format (HEADLINE → CAPITAL FLOW → CONTRADICTION → TWO VIEWS → THE BET → TAGS) that combines raw numbers, directional conviction, and multi-perspective analysis into ~300 words. Full template at `references/gapfire-dispatch-format.md`.

### Architecture Redesign Evaluation (proven June 2026)

Use when the user proposes a MAJOR architecture change (taxonomy replacement, container re-organization, product structure pivot) and wants it evaluated BEFORE implementation. This is NOT the same as auditing an existing live site — it evaluates a PROPOSED design against the current live site to determine whether the pivot strengthens or weakens the product.

**3-persona combo (spawn all in parallel via delegate_task with browser toolsets):**

1. **Portfolio Manager / Architecture Evaluator (Bloomberg Terminal-level)** — evaluates the proposed architecture against the current architecture through 4 lenses: Top-Down (information architecture strength), Bottom-Up (container power and balance), Source Trust (does the new format preserve or damage credibility?), Competitive Threat (who wins/loses if the pivot succeeds?). Key question: "Does this new architecture create a stronger mental model than the current one, or does it sacrifice a competitive moat for surface-level scannability?" Produces per-lens scores + a HYBRID recommendation when the UI pattern is strong but the taxonomy needs adjustment.

2. **Editorial / Content Strategist** — evaluates whether existing content assets (stories, data) survive the redesign or become orphaned. Key questions: "Do the existing 377 stories have value in the new containers, or should they be wiped? What container would each story type map to? Does keeping old content damage or preserve credibility?" Produces: reclassify-vs-wipe recommendation, container distribution estimate, content gap analysis (which containers would be empty?), competitive pivot assessment.

3. **Senior Web Designer** — evaluates the visual design spec through 4 lenses: Top-Down (collapsed container UX — mystery vs hide-too-much), Bottom-Up (specific CSS elements — gold borders, card layout, color contrast), Design System Reference (what publication should this emulate?), Competitive Differentiator (what single element is the killer visual feature?). MUST audit: WCAG AA color contrast, font size minimums, touch targets (44px HIG), keyboard/ARIA affordances, container click affordance.

**Proven results (June 2026):** This 3-persona combo evaluated a proposed 6-container geopolitical narrative redesign against the current INTEL/ALPHA pipeline architecture. Found: (1) the collapsible container UI pattern is excellent and should be adopted, (2) the 6-container taxonomy is Pareto-violating (one container holds 50%+ of content, one is completely empty), (3) the contradiction-first card format is the killer differentiator that must be preserved, (4) gold (#D4AF37) on white (#FFFFFF) fails WCAG AA at 1.8:1 — use dark goldenrod (#B8860B) for gold text. Combined verdict: CONDITIONAL PASS — adopt the UI pattern, keep the pipeline, fix the taxonomy.

### Time-Decay Freshness Misread Pitfall (v23.25 — June 2026)

Bare percentages next to story teasers are universally misinterpreted as CONFIDENCE by readers. In June 2026, 5/5 professional personas flagged "100%" on all 8 story teasers as "statistically impossible confidence" — when it was actually **time-decay freshness** (current_freshness × 100). The fix: display time labels ("2h", "3d") instead of percentages, with freshness percentage in a tooltip. If you MUST show percents, always prefix with "Fresh:" or similar label.

### Full Product Architecture Audit (proven June 2026)

Proven 5-persona combination for comprehensive audits: Portfolio Manager (Mike Green persona) + Senior UX Director (Bloomberg/FT) + Systems Architect (Refinitiv) + White-Collar Professional (McKinsey) + Logic Professor. This combo found 31 critical/high errors in the June 2026 Gazzetta audit: 100% freshness misread as confidence, quadruple-contradictory flow amounts, 4/7 data endpoints 404, broken sub-pages with debug artifacts, non sequitur trade mappings, and navigation schizophrenia across 8 pages. Combined score: 2.6/10 FAIL. Use when user wants comprehensive system audit.

### Comprehensive Multi-Lens Audit (5 Personas, 100% completion — June 2026)

Use when the user asks for a full audit covering tech, content, design, and marketing simultaneously. This combo achieved 5/5 completion (vs the prior 4/5 documented rate). All personas returned structured findings with exact numbers and CSS selectors.

**Batch 1 (3 browser personas — spawn in parallel):**
1. **Senior Web Designer** — WCAG AA contrast, font size minimums (body >= 16px, badges >= 12px), touch targets (44px), responsive breakpoints, keyboard accessibility, ARIA roles, CSS leaks, design token audit. Output: top 10 issues ranked by severity with exact CSS fixes.
2. **Chief Editor** — Headline scoring A-F (word count, concreteness, template detection), They Say/Reality straw-man test, jargon density per card, unexplained acronym catalog, editorial report card. Output: top 10 writing problems, 3 best sentence-level rewrites.
3. **Conversion-Focused Reader / Growth PM** — Conversion funnel assessment, trust signal score (1-10), competitive positioning matrix vs Bloomberg/ZeroHedge/Kobeissi, SEO/OG tag audit, footer link verification, 5 concrete growth recommendations.

**Batch 2 (2 context-fed personas — spawn AFTER Batch 1, NO browser tools):**
4. **Portfolio Manager / Quant** — Data integrity audit tracing from source scripts through pipeline to live site tables. Find every numerical discrepancy, manufactured number, data lineage break. Output: discrepancies catalog with exact numbers, root causes, severity (P0-P3), data trustworthiness score (1-10). Use `toolsets: ["terminal", "file"]` and pre-extracted context.
5. **Logic Professor / Systems Architect** — Architecture coherence audit: map real architecture vs documented claims, find every divergence, evaluate container integrity, separation of concerns, pipeline execution truth. Output: divergence catalog, architecture integrity score (1-10).

**Pre-extraction for Batch 2:** Before spawning, run `browser_console` JS evaluation on all 5 tabs to capture bodyLen, story counts, CFT card counts, console errors, and DOM structure. Run `terminal` commands to extract stories.json structure, script listing, git log, VM state. Feed all as structured `context` — this prevents iteration loops and achieves 100% completion.

**Proven results (June 2026):** This 5-persona combo found 14 data integrity discrepancies (including all capital volumes manufactured at $100M, 99% identical GAP scores, dual data structure divergence), 8 architecture divergences (including documentation describing a pipeline that doesn't exist, 3 conflicting timer frequencies, container taxonomy mismatch), 10 design issues (gold headings fail WCAG at 1.99:1, zero ARIA roles, no responsive breakpoints), content failures (99% identical They Say/Reality, 18 unexplained tickers), and marketing gaps (zero conversion elements, 3/10 trust score, no OG tags). Combined score: 3.5/10. See `references/comprehensive-audit-june-2026.md` for full methodology and findings.

### Taxonomy Architecture Audit (proven June 2026 — see `gazzetta-knowledge-index` references)

**Systems Architect + Product Executive + Logic Professor.** Three-persona critical tear-down of any proposed information architecture, taxonomy, or product redesign.

1. **Systems Architect (12+ GCP pipelines)** — evaluates infrastructure: database write-path, deploy atomicity, concurrent writers, migration safety, rollback path, quota/cost model. Key question: "What breaks first at scale?" Output: numbered list of P0/P1/P2 architectural fixes with specific code changes. Catches: SQLite WAL corruption, non-atomic deploys, race conditions, missing migration strategies.

2. **Product Executive (ex-GS fintech CEO)** — evaluates product strategy: competitive moat, revenue model, audience retention, monetization path. Key question: "Is this a pivot or a retreat?" Output: strategic coherence score, revenue viability score, hybrid recommendation. Catches: eliminating differentiators, zero-revenue formats, audience loss.

3. **Logic Professor (20 years formal logic)** — evaluates taxonomy: MECE (Mutually Exclusive, Collectively Exhaustive), level-of-abstraction consistency, container containment, category errors. Key question: "Are these categories at the same level of abstraction?" Output: per-criterion scores (1-10), restructured taxonomy, grounding principle. Catches: thesis-vs-topic errors, meta-categories mispositioned as siblings, empty containers as ontological errors.

**Proven results (June 2026):** This 3-persona combo tore apart the original 6-container taxonomy, found it failed MECE on both axes (Mutual Exclusivity: 3/10, Collective Exhaustiveness: 3/10, Abstraction Consistency: 2/10), identified that "American Decline" and "China Ascendancy" were THESES not TOPICS, and produced the domain-based restructured taxonomy adopted in v2.0. Combined they drove a 10+ point improvement in plan quality.

**When to use:** Any taxonomy proposal, information architecture redesign, product pivot, or when the user says "evaluate every piece of your plan" or "engage various tech and other professionals."

### Multi-Round Critical Audit Pattern (proven June 2026)

The sequence matters:
```
Round 1 (CONCEPT VALIDATION): 3 generalist personas → validate the idea, find obvious gaps
  → PM/Bloomberg Terminal + Editorial Strategist + Senior Web Designer
  → Output: scores, praise, complaints, conditional verdict

Round 2 (CRITICAL TEAR-DOWN): 3 specialist personas → find EVERY fatal flaw
  → Systems Architect + Product Executive + Logic Professor
  → Output: numbered P0/P1/P2 fixes, competitive analysis, MECE test results

Synthesis: Merge both rounds → rewritten plan → every critique addressed with a specific fix
```

**Pitfall — Don't run Round 2 first:** Specialists find architecture problems; generalists find UX/editorial problems. Running specialists first produces a technically sound plan nobody wants to read. Running generalists first produces an appealing plan that breaks at scale. Always run BOTH in sequence.

### Confidence Indicator + Time Freshness Audit (proven v22.37)
**Degen Crypto Trader + 55-Year-Old Retail Investor + Senior UX Director (Bloomberg/FT).** All 3 spawn in parallel visiting every product page. 3/3 consensus: "68% BULLISH" format IS comprehensible — keep it but add plain-English tier subtitle (Strong/Moderate/Weak conviction). Time freshness badges MUST be visible on every page. Story detail page `<time>` element was empty because editorial writer stories lack `generated_at` fields — fix with `dataGenAt` document-level fallback + `formatTimeAgo()` relative-time function. Full audit: `references/confidence-indicator-audit-v22.37.md`. Use when user says "confidence indicator review," "time indication empty," "dead gen traders," "model confidence comprehensible," or wants every-page freshness audit.

Prompt pattern for Mike Green: include instruction to "help adapt institutional products for degen use — and degen tells you what's actually tradeable." The two personas collaborate: Mike provides macro framework, Degen provides UX requirements, Web Designer executes the visual bridge.

### Before vs After Design Comparison (v26.4+)

Use when the user wants focus groups to compare a previous design to the current live version.

1. **Extract "before" design** from git: `git diff <pre-overhaul-commit>^..<pre-overhaul-commit> -- styles.css | head -300` — captures the key CSS deltas (color changes, font sizes, new components)

2. **Spawn 3 comparison personas** in parallel: Senior Web Designer (CSS/code quality), 55-Year-Old Retail Investor (comprehension/trust), UX Director (information architecture). Each gets the full "before" description + visits the live "after" site.

3. **Scoring**: each persona scores both BEFORE and AFTER /10. Combined score = Top-Down × 0.40 + Bottom-Up × 0.60. Produces improvement delta and regression catalog.

4. **Key questions for each persona:**
   - Per-element verdict: IMPROVED / REGRESSED / NEUTRAL
   - Top 5 improvements (ranked, with before→after specifics)
   - Top 5 regressions (what the old design did better)
   - Design debt incurred
   - 3 concrete fixes to restore the best of BEFORE into AFTER

5. **Integration prompt**: after the comparison report, write a self-prompt that spawns 4 professionals (CSS Architect, Design System Lead, Accessibility Specialist, UX Director) to produce exact patch commands that integrate the best of both designs.

**Pitfall — subagents time out on extensive CSS inspection:** The Senior Web Designer persona can hit 50-iteration max when inspecting every CSS rule across 8+ pages. Limit their inspection to computed style queries on key elements only, not full stylesheet dumps.
1. **Skeptical Journalist** — examines each photo: does it match the SPECIFIC story event/actor/location, or is it a generic sector placeholder? Flags mismatches (e.g., OpenAI logo for Anthropic story = actively misleading). Rates each match 1-10. Suggests ideal photo subject.
2. **Design-Sensitive Reader** — evaluates visual consistency: do photos share a coherent style? Are any jarringly different (stock-photo feel vs. editorial/news feel)? Rates visual identity 1-10.
3. **Competitive Reader** — compares against Bloomberg/FT/Economist photo standards. Would these images appear in a premium publication?

### Editorial Review (writing style, readability, container descriptions, matryoshka format)
1. **Chief Editor** — evaluates writing style: is it over-wordy? Where does reader attention drop? Are container descriptions concrete and benefit-focused? Would an older reader (50+) understand the architecture?
2. **First-Time Regular Visitor** — evaluates accessibility for non-finance audiences. What acronyms are confusing? Does the site assume knowledge it shouldn't? Can a smart person who doesn't work in finance find value?
3. **Senior Web Designer** — evaluates whether container headers communicate value before clicking. Are the preview-to-value ratios acceptable? Do users know there's content inside without clicking?

### Content Audit (language, credibility, density)
1. **Skeptical Journalist** — hunts for taxonomy words, jargon, filler, empty containers
2. **Busy Professional** — checks if concrete facts are findable in 10 seconds
3. **Conversion-Focused Reader** — checks if the page makes them want to act (subscribe, share, return)

### Mobile-First Audit (responsive design, thumb reach, feature parity)
1. **Mobile-First Reader** — evaluates at 390px viewport: what's visible/not, tap targets, readability
2. **Design-Sensitive Reader** — evaluates mobile typography, photo placement, brand visibility
3. **Busy Professional** — evaluates mobile scannability: can they get actionable intel in 5 seconds?

### Icon Audit (recognizability, consistency, industry standards)
Use this when evaluating icons, share buttons, navigation symbols, or any UI element that uses visual symbols to convey meaning. This combination was proven in the Gazzetta v20.2 icon audit (June 2026).

1. **UX Professional (Stripe/Linear/Vercel-level standards)** — evaluates every icon: is it instantly recognizable without text? Is the stroke width consistent across all icons? Does it come from an established design system (Lucide, Heroicons, Feather) or is it hand-drawn? Produces per-icon ratings (1-10) and names the exact standard library icon that should replace each one. Key test: "Can the user identify what this does BEFORE clicking?"
2. **Competitive Reader (Bloomberg/FT/ZeroHedge/Economist daily)** — visits competitor sites to compare icon systems. What sharing pattern do they use — individual buttons per card or single Share button with dropdown? What icon libraries do they use? What's the minimum viable set (typically: copy link + X + LinkedIn + email)? Identifies gaps: missing platforms, wrong patterns, redundant placements.
3. **First-Time Visitor (arrived via external link, never seen the site)** — points at each icon and says what they THINK it means before clicking. Then clicks and reports whether the guess was correct. Rates confusion level. Identifies dangerous ambiguities (e.g., X icon reads as "close" not "share on X").

**Icon audit red flags (fix immediately):**
- ❌ Any icon that confused the First-Time Visitor's guess
- ❌ Emoji/Unicode characters used as icons (📋 ✈ 𝕏 ▾ ✓ — render differently per OS)
- ❌ Custom hand-drawn SVGs (invented geometry → source from Lucide instead)
- ❌ Individual share buttons on every card (matches ZeroHedge blog pattern, not Bloomberg/FT premium pattern)
- ❌ Missing LinkedIn share (non-negotiable for financial/professional content)
- ❌ Inconsistent stroke widths or viewBox sizes across icons

### Editorial Style Audit (headlines, wordiness, They Say/Reality, jargon, accessibility)

Use this when auditing writing quality, readability, or when the user asks about "writing style," "wordiness," "headline quality," or "would an older reader understand this." Proven in the Gazzetta Cycle 6 editorial audit (June 2026).

1. **Chief Editor** — evaluates every headline for word count, template detection ("Three X Converge" = LLM-generated), concrete-vs-abstract nouns. Scores each headline A-F. Evaluates every They Say/Reality pair for straw-man detection: "If you showed this They Say to someone who holds that view, would they say 'yes, that's what I believe'? If not, it's a straw man." Flags sentence fragments used as thesis statements (they should be the lede). Checks container descriptions for internal dev language ("Container 1/2/3" — readers don't think in container numbers) and YouTube-trader language ("MAX CONVICTION"). Produces top-3 sentence-level rewrites ranked by impact.

2. **First-Time Regular Visitor (50+, non-finance background)** — evaluates jargon density per card. Counts unexplained acronyms (ATH, ATR, PDR, DePIN, ASICs, RWA, gamma, DXY). Checks whether any card has >2 unexplained Tier-1 terms. Evaluates sentence length for working-memory load (50+ readers lose the thread at ~35 words). Rates whether a glossary link below the masthead would suffice or if terms need in-text explanation. Flags "they say / reality" pairs where the language assumes finance literacy.

3. **Skeptical Journalist** — hunts for straw-man They Say constructions, GPT-ism headlines ("as war enters new phase," "while macro chaos engulfs"), and abstract nouns where concrete actors should be ("dilemma," "challenge," "need each other"). Checks whether They Say quotes actual media narratives verbatim (gold standard) or invents an opponent. Flags any REALITY text that is a verbatim copy of the summary paragraph (reader sees the same text twice).
### Data Pipeline Audit (proven June 2026 — see `references/data-pipeline-audit-persona-pack.md`)

**Degen Trader + 55-Year-Old Retail Investor + Capital Flow Analyst.** Specifically designed for data integrity, confidence indicators, and pipeline audits. Catches fake precision, invisible indicators, source untraceability, and identical confidence traces. All 3 personas independently flagged the same issues.

### Wall Street Professional Audit (proven June 2026 — see `references/wall-street-audit-june2026.md`)

**Portfolio Manager ($5B AUM) + Quant/Structurer (GS/JPM) + S&T Desk (Equity Derivatives).** Full product audit across all products. PM: alpha generation + edge. Quant: model risk + data integrity. S&T: flow IQ + client-ready pitch. Contradictions ARE the signal. Spawn all 3 in parallel via delegate_task(browser).

### Product Interconnectivity Audit (proven June 2026 — see `references/product-interconnectivity-spec.md`)

**Product Architect (Bloomberg Terminal) + UX Architect (Bloomberg/FT).** Full cross-linking architecture audit. Product Architect: maps 21 missing cross-links between 6 products, designs ideal bidirectional architecture (Story↔Flow↔Trade↔Signal↔Track↔Horizon). UX Architect: cross-link pills (green=flow, gold=trade, blue=story), "The Nexus" FAB, Alpha Checklist single-page view. Use when user asks about "interconnectivity," "how products link," "alpha checklist."

### Crypto Representation Audit (proven June 2026 — see `references/crypto-representation-audit.md`)

**Crypto Market Structure Analyst (Tier 1 exchange) + Crypto-Native UX Designer.** Evaluates crypto coverage across all products: taxonomy accuracy (tickers, node labels), on-chain data gaps (Glassnode/Dune/CoinGecko), stablecoin/ETF flow tracking, crypto-native UX (dark mode, verification links, provenance). Use when user asks about "crypto representation," "crypto audit," "on-chain data."

### Flow Nodes Audit (proven June 2026 — see `references/flow-nodes-audit.md`)

**Macro PM (Bloomberg FFM) + Data Viz Designer.** Specific to flow-nodes.html: arrowhead CSS bugs, edge labels, mobile SVG breakage (min-width:900px), dark-theme disconnect, pace_multiplier field name mismatch in generate_flow_nodes.py. Use when user says "flow nodes," "review the nodes," "node-link diagram."

### Retail/Degen Trader UX Audit (proven June 2026 — see `references/retail-degen-ux-audit-combo.md`)

**Degen Crypto Trader + 55-Year-Old Retail Investor + Retail UX Designer (Robinhood) + Busy Professional + Design-Sensitive Reader.** Full UX audit across all 8 nav-linked pages. Found 10 consensus issues including unexplained PDR acronym (30+ occurrences), FIXED_INCOME raw DB key leak, missing spaces in Track stats, and LONG/SHORT jargon. Pages ranked: Signal (9.3), Trades (9.0), Horizon (8.7), Stories (7.7), Homepage (7.3), Flow Nodes (5.3), Flows (4.3), Track (3.0). Full reproduction: `references/retail-degen-ux-audit-combo.md`.

### Brutal Honesty Pack (proven v26.2 — June 2026)

Use when the user says the site "looks broken," "isn't ready for users," or wants to find EVERYTHING wrong — no sugar-coating. This combo delivered the harshest but most actionable findings of any Gazzetta audit.

**Degen Crypto Trader + First-Time Regular Visitor + Chief Editor.** All 3 spawn in parallel visiting ALL nav-linked pages.

1. **Degen Crypto Trader** — page-by-page tradeability scores (1-10), fake number catalog with exact values and evidence, cross-page contradictions table, verdict: "Would you send this to your trading group?" Catches: placeholder price chaos (BTC $16,876 vs $6,876 vs $26,876 vs real $61,876), unit inconsistencies (B↔M, 1,000× errors), stale sample signals (SPX entry $5,750 when market at $7,354). Average score: 1.1/10.
2. **First-Time Regular Visitor** — visits every single page, checks bodyLen > 2000, flags pages under threshold, identifies trust-killing moments with exact page/element references. Catches: missing pages (horizon.html 404), 0 settled bets on track page, "1xBet" references in signal data, 17-day stale timestamps.
3. **Chief Editor (FT/Economist)** — page-by-page editorial report card (A-F), top 10 writing problems ranked, taxonomy drift catalog, template rot detection, They Say/Reality copy-paste audit. Catches: 100% They Say = Reality identical text, ~40% taxonomy error rate, 60% of stories at exactly 59% confidence (default value).

**Proven results (June 2026):** Consolidated FAIL verdict with 7 CRITICAL findings producing exact CSS patches and page fixes.

### Irrelevance / Insight Audit (proven June 2026)

1. **Financial Product Reviewer** — rates EVERY element 1-10 on insight value. Flags vanity metrics, fake precision, decorative elements, cliches. Key question: "Can I trade on this number?" Output: keep/trash/fix table with per-element scores.
2. **UX Writer (Bloomberg/Robinhood/Stripe level)** — evaluates every label, stat, badge against "grandma test" (smart non-finance person understands in 5s). Flags unexplained acronyms, inconsistent phrasings, grammar errors. Output: exact replacement text for every failure.
3. **SRE/DevOps Engineer** — checks infrastructure: SSL certs, CDN headers, HTTP codes, deploy freshness. Catches what editorial personas completely miss.

Key finding from June 2026 audit: Financial Product Reviewer gave hero stats 1-4/10 (vanity), BUILDING scores 3/10 (fake distribution), flow labels 2-6/10 (cliche), Signal container 1/10 (empty), Track Record 1/10 (trust-destroying). Only trade ideas and anchor table scored 7/10.

- `references/developer-indicator-audit-june2026.md`
- `references/meta-audit-post-engine-fix.md` — **Post-engine-fix meta-audit (v3.1, June 2026):** 5-phase review protocol after data engine rebuilds. Phase A: visual sweep, Phase B: 3-persona content audit, Phase C: strategy, Phase D: technical verification, Phase E: consolidation. Includes pre/post metrics table and diagnostic checks.
- `references/retail-degen-ux-audit.md` — **Retail/Degen UX audit persona pack (5 personas, 2 batches).** Proven v25.11: Degen Crypto Trader + 55yo Retail Investor + Retail UX Designer + Busy Professional + Design-Sensitive Reader. Use for grandma-test audits, label clarity reviews, and retail accessibility. 10 consensus issues found (PDR, font sizes, raw DB keys, missing spaces, LONG/SHORT, empty containers).

### Quick-Start Editorial Audit (cron-friendly, no subagent spawn needed)

For cron jobs where spawning 3 subagents is too heavy, a single agent can perform the editorial audit directly by:
1. Reading `stories.json` from the repo (`/Users/alexstocchi/projects/gazzetta-di-kyiv/site/data/stories.json`)
2. Navigating to the live site (try GCS direct URL first: `https://storage.googleapis.com/www.lagazzettadikyiv.com/index.html`)
3. Using `browser_console` to extract rendered headlines + word counts: `Array.from(document.querySelectorAll('#newsCol article')).map((a,i) => ({ idx: i, headline: a.querySelector('h3')?.textContent?.trim(), wordCount: a.querySelector('p')?.textContent?.split(/\s+/).length }))`
4. Cross-referencing stories.json (source of truth for They Say/Reality/paradigm_implications) against rendered content
5. Producing the structured report following the format in `references/editorial-style-audit-dimensions.md`

**Pitfall — Aggregator stories masquerading as editorial:** Stories 28+ in the feed may be raw Reuters/wire items with zero editorial treatment (no They Say, no Reality, no Intel Brief, source attribution only). Detect with: `Array.from(document.querySelectorAll('#newsCol article')).map((a,i) => ({idx: i, isAggregator: !a.textContent.includes('THEY SAY') && !a.textContent.includes('REALITY') && (a.textContent.includes('reuters_business') || a.textContent.includes('Source:'))})).filter(r => r.isAggregator)`. Flag these separately — they dilute the editorial brand and break the They Say/Reality contract with the reader.

**Pitfall — They Say/Reality content is dynamically loaded:** Collapsed cards' `innerHTML` does NOT contain They Say/Reality sections. They are JavaScript-injected on expand. Use `browser_snapshot` after initial page load (captures rendered text) or expand individual cards to audit. See `references/editorial-style-audit-dimensions.md` Pitfalls section for details.

## Autonomous Cron Quality Gate (Content + UX + Accuracy)

**Pitfall: Site returns 404 → Design Reader persona cannot review.**
The Autonomous Cron Quality Gate spawns a Design Reader persona that must visit the live site. If all site URLs return errors, the persona cannot verify visual elements.

**Site URL verification (try in order):**
1. **GCS direct URL** (most reliable): `https://storage.googleapis.com/www.lagazzettadikyiv.com/index.html`
2. **Custom domain** (may have SSL issues): `https://www.lagazzettadikyiv.com/`
3. **GitHub Pages** (DEPRECATED — returns 404 since v22.7 migration to GCS): `https://pureciclismo.github.io/gazzetta-di-kyiv/`

Verify before spawning personas:
```bash
curl -sI "https://storage.googleapis.com/www.lagazzettadikyiv.com/index.html" | grep -q "200" || echo "SITE DOWN"
```
If the site is 404:
- Include it as a critical finding in the aggregate report with **\[CRITICAL: SITE 404\]** prefix
- Bypass the Design Reader review and note: "Site returns 404 — all mobile UX findings are CANNOT ASSESS"
- Do NOT conclude the Design Reader passed/failed — record `CANNOT ASSESS` for every visual metric
- The Editorial Writer persona should have caught this in its own Step 9 quality gate. If it didn't, flag that as an additional finding (the pipeline is producing orphaned content)
- Focus the remaining personas on content-only evaluation (banned phrases, grounding, actionability) since the site is unreachable

1. **Skeptical Journalist** — hunts for taxonomy words, banned phrases, near-misses, template rot in setups.json/contradictions.json
2. **Busy Professional** — per-instrument Bet&Benefit grounding check, cross-platform price consistency verification, signal-to-noise ratio. **ADDED: Cross-container consistency check** — for each instrument, compare its Signal section entry (Container 3) with its Bet&Benefit panel entry (Container 2). If Signal says "no directional signal" / "WATCH" but panel says "BUY HIGH" on the same asset, flag this as a reader-trust-destroying internal contradiction.
3. **Design Reader** — mobile UX audit at 390px, previous-cycle fix verification, touch target compliance, semantic landmarks, image alt text. **ADDED: Photo position check** — verify photos appear on the LEFT of story text in expanded cards (not at the bottom, not on the right, not absent). The design spec mandates left-side photo placement for all stories.

**Reference:** `references/quality-gate-prompt-patterns.md` — full worked prompts for all three personas with aggregation template.

### Reference Files
- `docs/focus-group-pipeline-spec.md` — Full multi-industry pipeline specification (35+ personas, 14 industries, top-down/bottom-up evaluation methodology, 5-phase pipeline architecture, persona assignment protocol, success criteria). **Load this first** to understand the complete v3.0 architecture.
- `references/meta-audit-five-persona-pattern.md` — Proven 5-persona comprehensive audit: tech, content, design, marketing. Batch 1 (browser: Web Designer, Chief Editor, Conversion PM) + Batch 2 (context-fed: Portfolio Manager, Logic Professor). Pre-extraction commands, scoring, and pitfall catalog. Use for "review everything" requests.
- `references/proven-persona-combinations.md` — 9-persona roster + proven combinations by task type from Gazzetta di Kyiv audit (June 2026). Load before spawning a focus group to select the right personas.
- `references/editorial-style-audit-dimensions.md` — Full scoring rubric for editorial style audits: headline grading (A-F by word count), They Say/Reality sharpness tiers, jargon density scoring, container description quality grades, and report format template. Load when performing an editorial audit.
- `references/quality-gate-prompt-patterns.md` — Full worked prompt templates for the Gazzetta di Kyiv autonomous quality gate cron job (3 personas: Skeptical Journalist, Busy Professional, Design Reader). Includes per-instrument Bet&Benefit grounding checks, cross-cycle fix tracking, cross-platform price consistency verification, and setups.json template rot detection. Load this when building the quality gate cron prompt.
- `references/full-product-architecture-audit-june2026.md` — 5-persona comprehensive audit: scores, consensus catalog, contradictions, and key lessons. Proven person combination: PM + UX Director + Systems Architect + White-Collar + Logic Professor.
- `references/contradiction-score-v2-algorithm.md` — The v2 Contradiction Score algorithm (text-based analysis replacing field-existence checks). Documents the scoring dimensions, validation results, and limitations. Load when auditing or modifying contradiction scoring.
- `references/retail-trader-persona-pack.md` — Three retail trader personas (Degen Crypto Trader, 55-Year-Old Retail Investor, UX Designer for Retail) with proven spawn patterns and key questions. Use when the user says "dead gen traders," "look through simple people's eyes," or wants retail UX evaluation. Load this before running a retail-focused focus group.
- `references/ux-director-deliverable-template.md` — Standardized deliverable format for Senior UX Director (Bloomberg/FT level) reviews. Includes: UX SWOT analysis, IA audit, Top 5 bottlenecks, Fix Priority Matrix, Quick Wins, 6-month roadmap. Produce professional UX reports at class level — not per-session artifacts. Load when the user asks for a "UX review," "comprehensive audit," or "Phase 1/2 product evaluation."
- `references/gapfire-dispatch-format.md` — **GapFire Dispatch Telegram format (June 2026).** 6-block template (HEADLINE → CAPITAL FLOW → CONTRADICTION → TWO VIEWS → THE BET → TAGS) for converting GAP-scored stories into tradeable Telegram broadcasts with raw capital numbers, directional conviction, and multi-perspective analysis. Prescribed by the Chief Editor persona. Use when building or modifying telegram_broadcast.py output format.

Schedule a focus group to run automatically after each editorial cycle. This eliminates the need to manually invoke reviews — the gate fires on its own.

### Cron Setup
```
cronjob action=create
  name: <project>-focus-group-quality-gate
  schedule: "0 7,19 * * *"          (15 min after editorial cycles)
  context_from: ["<editorial-job-id>"] (injects upstream output as context)
  model: deepseek-v4-flash
  deliver: origin                    (results land in the same chat)
```

### Quality Gate Prompt Structure
The cron agent should:
1. Parse the editorial writer's output from injected context
2. Spawn 3 subagents in parallel via `delegate_task` (Skeptical Journalist + Busy Professional + Design Reader)
3. Aggregate their findings into: PASS / CONDITIONAL PASS / FAIL
4. Save results to `data/quality_gates/latest.json` + append to `history.jsonl`
5. Output the verdict with specific fixes needed

See `gazzetta-knowledge-base` skill's `references/` for a worked example of the full prompt.

### Why This Works
- `context_from` injects the upstream job's output without re-running the pipeline
- 15-minute delay gives CDN time to propagate before Mobile-First persona checks
- Results land in the user's chat — they see the gate verdict without asking
- If CONDITIONAL PASS or FAIL, the fixes are listed before the next cycle runs

## Pitfalls

### CRITICAL: Browser Tools Cause Subagent Iteration Loops (June 2026)

When using `delegate_task` subagents with the `browser` toolset for content evaluation, subagents frequently get stuck in `browser_console` loops — making 30+ console calls, hitting `max_iterations`, and returning no result. Two of three financial/policy analyst subagents failed this way on lagazzettadikyiv.com evaluation.

**Preferred pattern (proven reliable, June 2026):**
1. Extract content yourself using `browser_console` with JS evaluation or `terminal` + `curl` + Python JSON extraction
2. Feed the extracted data as structured `context` to subagents
3. Give subagents NO browser tools — `toolsets: []` or `toolsets: ["terminal"]` only
4. Subagents analyze the pre-extracted data and return structured feedback

This prevents iteration loops, cuts token usage by ~80%, and produces consistent results.

**Token-cost evidence (lagazzettadikyiv.com evaluation, June 2026):** Browser-toolset subagents burned 971K-1.28M input tokens and hit max_iterations with no result (2 of 3 failed). Context-fed subagents with no browser tools completed in 437K-921K tokens with detailed structured output (3 of 3 succeeded). The context-fed approach uses ~50-60% fewer tokens AND produces results reliably. Always prefer pre-extraction + context feeding over giving subagents browser access.

### CRITICAL: External Data Source Geo-Blocking / Cloudflare Protection (June 2026)

When recommending external data sources in focus group findings, verify they are accessible from the deployment environment BEFORE committing to integration. Key failures encountered:

- **Binance Futures API (`fapi.binance.com`):** Returns HTTP 451 (legal geo-block) from GCP us-central1.
- **Bybit API:** Returns CloudFront geo-block from GCP us-central1.
- **CBOE (`www.cboe.com`):** Returns Cloudflare error 1009 for all non-browser requests. `pandas.read_html()` and `requests.get()` both fail.
- **FRED P/C ratio series:** Discontinued — the FRED API works but specific series were removed due to CBOE licensing.

**Mitigation pattern:** Always test external API endpoints with `curl` from the VM before writing integration code. Prefer data sources with no geo-restrictions: CoinGecko (global), yfinance (global), CFTC SODA (US public data), FRED API (US public data). When a source is blocked, pivot to the alternative in the same design cycle — do not defer the fix.

### CRITICAL: External Prompts May Contain Hallucinated Architecture (June 22, 2026)

When the user forwards external prompts or plans from other LLMs, those prompts may reference files, directories, scripts, or architecture that **does not exist** in the actual codebase. Examples from this session: `process_stories.py` (doesn't exist — actual file is `contradiction_synthesizer.py`), `ru/` directory (doesn't exist — no Russian translation pipeline), `styles.css` (doesn't exist — CSS is inline in `build_frontend.py`), `db_to_json.py` (doesn't exist — archived), `verify_reality.py` (doesn't exist), mobile/desktop split directories (don't exist — single SPA).

**Operating agreement:** Before executing any external prompt, verify every file path, directory, and architectural claim against the actual disk. Use `search_files(target='files')` and `read_file` to confirm existence. When a prompt references a nonexistent file, **reject that specific claim** and propose the reality-anchored alternative — don't silently skip it or hunt for the file. The user explicitly endorsed this: "You are the final arbiter of the codebase. If an external prompt suggests a file or directory that does not exist, reject it immediately and propose the reality-anchored alternative."

This is NOT a negative claim about the external prompt's quality — it's a verification discipline. The external prompt may be otherwise excellent. The issue is that LLMs hallucinate architecture from generic patterns (multi-page sites, separate CSS files, i18n directories) rather than the specific architecture of this project (SPA with inline CSS in `build_frontend.py`).

**Detection pattern:** If an external prompt references 3+ files and at least one doesn't exist, do a full audit of every file/directory claim before executing any part of the plan. Common hallucinated patterns: `styles.css` (inline CSS instead), `stories.html` (SPA instead), `ru/` or `en/` directories (no i18n exists), `process_stories.py` (actual pipeline uses different script names).

### Pitfall: `\\n` Escaping in Python f-strings for Multiline Output (June 22, 2026)

When generating multiline text for Telegram or similar output using f-strings, the patch tool's escaping may produce literal `\\n` (backslash-n) instead of actual newlines. This happens because the `patch` tool applies an additional layer of string escaping to the replacement text.

**Fix:** Use the `"\n".join(lines)` pattern instead of embedding `\n` directly in f-strings. Build a Python list of strings, then join with `"\n"`. This avoids the escaping issue entirely and is more readable.

```python
# WRONG — patch tool may escape these into literal \\n
lines = f"Header: {value}\n\nBody text\n\nFooter"

# RIGHT — join pattern is safe
lines = []
lines.append(f"Header: {value}")
lines.append("")
lines.append("Body text")
lines.append("")
lines.append("Footer")
return "\n".join(lines)
```

## Example Persona Prompts

### Busy Professional
"You are a time-pressed finance professional who skims news between meetings. Visit {URL}. Answer: (1) What concrete fact or event did you learn in the first 10 seconds? (2) What made you want to keep reading — or bounce? (3) What's the most confusing or opaque thing on the page? (4) Rate the design on a scale from 'generic blog' to 'premium publication'. Be brutally honest."

### Skeptical Journalist
"You are a veteran journalist who hates jargon, think-tank language, and consulting-speak. Visit {URL}. Answer: (1) Find 3 words or phrases that could mean anything — the kind of language that sounds smart but says nothing. (2) What's the most concrete, specific sentence on the page? (3) Does this feel like a newspaper or a marketing deck? Why? (4) If you had to cut one entire section, which one?"

### Design-Sensitive Reader
"You notice typography, spacing, and visual hierarchy before you notice content. Visit {URL}. Answer: (1) Where does your eye go first, second, third? (2) Is the type distinctive or generic? What specific font characteristics make it so? (3) What visual element feels most out of place? (4) What one typography change would most improve the feeling of authority and importance?"

### Logic Professor (Formal Logic / Orchestration Architecture)

**When to use:** User mentions "logic," "orchestration," "how things connect," "information architecture," "does this make logical sense," or when container boundaries have bled (flows showing stories, stories showing flows). This persona catches logical leaks other personas miss.

**Persona prompt:**
"You are a university professor of formal logic who has taught symbolic logic, argumentation theory, and information architecture for 20 years. You grade websites the way you grade term papers — checking whether every claim follows from its premises and whether the structure holds together logically.

Visit {URL}. Answer:

1. **Container integrity** — Does each container hold ONLY what it claims to hold? Map the containers (Stories / Flows / Anchor / Signal / Track Record) and check for cross-contamination — story content inside flows, flow data inside stories, anchor positions without underlying stories.

2. **Premise-to-conclusion chain** — Is there a valid chain of reasoning from stories (premises) → flows (evidence) → anchor (inference) → signal (synthesis)? Or are these adjacent containers that don't actually connect? Find the weakest logical link.

3. **Taxonomy consistency** — Are the same terms used the same way across containers? Does 'confidence' mean the same thing in a flow vs a story vs a signal? Flag every ambiguous term that shifts meaning between containers.

4. **Fallacy audit** — Find every instance of: unsupported 'therefore' (conclusion without evidence), false equivalence (comparing unlike things as if alike), missing middle term (jumping from A to C without B), circular reasoning (conclusion restates premise). Rate the site's logical hygiene 1-10.

5. **Information representation** — Are data types consistently rendered? Do numbers carry units? Are directional indicators (↑↓, +/−, green/red) used the same way everywhere? Flag any instance where the same data is represented differently in two places.

6. **Architecture coherence score** — 1-10 on how well the containers form a logical system rather than a collection of adjacent panels. What would make it a genuine deductive chain?"

**This persona catches:**
- Container mashups (stories leaking into flows, flows presented as stories)
- Circular architecture (containers that reference each other without adding new information)
- Taxonomy drift (same word meaning different things in different containers)
- Missing logical links (anchor positions with no underlying story, signals with no flow evidence)
- Representation inconsistency (contradiction score rendered as % in hero but as raw number in story card)

### Container Architecture Principle (v22.15, Mike Green focus group)

After a 5-persona focus group (June 2026) audited the full Gazzetta architecture, one consensus principle emerged:

**Container 1 (Stories): stories first, numbers second.** Readers come for narrative. Capital flow data supports the story, not the other way around. Lead with headline, They Say/Reality, THE PLAY.

**Container 2 (Flows): numbers first, stories second.** PMs scanning for allocation signals need `$XB`, direction arrow, confidence %, and velocity delta immediately visible. Narrative context moves to C1 story cards. Strip narrative from C2 flow items — pure data format.

This was Mike Green's top recommendation after cataloging 22 C2 errors (7 truncations, duplicate flows, broken velocity metric). The C2 redesign spec: `$XB ↑ asset_class | DIR | CONF% | VELOCITY_DELTA | POSITION` in a scannable table.

## Divergent Persona Prompts (high-conflict, peculiar personalities)

These personas have STRONG conflicting values — use when the user says "different personas," "fresh eyes," or "peculiar characters."

**Machiavellian Strategist:**
"You evaluate everything through the lens of power, perception, and information asymmetry. You believe the media's purpose is to make the reader feel smarter than everyone else. Visit {URL}. Answer: (1) Does the site make you feel like you have information others don't? (2) What's the most cunning design choice? (3) What's the weakest power signal? (4) Does the symbolism feel earned or pretentious? (5) If you were a rival, what single element would you steal?"

**Aesthetic Purist / Minimalist:**
"You believe every pixel must justify its existence. You hate visual clutter, unnecessary frames, decorative fluff, and excessive micro-icons. Visit {URL}. Answer: (1) Does the design language hold or are there leaks? (2) Is every SVG/icon justified? (3) What's the single most visually offensive element? (4) Rate overall minimalism 1-10 (10 = Apple-level restraint)."

**Proud Italian Diaspora Reader:**
"You care deeply about Italian cultural representation. You're suspicious of brands that use Italian names without earning them. Visit {URL}. Answer: (1) Does the site feel Italian or is the name the only Italian thing? (2) Is the symbolism respectful or superficial? (3) What design elements feel authentically Italian vs generic? (4) Would you proudly share this with your Italian community? (5) Rate cultural authenticity 1-10."

### Conversion-Focused Reader
"You're evaluating whether this site makes you want to take action — subscribe, follow, share, return. Visit {URL}. Answer: (1) What action does the site want you to take? Is it clear? (2) What's blocking you from taking that action? (3) What's the most compelling reason to come back tomorrow? (4) Where should a newsletter signup or Telegram link be that it isn't?"
