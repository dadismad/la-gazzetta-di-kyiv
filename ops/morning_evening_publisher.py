#!/usr/bin/env python3
import subprocess, json, datetime, pathlib
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
steps=[
 'python3 ops/representation_curator.py',
 'python3 ops/newsletter_builder.py',
 'python3 ops/brandbook_enforcer.py',
 'python3 ops/ui_contract_check.py',
 'python3 ops/claims_container_guard.py',
 'python3 ops/ceo_upgrade_executor.py'
]
res=[]; ok=True
for s in steps:
 p=subprocess.run(s,shell=True,capture_output=True,text=True,cwd=ROOT)
 res.append({'cmd':s,'code':p.returncode,'out':p.stdout[-300:],'err':p.stderr[-300:]})
 ok=ok and p.returncode==0
out={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ok':ok,'steps':res}
(ROOT/'data'/'morning_evening_run.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'ok':ok}))