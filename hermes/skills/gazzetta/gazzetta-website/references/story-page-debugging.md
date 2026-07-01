# Story Detail Page Debugging (v27.1 — June 2026)

## Symptom: "Loading intelligence report…" stuck forever

Story detail page (`/story.html?id=XXX`) never renders content. Three root causes found:

### Cause 1: story-app.js script tag MISSING from story.html

The `story.html` template loaded `i18n.js` and `app.js` but NOT `story-app.js`. The story rendering logic (fetch data → find story → buildHTML → inject) lives in `story-app.js` — without it, the page shows "Loading intelligence report…" forever.

**Fix:** Add `<script src="./story-app.HASH.js"></script>` to `story.html` after the `app.js` script tag. The hashed version changes on each build — use `build_hashed_assets.py` to regenerate.

### Cause 2: Raw inline JS missing `<script>` opening tag

The flow node interlink block at the bottom of `story.html` had:
```html
    </div>
    (function(){
      var sid = new URLSearchParams(location.search).get('id');
      ...
    })();
    </script>
```

The opening `<script>` tag was MISSING. The raw JS rendered as visible text on the page. The closing `</script>` from a different block matched the trailing tag, making this hard to spot in diffs.

**Fix:** Add `    <script>` before the IIFE.

### Cause 3: `renderMultiPersona(t)` — ReferenceError: t is not defined

In `story-app.js`, the `buildHTML()` function defines `t` as a local:
```js
const t = window.i18n ? (k, fb) => i18n.t(k, fb) : (k, fb) => fb;
```

The `renderMultiPersona()` function (called from `buildHTML()`'s template literal) references `t`:
```js
function renderMultiPersona(story) {
    ...
    h += '<h2>' + t('multi_persona_label', 'MULTI-PERSONA ANALYSIS') + '</h2>';
```

But `renderMultiPersona` is a SIBLING function to `buildHTML`, not nested inside it. `t` is undefined in its scope → `ReferenceError: t is not defined` → init() throws → "Failed to load intelligence report."

**Fix:** Pass `t` as a parameter:
```js
// In buildHTML template literal:
${renderMultiPersona(story, t)}

// In renderMultiPersona signature:
function renderMultiPersona(story, t) {
```

**Pitfall:** The try/catch wrapper in init() caught this error but only logged it to console. The user-visible message was generic "Failed to load intelligence report." When debugging story page failures, always check browser console for `[story-app] init failed:` messages.

## Verification Checklist

After fixing:
1. Navigate to `story.html?id=<valid_id>&_v=N` with fresh cache-bust
2. Check `document.querySelector('.intel-report')` — must be non-null
3. Check `document.body.innerHTML.length > 15000` — populated page
4. Check `document.querySelector('script[src*="story-app"]').src` — correct hash
5. Verify no raw JS visible as text (search body for `function(){`)
