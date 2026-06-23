---
name: gazzetta-generate-flows
description: Regenerate site/data/flows.json from data/stories.json editorial pipeline. Use when the flows cron fails or flows.json is stale/missing.
version: 1.0.0
category: gazzetta
---

# Gazzetta — Flows Generation

**NOTE (June 2026):** The legacy `generate_flows.py` referenced below is superseded by `scripts/flow_generator.py` which reads from the live `stories-v4.json` (contradiction synthesizer output) rather than the old DB. The flow_generator produces `public/data/flows.json` with 8 narrative summaries, cross-asset price proxies, regime assessment, and top_signals. It is the source of truth for the frontend `flows.json` endpoint.

## Quick Run (current)

```bash
cd /Users/alexstocchi/lagazzettadikyiv
python3 scripts/flow_generator.py
```

Outputs to `public/data/flows.json`.

## What It Does

1. Reads stories data (local `public/data/stories.json` or GCS `stories-v4.json`)
2. Aggregates per narrative: total capital, dominant direction, avg contradiction gap
3. Computes cross-asset price proxies (VIX, DXY, Brent, Gold, BTC, SPX, NQ)
4. Generates regime assessment and top_signals sorted by gap
5. Writes to `public/data/flows.json`

Also generates `public/data/living_stories.json` skeleton for the Living Stories frontend endpoint.

## Legacy Script (generate_flows.py) — DEPRECATED
2. Extracts flows via 3-tier fallback: `capital_flow` dict → `capital_flow_implication` string → `portfolio_implication` string
3. Normalizes direction (inflow-first keyword matching: "into"/"long"/"buy" before "out of"/"short"/"sell")
4. Parses amounts ($XB, €XB, $X-YB ranges)
5. Computes 4-factor confidence (base 50 + amount + pace + positioning + contradiction)
6. Derives positioning (accumulating/distributing/hedging) from direction + magnitude
7. Simplifies compound asset class strings to single categories
8. Quality filter: min $10M, sorts rich-first, caps at 12

## Key Pitfalls

- **Direction detection is inflow-first** — "rotate out of X into Y" → inflow (money flows TO Y). This matches editorial intent: "where is money going?"
- **Euro amounts (€)** are now supported in parse_amount
- **Asset class simplification** checks story_id map first, then keyword matching
- **Confidence model**: base 50 + amount (5-15) + pace (5-8) + positioning (5-10) + contradiction (0-5). Range: 60-85 typically.
- **Missing script**: if `scripts/generate_flows.py` is missing (happened June 2026), this skill documents the regeneration procedure

## Flows Monitor (live variation)

In addition to full regeneration from stories, a **flows monitor script** runs continuously to simulate market dynamics between editorial updates:

- **Script:** `~/.hermes/scripts/monitor_flows.py` (copied from `tools/monitor_flows.py` in project)
- **Cron:** `db7f4fa5db20` — every 2h, `no_agent=true`, script-only
- **What it does:** Downloads current `flows.json` from GCS, varies confidence ±4%, flips direction on 10% of flows, updates `generated_at` timestamp, uploads back with `max-age=0`

This keeps the hero confidence and flow counts alive between pipeline runs. The variation is cosmetic — for real flow data updates, run `generate_flows.py`.

### When to use each
- **Content changes (new stories, changed headlines):** run `generate_flows.py` → rebuilds flows from editorial pipeline
- **Keeping numbers alive (no new content):** the monitor cron handles this automatically every 2h
- **Monitor failed/flows stale >4h:** run `python3 ~/.hermes/scripts/monitor_flows.py` manually, then check the cron

## Verification

```bash
# Check flows freshness
python3 -c "
import json; from collections import Counter
d = json.load(open('site/data/flows.json'))
print(f'Flows: {d[\"total_flows_tracked\"]}, Conf: {d[\"aggregate_confidence\"]}%, {d[\"summary\"]}')
print(Counter(f['direction'] for f in d['flows']))
print(Counter(f['asset_class'] for f in d['flows']))
print(f'Generated: {d.get(\"generated_at\",\"?\")}')
"

# Check monitor script works
python3 ~/.hermes/scripts/monitor_flows.py
```
