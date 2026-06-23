# Story Page Integrity Checklist (v27.1)

Checklist for verifying the story detail page (`story.html`) after any template or JS change.

## Script Order (must be exact)

```html
<script src="./i18n.HASH.js"></script>
<script src="./app.HASH.js"></script>
<script src="./story-app.HASH.js"></script>  ← THIS MUST BE PRESENT
```

If `story-app.HASH.js` is missing:
- Page shows "Loading intelligence report…" stuck permanently
- `bodyLen` stays at ~11KB (template-only, no injected content)
- No console errors — silent failure

## Missing `<script>` Opening Tag

The inline flow node interlink code at the bottom of story.html MUST be wrapped:
```html
<script>
(function(){
  // flow node interlink logic
})();
</script>
```

Without the opening `<script>` tag, raw JS renders as visible text on the page.

## Verification Steps

```
1. browser_navigate → story.html?id=ANY_VALID_ID&_v=N
2. Wait 3s for async init
3. browser_console → check bodyLen > 15000
4. browser_console → check document.querySelector('.intel-report') is not null
5. browser_console → check no raw JS text visible: !document.body.textContent.includes('function(){')
```

## Known Hard-to-Diagnose Failure

The story-app.js `init()` is async and wrapped in an IIFE. If it fails:
- `Gazzetta.Story.loaded` will be `true` (set outside the async init)
- `copyStoryLink` and `shareTo` will be defined (set synchronously)
- But the DOM stays at "Loading intelligence report…"
- Root cause is usually in `async function init()` — try adding `console.error` catch

## Deploy Workflow After Any JS/CSS Change

```
cd ~/lagazzettadikyiv
python3 scripts/build_hashed_assets.py    # Re-hash all assets, update HTML references
~/lagazzettadikyiv/devvit/google-cloud-sdk/bin/gsutil -m -h "Cache-Control:no-store,max-age=0" rsync -d -r public/ gs://www.lagazzettadikyiv.com/
~/lagazzettadikyiv/devvit/google-cloud-sdk/bin/gsutil -m -h "Cache-Control:no-store,max-age=0" rsync -d -r public/ gs://lagazzettadikyiv.com/
```

**CRITICAL:** Skipping `build_hashed_assets.py` means the browser loads old hashed files from cache — your CSS/JS edits won't appear live. Symptom: `getComputedStyle()` returns old values despite correct source.
