# db_to_json.py — Authoritative Flows Source (v25.0, June 2026)

## Two Generators, One Output File

Gazzetta has TWO independent flows.json generators that write to the same file:

| Generator | Source | Output | Flow Count | Cron? |
|-----------|--------|--------|-----------|-------|
| `scripts/db_to_json.py` | `gazzetta.db` (SQLite) | `site/data/flows.json` | 80-85 | ✅ Yes |
| `scripts/generate_flows.py` | `data/stories.json` | `site/data/flows.json` | 12-20 | Separate |

**`db_to_json.py` is authoritative.** It reads directly from the SQLite
database and outputs the full flow set. The cron pipeline runs it.

## The Overwrite Hazard

Running `generate_flows.py` standalone overwrites `site/data/flows.json`
with a 12-flow file. If deployed, the site goes from 84 flows → 12.

**How this was discovered (June 2026):** I ran `generate_flows.py` to fix
"neutral" directions, got "✅ Generated 12 flows", and nearly deployed.
Only caught it because the flow count looked wrong.

## Recovery
```bash
cd ~/projects/gazzetta-di-kyiv
python3 scripts/db_to_json.py   # regenerates from DB
# Verify: python3 -c "import json; print(len(json.load(open('site/data/flows.json'))['flows']))"
# Must show 80+ flows
```

## "neutral" Direction Fix

`db_to_json.py` loads flow JSON from `gazzetta.db`'s `flows` table.
The DB stores raw direction strings from `fetch_intel.py`'s `detect_direction()`,
which returns "neutral" when no bullish/bearish keywords match.

The fix (line 258-260 in `db_to_json.py`):
```python
def _normalize_direction(text):
    if not text: return "inflow"
    r = str(text).lower()
    if any(kw in r for kw in ['inflow','into','buy','long','accumulat','overweight','add']):
        return "inflow"
    if any(kw in r for kw in ['outflow','out of','sell','short','distribut','underweight','trim','reduce','exit']):
        return "outflow"
    return "inflow"  # neutral → inflow (capital-first bias)

# In compile_flows():
flow["direction"] = _normalize_direction(flow.get("direction", ""))
```

## Verification
```bash
curl -sk https://www.lagazzettadikyiv.com/data/flows.json | python3 -c "
import json,sys;d=json.load(sys.stdin)
bad=sum(1 for f in d['flows'] if f['direction'] not in ('inflow','outflow'))
print(f'{bad} bad dirs (must be 0)')
print(f'{len(d[\"flows\"])} total flows (must be > 50)')
"
```
