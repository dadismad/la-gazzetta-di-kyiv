# JS Scope Bug: Closure Variable Not Passed to Extracted Function

## Pattern

A function defines a local variable (`t` for i18n) and uses it in template literals. A helper function is extracted from the parent but the closure variable is NOT passed as a parameter. The extracted function references the variable but it's out of scope → `ReferenceError`.

## Reproduction (story-app.js, June 2026)

```js
// buildHTML() defines t at its top:
function buildHTML(story, allStories, currentIdx) {
    const t = window.i18n ? (k, fb) => i18n.t(k, fb) : (k, fb) => fb;
    // ...
    return `
      ${renderMultiPersona(story)}   // ← t NOT passed
    `;
}

// renderMultiPersona uses t but doesn't receive it:
function renderMultiPersona(story) {       // ← missing 't' parameter
    var h = '<section class="intel-multi-persona">';
    h += '<h2>' + t('multi_persona_label', 'MULTI-PERSONA ANALYSIS') + '</h2>';
    //          ^ ReferenceError: t is not defined
}
```

## Symptoms

- Page shows "Loading intelligence report…" forever
- `Gazzetta.Story.loaded` is `true` (IIFE ran)
- `window.i18n._ready` is `true` (not an i18n timing issue)
- `fetch('./data/stories.json')` returns 200 with correct data
- Console shows: `ReferenceError: t is not defined at renderMultiPersona`
- The `init()` function's `.catch()` is empty — the error is swallowed silently

## Detection

```bash
# Check for function definitions that reference variables not in their parameter list
# In this case: renderMultiPersona uses t() but function signature lacks 't'
grep -n 'function renderMultiPersona' site/story-app.js
# Output: function renderMultiPersona(story) {   ← missing 't'
```

## Fix

Two changes required:

```js
// 1. Pass t to the function call:
${renderMultiPersona(story, t)}   // was: ${renderMultiPersona(story)}

// 2. Accept t in the function signature:
function renderMultiPersona(story, t) {   // was: function renderMultiPersona(story) {
```

## Prevention

When extracting helper functions from a parent that defines closure variables used in template literals:
1. Search for ALL variable references in the extracted function body
2. Add any referenced variables to the parameter list
3. Update ALL call sites to pass those parameters
4. After extraction, grep for `function NAME(` and verify all referenced variables appear in the signature
