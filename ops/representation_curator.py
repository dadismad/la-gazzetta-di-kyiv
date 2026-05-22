#!/usr/bin/env python3
import json, pathlib, datetime
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
SRC=ROOT/'data'/'narratives.json'
OUT=ROOT/'data'/'narratives_curated.json'
if not SRC.exists():
    print('{"ok":false,"error":"narratives.json missing"}')
    raise SystemExit(1)
obj=json.loads(SRC.read_text())
reviews=obj.get('narrative_reviews',[])
seen=set(); curated=[]
for r in reviews:
    topic=(r.get('topic') or 'macro').lower()
    headline=(r.get('headline') or f'{topic.upper()} narrative requires tactical attention.').strip()
    if headline in seen:
        headline=f"{headline} (sector-specific update)"
    seen.add(headline)
    curated.append({
      'topic':topic,
      'headline':headline,
      'review':(r.get('review') or 'Narrative evolving with cross-asset implications.').strip(),
      'actionable': f"For {topic.upper()}: define entry trigger, invalidation level, and 72h monitoring checklist.",
      'flow_3d_billion_usd': r.get('flow_3d_billion_usd', None),
      'projection_3d_pct': r.get('projection_3d_pct', None)
    })
res={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'narratives':curated}
OUT.write_text(json.dumps(res,indent=2))
print(json.dumps({'ok':True,'out':str(OUT),'count':len(curated)}))