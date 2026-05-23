#!/usr/bin/env python3
import json, pathlib, datetime
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
D=ROOT/'data'; D.mkdir(exist_ok=True)

src=D/'narratives_curated.json'
if not src.exists():
    src=D/'narratives.json'
obj=json.loads(src.read_text()) if src.exists() else {}
items=obj.get('narratives') or obj.get('narrative_reviews') or []

def pick(topic_keys, fallback='macro'):
    for it in items:
        t=(it.get('topic') or '').lower()
        if any(k in t for k in topic_keys):
            return it
    return {'topic':fallback,'headline':'No strong signal yet','review':'Monitoring convergence and flow shifts.','actionable':'Wait for confirmation and preserve risk budget.'}

emerging=pick(['ai','crypto','drone','semiconductor','chip'])
convergence=pick(['energy','oil','rates','inflation','eu','china'])
invest=pick(['election','russia','ukraine','rates','ai'])

pack={
 'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'morning_evening_ready':True,
 'sections':{
   'emerging_tech':emerging,
   'convergence_points':convergence,
   'investment_implications':invest
 }
}
(D/'newsletter_bundle.json').write_text(json.dumps(pack,indent=2))
print(json.dumps({'ok':True,'out':str(D/'newsletter_bundle.json')}))