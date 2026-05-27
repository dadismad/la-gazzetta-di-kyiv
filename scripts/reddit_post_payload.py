#!/usr/bin/env python3
import json, os, time
SCORES='data/phase2_scores.json'
DRAFTS='data/reddit_gazzetta_drafts.json'
OUT='data/reddit_post_payload.md'

if not os.path.exists(SCORES):
    raise SystemExit('missing data/phase2_scores.json')
if not os.path.exists(DRAFTS):
    raise SystemExit('missing data/reddit_gazzetta_drafts.json')

with open(SCORES,'r',encoding='utf-8') as f: s=json.load(f)
with open(DRAFTS,'r',encoding='utf-8') as f: d=json.load(f)

best=(s.get('top') or [{}])[0]
draft=(d.get('items') or [{}])[0]

actors=', '.join((draft.get('actors') or ['Market participants','Policy actors'])[:2])
prob=(draft.get('bet_snippet_24_72h') or {}).get('probability_pct', 58)
inv=(draft.get('bet_snippet_24_72h') or {}).get('invalidation', 'Narrative engagement collapses and cross-asset confirmation fails.')
inst=(draft.get('bet_snippet_24_72h') or {}).get('instrument','NASDAQ-100 proxy')
dirn=(draft.get('bet_snippet_24_72h') or {}).get('direction','two-way / selective risk-on')

lines=[]
lines.append('## La Gazzetta di Kyiv — Capital Flow Brief')
lines.append('')
lines.append(f'**Regime:** {best.get("regime","mixed")} | **Lead sector:** {best.get("sector","Broad Risk Basket")}')
lines.append(f'**Actors in play:** {actors}')
lines.append('')
lines.append(f'**Claim:** attention is converting into incremental allocation toward {best.get("sector","lead sectors")}, with spillover into related risk assets.')
lines.append('**Contradiction:** price optimism is rising faster than fundamental clarity; if narrative velocity stalls, positioning can unwind quickly.')
lines.append(f'**24–72h path ({prob}%):** {inst} -> {dirn}.')
lines.append(f'**Invalidation:** {inv}')
lines.append('')
lines.append('Evidence:')
lines.append('- https://pureciclismo.github.io/gazzetta-di-kyiv/')
lines.append('- https://pureciclismo.github.io/gazzetta-di-kyiv/data.html')
lines.append('')
lines.append('READY_FOR_DEVVIT_POST')

os.makedirs('data',exist_ok=True)
with open(OUT,'w',encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(json.dumps({'ok':True,'output':OUT,'generated_at':int(time.time())}))