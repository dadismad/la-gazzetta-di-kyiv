# Single Source of Truth — JS Data Pipeline (v25.7)

## Problem

`boot()` and `populateTeasers()` both fetched `stories.json` independently. Two separate HTTP requests to the same 16MB file. Two disconnected in-memory copies. Race condition: whichever fetch completed first determined what content the user saw. Homepage teaser could show `"SpaceX IPO"` while the stories page first card showed `"Iran Strikes Kuwait"` — from the same underlying data, just different slices.

**Critical symptom:** `populateTeasers()` did `const storiesData = await getJSON(getDataPath(), null)` — completely independent of `boot()`'s `STORIES_DATA`. If the user was on the homepage and navigated to stories, the stories page did a fresh fetch. No data sharing occurred.

## The Fix Pattern

**One fetch, one array, consumed everywhere:**

```javascript
// In boot() — populate the shared store:
STORIES_DATA = all;                     // module-scoped (let, not window)
window.STORIES_DATA = all;              // ALSO attach to window for cross-function access

// In populateTeasers() — poll for shared data, fall back to direct fetch only as last resort:
let storiesData = null;
for (let attempt = 0; attempt < 20; attempt++) {
  if (window.STORIES_DATA && window.STORIES_DATA.length > 0) {
    storiesData = { lead: window.STORIES_DATA[0], stories: window.STORIES_DATA.slice(1) };
    break;
  }
  await new Promise(r => setTimeout(r, 150));
}
if (!storiesData) {
  storiesData = await getJSON(getDataPath(), null);  // fallback only
}
```

## The `let` vs `window` Pitfall

**Critical:** Top-level `let STORIES_DATA` in a regular `<script>` tag does NOT create a property on `window`. Only `var` does. `let` creates a block-scoped variable in the script's module-like scope. Cross-function code that polls `window.STORIES_DATA` will find `undefined` — every time.

```javascript
// ❌ Does NOT make window.STORIES_DATA accessible
let STORIES_DATA = [];

// ✅ Does
var STORIES_DATA = [];
// OR explicitly:
window.STORIES_DATA = all;
```

**Always pair `STORIES_DATA = all` with `window.STORIES_DATA = all`.** If any other function polls `window.STORIES_DATA`, it will fail silently without the window assignment.

## Verification

After any change to the data pipeline:
1. `browser_navigate` to homepage → wait 3s
2. `browser_console`: `window.STORIES_DATA?.[0]?.headline` — must return actual headline
3. `browser_console`: `document.getElementById('storiesTeaserContent')?.querySelector('.teaser-item')?.textContent` — must include the SAME headline
4. `browser_navigate` to stories page → `browser_console`: first card headline must match
5. If they differ, you have two data silos.

## Loading Skeleton Pattern

When a page takes 2+ seconds to populate (190 cards at 440px each = 74,000px of DOM), the user sees a blank white void. Fix:

```html
<!-- In HTML, before the content container: -->
<div id="storiesLoading" style="padding:40px 20px;text-align:center;">
  <div style="display:inline-block;width:40px;height:40px;border:3px solid
    var(--divider);border-top-color:var(--gold);border-radius:50%;
    animation:spin 0.8s linear infinite;"></div>
  <p>Loading intelligence feed…</p>
</div>
```

```css
@keyframes spin { to { transform: rotate(360deg); } }
#storiesLoading.hidden { display: none; }
```

```javascript
// In boot(), after first cards populate:
const skel = document.getElementById('storiesLoading');
if (skel) skel.classList.add('hidden');
```

The skeleton shows a gold spinner immediately on page load. It auto-hides when the first cards render. No more blank white void.
