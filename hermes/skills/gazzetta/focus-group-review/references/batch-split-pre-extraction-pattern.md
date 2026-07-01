# Batch Split + Pre-Extraction Pattern (Proven June 2026)

## When to Use

Any focus group with 5+ personas where some are analytical (Logic Professor, Systems Architect, McKinsey Partner) and some are visual (UX Director, Senior Web Designer, Design-Sensitive Reader).

## The Pattern

### Batch 1: Visual Personas (browser tools) — 3 personas

Give `toolsets: ["browser"]`. These personas need to SEE the page. Include in every prompt:
- Exact URL: `https://www.lagazzettadikyiv.com/?_v=focus1`
- "WAIT 3 seconds after each page load for JavaScript data fetch to complete"
- "bodyLen > 2000 = page loaded"
- "Don't navigate away from lagazzettadikyiv.com"
- "Check ALL nav-linked pages"

**Proven Batch 1 combo (2/3 succeeded, Logic Professor failed — as predicted):**
1. Portfolio Manager (data integrity + tradeability)
2. Senior UX Director (visual design + accessibility)
3. ~~Logic Professor~~ → Move to Batch 2

### Batch 2: Analytical Personas (NO browser tools) — 2-3 personas

Pre-extract site data, feed as rich structured context. Give `toolsets: []` or `toolsets: ["terminal"]`.

**Proven Batch 2 combo (3/3 succeeded):**
1. Logic Professor (taxonomy, container integrity, fallacy audit)
2. McKinsey Partner / White-Collar Professional (trust, would-pay, brand positioning)
3. Systems Architect (infrastructure, scaling, resilience)

## Pre-Extraction Commands

Run these BEFORE spawning Batch 2. Include the output in the `context` field of each subagent task.

### 1. Site Health Check
```js
// browser_console
JSON.stringify({
  storyCount: document.querySelectorAll('article').length,
  pageTitle: document.title,
  bodyLength: document.body.innerHTML.length,
  mastheadText: document.querySelector('h1')?.textContent?.trim(),
  navItems: Array.from(document.querySelectorAll('nav button, nav a')).map(e => e.textContent?.trim()).filter(Boolean).slice(0,10)
})
```

### 2. Story Card Sample (first 10 cards)
```js
// browser_console
JSON.stringify(Array.from(document.querySelectorAll('article')).slice(0,10).map(a => ({
  headline: a.querySelector('h3')?.textContent?.trim(),
  gap: (a.textContent.match(/GAP:\s*(\d+)/) || [])[1],
  source: (a.textContent.match(/FEED_SOURCE:\s*([^\n]+)/) || [])[1]?.trim(),
  tier: (a.textContent.match(/(BREAKING|ACTIVE|SETTLING)/) || [])[1]
})))
```

### 3. Data Layer Check (from local repo)
```bash
python3 -c "
import json
with open('data/stories.json') as f:
    d = json.load(f)
print(f'Total stories: {d.get(\"total_stories\", len(d.get(\"all_stories\",[])))}')
print(f'Containers: {list(d.get(\"containers\",{}).keys())}')
# Narrative distribution
from collections import Counter
narr = Counter(s.get('narrative_id','unknown') for s in d.get('all_stories',[]))
for n,c in narr.most_common(10): print(f'  {n}: {c}')
"
```

### 4. Infrastructure Context (for Systems Architect)
Include: VM specs (e2-micro, 1GB RAM, 30GB disk), pipeline stages, build frequency (10min), deploy target (GCS static), data sources (yfinance, AlphaVantage, SCMP RSS, OilPrice, Sportico), test results (105 PASS / 2 FAIL non-blocking).

## Token Cost Evidence

| Approach | Input Tokens | Completion | Personas |
|---|---|---|---|
| Browser tools (Batch 1) | 378K-1.52M | 2 of 3 | PM, UX Dir, Logic Prof |
| Context-fed (Batch 2) | 15K-73K | 3 of 3 | Logic Prof, McKinsey, SysArch |

**Savings: ~60-95% token reduction. 100% completion rate.**

## Pitfall: Don't Trust Batch 1 Logic Professor

The Logic Professor persona with browser tools will ALWAYS hit max_iterations. It tries to inspect every DOM element, every browser_console statement, every filter button behavior. It never converges. Always move Logic Professor to Batch 2 with pre-extracted context.
