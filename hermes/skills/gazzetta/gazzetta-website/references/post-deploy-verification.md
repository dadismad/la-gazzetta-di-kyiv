# Post-Deployment Verification Checklist
# v1.0 — SOP Rule 7 compliance

Run these checks via browser_console() after EVERY deployment to GCS.
Navigate to `https://www.lagazzettadikyiv.com/?_v=<timestamp>` first.

## Mandatory Checks

### 1. CSS Loading
```js
!!document.querySelector('link[href*="styles.css"]:not([href*="fonts"])')
```
Expected: `true`

### 2. Font Rendering
```js
getComputedStyle(document.body).fontFamily
```
Expected: must include `"Source Serif 4"` (NOT "Times" — indicates CSS not loaded)

### 3. Masthead Gold Border
```js
getComputedStyle(document.querySelector('.masthead')).borderBottom
```
Expected: `"2px solid rgb(212, 175, 55)"` (NOT "0px none" — CSS missing)

### 4. SVG Size Sanity
```js
document.querySelector('.masthead-caduceus svg').getBoundingClientRect()
```
Expected: width ~12px, height ~22px
FAIL if: width >200px (CSS not constraining SVGs — viewport-width explosion)

### 5. JavaScript Errors
Check console output for uncaught exceptions.
Zero errors expected after page load completes (wait 3s for async rendering).

### 6. Story Card Rendering (stories.html)
```js
document.querySelectorAll('.story-card').length
```
Expected: >0 (cards rendered by app.js)
```js
document.querySelector('.story-card .story-contradiction') !== null
```
Expected: true (contradiction line present)

### 7. Navigation Dropdowns
```js
document.querySelectorAll('.nav-dropdown').length
```
Expected: 2 (INTEL and ALPHA dropdowns)

## Verification Pyramid (most reliable first)

1. `browser_console(expression=<JS>)` — live DOM inspection with computed styles (GOLD STANDARD)
2. `browser_vision()` + `getComputedStyle()` cross-check — screenshot + computed values
3. `browser_snapshot()` — accessibility tree (pre-JS, shows `—` placeholders)
4. `curl` — static HTML (UNRELIABLE, shows `—` placeholders before JS populates)
5. `git log` — source control (NOT live state)

## Golden Rule
If you cannot confirm it with getComputedStyle() in browser_console, it is NOT confirmed.
browser_vision hallucinates colors — always cross-check with computed styles.
