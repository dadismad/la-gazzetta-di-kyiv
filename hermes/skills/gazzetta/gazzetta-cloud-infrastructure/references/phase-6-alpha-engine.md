# Phase 6 — Alpha Generation Engine (RCI)

Deployed June 21, 2026. Converts absolute capital-at-stake figures into relative dominance metrics measured against the correct market segment denominator.

## Key Files

| File | Purpose |
|------|---------|
| `scripts/fetch_macro_baselines.py` | Weekly cron: writes `data/macro_baselines.json` |
| `scripts/calculate_capital.py` | Per-cycle: reads baselines, computes RCI per story + per narrative |
| `data/macro_baselines.json` | Denominators + segment mapping + saturation threshold |

## macro_baselines.json Schema

```json
{
  "updated": "2026-06-21T19:37:10Z",
  "baselines": {
    "global_equities_usd": 100000000000000,
    "us_m2_usd": 22800000000000,
    "total_crypto_mcap_usd": 2287652623583
  },
  "narrative_segments": {
    "dollar_decline": "us_m2_usd",
    "rate_cycle": "us_m2_usd",
    "crypto_reserve": "total_crypto_mcap_usd",
    "tech_convergence": "global_equities_usd",
    "...": "global_equities_usd"
  },
  "saturation_threshold": 0.15
}
```

**PITFALL — Segment key suffix mismatch (June 21, 2026):** Segment keys MUST include `_usd` suffix to match baseline keys. The initial deploy had `"us_m2"` (no suffix) → `baselines.get("us_m2", 1)` returned 1 → all segment caps were $1 → dominance showed trillions of percent. Fixed by adding `_usd` suffix to all `narrative_segments` values in `fetch_macro_baselines.py`.

## RCI Formula (in calc_capital.py)

Per-story:
```python
segment_key = narrative_segments.get(nid)
segment_cap = baselines.get(segment_key, 1) if segment_key else 1
velocity_mod = gap / 100.0 if gap > 0 else 0.01
rci = (capital_usd / max(segment_cap, 1)) * velocity_mod
dominance = capital_usd / max(segment_cap, 1)
```

## Narrative Aggregation — Median-per-Asset-Base (June 21 Fix)

**PITFALL — Naive sum double-counts the same underlying data.** If 33 dollar_decline stories all reference the same gold CFTC position ($57.3B notional), summing capital_at_stake across all 33 stories inflates the total 33x. The fix: group stories by unique `asset_base` within each narrative, apply the **median** gap for that base, then sum across distinct bases.

```python
# narrative_data: {nid: {asset_base: {"gaps": [gap1, gap2, ...], "fidelity": tier}}}
narrative_data = {}
for story in all_stories:
    ...
    if nid and nid != "unassigned" and asset_base > 0:
        if nid not in narrative_data:
            narrative_data[nid] = {}
        if asset_base not in narrative_data[nid]:
            narrative_data[nid][asset_base] = {"gaps": [], "fidelity": fidelity}
        narrative_data[nid][asset_base]["gaps"].append(gap)

# Then for each narrative:
import statistics
for nid in sorted(narrative_data.keys()):
    total_cap = 0
    for asset_base, info in narrative_data[nid].items():
        median_gap = statistics.median(info["gaps"])
        mult = FIDELITY_MULTIPLIERS.get(info["fidelity"], 0.5)
        total_cap += asset_base * (median_gap / 100.0) * mult
```

## Per-Story Output Fields

- `rci` — Relative Capital Intensity (float, 8 decimal places)
- `dominance_ratio` — capital_at_stake / segment_cap (float, 8 decimal places)
- `segment_cap_usd` — denominator in USD (int)

## Narrative Alpha Section (in stories.json)

```json
"narrative_alpha": {
  "dollar_decline": {
    "total_capital_usd": 46665576000,
    "segment": "us_m2_usd",
    "segment_cap_usd": 22800000000000,
    "dominance_ratio": 0.002047,
    "flow_saturated": false
  }
}
```

## Live Results (June 21, 2026 — median-per-base, corrected)

| Narrative | Total Capital | Segment | Dominance | Saturated |
|-----------|--------------|---------|-----------|-----------|
| dollar_decline | $46.67B | $22.8T (M2) | 0.20% | No |
| rate_cycle | $9.61B | $22.8T (M2) | 0.04% | No |
| commodity_supercycle | $9.35B | $100T (Equities) | 0.01% | No |
| crypto_reserve | $5.14B | $2.3T (Crypto) | 0.22% | No |
| gene_editing | $0.02B | $100T (Equities) | <0.01% | No |
| ... | | | | |

No narrative triggers the 15% saturation threshold. Dominance ratios dropped ~26x after removing double-counting (e.g., dollar_decline: 5.37% → 0.20%).

## Cron

```
0 3 * * 6 /opt/gazzetta-di-kyiv/venv/bin/python /opt/gazzetta-di-kyiv/scripts/fetch_macro_baselines.py >> /opt/gazzetta-di-kyiv/logs/macro_baselines_cron.log 2>&1
```

Runs weekly Saturday 03:00 UTC. Fetches live crypto total market cap from CoinGecko free API (`/api/v3/global`). Falls back to last-known value on API failure.
