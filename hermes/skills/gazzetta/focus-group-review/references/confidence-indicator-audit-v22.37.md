# Confidence Indicator Audit — v22.37 Focus Group (June 9, 2026)

3-persona focus group (Degen Crypto Trader + 55-Year-Old Retail Investor + Senior UX Director) audited the model confidence indicator across all 8 product pages.

## Consensus (3/3 personas)

### What works: "68% BULLISH" format
- Degen Trader: "68% BULLISH tells me there's a 68% chance things go up. That's clear."
- 55yo Retail: "I understand it as '68% chance this goes up.' Pretty intuitive."
- UX Director: "Percentage + direction badge is the right format. Don't change the core pattern."

### What doesn't work: Missing plain-English tier label
- All 3 flagged that "MEDIUM" / "HIGH" / "LOW" labels alone are opaque without context
- "68% BULLISH" plus "MEDIUM" on story page — is 68% medium? What scale?

## Fix Applied (v22.37)

Changed `updateHeroConfidence()` in app.js:

```
BEFORE: el.innerHTML = `<span style="color:...">${pct}% ${badge}</span>`;
AFTER:  el.innerHTML = `<div><span style="color:...">${pct}% ${badge}</span></div>
        <div style="font-size:9px;color:var(--ink-muted);">${tierLabel}</div>`;
```

Tier labels:
- ≥80% → "Strong conviction"
- 60-79% → "Moderate conviction"  
- <60% → "Weak signal"

Also updated tooltip to explain 5-factor model: "Flow confidence: X% (label). Based on: flow magnitude, pace, institutional positioning, contradiction score, source quality."

## Time Freshness Audit — Key Findings

| Page | Time Badge | Status |
|------|-----------|--------|
| Homepage | Masthead timestamp ✓, teaser "8 stories" ✓ | Works |
| Stories | "1H AGO" per story ✓ | Works |
| Flows | "1d ago" ✓ | Works (stale data, but badge renders) |
| Trades | "Reference prices · reviewed" ✓ | Works |
| Signal | "updated 1d ago" ✓ | Works (after fix) |
| Story detail | WAS empty — `<time datetime="" title="">` | Fixed — added `dataGenAt` fallback |

## Story Page Time Fix (story-app.js)

Root cause: Editorial writer stories lack `generated_at`, `timestamp`, `date` fields.

Fix chain:
1. `dataGenAt = data.generated_at || ''` — document-level fallback
2. `date = formatDate(story.timestamp \|\| story.date \|\| story.generated_at \|\| dataGenAt)`
3. `<time datetime="${... \|\| dataGenAt}" title="${date}">${formatTimeAgo(... \|\| dataGenAt)}</time>`

`formatTimeAgo()` function added to story-app.js (previously only in app.js):
```js
function formatTimeAgo(isoString) {
    if (!isoString) return '';
    const diff = Date.now() - new Date(isoString).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return mins + 'm ago';
    const hours = Math.floor(mins / 60);
    if (hours < 24) return hours + 'h ago';
    const days = Math.floor(hours / 24);
    return days + 'd ago';
}
```
