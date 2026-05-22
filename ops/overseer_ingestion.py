#!/usr/bin/env python3
import json, datetime, pathlib
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
D=ROOT/'data'; S=pathlib.Path('/Users/alexstocchi/.hermes/data/social_umbrella')
out=D/'overseer_ingestion.json'
now=datetime.datetime.now(datetime.timezone.utc)
checks={
 'events_ndjson_exists': (S/'events.ndjson').exists(),
 'events_db_exists': (S/'events.db').exists(),
 'sources_exists': (S/'sources.json').exists(),
}
fresh=False
if (S/'events.ndjson').exists():
 fresh=(now-(datetime.datetime.fromtimestamp((S/'events.ndjson').stat().st_mtime, tz=datetime.timezone.utc))).total_seconds()<6*3600
checks['events_fresh_6h']=fresh
score=sum(25 for v in checks.values() if v)
state='running' if score>=75 else 'degraded'
obj={'group':'ingestion','generated_at':now.isoformat(),'state':state,'score':score,'checks':checks,'blockers':[] if state=='running' else ['collector stale or missing'],'root_cause_hypothesis':'schedule drift or collector failure' if state!='running' else '', 'fix_plan':'run collector + validate sources schema', 'eta':'next run < 8h'}
out.write_text(json.dumps(obj,indent=2))
print(json.dumps({'ok':True,'file':str(out),'score':score}))