# Gazzetta di Kyiv — Autonomous Media Business Plan

## 0) Status Snapshot
- **Operations stopped:** all cron jobs removed per instruction.
- **Prepared:** governance docs, brandbook checks, watchdog scripts, content builders, channel bundle builders.
- **Under development:** complete front-end visibility consistency + cross-channel publication verification loops.

## 1) Mission, Vision, Objectives
### Mission
Deliver high-frequency, investment-oriented narrative intelligence with clear action paths, confidence, and risk invalidation.

### Vision
Operate as an autonomous digital newspaper with institutional-grade reliability and cross-channel consistency (Website + Newspaper X + Chief Editor X).

### Objectives (90-day)
1. Visible twice-daily content refresh on all surfaces.
2. 99% publish-cycle completion reliability.
3. 100% narrative objects with required fields.
4. 0 unresolved stale-UI incidents beyond one cycle.

## 2) Priorities (in order)
1. **Visibility first:** every completed pipeline must be visibly reflected to users.
2. **Content quality:** unique, non-generic, short-term actionable, confidence-tagged.
3. **Cross-channel consistency:** same narrative core, adapted format by channel.
4. **Autonomous governance:** stop/slow loops automatically when quality drops.

## 3) Pipeline Reviews
### A) Data Pipeline Review
**Purpose:** ingest, normalize, and score narrative candidates.
- Strengths: ingest cadence established; source update scaffold exists.
- Gaps: source quality weighting and freshness SLAs not fully enforced end-to-end.
- Upgrade: implement source confidence score, dedup hash, and freshness expiry.

### B) Content Pipeline Review
**Purpose:** transform data to investment-readable narrative objects.
- Strengths: schema fields drafted; brandbook checks exist.
- Gaps: occasional generic phrasing and visibility mismatch.
- Upgrade: enforce mandatory fields + banned-generic lexicon + quality score gate.

### C) Management Pipeline Review
**Purpose:** orchestration, QA gates, incident handling.
- Strengths: control-loop and watchdog concepts in place.
- Gaps: overlapping jobs historically created ambiguity.
- Upgrade: single orchestrator, deterministic state machine, stop-the-line policy.

### D) Representation Pipeline Review
**Purpose:** map content into UI and channel formats.
- Strengths: channel bundle model exists.
- Gaps: front-end binding lag created “unchanged site” perception.
- Upgrade: schema-contract tests against live HTML/JS and visual acceptance checks.

### E) Placement / Distribution Review
**Where content should be represented:**
1. Website homepage (left: narrative depth, right: tactical action cards)
2. Newspaper X page (headline + implication + action + confidence)
3. Chief Editor X page (editorial POV + controversial angle + risk framing)
4. Subreddit/long-form discussion surface (threaded context + comments cues)

## 4) Enterprise Operating Model (Autonomous Loops)
### Loop 1 — Ingestion (every 30m)
Collect, dedup, score sources, publish candidate set.

### Loop 2 — Content Build (06:30, 18:30)
Generate narrative objects with required fields and projections.

### Loop 3 — Representation Sync (after Loop 2)
Render website + package X variants + produce publish payloads.

### Loop 4 — Verification (every 15m)
Live endpoint + renderability + content-visibility assertions.

### Loop 5 — Governance (every 2h)
Score pipelines, detect regressions, pause non-critical operations on failure.

## 5) Policies, Procedures, Rules
- **Policy:** no “completed” status unless visible live.
- **Procedure:** draft → review → approve → publish → verify.
- **Rule:** if visibility fails, switch to degraded and pause publication loops.
- **Rule:** confidence + invalidation required for each tactical recommendation.

## 6) Master Execution Prompt
```text
You are Hermes acting as Autonomous COO/Editor for Gazzetta di Kyiv.
Execute the 5-loop operating model (ingestion, content, representation, verification, governance).
Enforce required narrative schema and brandbook.
Publish only when live visibility checks pass.
If visibility or quality score fails, pause non-critical loops, keep watchdog + remediation loop active, and report incident with ETA.
Output: audit report, action queue, updated channel bundles, and verified live links.
```

## 7) Skill Acquisition Prompt
```text
Search for and load all relevant skills for autonomous media operations: Hermes-agent operations, social posting workflows, reliability/watchdog, editorial governance, and data pipeline QA.
For each missing capability, create or update a skill with SOP steps, pitfalls, verification checks, and rollback actions.
Then execute the operating model using those skills and produce evidence artifacts.
```

## 8) Professional Industry Review Prompt
```text
Act as an industry media-operations consultant. Perform a professional audit of this project across editorial quality, market-intelligence usefulness, reliability engineering, governance, and distribution operations.
Score each area 0-100, benchmark against best practices, identify critical gaps, and provide a phased remediation roadmap.
Save outputs into procedures, rules, policies, processes, goals, mission, vision, objectives documents.
```

## 9) Immediate Next State to Relaunch (when approved)
1. Recreate only 3 jobs initially: verification, content build (2x/day), governance.
2. Run 24h trial with strict stop-the-line rules.
3. Add channel publishing loops only after visibility score >= 90 for 3 consecutive cycles.
