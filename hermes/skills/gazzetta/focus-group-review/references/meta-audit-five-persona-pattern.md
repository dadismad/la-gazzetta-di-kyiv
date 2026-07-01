# Meta-Audit Five-Persona Pattern (June 2026)

## When to use
When the user asks for a comprehensive audit spanning tech, content, design, and marketing simultaneously — or says "review everything," "audit from all angles," "review accomplishments vs requests."

## Proven Persona Combination

| Batch | Persona | Tools | Lens | Output |
|-------|---------|-------|------|--------|
| 1 (browser) | Senior Web Designer | browser | Design/CSS/WCAG/UX | Top 10 issues ranked, exact CSS fixes, praise-worthy elements |
| 1 (browser) | Chief Editor | browser | Headlines/They-Say/Straw-man/Jargon | A-F headline grades, editorial report card, top 10 writing problems |
| 1 (browser) | Conversion PM | browser | CTAs/Trust/SEO/Competitive | Conversion funnel, trust score, competitive matrix, 5 growth recommendations |
| 2 (context-fed) | Portfolio Manager/Quant | terminal, file | Data integrity/Capital flows/Pipeline | 14 discrepancies, data trustworthiness score, root cause catalog |
| 2 (context-fed) | Logic Professor | terminal, file | Architecture/Docs-vs-reality/Coherence | Divergence catalog, architecture integrity score, ground truth summary |

## Key Principle: Batch 1 = Browser, Batch 2 = Context-Fed

**Why:** Browser-toolset subagents for analytical evaluation burned 971K-1.28M input tokens and hit max_iterations with no result (June 2026). Context-fed subagents completed in 437K-921K tokens with detailed structured output.

- **Batch 1 personas (browser tools):** MUST see the page visually — Senior Web Designer, Chief Editor, Conversion PM. Give `toolsets: ["browser"]` with exact URL + cache-bust + 3-second wait instruction.
- **Batch 2 personas (no browser):** Pre-extract all relevant site data using `browser_console` JS evaluation or `terminal + curl + Python`. Feed as rich `context` to subagents. Give `toolsets: ["terminal", "file"]` or `[]`.

## Pre-Extraction Commands for Context-Fed Personas

```javascript
// In browser_console, extract stories.json structure:
JSON.stringify({
  bodyLen: document.body.innerText.length,
  storyCount: document.querySelectorAll('article').length,
  tabCount: document.querySelectorAll('nav button').length,
  headings: Array.from(document.querySelectorAll('h2')).map(h => h.textContent),
  sidebarCaps: Array.from(document.querySelectorAll('.complementary a')).map(a => a.textContent.trim()),
})

// Extract all visible data from Stream tab
Array.from(document.querySelectorAll('article')).map(a => ({
  headline: a.querySelector('h3')?.textContent,
  gap: a.querySelector('[class*=gap], [class*=GAP]')?.textContent,
  source: a.querySelector('[class*=source], [class*=feed]')?.textContent
}))
```

```bash
# Terminal: extract stories.json stats
ssh gazzetta-prod "python3 -c \"
import json; from collections import Counter
with open('/opt/gazzetta-di-kyiv/public/data/stories.json') as f:
    d = json.load(f)
stories = d.get('all_stories', [])
gaps = Counter(int(s.get('contradiction_gap',0)) for s in stories)
print(f'Total stories: {len(stories)}')
print('GAP distribution (top 10):')
for gap, cnt in gaps.most_common(10):
    print(f'  GAP={gap}: {cnt}')
\""
```

## What This Pattern Caught (June 2026)

- Design: 10 WCAG/ARIA/mobile failures, 6 praise-worthy elements, 5.5/10 combined
- Content: 35% A-grade headlines, 4x EasyJet template duplication, 189/191 identical They-Say/Reality, editorial voice 8/10
- Marketing: Zero conversion elements, 3/10 trust score, no OG tags/favicon, 5 concrete growth recommendations
- Data: 14 discrepancies, data trustworthiness 2/10, all capital manufactured, calculate_capital.py never ran
- Architecture: 8 divergences between documentation and reality, architecture integrity 3/10, three conflicting timer frequencies

## Pitfalls

- **Don't give browser tools to Logic Professor or Portfolio Manager personas.** They try to inspect every DOM element via browser_console and never converge. 2 of 3 failed this way (June 2026).
- **Pre-extract VM data before spawning Batch 2.** The context-fed personas need stories.json structure, script listings, VM state, and pipeline output. Without this, they make incorrect assumptions about what files exist.
- **Cache-bust the URL.** Add `?_v={random}` to prevent CDN caching from giving subagents stale pages. Verify origin freshness with `gsutil ls -la` before spawning.
- **The 3-second wait is real.** Instruct Batch 1 personas to wait 3 seconds after each navigation. The JS data fetch has a 1-2 second retry window — evaluating during that window produces "empty data shell" false positives.
