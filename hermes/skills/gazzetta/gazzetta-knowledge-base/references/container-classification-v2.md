# Container Classification v2.0 — Methodology & Pitfalls

June 2026. Reclassified all 377 stories from flat auto-classification into 6 MECE containers using headline keyword patterns.

## The 6 Containers (MECE)

| Container | Domain | Stories (post-fix) |
|---|---|---|
| monetary_order | Dollar, Bitcoin, CBDCs, sanctions, reserve competition, markets, banking, M&A | 82 |
| energy_resources | Oil, gas, renewables, nuclear, rare earths, critical minerals, pipelines | 40 |
| technology_ai | Semiconductors, AI race, quantum, big tech, cybersecurity, cloud | 102 |
| information_narrative | Propaganda, disinformation, censorship, social media geopolitics, media | 5 |
| biosecurity_health | Pandemics, biotech, longevity, bioweapons, vaccine geopolitics, pharma | 8 |
| flashpoints | Ukraine, Taiwan, Middle East, South China Sea, resource wars, military | 140 |

## Classification Methodology

### Multi-Pass Keyword Refinement

1. **Start broad** — Write keyword patterns for each container. Check with `re.IGNORECASE` flag.
2. **Run classification** — Apply to all 377 stories via SQLite UPDATE.
3. **Spot-check samples** — Pull 5 stories from each container. Flag misclassified ones.
4. **Refine patterns** — Add missing keywords, fix false-positive patterns.
5. **Repeat** — Usually 3-4 passes to dial in distribution.

### Critical Pitfall: Case Sensitivity

**CRITICAL:** All headlines are lowered to lowercase before matching. ALL regex patterns MUST use `re.IGNORECASE` flag, or ALL patterns must be written in lowercase only. Mixed case in patterns + lowered input = silent misses.

Correct:
```python
h = headline.lower()
if re.search(r'\bwti\b', h, re.IGNORECASE):  # matches both "WTI" and "wti"
    return 'energy_resources'
```

Wrong:
```python
h = headline.lower()
if re.search(r'\bWTI\b', h):  # h is lowercase, WTI is uppercase → NO MATCH
    return 'energy_resources'
```

### Pattern Order Matters

Narrowest domains check FIRST. Order:
1. biosecurity_health (narrowest — few stories, specific keywords)
2. information_narrative (narrow — propaganda/media keywords)
3. energy_resources (medium — oil/gas/nuclear)
4. technology_ai (medium — AI/semiconductors)
5. monetary_order (broad — markets/finance)
6. flashpoints (default catch-all for anything geopolitical)

### Sector Column is Unreliable

The `sector` column in `stories` table is NOT trustworthy for classification. Stories about Middle East conflicts had `sector='tech'`. Stories about markets had `sector='defense'`. DO NOT use sector for classification decisions — use headline keywords only.

## HTML Entity Cleanup

28 of 377 stories had HTML entities in headlines (`&#039;`, `&amp;`, etc.). Fix at source — in `db_to_json.py`:

```python
import html
# After json.loads(fj_str):
if story.get("headline"):
    story["headline"] = html.unescape(story["headline"])
```

This is cleaner than fixing in the frontend JS, which would need to decode entities in every render path.

## Archive URL Param Filtering

The "View all X stories in CONTAINER →" links on the front page go to `archive.html?container=monetary_order`. The archive inline JS must read this param:

```javascript
const urlParams = new URLSearchParams(window.location.search);
const containerParam = urlParams.get('container');
if (containerParam) {
    filter = containerParam;
    const btn = document.querySelector('#archive-controls .container-pill[data-filter="' + containerParam + '"]');
    if (btn) btn.classList.add('active');
}
```

This sets the initial filter AND activates the corresponding pill button so the UI reflects the state.

## Systematic Audit Workflow

When the user reports "bugs" or "things not working," run this checklist:

1. **Expand all containers** — check story counts match expected distribution
2. **Trace every link** — nav pills, "View all" links, archive links, social links
3. **Check data format** — curl stories.json, verify container structure, spot-check headlines
4. **Check all scripts loading** — `document.querySelectorAll('script')` — verify app.js, i18n.js presence
5. **Check browser console** — JS errors, failed fetches
6. **Reclassify if misclassification found** — use keyword pattern refinement loop
7. **Deploy in stages** — DB first, then public/, then verify live

Never report success based on local file writes. Always verify via browser_console with `getComputedStyle()` or DOM queries on the LIVE URL.
