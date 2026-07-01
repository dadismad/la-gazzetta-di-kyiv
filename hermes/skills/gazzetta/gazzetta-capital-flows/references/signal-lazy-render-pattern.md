# Signal Container — Lazy-Render Pattern (v22.12)

## Problem
`renderTriangulation()` reads `.card[data-story-id]` elements from DOM. When called at boot via `scheduleTriangulation()`, story cards may not be in DOM yet (async fetch). Retry loop sometimes exhausts before cards arrive → Signal container renders empty.

## Solution: Render on Expand
In `wireCollapsibleContainers()`, detect when the Signal container is expanded and trigger `renderTriangulation()` at that moment. By the time a user clicks to expand the container, stories are guaranteed loaded.

```javascript
// In wireCollapsibleContainers():
header.addEventListener('click', function(e) {
  e.stopPropagation();
  container.classList.toggle('expanded');
  // Signal container: render triangulation on expand
  if (container.classList.contains('expanded') && container.querySelector('#triangulationList')) {
    renderTriangulation();
  }
});
```

## Why This Works
- User-initiated expand always happens AFTER boot + polling cycles complete
- Cards are guaranteed in DOM by the time a user interacts
- No retry loop, no mutation observer, no timing hacks
- If triangulation data changes later, re-expanding re-renders fresh

## Alternative (not chosen)
- `scheduleTriangulation()` retry loop with increasing delays — fragile, wastes cycles
- MutationObserver on `#newsCol` — overengineered for this case
- Call after every `refreshFlowStoryLinks()` — unnecessary double-render
