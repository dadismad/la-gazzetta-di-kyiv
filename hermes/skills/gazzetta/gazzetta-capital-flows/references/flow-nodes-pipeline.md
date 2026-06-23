# Flow Nodes Pipeline — Data Model & Pitfalls

## Pipeline Architecture

```
data/stories.json (source of truth — 19 stories with capital_flow dicts)
        │
        ▼
scripts/generate_flow_nodes.py  ← reads DATA_SOURCE, NOT site/data/stories.json
        │                          parse_amount_from_cf() handles 3-tier fallback
        ▼
site/data/flow_nodes.json       ← output (nodes + edges)
        │
        ▼
deploy_to_gcs.sh                ← Tier 3: private, no-store
        │
        ▼
flow-nodes.html                 ← SVG visualization (13 nodes, 19 edges)
```

## Amount Parsing — 3-Tier Fallback (MANDATORY)

19/19 stories have `capital_flow.amount` set to `NONE`. The `claim` field contains real amounts (e.g., "$80.0B ↑ equities", "$11.5B ↓ crypto"). Any script that reads `capital_flow` dicts directly MUST implement:

```python
def parse_amount_from_cf(cf):
    # Tier 1: amount field
    amt_b = parse_amount(cf.get("amount", ""))
    if amt_b > 0: return amt_b
    
    # Tier 2: claim text ("$80.0B ↑ equities")
    claim = cf.get("claim", "")
    amt_b = parse_amount(claim)
    if amt_b > 0: return amt_b
    
    # Tier 3: amount_b field (hardcoded fallback, often 5.0)
    return cf.get("amount_b", 0)
```

Without this fallback, every flow returns amount=0 and is filtered out by the `amount_b < 0.1` quality gate.

## Schema Mismatch — metadata vs summary (v22.26)

The `flow-nodes.html` page destructures data as:
```javascript
const { nodes, edges, metadata, node_types } = data;
```

But `generate_flow_nodes.py` outputs `summary` not `metadata`. This causes `metadata` to be `undefined`, crashing the SVG render with:
```
Cannot read properties of undefined (reading 'total_flow_tracked_b')
```

**Fix:** Always use fallback destructuring:
```javascript
const { nodes, edges, metadata, node_types, summary } = data;
const meta = metadata || summary || {};
```
Then reference `meta.total_flow_b`, `meta.total_nodes`, etc.

## Node Type Mapping

Asset classes → node types for source/destination assignment:

| Asset Class | Node Type |
|-------------|-----------|
| equities | institutional |
| crypto | crypto |
| commodities | corporate |
| bonds | gov |
| tech | corporate |
| gold | retail |
| defense | gov |
| energy | corporate |
| forex | gov |

## Confidence Model

4-factor model (matching generate_flows.py):
- Amount: +5 (micro) to +15 (≥$5B)
- Pace: +5 (normal) to +8 (≥3x)
- Base: 50
- Cap: 100

## Edge Direction Logic

- inflow → source=institutional, target=asset_class node
- outflow → source=asset_class node, target=gov (money flees to safety)
