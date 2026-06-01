#!/usr/bin/env python3
import json, os, time
SRC='data/phase2_scores.json'
OUT='data/phase4_sector_history.json'
if not os.path.exists(SRC):
    print(json.dumps({'ok':False,'error':f'missing {SRC}'})); raise SystemExit(1)
with open(SRC,'r',encoding='utf-8') as f: d=json.load(f)
sectors={}
for x in d.get('top',[]):
    s=x.get('sector','Unknown')
    sectors.setdefault(s, {'count':0,'avg_beneficiary':0,'avg_flow':0})
    sectors[s]['count']+=1
    sectors[s]['avg_beneficiary']+=x.get('beneficiary_score',0)
    sectors[s]['avg_flow']+=x.get('capital_flow_score',0)
rows=[]
for s,v in sectors.items():
    c=max(1,v['count'])
    rows.append({'sector':s,'count':v['count'],'avg_beneficiary':round(v['avg_beneficiary']/c,1),'avg_flow':round(v['avg_flow']/c,1)})
rows.sort(key=lambda r:(r['avg_beneficiary'],r['avg_flow']), reverse=True)
out={'generated_at':int(time.time()),'rows':rows}
with open(OUT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2)
print(json.dumps({'ok':True,'sectors':len(rows),'output':OUT}))
