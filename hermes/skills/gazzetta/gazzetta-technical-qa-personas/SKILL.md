---
name: gazzetta-technical-qa-personas
description: "Technical QA focus group pack — infrastructure, UX writing, mobile, and empty-container detection. Supplements editorial personas. Catches SSL certs, broken features, ambiguous labels, CSS breakage."
version: 2.0.0
category: gazzetta
---

# Technical QA Persona Pack

Supplement to editorial personas. These catch what the narrative/design personas miss: infrastructure failures, empty containers, ambiguous labels, and mobile breakage.

## Persona Roster

### 1. SRE/DevOps Engineer
**Catches:** SSL certs, CDN propagation, HTTP errors, deploy failures, cache issues
**Questions:** 
- Does the custom domain resolve and serve over HTTPS without certificate errors?
- Are CDN cache headers correctly set (max-age=0, must-revalidate)?
- Does the GCS direct URL work as fallback?
- Are there 404s, 500s, or mixed-content warnings?
- Is the deploy pipeline completing (check last deploy timestamp vs expected cadence)?

### 2. QA/Tester
**Catches:** Empty containers, JS errors, NaN values, broken click handlers, missing data, orphan DOM elements, dead freshness indicators, corrupted JS files, mystery numbers, debug artifacts in production
**Questions:**
- Are ALL containers populated (stories, flows, anchor, signal, track record)?
- Does the signal container show triangulation data or is it empty?
- Are there console errors? JS exceptions? **Empty-message JS exceptions** (`"message": ""`) are often cross-origin script errors or corrupted-file parse failures — investigate them even if the page appears to load.
- Do expand/collapse toggles work on all containers?
- Are flow→story links resolving (not showing "Loading...")?
- **Are freshness indicators populated?** Cross-reference `<span id="storyFreshness">`, `<span id="flowFreshness">`, `<span id="heroFreshness">`, `<span id="heroContradictions">`, `<span id="heroTopVelocity">` against `grep -c "byId('X')" app.js` — any element in HTML without a JS reference is an orphan.
- **Do hero indicators show real values?** Check `#heroFreshness`, `#heroContradictions`, `#heroTopVelocity` — if they show `—` after page load, the JS to populate them is missing or broken.
- **Do count/subtitle elements show real values?** Check `#teaserStoryCount`, `#teaserFlowSub`, `#teaserTradeSub`, `#teaserSignalSub`, `#teaserTrackSub`, `#heroProductCount` — if they show `—` after page load, the populator function didn't fire.
- **Are story detail pages rendering? (v25.1)** Navigate to `story.html?id=<any_valid_id>`. Check `bodyLen > 3000` AND no "Loading intelligence report…" stuck. A corrupted `story-app.js` (line-number prefixes embedded in every line) parses as invalid JS — the page stays stuck with zero console errors. Verify with: `curl -sk $SITE/story-app.HASH.js | head -1` — must start with `// story-app.js` (no leading whitespace+digits+pipe). **NEW v26.8: Raw JS visible as DOM text** — if `<script>` tags are malformed (encoding issue, HTML-in-JS escaping failure, or build pipeline corruption), the browser renders the entire inline script block as visible page text. Symptom: user sees raw `const app = …`, `fetch('/data/…')`, `document.querySelector…` as paragraphs below the masthead. Check with: `document.body.textContent.includes('const app') || document.body.textContent.includes('addEventListener')` — if true, the script tags are not being parsed. Fix is in build pipeline (HTML templating), not CSS.
- **Are market regime cards populated? (v25.1)** On flows.html, check all `.regime-value` elements: none should be `—`. If all three show `—`, `renderMarketRegime()` failed silently — likely `Object.forEach()` on a dict or field-name mismatch (`ind.indicator` vs JSON key).
- **Are freshness labels time-based, not percentages? (v25.1)** Check `.freshness-ago` elements: `hasPercents` must be false. Bare percentages (`100%`, `75%`) are read as confidence scores by every user. The fix is `formatTimeAgo(s.generated_at)` instead of `{pct}%`.
- **Are flow heat/signal numbers labeled? (v25.1)** On flows.html, the number after "PDR 7.5x" must have a visible label (e.g., "Signal 100", not bare "100"). Bare numbers are uninterpretable without hover.
- **Are there debug artifacts in production? (v25.1)** Check flow-nodes.html for "KEYS: 1-6 FILTER · ESC CLOSE · ←↑↓→ NAVIGATE" — this `.cn-kb-hint` span must be hidden (`display: none`). Check all pages for line-number prefixes (`N|`) in visible text.
- **Do WATCH-level trades show "Monitoring" not "Stop —"? (v25.1)** On trades.html, assets with WATCH bias should show "Monitoring" (not "Stop — · 2×ATR") when no stop price is computed. A dash looks like broken data.
- **Are sector labels displaying human-readable names? (v25.1)** On flows.html sidebar, `.sector-stat-label` must show "Fixed Income" (not "fixed_income"), "Crypto" (not "crypto"), etc. Raw DB keys look unprofessional.

