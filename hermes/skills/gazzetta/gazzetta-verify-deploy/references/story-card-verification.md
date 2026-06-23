# Story Card Verification (v28.0+)
# Added June 2026 — Contradiction-first 4-line card rendering

After every deploy, verify the new story card structure is rendering correctly on /stories.html.

## Quick Verification (browser_console)

```js
JSON.stringify({
  cards: document.querySelectorAll('.story-card').length,
  firstCard: {
    headline: document.querySelector('.story-card .story-headline a')?.textContent?.trim()?.substring(0, 60) || 'none',
    hasContradiction: !!document.querySelector('.story-card .story-contradiction'),
    gapScore: document.querySelector('.story-card .con-score')?.textContent || 'none',
    flowAmt: document.querySelector('.story-card .flow-amount')?.textContent || 'none',
    flowDir: document.querySelector('.story-card .flow-direction')?.textContent || 'none',
    hasActions: !!document.querySelector('.story-card .story-actions'),
    hasTier: !!document.querySelector('.story-card .tier-badge')
  },
  navDropdowns: document.querySelectorAll('.nav-dropdown').length,
  mastheadBorder: getComputedStyle(document.querySelector('.masthead')).borderBottom
})
```

## PASS Criteria

- `cards` > 0 (minimum: 1, typical: 200+ after data load)
- `hasContradiction`: true
- `gapScore`: contains "/100" (e.g., "Gap: 45/100")
- `flowAmt`: contains "$" (e.g., "$50M", "$0.1B")
- `flowDir`: "INFLOW" or "OUTFLOW"
- `hasActions`: true
- `hasTier`: true
- `navDropdowns`: 2 (INTEL and ALPHA)
- `mastheadBorder`: "2px solid rgb(212, 175, 55)" (gold)

## Failure Patterns

### CSS 404 — Story cards exist but unstyled
Cause: Hashed CSS file never uploaded to GCS.
Fix: Revert to `./styles.css` + redeploy ALL HTML.

### cards = 0
Cause: app.js not loaded or failed to parse.
Check: `node -c public/app.js`

### hasContradiction = false
Cause: Old app.js deployed (pre-v28.0).
Check: Verify `livingCardHTML()` contains `story-contradiction` class.

### navDropdowns = 0
Cause: Old header template deployed (pre-v26.7).
Check: Verify `templates/header.html` has `.nav-dropdown` divs.
