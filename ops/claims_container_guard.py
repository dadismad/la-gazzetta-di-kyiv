#!/usr/bin/env python3
import json, pathlib, datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
site_data=ROOT/'site/data/narratives.json'
app=ROOT/'site/app.js'
issues=[]
count=0
if not site_data.exists():
    issues.append('missing site/data/narratives.json')
else:
    obj=json.loads(site_data.read_text())
    count=len(obj.get('narrative_reviews',[]))
    if count==0:
        issues.append('narrative_reviews empty')
js=app.read_text(errors='ignore') if app.exists() else ''
if 'No active claims yet' not in js:
    issues.append('missing empty-state fallback in claims container')
out={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ok':len(issues)==0,'narrative_reviews_count':count,'issues':issues}
(ROOT/'data/claims_container_guard.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))