### 3. Content Designer / UX Writer
**Catches:** Ambiguous labels, jargon without explanation, missing context, misleading terms, raw DB keys in display, empty-state labels that look broken
**Questions:**
- Does every visible label communicate what it measures? ("DEVELOPING 50" → what?)
- Are acronyms explained? (PDR, ATR, bp, DXY)
- Do tier labels match user expectations? ("ALIGNED" = positive word, low-edge meaning)
- Is the scale/context visible without hover? ("50" needs "/100")
- Would a first-time user understand every stat without hovering?
- **Are sector labels human-readable? (v25.1)** "fixed_income" → should be "Fixed Income". "fx" → "FX" is acceptable. Raw DB keys must never appear as user-facing labels.
- **Are empty states graceful? (v25.1)** "Stop —" on WATCH trades looks like broken data. Use "Monitoring" or "No stop set" instead of dashes for intentionally empty fields.
- **Are signal numbers labeled? (v25.1)** Bare numbers after PDR (e.g., "PDR 7.5x 100") need a visible label like "Signal 100" or "Score 100/100". Tooltip-only labels fail the "no hover required" test.
- **Are freshness labels time-based, not percentages? (v25.1)** "100%" on a story teaser is universally read as confidence, not recency. Must show time-ago labels ("2h ago", "yesterday").
- **Do hero stats have timeframe context? (v25.1)** "72 DIVERGENCES" — in what timeframe? "2.3× TOP VELOCITY" — relative to what baseline? Add context in tooltips or subtitles.

### 4. Mobile-First Designer
**Catches:** Responsive breakage, touch target sizes, horizontal overflow, illegible text
**Questions:**
- At 390px: do hero stats stack or overflow?
- Are tap targets ≥44px?
- Is text ≥14px for body, ≥16px for inputs?
- Does any content require horizontal scroll?
- Are container descriptions readable on small screens?

## Spawn Pattern (parallel, 3 agents max — limitation)
**max_concurrent_children defaults to 3.** If you need all 4 personas, run 3 first, then the 4th after the first batch completes. Prefer SRE + QA + UX Writer in round 1 (these find the most issues), then Mobile in round 2.

Round 1 (3 agents in parallel):
```
delegate_task(tasks=[
  {goal: "SRE review of {URL}...", toolsets: ["browser", "terminal"]},
  {goal: "QA review of {URL}...", toolsets: ["browser"]},
  {goal: "UX Writing review of {URL}...", toolsets: ["browser"]},
])
```

Round 2 (after round 1 completes):
```
delegate_task(goal: "Mobile review of {URL} at 390px...", toolsets: ["browser"])
```

## DevOps Infrastructure Audit (SRE + Platform Engineer + Build/Release Engineer)

Use when the user says "organise as devops would," "audit the infrastructure," "review the directory structure," or "engage team professionals" for any filesystem/infrastructure review. This is a **general-purpose combo** — not Gazzetta-specific. Works for auditing `~/.hermes/`, project repos, deployment pipelines, or any directory tree.

### Persona 1: Senior SRE (Google-scale experience)
**Catches:** Separation of concerns violations, security risks, unbounded growth, missing .gitignore, PII exposure, missing retention policies, missing documentation
**Prompt template:**
```
You are a Senior SRE with 15 years experience. Audit {TARGET_PATH} for:
1. Separation of concerns — do project files live in runtime space? Are there cross-contamination risks?
2. Security — are there secrets, auth tokens, or PII in unexpected locations? Is there a .gitignore?
3. Unbounded growth — which directories have no TTL or eviction policy?
4. Structure — does the layout make sense to a new engineer? What's missing?
Return P0-P3 findings with severity, violation type, and recommended fix.
```
**Toolsets:** `["terminal", "file"]`

### Persona 2: Platform Engineer (Agent infrastructure specialization)
**Catches:** Missing structure docs, poor config/data separation, ad-hoc scratch directories, retention policy gaps, duplicate runtimes
**Prompt template:**
```
You are a Platform Engineer specializing in agent infrastructure. Design the ideal directory structure for {TARGET_PATH} following DevOps conventions.
1. Separate config vs runtime vs data vs cache vs logs
2. Project files must NOT live in agent runtime space
3. Everything discoverable and documented
Return a tree diagram with annotations explaining each directory's purpose and retention policy.
```
**Toolsets:** `["terminal", "file"]`

