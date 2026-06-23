# Comprehensive Website Audit Workflow

Trigger: user says "debug everything, every button, every container, every feature" or "engage everything and everyone" or "comprehensive audit."

This is the maximum-coverage pattern — used when incremental fixes haven't held and the user wants a systematic sweep.

## Execution Order (parallel where possible)

### Phase 1: Integrity Check (30s, terminal only)
Run the gazzetta-integrity-check quick check to catch obvious issues before spending focus-group cycles:
- HTTP codes on all major endpoints
- Source parity (data/ vs public/ vs live GCS)
- Script tag balance on all HTML pages
- Pipeline cron health

### Phase 2: Focus Groups + Browser Audit (parallel, 3 agents max)
Spawn simultaneously:
1. **SRE persona** — SSL, cache headers, HTTP codes, asset accessibility, redirect config
2. **QA persona** — all 12 pages, every button, container population, JS errors, hero stats, story expansion, barometer sections
3. **UX Writer persona** — raw DB keys, unexplained acronyms, bare numbers, broken empty states, vague CTAs

All three run in parallel (max_concurrent_children=3).

### Phase 3: Direct Browser Verification (concurrent with Phase 2 if possible)
While personas run, navigate the 3-4 most critical pages yourself:
- Homepage: hero stats populated? Containers populated?
- Flows page: barometer 4 sections present? Capital Flow Methodology link text correct?
- Story page: story.html?id=X renders content (not raw JS text)?
- Geopolitics/Markets: pages NOT empty?

### Phase 4: Mobile Audit (after Phase 2 completes)
Spawn Mobile-First Designer persona at 390px viewport.

### Phase 5: Synthesize
Cross-reference findings across all auditors. Prioritize:
- P0: page broken, 404, content not rendering
- P1: stale cache, missing security headers, hero stats showing dashes
- P2: raw DB keys, unexplained acronyms, missing tooltips
- P3: cosmetic issues

### Phase 6: Fix + Verify
Execute fixes in priority order. After each fix group, run pipeline + verify live site.

## Common Root Causes Discovered

1. **Docker stale-files trap** — `COPY public/ /app/public/` bundles old HTML that `build_site.py` doesn't overwrite, then gets deployed to GCS
2. **Script tag imbalance** — extra `</script>` or missing `<script>` renders raw JS as visible DOM text
3. **Pipeline silently failing** — test gate catches freshness issues but the underlying cause is stale bundled files, not data quality
4. **Focus group coverage gap** — some pages (geopolitics, markets) have no dedicated rendering and show as empty; personas catch this

## Pitfalls

- Don't run all 4 personas at once — hit the 3-task limit and get errors
- Don't skip the integrity check before spawning focus groups — obvious issues waste persona iterations
- Don't trust that "pipeline is passing" means "site is correct" — verify live GCS data independently
- Raw DB keys (snake_case) as labels are caught by UX Writer, not QA — QA checks function, not copy quality
