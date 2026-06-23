# Gazzetta Namespace Migration (v23.8)

## Problem
`app.js` (2274 lines) and `story-app.js` used bare global variables (`const`, `let`, `function`) at top-level scope. This caused:
- **Scope fragility**: Adding any new `const` or `function` to story-app.js silently broke the story detail page
- **Silent catch blocks**: 19 `catch(e){}` blocks swallowed errors with zero console output
- **Collision risk**: Any future module (login, premium gate, analytics) would pollute global scope

## Solution: `window.Gazzetta` Namespace

Three sub-namespaces separate concerns:

```javascript
window.Gazzetta = {
  UI:    { byId },                          // DOM helpers
  Data:  { getJSON, getDataPath, getFlowsPath },  // Data fetching
  State: { capturedStoryIds, STORIES_CACHE, flowsData, initialized, storyCount },  // Runtime state
  Story: { init, renderIntelReport },       // Story page (story-app.js)
};
```

## Implementation Pattern

### app.js (top of file, after FLOWS_POLL_INTERVAL)

```javascript
window.Gazzetta = window.Gazzetta || {};
Gazzetta.State = {};
Gazzetta.UI = {};
Gazzetta.Data = {};

// Export key globals
Gazzetta.Data.getJSON = getJSON;
Gazzetta.Data.getDataPath = getDataPath;
Gazzetta.Data.getFlowsPath = getFlowsPath;
Gazzetta.UI.byId = byId;
Gazzetta.State.capturedStoryIds = capturedStoryIds;
Gazzetta.State.STORIES_CACHE = STORIES_CACHE;
```

### boot() exports (at end of boot)

```javascript
Gazzetta.State.initialized = true;
Gazzetta.State.storyCount = capturedStoryIds.size;
if (typeof CAPITAL_FLOWS_DATA !== "undefined") { Gazzetta.State.flowsData = CAPITAL_FLOWS_DATA; }
if (typeof ANCHOR_ASSETS !== "undefined") { Gazzetta.Data.ANCHOR_ASSETS = ANCHOR_ASSETS; }
```

### story-app.js

```javascript
window.Gazzetta = window.Gazzetta || {};
Gazzetta.Story = {};
Gazzetta.Story.init = init;
Gazzetta.Story.renderIntelReport = renderIntelReport;
```

## Verification

```javascript
// Browser console
typeof window.Gazzetta  // "object"
Object.keys(Gazzetta.UI)    // ["byId"]
Object.keys(Gazzetta.Data)  // ["getJSON", "getDataPath", "getFlowsPath"]
Object.keys(Gazzetta.State) // ["capturedStoryIds", "STORIES_CACHE", ...]

// Leak check: all detected "leaks" should be browser built-ins (alert, atob, etc.)
// No Gazzetta-specific globals should appear outside the namespace
```

## Backward Compatibility

All existing function calls work at global scope — the namespace is additive, not a replacement. `byId()`, `getJSON()`, `boot()`, `formatTimeAgo()` all remain callable from global context.
