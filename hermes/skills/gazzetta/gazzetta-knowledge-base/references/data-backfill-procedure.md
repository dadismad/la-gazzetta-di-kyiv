# Data Backfill Procedure — Pace & Confidence

When stories.json shows flat values (all 1.0 pace, all 50% confidence), run these
backfills instead of re-running the full pipeline (which would wipe hand-edited data).

## Pace Backfill

Uses `backfill_pace.py` which derives pace from story content fields:
- Horizon base (1-6h → 3.0, structural → 0.8)
- Urgency keywords in headline/thesis (breaking, crash, surge, etc.)
- Contradiction score multiplier
- Asset class velocity (crypto 1.3, equities 0.95, etc.)

```bash
cd ~/projects/gazzetta-di-kyiv
python3 scripts/backfill_pace.py
```

Only updates stories where `pace_multiplier == 1.0` and derived pace ≠ 1.0.

## Confidence Backfill

Uses `compute_confidence()` from `generate_flows.py` — a 5-factor model:
- Amount (log-scale, 0-25 points)
- Pace (1.0-3.0+, 0-20 points)
- Positioning (accumulating/distributing/hedging, 5-15 points)
- Contradiction bonus (0-15 points)
- Source quality (tier1/tier2/tier3, 3-10 points)
- Base: 25 points. Range: 25-100.

```python
cd ~/projects/gazzetta-di-kyiv
python3 << 'PYEOF'
import json, sys
sys.path.insert(0, 'scripts')
from generate_flows import compute_confidence

d = json.load(open('data/stories.json'))
stories = d.get('stories', [])
updated = 0

for s in stories:
    cf = s.get('capital_flow', {})
    old_conf = cf.get('confidence_pct', 50)
    if old_conf == 50:
        amount_b = cf.get('amount_b', 0) or 0
        pace_mult = cf.get('pace_multiplier', 1.0) or 1.0
        direction = cf.get('direction', 'inflow')
        positioning = "accumulating" if direction == 'inflow' else \
                      "distributing" if direction == 'outflow' else "hedging"
        cs = s.get('contradiction_score', 0) or 0
        contr_bonus = min(15, max(0, (cs - 40) // 4))
        source = s.get('source', '')
        
        new_conf, level, trace = compute_confidence(
            amount_b, pace_mult, positioning, contr_bonus, source)
        cf['confidence_pct'] = new_conf
        cf['confidence_level'] = level
        cf['confidence_trace'] = trace
        updated += 1

json.dump(d, open('data/stories.json', 'w'), indent=2, ensure_ascii=False)
print(f'Updated {updated} stories')
PYEOF
```

## Post-Backfill Deploy

CRITICAL: Do NOT run `shipit.sh` after backfill — its `db_to_json` stage reads from
`gazzetta.db` and overwrites `data/stories.json` with the old values.

Instead, deploy directly:

```bash
cp data/stories.json site/data/
gsutil -m rsync -d -r site/ gs://www.lagazzettadikyiv.com/
gsutil -m setmeta -h "Cache-Control:no-store, must-revalidate" \
  gs://www.lagazzettadikyiv.com/index.html \
  gs://www.lagazzettadikyiv.com/stories.html
gsutil setmeta -h "Cache-Control:private, no-store" \
  "gs://www.lagazzettadikyiv.com/data/**.json"
```

## Verification

After deploy, verify the live data has diverse values:
```bash
curl -s https://www.lagazzettadikyiv.com/data/stories.json | python3 -c "
import json,sys
d=json.load(sys.stdin)
stories=d.get('stories',[])
pces=set(); confs=set()
for s in stories:
    cf=s.get('capital_flow',{})
    pces.add(cf.get('pace_multiplier','?'))
    confs.add(cf.get('confidence_pct','?'))
print(f'{len(stories)} stories, {len(pces)} unique paces, {len(confs)} unique confidences')
"
```

Target: >5 unique pace values, >8 unique confidence values (not just 50/65/75).
