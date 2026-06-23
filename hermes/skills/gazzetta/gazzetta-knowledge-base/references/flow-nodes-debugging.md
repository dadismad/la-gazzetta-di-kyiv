# Flow Nodes — SVG Rendering Debug Playbook

Diagnosed June 2026 when the flow-nodes.html page showed empty SVG (0 nodes, 0 edges despite valid flow_nodes.json with 13 nodes, 23 edges).

## Symptoms
- `document.querySelector('#cn-graph')` exists with viewBox
- `document.querySelector('#cn-nodes-layer > *').length` → 0
- `document.querySelector('#cn-edges-layer > *').length` → 0
- 2 JS errors with empty source (exception)
- Browser console: `window.__CN_DATA__` undefined

## Root Cause Chain

### Bug 1: Null DOM element crash blocks IIFE
```javascript
// Line ~1145 in flow-nodes.html
const themeBtn = document.getElementById('cn-theme-toggle');
themeBtn.addEventListener('click', () => { ... });
```
`cn-theme-toggle` doesn't exist in the HTML → `TypeError: Cannot read properties of null (reading 'addEventListener')`. This throws BEFORE `init()` is registered → entire inline IIFE stops → graph never renders.

**Fix:** Null-guard:
```javascript
const themeBtn = document.getElementById('cn-theme-toggle');
if (themeBtn) themeBtn.addEventListener('click', () => { ... });
```

### Bug 2: Missing stats elements crash render()
The `render()` function sets `.textContent` on elements that don't exist in the HTML:
```javascript
document.getElementById('cn-last-updated').textContent = ... // null
document.getElementById('cn-total-tracked').textContent = ... // null
document.getElementById('cn-node-count').textContent = ...    // null
document.getElementById('cn-edge-count').textContent = ...    // null
```
Even after Bug 1 is fixed, render() crashes here with `TypeError: Cannot set properties of null (setting 'textContent')`.

**Fix:** Null-guard all element access:
```javascript
const luEl = document.getElementById('cn-last-updated');
if (luEl) { luEl.textContent = ...; luEl.setAttribute(...); }
```

### Bug 3: app.js injected into standalone page
`build_hashed_assets.py` (or a prior manual edit) injects `<script src="./app.xxx.js">` into flow-nodes.html. The 2498-line app.js `boot()` function:
- Polls for non-existent DOM elements
- Creates AbortControllers
- Fires fetch requests to paths that don't exist from this page context
- Throws uncaught exceptions

**Fix:** Remove app.js from flow-nodes.html:
```bash
sed -i '' '/script src=.*app\./d' site/flow-nodes.html
```
The flow-nodes page has its own complete inline JS — it doesn't need app.js.

## Debugging Technique

1. Test SVG DOM accessibility:
```javascript
document.getElementById('cn-nodes-layer').innerHTML = '<circle cx="100" cy="100" r="30" fill="red"/>';
```
If this works, the SVG DOM is fine — the issue is in the data fetch or render logic.

2. Test data loading:
```javascript
var x = new XMLHttpRequest();
x.open('GET', './data/flow_nodes.json', false);
x.send();
var d = JSON.parse(x.responseText);
console.log('nodes:', d.nodes.length, 'edges:', d.edges.length);
```

3. Test layout computation:
```javascript
// Copy computeLayout() function and run with real data
// Verify positions object has entries for ALL node IDs
```

## Prevention
- All `document.getElementById()` calls in standalone pages MUST be null-guarded
- Standalone pages (flow-nodes, event_horizon) must NOT load app.js
- After shipit, verify: `grep -l 'script src.*app\.' site/flow-nodes.html` should return empty
