#!/usr/bin/env python3
import json, datetime, pathlib, subprocess
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
D=ROOT/'data'; out=D/'overseer_design.json'
p=subprocess.run(['python3','ops/design_compare.py'],cwd=ROOT,capture_output=True,text=True)
checks={'design_compare_exec':p.returncode==0}
score=100 if checks['design_compare_exec'] else 40
state='running' if score>=80 else 'degraded'
obj={'group':'design','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':state,'score':score,'checks':checks,'blockers':[] if state=='running' else ['design comparator failed'],'root_cause_hypothesis':'CSS/HTML drift or script error','fix_plan':'run design_dev_runner and patch UI','eta':'next run < 8h'}
out.write_text(json.dumps(obj,indent=2)); print(json.dumps({'ok':True,'file':str(out),'score':score}))