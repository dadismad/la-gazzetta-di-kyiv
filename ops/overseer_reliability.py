#!/usr/bin/env python3
import json, datetime, pathlib
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
D=ROOT/'data'; out=D/'overseer_reliability.json'
files=['overseer_ingestion.json','overseer_analysis.json','overseer_publishing.json','overseer_governance.json','overseer_design.json']
checks={f:(D/f).exists() for f in files}
score=round(100*sum(checks.values())/len(files),1)
state='running' if score>=80 else 'degraded'
obj={'group':'reliability','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':state,'score':score,'checks':checks,'blockers':[] if state=='running' else ['one or more overseers missing'],'root_cause_hypothesis':'oversight chain incomplete','fix_plan':'execute missing overseers and refresh status','eta':'next run < 8h'}
out.write_text(json.dumps(obj,indent=2)); print(json.dumps({'ok':True,'file':str(out),'score':score}))