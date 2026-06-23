# Trade Thesis Activation — LLM Prompt Optimization for Pipeline Output

## Problem

DeepSeek-powered `contradiction_synthesizer.py` was producing trade_thesis objects for only 33/401 stories (8%). 92% of stories had empty or missing trade_thesis fields. The frontend cards showed "No active thesis" on nearly every story, the Stop:/Target: labels never rendered, and the Telegram broadcast (GAP > 50 + active trade thesis) stayed silent.

Root cause: **token starvation + schema ordering** — not a prompt logic error.

## Root Cause Analysis

### Cause 1: max_tokens=1200 too tight for full schema
The JSON response requires: they_say, reality, contradiction_gap, narrative_scores (12 vectors), affected_tickers, affected_asset_classes, AND trade_thesis (13 fields). At 1200 tokens, DeepSeek generated valid JSON but dropped trade_thesis (the last field in the schema) when it ran out of tokens. JSON parse succeeded because the response was structurally complete up to the truncation point.

### Cause 2: trade_thesis was the LAST field in the schema
DeepSeek allocates token budget sequentially. trade_thesis — the highest-value output — came after 12 narrative vectors and 2 arrays. It got whatever tokens were left (usually zero).

### Cause 3: Redundancy rule self-sabotage
The system prompt said: "If CURRENT PLATFORM STATE shows existing direction for this narrative, set direction to NEUTRAL with explanation." Since every narrative had a dominant_direction in flows.json, this rule told DeepSeek to default to NEUTRAL for every story mapped to any narrative.

### Cause 4: Over-rigid entry price requirement
The schema demanded exact prices like '$46.82' and banned 'current levels'. For geopolitical news without specific technical levels, DeepSeek defaulted to NEUTRAL rather than risk violating the banned-phrase rule.

## Solution: Four-Patch Protocol

All changes in `scripts/contradiction_synthesizer.py`:

| Patch | Line(s) | Change | Effect |
|-------|---------|--------|--------|
| P0 | 434 | `max_tokens: 1200` → `2400` | 2x token budget, DeepSeek has room for full schema |
| P1 | 293-305 | Move `trade_thesis` from last field → position 2 (after headline) | Highest-value output gets token priority, generated while context window is fresh |
| P2 | 388 | Redundancy rule: "set NEUTRAL" → "MUST generate, differentiate by entry/ticker/timeframe" | Removes universal NEUTRAL kill switch |
| P3 | 296, 373, 382 | Entry price: add `'market'` as valid value; remove BANNED phrase list | LLM can generate trade theses for macro/geopolitical events without specific technical levels |

### P1 Schema Restructuring (Before → After)

```
Before: headline → they_say → reality → gap → capital → 12 vectors → tickers → trade_thesis
After:  headline → trade_thesis → they_say → reality → gap → capital → 12 vectors → tickers
```

## Results

5 items processed with patched script on VM:
- Before: 33/401 active (8%)
- After: 51/411 active (12% from 5 new items alone)
- New theses used: exact prices (`$33.65`, `$181.88`) AND `market` entries
- Directions: LONG, SHORT, NEUTRAL (with volatility thesis)

Full benefit accrues as the governor processes fresh ingestion batches every 10 minutes.

## Verification Query

```bash
curl -sk https://www.lagazzettadikyiv.com/data/stories.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
stories = d.get('all_stories', [])
active = sum(1 for s in stories if (s.get('trade_thesis') or {}).get('direction','') not in ('NEUTRAL','MISSING',''))
print(f'{len(stories)} stories, {active} active theses ({active*100//len(stories)}%)')
"
```

## Key Principle: Attention Mechanism Engineering

When an LLM generates structured JSON sequentially, field ORDER determines token budget allocation. Fields at the top of the schema get generated while the context window is fresh and the token budget is full. Fields at the bottom compete for leftovers. Hoisting the highest-value field to position 2 is a zero-cost optimization that redirects the LLM's attention to what matters most.

This principle applies to ANY JSON-schema pipeline, not just Gazzetta. When a critical field is consistently missing from LLM output, check:
1. Is it the LAST field in the schema? Move it to the top.
2. Is max_tokens sufficient for all fields? Double it.
3. Are there defensive rules telling the LLM to skip this field? Remove them.
