# appendStoryCard `afterbegin` Reversal Bug (v25.10)

## Symptom
The stories page (`/stories.html`) and homepage teasers show completely different story orders. Homepage shows newest stories first (business/tech). Stories page shows oldest stories first (geopolitics/war).

## Root Cause

`appendStoryCard()` at line 1638 uses `insertAdjacentHTML('afterbegin', html)` — PREPENDS each card. The `boot()` function iterates `all.forEach((s, i) => appendStoryCard(s, i === 0))` over 205 stories in forward order (newest→oldest).

With `afterbegin`, each subsequent card gets inserted BEFORE the previous one:
- Iteration 1: "Stock Market Today" (lead, newest) inserted → position: only child
- Iteration 2: "AI Unemployment" prepended → position: top, pushes lead down
- ...
- Iteration 205: "Iran Strikes Kuwait" (oldest) prepended → position: TOP

Result: array order is completely reversed. The oldest story appears at the visual top.

Meanwhile, `populateTeasers()` uses `innerHTML = items.map().join('')` which preserves forward order. The lead story (newest) stays at the visual top.

## Why afterbegin exists

The comment says "Insert at the top — newest first." The intent was correct (newest at top), but `afterbegin` with forward iteration produces the OPPOSITE result (oldest at top).

`afterbegin` is also used by `pollLivingStories()` for live updates — new breaking stories should appear at the top during polling, which `afterbegin` does correctly.

## Fix (v25.10)

Reverse the iteration in `boot()` only — keep `afterbegin` unchanged for poll behavior:

```js
// BEFORE (broken):
all.forEach((s, i) => appendStoryCard(s, i === 0));

// AFTER (fixed):
const rev = [...all].reverse();
rev.forEach((s, i) => appendStoryCard(s, i === rev.length - 1));
```

The lead story (original `all[0]`, newest) becomes `rev[rev.length-1]` in the reversed array. It gets iterated LAST, prepended LAST → appears at visual TOP. ✓

Poll behavior unchanged — `pollLivingStories()` still uses forward iteration with `afterbegin`, so new breaking stories during live polling still appear at the top.

## Affected locations

- `app.js` line 2241: `boot()` livingData path
- `app.js` line 2285: `boot()` stories.json fallback path
- NOT affected: `pollLivingStories()` line 2089 (poll behavior correct as-is)

## Verification

```js
// Both pages must show identical first 5 stories
// Stories page:
Array.from(document.querySelectorAll('#newsCol article')).slice(0,5).map(a => a.querySelector('h3')?.textContent)
// Homepage:
Array.from(document.querySelectorAll('.teaser-item, #storiesTeaserContent a')).slice(0,5).map(a => a.textContent?.trim())
// Must match.
```
