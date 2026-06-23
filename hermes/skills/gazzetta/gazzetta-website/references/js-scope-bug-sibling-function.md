# JS Scope Bug Pattern: Sibling Function References Local Variable

## Pattern

When a function `A()` defines a local variable and calls a SIBLING function `B()` (not nested, defined at the same scope level), `B()` cannot access `A()`'s locals:

```js
// ❌ BROKEN
function buildHTML(story) {
    const t = window.i18n ? (k, fb) => i18n.t(k, fb) : (k, fb) => fb;
    return `<div>${renderMultiPersona(story)}</div>`;
}

function renderMultiPersona(story) {  // SIBLING, not nested!
    return '<h2>' + t('label', 'FALLBACK') + '</h2>';  // ReferenceError!
}
```

## Detection

When a function exists and is callable, but throws `ReferenceError: <var> is not defined` from within a template literal or callback, check if the referenced variable is local to the CALLER, not the callee.

## Fix

Pass the variable as a parameter:

```js
// ✅ FIXED
function buildHTML(story) {
    const t = window.i18n ? (k, fb) => i18n.t(k, fb) : (k, fb) => fb;
    return `<div>${renderMultiPersona(story, t)}</div>`;
}

function renderMultiPersona(story, t) {
    return '<h2>' + t('label', 'FALLBACK') + '</h2>';
}
```

## Pitfall: Try/catch hides the error

When async init() wraps everything in try/catch, the `ReferenceError` is caught and logged to console but the user sees a generic "Failed to load" message. Always check `console.error` output when debugging "stuck loading" screens.

## Gazzetta Instance

In `story-app.js`, the `buildHTML()` function defined `t` as a local i18n shortcut. `renderMultiPersona()` was a sibling function that referenced `t` — but `t` was only in `buildHTML`'s scope. Fixed by adding `t` parameter: `renderMultiPersona(story, t)`.
