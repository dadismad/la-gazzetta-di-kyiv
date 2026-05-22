#!/usr/bin/env python3
import json, pathlib, datetime, re
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
SITE=ROOT/'site'; DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
css=(SITE/'styles.css').read_text(errors='ignore')
js=(SITE/'app.js').read_text(errors='ignore')
index=(SITE/'index.html').read_text(errors='ignore')
issues=[]
for token in ['#F7FAFF','#3E6FAE','#10233F','#6BB6FF']:
    if token.lower() not in css.lower(): issues.append(f'missing palette {token}')
if 'flow 3d' not in js.lower(): issues.append('missing 3-day flow metric')
if 'projection 3d' not in js.lower(): issues.append('missing 3-day projection metric')
if 'focus' not in index.lower(): issues.append('missing narrative focus section')
# simple repetition guard (avoid left-right verbatim duplication markers)
if "${x.sentence}" in js and "focus-title" in js:
    issues.append('potential repeated focus headline binding')
ok=len(issues)==0
out={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ok':ok,'issues':issues}
(DATA/'brandbook_enforcement.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))