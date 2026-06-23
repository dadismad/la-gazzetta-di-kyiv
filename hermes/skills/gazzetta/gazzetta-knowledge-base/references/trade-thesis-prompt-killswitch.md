# Trade Thesis Drought — Prompt Kill-Switch Pattern (June 2026)

## Symptom

191 stories in stories.json, 0 with active trade theses. Every card shows "No active thesis." The contradiction_synthesizer pipeline runs without errors (HTTP 200, valid JSON), but the `trade_thesis.direction` field is universally NEUTRAL or empty.

## Root Cause: Redundancy Rule = Universal Kill Switch

In `contradiction_synthesizer.py` line 388, the system prompt contains:

```
- Redundancy: If the CURRENT PLATFORM STATE shows an existing trade direction
  (e.g., "direction short") for this narrative, do NOT generate an identical trade
  thesis. Either differentiate (different entry, different ticker) or set direction
  to NEUTRAL with explanation.
```

### The Chain

1. `build_narrative_context()` (line 140) reads `flows.json` and builds a `CURRENT PLATFORM STATE` block showing `dominant_direction` for every narrative.

2. This block is injected into **every user prompt** (line 404-406). DeepSeek sees:
   ```
   CURRENT PLATFORM STATE:
     energy_sovereignty: 74 stories, avg GAP 37, capital $3.3B, direction inflow
     space_economy: 38 stories, avg GAP 65, capital $1.7B, direction outflow
     ... (all 12 narratives have a direction)
   ```

3. DeepSeek reads line 388: "If platform state shows an existing direction... set NEUTRAL."

4. Since **every narrative has a `dominant_direction`** in flows.json, **every single story** triggers the "set NEUTRAL" escape hatch. 191 stories → 191 NEUTRAL trade theses.

### Secondary Contributor: Over-Rigid Schema

Lines 316-317 in the system prompt demand exact single prices for `limit_entry_price`, `stop_loss`, and `take_profit` — with "current levels" explicitly BANNED. For geopolitical news articles without specific price levels, DeepSeek defaults to NEUTRAL rather than risk violating the banned-phrase rule.

### Tertiary Contributor: Token Budget

`max_tokens: 1200` (line 434) is tight for the full response schema (they_say, reality, narrative_scores for 12 vectors, capital_volume_usd, affected_tickers, AND trade_thesis with 13 fields). DeepSeek may truncate the trade_thesis to fit required fields.

## The Fix

| Priority | Line | Change |
|----------|------|--------|
| P0 | 388 | Replace NEUTRAL escape hatch: "MUST still generate a trade thesis. Differentiate by entry price, timeframe, or ticker. Only omit if the story adds zero new information." |
| P1 | 316-317, 382 | Relax entry price: allow `"market"` for current-price execution. Remove "BANNED" language — replace with "prefer exact prices when available." |
| P2 | 434 | `"max_tokens": 2000` — give DeepSeek room for full trade_thesis schema. |

## Diagnostic Pattern for Prompt Kill-Switches

When a pipeline produces 0 results despite no errors:

1. **Check the system prompt for universal escape hatches.** Look for rules containing "if X exists, set NEUTRAL/empty/skip." These become kill switches when X is always true.

2. **Check what the LLM actually sees.** The prompt is assembled from multiple pieces (platform state, market context, news text). One of those pieces may guarantee the kill condition is met for every item.

3. **Check token budget.** If the response schema demands 15+ fields and the budget is tight, the LLM will silently drop fields. Fields at the end of the schema (like trade_thesis) are dropped first.

4. **Check schema rigidity.** If the schema demands exact, falsifiable numbers that the input data can't provide, the LLM will choose safety (NEUTRAL) over fabrication.
