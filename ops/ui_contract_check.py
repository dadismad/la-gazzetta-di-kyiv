#!/usr/bin/env python3
import re, json, pathlib, datetime
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
css=(ROOT/'site/styles.css').read_text(errors='ignore')
js=(ROOT/'site/app.js').read_text(errors='ignore')
issues=[]
if 'font-size:10px!important' not in css: issues.append('font cap not enforced')
for token in ['#F7FAFF','#3E6FAE','#10233F','#6BB6FF']:
    if token.lower() not in css.lower(): issues.append(f'missing palette token {token}')
if "focus-copy'>${x.context}" in js or "focus-title'>${x.sentence}" in js:
    issues.append('focus repeats left content')
ok= len(issues)==0
out={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ok':ok,'issues':issues}
(ROOT/'data/ui_contract_check.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))