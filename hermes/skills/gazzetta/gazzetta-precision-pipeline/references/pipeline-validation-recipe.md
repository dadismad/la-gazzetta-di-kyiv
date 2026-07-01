# Pipeline Data Validation Recipe

## The "undefined" propagation bug (2026-06-06)

**Symptom:** Live site story cards showed `undefined — projected undefined change at undefined confidence`.

**Trace:**
1. `intel_to_stories.py` created stories with `capital_flow` dicts missing `projected`, `confidence_pct`, `pace_multiplier`
2. `generate_flows.py` extracted broken capital_flow into flow entries — no field checking
3. `app.js` line 358 rendered `${f.projected}` → "undefined" because field was missing
4. 3 of 4 story cards showed broken data. Only 1 card (with properly formatted original story) rendered correctly.

## Required capital_flow fields

Every story's `capital_flow` dict MUST have:

```json
{
  "direction": "inflow" | "outflow",
  "amount_b": <number — billions>,
  "projected": "<string — what's expected to happen next>",
  "pace_multiplier": <number — 1.0 = normal pace>,
  "confidence_pct": <number — 50-95>,
  "confidence_level": "high" | "medium" | "low",
  "asset_class": "equities" | "commodities" | "crypto" | "fixed_income" | "defense" | "tech"
}
```

Missing any of these causes `undefined` in the frontend.

## Validation script pattern

The `validate_stories.py` approach:
1. Load stories.json
2. For each story, check capital_flow dict for all required fields
3. Derive missing fields from story content:
   - `projected` ← portfolio_implication or reality or headline
   - `confidence_pct` ← story.confidence (map "high"→80, "medium"→65, "low"→50)
   - `direction` ← parse thesis text for LONG/SHORT keywords
   - `pace_multiplier` ← default 1.0
   - `asset_class` ← story.sector or keyword detection from thesis+event
4. Write back repaired stories
5. Sync to site/data/

Run this BEFORE generate_flows.py in the pipeline chain.

## Detection: browser console check

```javascript
// Check for broken capital_flow dicts in loaded stories
fetch('./data/stories.json', {cache: 'reload'}).then(r => r.json()).then(d => {
  const broken = d.stories.filter(s => !s.capital_flow?.projected || !s.capital_flow?.confidence_pct);
  console.log(`Broken stories: ${broken.length}/${d.stories.length}`);
});
```

0 broken stories = pipeline healthy. Any number > 0 = validation step missing or failing.

## Prevention

Any new data-producing script MUST be tested by:
1. Running it in isolation
2. Running the full pipeline chain
3. Checking the live site with the browser console query above
4. If `undefined` appears anywhere, the script's output format is wrong — fix the script, not the consumer
