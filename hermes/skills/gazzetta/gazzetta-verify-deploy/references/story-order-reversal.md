# Story Order Reversal: afterbegin + forEach Trap

**Found:** v25.10, June 2026  
**Symptom:** Stories page shows completely different stories than homepage teasers — same STORIES_DATA, different visual order.  
**Root cause:** `insertAdjacentHTML('afterbegin', html)` PREPENDS elements. Combined with forward `forEach`, the array order gets reversed.

## The Bug

```js
// boot() in app.js, line ~2283
const all = [data.lead, ...filteredStories];  // newest first (stories.json order)
all.forEach((s, i) => appendStoryCard(s, i === 0));

// appendStoryCard(), line ~1638
el.insertAdjacentHTML('afterbegin', html);  // PREPENDS — reverses order
```

**Result:** 
- Iteration 1: lead (newest) inserted
- Iteration 2: story 1 PREPENDED before lead → story 1 at top
- Iteration 205: story 204 (oldest) PREPENDED → oldest at TOP

**Visual:** Oldest stories (geopolitics, June 7-9) appear first. Newest stories (business/tech, June 11) appear last.

## The Fix

Reverse the iteration so `afterbegin` produces correct order:

```js
// Fixed boot()
const rev = [...all].reverse();
rev.forEach((s, i) => appendStoryCard(s, i === rev.length - 1));
// i === rev.length - 1 flags the lead story (original all[0], now at end of reversed array)
```

**Why not change afterbegin → beforeend?**  
`pollLivingStories()` calls `appendStoryCard()` for new breaking stories during live polling. With `beforeend`, new stories would appear at BOTTOM of feed. With `afterbegin` + forward iteration in the poll, new stories PREPEND → appear at TOP. The poll behavior is correct; only the initial load iteration was wrong.

## Verification

```js
// After deploy, check both pages show same first 5:
// homepage teasers
JSON.stringify(Array.from(document.querySelectorAll('.teaser-item')).slice(0,5).map(a => a.textContent.substring(0,60)))

// stories page
JSON.stringify(Array.from(document.querySelectorAll('#newsCol article h3')).slice(0,5).map(h => h.textContent.substring(0,60)))
```

Both must match exactly. Before fix: teasers showed business/tech (newest), stories showed geopolitics (oldest). After fix: both show same order.
