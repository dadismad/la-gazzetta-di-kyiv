# RU Page Script & Data Path Bug — Full Reproduction

**Date:** June 2026  
**Severity:** Critical — all JS-rendered content dead on Russian version  
**Detection:** Visual sweep showed hero indicators as `—`, tickers empty, flow sectors empty, sentiment `—`

## Root Cause Chain

The RU index.html lives at `site/ru/index.html` and is served from `/ru/`. THREE independent path bugs combined:

### Layer 1: Script src paths
```html
<!-- BROKEN: resolves to /ru/app.bf173854.js → 404 -->
<script src="./app.bf173854.js"></script>
<!-- FIXED: resolves to /app.bf173854.js → 200 -->
<script src="../app.bf173854.js"></script>
```
Same for `./i18n.041121bb.js` and `./styles.ce1d3b65.css`.

### Layer 2: Data fetch paths (in app.js)
Even with scripts loading, `app.js` fetches data with page-relative URLs:
```js
// In app.js — resolves relative to PAGE URL, not script URL
fetch('./data/stories.json')  // from /ru/ → /ru/data/stories.json → 404
fetch('./data/flows.json')    // from /ru/ → /ru/data/flows.json → 404
```

### Layer 3: Inline script fetches (in index.html)
The RU index.html has inline `<script>` blocks that fetch data:
```js
fetch('./data/market_prices.json?...')  // → /ru/data/market_prices.json → 404
fetch('./data/track_record.json?...')   // → /ru/data/track_record.json → 404
```

## Complete Fix

1. **Script paths:** `./` → `../`
2. **Stylesheet path:** `./` → `../`
3. **Data preload paths:** `./data/` → `../data/`
4. **Inline fetch paths:** `./data/` → `../data/`
5. **`<base href="/">`** after `<meta charset>` — makes ALL page-relative URLs resolve from root, fixing app.js data fetches
6. **`lang="en"` → `lang="ru"`** on `<html>` tag
7. **Nav links:** `./stories.html` → `../stories.html` (product pages now redirect to index)

## Verification
```bash
# Script 200 check
curl -skI https://www.lagazzettadikyiv.com/ru/app.bf173854.js | head -1
# MUST: HTTP/2 200

# Data 200 check
curl -skI https://www.lagazzettadikyiv.com/data/stories.json | head -1
# MUST: HTTP/2 200

# Base tag check
grep -c '<base href="/">' site/ru/index.html
# MUST: 1

# Hero alive check (browser console)
JSON.stringify({
  heroDiv: document.getElementById('heroDivergence')?.querySelector('.hero-ind-value')?.textContent,
  sentiment: document.getElementById('sideSentValue')?.textContent,
  tickers: document.querySelectorAll('.ticker-item').length
})
# MUST: heroDiv ≠ "—", sentiment ≠ "—", tickers > 0
```
