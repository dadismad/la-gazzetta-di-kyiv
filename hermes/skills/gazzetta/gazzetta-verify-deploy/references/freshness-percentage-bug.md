# Freshness Percentage Bug — Reproduction & Fix

## Symptom
All story teasers on homepage show "100%" freshness labels instead of time-ago text (e.g., "2h ago", "yesterday"). 5/5 focus-group professionals read "100%" as a confidence score, destroying trust in the data.

## Root Cause
`app.js` `populateTeasers()` at line ~2311 computed a `time_decay.current_freshness` score (0-1 float), multiplied by 100, and displayed as `${pct}%`. The value represented a recency decay multiplier, NOT a confidence score — but the display format (`N%`) is universally interpreted as confidence by human readers.

## Fix (applied June 2026)
In `populateTeasers()`, replace:
```js
const pct = Math.round(fresh * 100);
freshHtml = ` <span class="freshness-ago ${cls}">${pct}%</span>`;
```
With:
```js
const timeLabel = s.generated_at ? formatTimeAgo(s.generated_at) : (fresh > 0.8 ? 'recent' : fresh > 0.4 ? 'today' : 'stale');
freshHtml = ` <span class="freshness-ago ${cls}">${timeLabel}</span>`;
```

The `fresh` score is still used to determine CSS class (`freshness-recent` / `freshness-today` / `freshness-stale`) for color-coding, but the displayed text uses `formatTimeAgo()` which produces human-readable relative timestamps.

## Verification
```js
JSON.stringify({
  labels: Array.from(document.querySelectorAll('.freshness-ago')).map(s => s.textContent).slice(0,5),
  hasPercents: Array.from(document.querySelectorAll('.freshness-ago')).some(s => s.textContent.includes('%'))
})
```
PASS: `hasPercents` = false. Labels should show time-ago strings like "3h ago", "yesterday", "2d ago".

## Pitfalls
- **Browser cache**: The site uses hashed filenames (`app.280e9b5e.js`). Deploying the fix to `app.js` alone leaves the hashed file stale. Must deploy to both.
- **CDN delay**: `Cache-Control: max-age=0, must-revalidate` is set, but browser sessions may hold in-memory caches.
- **Scope**: `formatTimeAgo()` is defined globally in `app.js` — accessible from `populateTeasers()` scope.
- **Fallback**: If `s.generated_at` is missing, falls back to text labels ("recent"/"today"/"stale") rather than reverting to percentage.
