#!/usr/bin/env python3
import json, datetime, pathlib
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
D=ROOT/'data'
out=D/'overseer_analysis.json'
now=datetime.datetime.now(datetime.timezone.utc)
files=['narratives.json','pipeline_audit.json','representation_techniques.json']
checks={f:(D/f).exists() for f in files}
fresh=True
for f in files:
 p=D/f
 if p.exists() and (now-datetime.datetime.fromtimestamp(p.stat().st_mtime,tz=datetime.timezone.utc)).total_seconds()>24*3600:
  fresh=False
checks['fresh_24h']=fresh
score=sum(25 for v in checks.values() if v)
state='running' if score>=75 else 'degraded'
obj={'group':'analysis','generated_at':now.isoformat(),'state':state,'score':score,'checks':checks,'blockers':[] if state=='running' else ['analysis artifacts stale/missing'],'root_cause_hypothesis':'build_site or audit script not executed','fix_plan':'run phase2 publish and rebuild artifacts','eta':'next run < 8h'}
out.write_text(json.dumps(obj,indent=2))
print(json.dumps({'ok':True,'file':str(out),'score':score}))