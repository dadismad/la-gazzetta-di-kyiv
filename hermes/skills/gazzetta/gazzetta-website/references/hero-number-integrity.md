# Hero Number Integrity Rules (v22.6, June 2026)

## Hard Rule

**All hero stats must use `—` as HTML fallback.** Never hardcode a number that changes. JS populates live values on load. Stale hardcoded numbers are lies.

## Bugs Fixed (v22.6)

### Bug 1: Story count overwritten by flow count
- `updateMastheadFlows()` was setting `heroStoryCount` to `flowsData.total_flows_tracked` (flow count, not story count)
- Result: hero showed 2 stories when 10 actually existed
- **Fix:** Removed story count line from `updateMastheadFlows`. Story count is set by `updateCumulativeStats` only.

### Bug 2: Cumulative localStorage shown instead of current count
- `updateCumulativeStats` used `tracked` (cumulative localStorage, accumulated across sessions → 28)
- **Fix:** Now uses `currentStories` (DOM `.card[data-story-id]` count → matches visible cards)

### Bug 3: Hardcoded HTML fallbacks
- `$17.1B`, `14`, `$18.4K` were hardcoded in HTML
- If JS failed to load, these stale values appeared as truth
- **Fix:** All five hero stat values use `—` as HTML default

## Verification Checklist

After any data change:
1. `heroStoryCount` = DOM `.card[data-story-id]` count
2. `heroFlowTotal` = sum of all `CAPITAL_FLOWS_DATA` amounts
3. `heroAssetCount` = `ANCHOR_ASSETS.length`
4. `heroBetTotal` = sum of entry prices × conviction multiplier (in K)
5. `heroConfidence` = aggregate from flows.json

**Anti-pattern:** Do NOT set `heroStoryCount` from flows data. Stories ≠ flows.
