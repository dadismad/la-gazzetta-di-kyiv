#!/usr/bin/env python3
import json, os, time
SRC='data/phase2_scores.json'
OUT='data/phase3_daily_brief.md'
if not os.path.exists(SRC):
    print(json.dumps({'ok':False,'error':f'missing {SRC}'})); raise SystemExit(1)
with open(SRC,'r',encoding='utf-8') as f: d=json.load(f)
items=d.get('top',[])[:5]
lines=["## Where Capital Goes — Daily Brief", ""]
for i,x in enumerate(items,1):
    lines.append(f"{i}. **{x.get('sector','n/a')}** — {x.get('title','n/a')}")
    lines.append(f"   - Captivation: {x.get('captivation_score')} | Flow: {x.get('capital_flow_score')} | Beneficiary: {x.get('beneficiary_score')}")
    lines.append(f"   - Regime: {x.get('regime','n/a')} | Link: {x.get('links',[None])[0]}")
    lines.append("")
lines.append(f"Generated at: {int(time.time())}")
text='\n'.join(lines)
os.makedirs('data',exist_ok=True)
with open(OUT,'w',encoding='utf-8') as f: f.write(text)
print(json.dumps({'ok':True,'output':OUT,'count':len(items)}))
