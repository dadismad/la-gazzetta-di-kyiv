#!/usr/bin/env python3
import json, datetime, pathlib
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
D=ROOT/'data'; W=ROOT/'.github/workflows/refresh-and-deploy.yml'; IDX=ROOT/'site/index.html'
out=D/'overseer_publishing.json'
checks={'workflow_exists':W.exists(),'site_index_exists':IDX.exists(),'retail_home_guard':('intensity' not in IDX.read_text(errors='ignore').lower() if IDX.exists() else False)}
score=sum(34 if k!='retail_home_guard' else 32 for k,v in checks.items() if v)
state='running' if score>=80 else 'degraded'
obj={'group':'publishing','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':state,'score':score,'checks':checks,'blockers':[] if state=='running' else ['publish pipeline risk'],'root_cause_hypothesis':'workflow drift or homepage regression','fix_plan':'validate workflow + redeploy + smoke check','eta':'next run < 8h'}
out.write_text(json.dumps(obj,indent=2))
print(json.dumps({'ok':True,'file':str(out),'score':score}))