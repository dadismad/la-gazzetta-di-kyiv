# Frontend DOM Timing Pitfalls

Pitfalls encountered during Gazzetta di Kyiv development where JS functions depended on DOM elements that didn't exist yet. These are general patterns that apply to any site with async-loaded content.

## Pitfall 1: QuerySelector-dependent render functions called before async content loads

**Symptom:** Container shows permanent "loading" state. Content never appears even though data is correct and the full render function exists.

**Root cause:** `renderTriangulation()` called `document.querySelectorAll('.card[data-story-id]')` — but it ran BEFORE `appendStoryCard()` had been called. The stories load from `getJSON()` (async), so at boot time there are zero cards in the DOM.

**Fix pattern:**
```javascript
// WRONG — called before cards exist
renderTriangulation();
const data = await getJSON('stories.json');
data.forEach(s => appendStoryCard(s));

// RIGHT — called after cards are appended
renderAnchor();
renderCapitalFlows();
const data = await getJSON('stories.json');
data.forEach(s => appendStoryCard(s));
renderTriangulation();  // NOW cards exist
```

**Checklist when debugging similar bugs:**
1. Find the render function that's not producing output
2. Find where it queries the DOM (`.querySelectorAll`, `.getElementById`)
3. Trace backward: what async operation populates those DOM elements?
4. Is the render function called before or after that async operation completes?

**Gazzetta-specific:** The `boot()` function has two code paths — `living_stories.json` and `stories.json` fallback. BOTH paths need the triangulation call AFTER `appendStoryCard()`.

## Pitfall 2: Container content rendered before its parent is in the DOM

**Symptom:** `byId('triangulationList')` returns `null` even though the HTML has `<div id="triangulationList">`.

**Root cause:** The container might be dynamically inserted via JS or might not be in the initial HTML. Always guard with `if (!el) return;`.

**Fix pattern:**
```javascript
function renderTriangulation() {
  const el = byId('triangulationList');
  if (!el) return;  // Container not in DOM yet — fail silently
  // ... rest of render
}
```

## Pitfall 3: Polling interval re-renders without deduplication

**Symptom:** Cards duplicate on every poll cycle. Story count grows indefinitely.

**Root cause:** `setInterval(pollLivingStories, 120000)` calls `appendStoryCard()` which adds new cards, but doesn't check if a card with that `story_id` already exists.

**Fix pattern:**
```javascript
// Guard in appendStoryCard or the render loop
if (el.querySelector(`[data-story-id="${story.story_id}"]`)) return;
```

**Note:** Use `data-flow-story-id` for flow items to prevent false dedup matches with story cards sharing the same story_id.

## Pitfall 4: Rendering NaN when data field is missing from hardcoded objects

**Symptom:** Signal/triangulation cards show `$NaNB` instead of real dollar amounts. The underlying data structure has the right value but in the wrong field.

**Root cause (Gazzetta-specific):** `CAPITAL_FLOWS_DATA` objects in `app.js` have `headline` (e.g., `"$4.2B flowing into energy ETFs"`) and `detail` (e.g., `"2.3x normal pace"`) fields, but the triangulation `computeTriangulation()` function did `parseFloat(flow.amount)` — and the `amount` field doesn't exist. `parseFloat(undefined)` returns `NaN`, producing `$NaNB`.

**Fix pattern — extract from string when dedicated field is missing:**
```javascript
// WRONG — flow.amount doesn't exist in the data structure
const amt = parseFloat(flow.amount);  // NaN

// RIGHT — regex-extract from the field that HAS the value
const amtMatch = (flow.headline || '').match(/\$([\d.]+)([MBT])/);
const amt = amtMatch ? parseFloat(amtMatch[1]) : 0;
const denom = amtMatch ? amtMatch[2] : 'M';
const paceMatch = (flow.detail || '').match(/(\d+\.?\d*)x/);
const pace = paceMatch ? parseFloat(paceMatch[1]) : 1;
```

**Checklist for similar bugs:**
1. The data renders correctly in one place (capital flows container) but shows NaN in another (signal cards)
2. The two renderers use different code paths — one reads from a field that exists, the other from a field that doesn't
3. Cross-reference: open the hardcoded data structure vs the function that's failing
4. If the field is missing, regex-extract from the field that DOES contain the value
