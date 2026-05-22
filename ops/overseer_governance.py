#!/usr/bin/env python3
import json, datetime, pathlib
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
DOC=ROOT/'docs'; D=ROOT/'data'
out=D/'overseer_governance.json'
checks={'operating_mandate':(DOC/'OPERATING_MANDATE.md').exists(),'variant_prompt':(DOC/'VARIANT_PROMPT.md').exists(),'ceo_status_exists':(D/'ceo_status.json').exists()}
score=sum(34 if i<2 else 32 for i,v in enumerate(checks.values()) if v)
state='running' if score>=80 else 'degraded'
obj={'group':'governance','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':state,'score':score,'checks':checks,'blockers':[] if state=='running' else ['governance docs/status incomplete'],'root_cause_hypothesis':'missing policy artifacts','fix_plan':'restore mandate/prompt and rerun CEO orchestrator','eta':'next run < 24h'}
out.write_text(json.dumps(obj,indent=2))
print(json.dumps({'ok':True,'file':str(out),'score':score}))