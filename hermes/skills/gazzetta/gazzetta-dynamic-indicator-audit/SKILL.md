---
name: gazzetta-dynamic-indicator-audit
description: "Scan site for hardcoded digits disguised as dynamic. Every visible number must be JS-updated from a data source — no static digits in HTML representing story counts, asset counts, flow counts, confidence %, or any quantity that changes."
version: 1.0.0
category: gazzetta
---

# Dynamic Indicator Audit — Continuous Loop

## Rule
Every visible number on the site that changes over time MUST be rendered by JavaScript from a data source. Zero hardcoded digits in HTML representing dynamic quantities.

## Violation Patterns

| Pattern | Example | Fix |
|---------|---------|-----|
| Hardcoded count in container desc | `"14 assets with..."` | Wrap in `<span id="...">` + update via JS |
| Hardcoded hero stat | `<span>10</span> Stories` | Already fixed: `heroStat` IDs + JS update |
| Hardcoded date/timestamp | `"June 5, 2026"` | Dynamic via `updateMasthead()` |
| Hardcoded flow count | `"12 flows tracked"` | Already dynamic via fetchFlows |
| Hardcoded confidence % | `"79% confidence"` in static text | Must come from flows.json |

## Audit Loop (run every 15m or on deploy)

```bash
# 1. Scan HTML for hardcoded digits outside of JS-managed spans
curl -sk $URL | python3 -c "
import sys, re
html = sys.stdin.read()
# Strip JS-updated elements
cleaned = re.sub(r'<span[^>]*id=\"[^\"]*\"[^>]*>[^<]*</span>', '', html)
cleaned = re.sub(r'<script[^>]*>.*?</script>', '', cleaned, flags=re.DOTALL)
# Find remaining digits that look like dynamic quantities
violations = re.findall(r'>(\d{1,3}(?:\.\d+)?)\s*(?:stories|assets|flows|bets|positions|inflows|outflows)', cleaned, re.I)
print('VIOLATIONS:', violations if violations else 'NONE')
"

# 2. Cross-check hero stats: DOM values vs data source
# heroStoryCount should match document.querySelectorAll('.card[data-story-id]').length
# heroFlowTotal should match flows.json total
# heroAssetCount should match ANCHOR_ASSETS.length

# 3. Check timestamps are present and non-empty
# document.querySelectorAll('time[datetime]') — datetime attr must be non-empty
```

## Integration Points

1. **gazzetta-ceo-overseer cron** — Add this audit as a check step
2. **gazzetta-interpret-review-execute Phase 5** — Run audit before claiming "done"
3. **Post-deploy verification** — Always scan for new hardcoded digits after HTML changes

## Current State (verified June 2026)
- Hero stats: all dynamic via JS ✓
- Container subtitles: all dynamic ✓
- Anchor count in description: dynamic via `#anchorCount` ✓
- DEVELOPING badges: computed from contradiction score ✓
- Flow count/subtitle: from flows.json ✓
- Timestamps: need verification (were empty in browser snapshot)

## Recurrence Patterns (June 2026)

Hardcoded digits are **frequently reintroduced** — not a one-time fix. Common recurrence patterns:

| Pattern | Example | Detected By | Frequency |
|---------|---------|-------------|-----------|
| Template literal in HTML | `<span id="anchorCount">14</span>` → deployed from template | CEO Overseer cycle | Every HTML deploy |
| Bulk site rebuild | `build_site.py` regenerates `index.html` from template with hardcoded counts | CEO Overseer cycle | Every pipeline run |
| Manual copy-paste | Developer copies `site/index.html` → edits → reintroduces old hardcoded value | CEO Overseer cycle | Ad-hoc edits |
| New container added | New feature's count hardcoded in static HTML (wasn't there before) | CEO Overseer cycle | New feature deploys |
| Root vs site divergence | Root `index.html` fixed but `site/index.html` inherited old template | CEO Overseer cycle | Root/site sync |

### Mitigation

1. **Auto-scan on every CEO Overseer cycle** (already integrated since June 2026)
2. **Pre-deployment checklist:** Before any HTML deploy, grep for `>\d+\s*(?:stories|assets|flows|bets)` outside JS-managed spans
3. **Dual-file fix:** Root and `site/` copies of `index.html` can diverge. Always check BOTH files when fixing static digits. In June 2026 root `index.html` was fixed but `site/index.html` still had the hardcode — the GCS deploy syncs from `site/`, not root.
4. **JS rendering verification post-deploy:** After deploy, open browser console and query `heroStoryCount.textContent`, `anchorCount.textContent` — these must be `—` (placeholder) in static HTML, populated by JS.