### Persona 3: Build/Release Engineer
**Catches:** Exact file paths of misplaced files, stale artifacts, duplicate data, orphaned caches, macOS junk (.DS_Store), conversation dumps, dead configuration
**Prompt template:**
```
You are a Build/Release Engineer. Identify every file in {TARGET_PATH} that does NOT belong there. For each: exact path, why it doesn't belong, and the mv/rm command to fix it. Be exhaustive — list every file. Group by category: project files in wrong location, stale configs, duplicate data, orphaned artifacts, temp files, dead features.
```
**Toolsets:** `["terminal", "file"]`

### Spawn Pattern (3 agents, parallel)
```
delegate_task(tasks=[
  {goal: "SRE audit of {TARGET}...", toolsets: ["terminal", "file"], context: "..."},
  {goal: "Platform engineer design for {TARGET}...", toolsets: ["terminal", "file"], context: "..."},
  {goal: "Build/release audit — every misplaced file in {TARGET}...", toolsets: ["terminal", "file"], context: "..."},
])
```

### Execution Order
1. Spawn all 3 in parallel
2. Synthesize findings: P0-P3 severity, consensus issues, exact shell commands for fixes
3. Execute fixes in priority order (P0 → P1 → P2 → P3)
4. Verify with final `du -sh` and `ls` audit

### Pitfalls
- **Don't skip the Build/Release Engineer** — the SRE and Platform Engineer find structural problems, but only the Build/Release Engineer produces the exact `rm`/`mv` commands for each file
- **Don't execute FHS restructures without checking config paths** — Hermes core expects specific paths (config.yaml, sessions/, skills/ at root). Moving them requires updating config.yaml paths and restarting the gateway
- **Don't edit bundled/protected skills** — `hermes-agent` SKILL.md is owned by the framework
- **Docker stale-files trap (June 2026)** — When a Docker image bundles `public/*.html` or `data/*.json` via `COPY`, those files are baked into the image at build time. If the pipeline's runtime scripts (`build_site.py`, `db_to_json.py`) fail silently, the stale bundled files are what get deployed to GCS — overwriting previously-working live pages with old/corrupted versions. **Fix:** Purge all generated files at Docker build time (`RUN find /app/public -name "*.html" -delete`) and let runtime scripts regenerate them fresh. If runtime generation fails, the deploy should fail loudly, not serve stale content.
- **Script tag imbalance → raw JS visible** — If `<script>` count ≠ `</script>` count in any HTML page, the browser renders the unclosed JS block as visible DOM text. Check with `grep -c '<script' page.html` vs `grep -c '</script' page.html`. A common cause: inline JS blocks missing their opening `<script>` tag after template refactoring.
- **`.gcloudignore` blocks Dockerfile `COPY gazzetta.db`** — If `.gcloudignore` has `*.db`, Cloud Build excludes `gazzetta.db` from the build context. The Dockerfile `COPY gazzetta.db /app/` fails with "file not found in build context." Fix: add `!gazzetta.db` exception line AFTER the `*.db` wildcard in `.gcloudignore`.
- **`story.html` missing `#storyContent` div** — The `story-app.js` rendering engine targets `getElementById('storyContent')` but the story page HTML may not contain this element. Without it, the page renders masthead+footer only with no story content. Verify with `grep -c 'storyContent' public/story.html` — must be ≥1.
- **`story.html` missing `story-app.js` include** — Even with the `#storyContent` div, the page won't render if it doesn't load the rendering engine. Verify with `grep 'story-app' public/story.html` — the hashed filename must appear in a `<script src>` tag.

## Integration
Add to `gazzetta-ceo-overseer` cron as a 4h quality gate (runs after editorial cycle). Combine with editorial personas for full coverage.

**Comprehensive audit workflow:** `references/comprehensive-audit-workflow.md` — full multi-phase pattern for "debug everything" requests. Spawns 3 focus groups + integrity check + browser verification simultaneously.

**Pipeline data-first diagnosis:** `references/pipeline-data-first-diagnosis.md` — when a pipeline field is empty across all stories, check the actual data endpoint before theorizing about prompt engineering. Includes the max_tokens starvation misdiagnosis from June 2026.

**7-stream institutional audit framework:** `references/comprehensive-institutional-audit.md` — full 183-check audit across SRE, QA, UX, Mobile, Data Pipeline, Accessibility, and Product Readiness. Use for quarterly audits or post-major-deploy verification. Spawns 7 independent persona streams in parallel batches of 3.
