# Gazzetta di Kyiv — Master Audit & Execution Blueprint (V3)

## 0) Executive Summary (Current Reality)
- The codebase has **new landing architecture implemented locally and pushed** (hero strip, CTA, "Stories in Play" section, story-card renderer).
- The **live website still renders old-state behavior/content**, indicating deployment/sync divergence, stale artifact routing, or cross-repo sync overwriting.
- Editorial surface is still too dashboard-like relative to mission: users want **stories + evolution + implications + forecasts**, not label grids.
- Ops has gates, but product-fit gates for story readability and narrative continuity are still weak.

Bottom line: technical change exists, but delivery chain and content contract are not reliably enforcing the intended product.

---

## 1) Vision / Mission / Goal Alignment

### Vision (as encoded in mandate)
European narrative-intelligence newspaper with institutional rigor and retail readability.

### Mission
Turn global story flow into actionable cause-effect intelligence for market participants.

### Product Goal
Every visit and every Telegram post should answer:
1. What stories are actually in play?
2. How are they developing?
3. What economic chains do they trigger?
4. What assets reprice next, in what direction, and with what invalidation?

### Gap vs Goal (today)
- UI still over-indexes on framework labels and under-delivers on readable story narrative.
- Deployment pathway is not deterministic from commit -> pages render.
- Content schema still allows generic filler and repeated boilerplate.

---

## 2) Full-System Audit (What We Have)

## A. Product / UX
Strengths:
- Distinct brand and palette.
- Useful structural primitives (frames, claims, regime).
- Data + API surfaces exist.

Weaknesses:
- Above-the-fold narrative promise is weak in live output.
- Story body lacks newsroom readability standards.
- Search/filter behavior tied to old `.claim-row` class while cards now use `.story-card`.
- CTA and trust widgets not consistently visible in live deployment.

Industry-fit required:
- Homepage must behave like an **intelligence front page**, not internal QA panel.

## B. Editorial Contract
Strengths:
- Operating mandate is strong and explicit.
- Telegram automation exists and runs.

Weaknesses:
- Story generation quality can degrade into templated filler.
- No strict lint for "story has development + implications + forecast" at website render time.

Industry-fit required:
- Hard editorial schema checks before publish.

## C. Data / Modeling
Strengths:
- Regime, setups, divergences, contradictions endpoints exist.
- Confidence/probability fields are present.

Weaknesses:
- Forecast ranges are partly placeholder-like in renderer.
- Missing explicit map from source claims -> repricing path per major asset cluster.

Industry-fit required:
- Asset repricing matrix should be generated from structured fields, not static fallback strings.

## D. Deployment / Reliability
Strengths:
- CI gate scripts exist.
- GitHub Pages workflow exists.

Weaknesses:
- Live mismatch strongly suggests deployment race, stale artifact, or sync override from peer/upstream workflow.
- Local repo has frequent modified generated files; not all are intended for commit.

Industry-fit required:
- Deterministic release train: commit hash must be visible on live page; if mismatch, alert and rollback policy.

## E. Governance / Observability
Weakness:
- No visible "build id / deployed commit" on page to prove recency.
- No synthetic smoke check validating that key selectors and headings changed after deploy.

---

## 3) Root Causes of "Nothing Changed" Perception
1. **Delivery verification missing**: commits were made but live page did not clearly prove deployed revision.
2. **Content contract mismatch**: user expects narrative stories; interface still reads as metrics dashboard.
3. **Insufficient anti-regression checks**: gate checks style/system integrity but not mission-level story quality.

---

## 4) Target Operating Blueprint (Industry-fit)

## Phase 1 — Truth & Control (Immediate)
1. Add visible build stamp on landing page (`deployed commit + UTC time`).
2. Add post-deploy synthetic check that asserts:
   - heading contains "Stories in Play"
   - story cards render with Development/Implications/Forecast labels
   - hero CTA exists
3. Block release if synthetic check fails.

## Phase 2 — Story-First Product Surface
1. Replace claim-list semantics with a true `stories` rendering pipeline.
2. Each story card must include:
   - what happened
   - what changed in last 2h/24h/3d
   - first-order effects
   - second-order spillovers
   - 24–72h asset repricing map
   - invalidation conditions
3. Add concise “Top 5 stories in play” front block.

## Phase 3 — Editorial Quality Gates
Create a `story_quality_guard.py` that fails build unless each published story has:
- min fact density (numbers/dates/entities)
- causality link words present (because/therefore/transmission)
- at least one explicit forecast with probability and invalidation
- at least two affected assets (winner/loser framing)

## Phase 4 — Distribution Synchronization
1. Unify website story schema and Telegram post schema from same source object.
2. Stop manually diverging templates.
3. Add snapshot archive per run for auditability.

## Phase 5 — Strategic KPI Layer
Track weekly:
- deploy truth rate (live hash == repo head)
- story readability score
- signal density score
- forecast hit-rate windowed by horizon
- narrative continuity coverage

---

## 5) Priority Backlog (P0 -> P2)

### P0 (must do now)
- Deployment truth stamp + synthetic smoke check.
- Fix renderer-search coupling to `.story-card` (currently still wired to `.claim-row`).
- Ensure live homepage renders stories, not single-token abstractions.

### P1 (next)
- Structured story schema + story quality guard.
- Repricing matrix tied to real fields (not static projection placeholders).

### P2 (after stabilization)
- Reader-mode/mobile narrative compaction.
- Evidence drawer with references per story.

---

## 6) Professional Prompt Pack (Use Before Action)

## Prompt A — Full-System Reality Audit
"Audit the entire Gazzetta di Kyiv stack end-to-end (content generation, website rendering, CI gates, deployment, Telegram distribution). Output: (1) current-state architecture map, (2) failure points causing user-visible mismatch, (3) mission-gap analysis vs mandate, (4) prioritized remediation plan with measurable acceptance criteria. Do not summarize vaguely; cite exact files, workflows, selectors, and data contracts."

## Prompt B — Story-First Homepage Refactor
"Refactor homepage from metric-dashboard feel into story-first intelligence front page while preserving existing visual doctrine and gate compatibility. Ensure `Stories in Play` renders top narratives with `Development`, `Implications`, `Forecast`, and `Invalidation` fields. Keep compact typography constraints but increase readability. Provide diffs and pass all gate scripts."

## Prompt C — Deployment Truth Enforcement
"Implement deterministic deploy verification for GitHub Pages: surface deployed commit hash in UI, run post-deploy synthetic validation against production URL, and fail/alert if expected selectors/content are absent. Add runbook for cache/version drift incidents."

## Prompt D — Editorial Quality Gate
"Create a build-time story quality gate that validates every generated story has numeric facts, explicit causality chain, cross-asset winners/losers, probability-based forecast, and invalidation trigger. Fail build on generic filler language."

## Prompt E — Telegram-Website Schema Unification
"Unify Telegram post and homepage story cards onto one canonical story object schema. Guarantee that every post claim is linkable to a corresponding website story block with references and forecast metadata."

---

## 7) Acceptance Criteria (Definition of Done)
- Visiting production URL shows story-first content immediately.
- Live page visibly displays deployed commit hash and update timestamp.
- `Stories in Play` section includes multi-line story development + implications + forecasts.
- CI fails on narrative filler and missing causality/forecast fields.
- Telegram post claims map 1:1 to website story objects with links.

---

## 8) Execution Mode
Authorized mode confirmed: ship with minimal downtime, verify after each deploy on production URL, and report only evidence-backed status.