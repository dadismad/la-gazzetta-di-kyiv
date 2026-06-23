# Flow Label Standardization & Cross-Linking — June 2026

## Issue
UX Writer audit flagged 6 different phrasings for "institutional selling" that cycled randomly via `POSITION_VARIANTS`:
- "Institutions distributing — net outflow detected"
- "Big money exiting — institutional selling confirmed"
- "Whales de-risking — net capital outflow"
- "Capital rotating out — net institutional selling"
- "Institutional supply hitting — net selling pressure"
- "Distribution in progress — net institutional outflow"

Users couldn't tell if these were different signals or stylistic variation. "Whales de-risking" and "Big money exiting" flagged as YouTube-channel cliches.

## Fix (v22.12)
Reduced from 7→3 variants per direction, clear language, no cliches:

```javascript
const POSITION_VARIANTS = {
  'accumulating': [
    'Institutions buying — net inflow',
    'Capital flowing in — accumulation detected', 
    'Positioning long — institutional demand'
  ],
  'distributing': [
    'Institutions selling — net outflow',
    'Capital flowing out — distribution detected',
    'Reducing positions — institutional selling'
  ],
  'hedging': [
    'Mixed signals — hedging both sides',
    'Direction unclear — capital in standby',
    'Balanced flows — no clear direction'
  ]
};
```

## Flow→Story Cross-Linking Fix

**Problem:** Flow items rendered before story cards loaded. Expand handler did `document.querySelector(.card[data-story-id="${sid}"])` but cards weren't in DOM yet. Showed "Loading..." forever.

**Fix (v22.12):**
1. `STORIES_CACHE` global — populated on `appendStoryCard()` with `story_id → {headline}`
2. `refreshFlowStoryLinks()` — scans all `.flow-story-title` showing "Loading..." or "Story not yet loaded", resolves from DOM first, then from STORIES_CACHE fallback. Shows headline even when DOM card isn't available.
3. Called after all story render paths (boot + poll + fallback)
4. Also retries on expand click (was checking only "Loading..." — now also checks "Story not yet loaded")

**File locations:** `site/app.js` lines 8-9 (STORIES_CACHE), ~400-430 (expand handler), ~445-470 (refreshFlowStoryLinks), boot paths at ~1565, ~1600.
