# Flow Generation Pipeline — Data Extraction & Bug Fixes (v22.6, June 2026)

## Extraction Tiers (generate_flows.py)

Flows are extracted from stories in 3-tier fallback order:

1. **capital_flow dict** — explicit flow data (rarely populated)
2. **capital_flow_implication string** — e.g. "$3.2B crypto outflows rotating into Dow"
3. **portfolio_implication string** — e.g. "LONG crude oil... SHORT SPX/QQQ"
4. **paradigm_implications array** — joined and parsed as text

## Direction Detection (first-match priority)

Portfolio text often contains MULTIPLE directional keywords:
- "LONG crude oil (Brent/WTI) as the Hormuz blockade extends... SHORT SPX/QQQ"
- Old code: outflow check ran FIRST, matched "SHORT" at position 178 and ignored "LONG" at position 23
- **Fix:** Find ALL matches, compare positions, use the earliest match in the text. Portfolio leads with primary trade.

```python
out_match = re.search(outflow_kw, text, re.IGNORECASE)
in_match = re.search(inflow_kw, text, re.IGNORECASE)
if out_match and (not in_match or out_match.start() < in_match.start()):
    direction = "outflow"
elif in_match:
    direction = "inflow"
```

Outflow keywords: short, exit, sell, underweight, trim, reduce, rotate out
Inflow keywords: long, buy, overweight, accumulate, add, rotate into

## Quality Filter

- Minimum $10M equivalent (`amount_b >= 0.01`)
- $XK amounts ignored (price targets, not capital flows)
- Headlines use compact format: `$XB flowing into/out of asset_class`

## The Stale Code Bug (v22.6 fix)

`generate_flows()` had INLINE extraction code that duplicated but didn't match `extract_flow_from_story()`:
```python
# OLD (broken — only checked 2 fields):
cf = story.get("capital_flow")
if not cf:
    imp = story.get("capital_flow_implication", "")
    if imp: cf = parse_flow_implication(imp)

# NEW (calls the full 3-tier function):
cf = extract_flow_from_story(story)
```

Result: went from 2 flows to 10 flows (all stories now contribute).
