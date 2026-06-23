# Sub-Page Count Badge Verification

Extends `gazzetta-verify-deploy` §4.5 (JS Interactivity Check). After every deploy where `app.js` changed, verify count badges on ALL sub-pages — not just homepage hero indicators.

## Why

`renderPDR()` and similar shared functions can crash silently on sub-pages due to missing DOM elements (e.g., `.pdr-trend` only exists on homepage). The crash blocks subsequent code — the page renders but count badges show `—` placeholders.

## After every app.js change, verify:

```js
// On EACH sub-page, check:
JSON.stringify({
  page: window.location.pathname,
  // trades.html: anchorCount must be a number
  anchorCount: document.getElementById('anchorCount')?.textContent?.trim(),
  // stories.html: storyCount must be a number
  storyCount: document.getElementById('storyCount')?.textContent?.trim(),
  // event_horizon.html: horizonCount must show filtered count
  horizonCount: document.getElementById('horizonCount')?.textContent?.trim(),
  // flows.html: regime values must not be —
  regimeMF: document.getElementById('regimeMFValue')?.textContent?.trim(),
  // signal.html: signalFreshness must not be —
  signalFreshness: document.getElementById('signalFreshness')?.textContent?.trim(),
  // All pages: zero undefined/null strings in DOM
  undefinedCount: (document.body.innerHTML.match(/undefined/g)||[]).length,
  nullCount: (document.body.innerHTML.match(/>null</g)||[]).length
})
```

## PASS criteria per page

| Page | Check | Must NOT be |
|------|-------|-------------|
| trades.html | `anchorCount` | `—` |
| stories.html | `storyCount` | `—` |
| event_horizon.html | `horizonCount` | `—` or empty |
| flows.html | `regimeMFValue` | `—` |
| signal.html | `signalFreshness` | `—` |
| ALL pages | `undefinedCount` | >0 |
| ALL pages | `nullCount` | >0 |

## Detection method

If a count badge shows `—` despite content rendering:
1. `browser_console` → manually call the render function → observe the crash
2. Check if a shared function queries a homepage-only DOM element without null guard
3. Fix with `const el = querySelector(...); if (el) el.textContent = ...`

Real case: `renderPDR()` → `el.querySelector('.pdr-trend')` null on sub-pages → crash before `anchorCount` update → badge shows `—` despite 14 anchor cards rendered.
