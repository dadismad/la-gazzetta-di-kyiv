# Gazzetta Website — Implementation Reference (v23.23)

Key technical patterns and pitfalls from live sessions. Read BEFORE making JS/CSS changes.

---

## §1. story-app.js Scope Fragility (CRITICAL)

### The Bug
The original story-app.js had an **orphaned `async` keyword** on line 160 with no function body, followed by a `function init()` that was NOT async but used `await` internally. This created a parsing edge case where:
- Adding ANY new `const` or `let` declaration at the module level could shift the parser's interpretation of the orphaned `async`, silently breaking the entire story detail page
- The page would show "Loading…" with empty console (no error thrown — just dead)

### The Fix (v23.23 rewrite)
1. **Remove orphaned keywords** — no standalone `async`, `yield`, or other contextual keywords without a following function
2. **Make `init()` properly `async function init()`**
3. **Use `var` for all declarations** in the critical rendering path — NO `const`/`let` to eliminate TDZ risk
4. **No template literals** (backtick strings) in the rendering path — use string concatenation (`+`) instead. Template literals inside IIFEs with `const` declarations can trigger TDZ errors in certain JS engines

### Enforcement
After ANY change to story-app.js, verify:
```bash
# 1. No orphaned context keywords
grep -n '^\s*async\s*$' site/story-app.js  # must return nothing
grep -n '^\s*await\s' site/story-app.js     # must return nothing (await only inside async)

# 2. No template literals in critical path
grep -c '`' site/story-app.js               # should be near zero

# 3. Browser verification (NOT just node --check)
# Navigate to story.html?id=<any_valid_id> and check:
#   - browser_console: document.getElementById('storyContent').innerHTML.length > 100
#   - browser_console: no errors
```

---

## §2. Font-Size Floor: 11px (WCAG AA)

### Rule
NO element may use `font-size` below 11px. The 7.5px–10px range used historically for badges, tags, navigation labels, sidebar stats, and teaser text is **unreadable** for retail investors and older readers.

### Enforcement command
```bash
cd ~/projects/gazzetta-di-kyiv
# Count violations (must return 0)
grep -cE 'font-size:\s*([7-9]|10)(\.\d+)?px' site/styles.css

# Auto-fix (bumps all <11px to 11px)
python3 -c "
import re
with open('site/styles.css') as f: css = f.read()
css = re.sub(r'font-size:\s*((?:[7-9]|10)(?:\.\d+)?)px(\s*!important)?',
             lambda m: f'font-size: 11px{m.group(2) or \"\"}', css)
with open('site/styles.css', 'w') as f: f.write(css)
"
```

### Exceptions
- `border-radius: 50%` — functional circles (avatars, dots), NOT decorative frames
- SVG icon `font-size` — icons use their own sizing; apply to container, not the icon text

---

## §3. Frameless Contract Enforcement

### Rule
- **border-radius: 0** on ALL elements. No rounded corners. Period.
- **box-shadow: none** on ALL elements. No drop shadows on cards, buttons, or containers.

### Exceptions (functional only)
- `border-radius: 50%` — for circular elements (status dots, avatar placeholders). These are functional shapes, not decorative frames.
- Subtle divider lines: `border-bottom: 1px solid var(--divider)` is acceptable

### Enforcement command
```bash
cd ~/projects/gazzetta-di-kyiv

# Count border-radius violations (should be ≤3 — only functional 50% circles)
grep -c 'border-radius' site/styles.css

# Count non-zero, non-50% border-radius
grep -cE 'border-radius:\s*(?!0|50%)' site/styles.css  # must be 0

# Count box-shadow violations (must be 0)
grep -c 'box-shadow' site/styles.css

# Auto-fix
python3 -c "
import re
with open('site/styles.css') as f: css = f.read()
css = re.sub(r'border-radius:\s*\d+px', 'border-radius: 0', css)
css = re.sub(r'border-radius:\s*\d+\.?\d*rem', 'border-radius: 0', css)
css = re.sub(r'box-shadow:\s*[^;};]+;', 'box-shadow: none;', css)
with open('site/styles.css', 'w') as f: f.write(css)
"
```

---

## §4. Sector Page Consolidation Pattern

### Problem
4 sector pages (markets.html, geopolitics.html, wealth.html, pleasure.html) were thin (~2KB each) with dynamic content loaded by sector.js. If sector.js fails, all 4 pages show "Loading…" forever. These pages had zero navigation links — orphaned from the product surface.

### Solution
1. **Convert sector pages to meta-refresh redirects** — each page becomes a ~300B HTML file that redirects to `story.html?sector=<name>`
2. **Add `renderSectorList()` to story-app.js** — filters stories by `sector` field and renders them as story cards inline
3. **Sector navigation** renders in-page with links to all 4 sectors

### Template for redirect pages
```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta http-equiv="refresh" content="0;url=./story.html?sector=MARKETS"/>
  <title>Markets — La Gazzetta di Kyiv</title>
</head>
<body>
  <p>Redirecting to <a href="./story.html?sector=MARKETS">Markets sector</a>…</p>
</body>
</html>
```

### Data dependency
Stories must have a `sector` field (e.g., `"markets"`, `"geopolitics"`, `"wealth"`, `"pleasure"`). If stories lack this field, sector filtering returns 0 results. The field must be populated at the pipeline level (intel_to_stories.py enrichment).

---

## §5. Cron Landscape Governance

### Current state (v23.23)
12 cron jobs: **6 script-only** (no_agent=true) + **6 LLM-agent**

### Script-only crons (deterministic, no tokens)
| Job | Script | Schedule |
|-----|--------|----------|
| gazzetta-product-factory | gazzetta_product_factory.sh | every 60m |
| gazzetta-health-check | gazzetta_health_check.sh | every 30m |
| gazzetta-living-stories-enrich | gazzetta_enrich_stories.py | every 2h |
| x-health-watchdog-gazzetta | x_health_watchdog.sh | every 8h |
| gazzetta-market-data-pipeline | fetch_all_market_data.sh | every 6h |
| gazzetta-phase3-daily-brief | phase3_daily_brief.py | daily 09:00 |

### LLM-agent crons (require reasoning)
| Job | Skill | Schedule | Why LLM |
|-----|-------|----------|---------|
| gazzetta-ceo-overseer | gazzetta-ceo-overseer | every 15m | Comprehensive multi-page oversight |
| gazzetta-hourly-narrative-review | — | 2x/day | Narrative synthesis from raw intel |
| gazzetta-focus-group-quality-gate | — | 2x/day | Editorial quality review |
| link-intelligence-synthesis | link-intelligence | daily 03:00 | Clustering + extraction |
| gazzetta-editorial-style-audit | focus-group-review | daily 10:00 | Design/content review |
| daily-session-review | daily-session-review | daily 22:00 | Session summarization |

### Conversion criteria
A cron is convertible to script-only when:
1. It runs deterministic commands (shell scripts, Python data pipelines)
2. It doesn't need to evaluate or summarize content
3. Its output is a data file or fixed-format message

If it needs to READ content, EVALUATE quality, or SUMMARIZE — it needs an LLM.
