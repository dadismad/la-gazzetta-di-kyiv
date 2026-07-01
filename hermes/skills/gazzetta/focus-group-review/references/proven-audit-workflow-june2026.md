# Proven Multi-Round Audit Workflow (June 2026)

## The 4-Phase Pattern

This pattern proved effective across two full cycles on June 12, 2026:

### Phase 1: Focus Groups (3-5 personas, 2 batches)
- **Batch 1**: Senior Web Designer + Busy Professional + Skeptical Journalist (design + content + trust)
- **Batch 2**: 55yo Retail Investor + Design-Sensitive Reader (accessibility + emotional response)
- Each persona visits ALL pages with browser tools, waits 3s for JS, checks bodyLen > 2000
- Output: per-persona scores + consensus catalog + contradiction map

### Phase 2: Expert Team (3 architects in parallel)
- **Product Architect** (Bloomberg Terminal level) — architecture sustainability, scalability
- **UX Director** (Bloomberg/FT) — IA audit, comprehension cliff, fix priority matrix
- **Systems Architect** (Refinitiv) — technical bottlenecks, SPOFs, error resilience
- Each receives Phase 1 report as context
- Output: SWOT + TOP 5 bottlenecks + 3-month roadmap

### Phase 3: Self-Prompt Generation
- Synthesize all findings into a detailed execution plan
- Write to `.hermes/plans/gazzetta-{name}.md`
- Include: exact CSS classes, file paths, before/after values, verification gates
- Prioritize: CRITICAL → HIGH → MEDIUM → LOW

### Phase 4: Execute + Deploy + Verify
- Make code changes (patch/write_file)
- Build: `build_site.py` then `build_hashed_assets.py`
- Deploy: `gsutil -m rsync -d -r site/ gs://www.lagazzettadikyiv.com/`
- Verify: browser_vision + browser_console on live URL with cache-bust `?_v={timestamp}`

## Key Pitfalls Learned

1. **Subagents see CDN-cached pages**: After deploy, wait 60s or use fresh cache-bust parameter. Always verify loaded CSS hash matches expected hash via `document.querySelector('link[href*="styles."]')?.href`.

2. **CSS specificity wars**: Adding `display: none` as a new rule doesn't work if old rule blocks with `display: flex` exist later in the file. DELETE the old blocks, don't just add overrides.

3. **Privacy page was 404**: Nav links to `/privacy.html` but the file didn't exist. The 55yo Retail Investor caught this. Always verify ALL nav-linked pages return 200.

4. **Data freshness timing**: Subagents checking `browser_console` during the 1-2s fetch retry window reported "empty pages." Instruct personas to wait 3s minimum and check `bodyLen > 2000` before evaluating.

5. **CSS hash build step**: `build_site.py` doesn't hash CSS. Must run `build_hashed_assets.py` separately after CSS changes, otherwise browsers load cached old CSS.

## Persona Combinations Proven Effective

### Full Site Audit (8 personas, 2 cycles)
**Cycle 1**: Senior Web Designer + Busy Professional + Skeptical Journalist + 55yo Retail + Design-Sensitive Reader
**Cycle 2**: First-Time Visitor + Degen Crypto Trader + Chief Editor

Combined findings: 22 bugs across 11 pages, privacy page 404, placeholder price chaos ($16,876 vs $61,876 real BTC), They Say/Reality identical on 100% of stories, ~40% taxonomy error rate.

### Design-Only Audit (3 personas)
**Design-Sensitive Reader + Busy Professional + 55yo Retail Investor**
Focus: visual hierarchy, scannability, comprehensibility, trust.
Found: hero underscaled (20px → 26px), teaser gaps too tight (4px → 6px), hero indicators competed with headline weight.

## Quick Audit (single persona, no subagent spawn)
For cron-friendly checks: one agent reads `stories.json`, navigates live site, uses `browser_console` to compare rendered vs source data, produces structured report.
