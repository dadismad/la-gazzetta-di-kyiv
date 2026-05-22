#!/usr/bin/env python3
import os, json, sqlite3
from datetime import datetime, timezone, timedelta

base=os.path.expanduser('~/.hermes/data/social_umbrella')
db=os.path.join(base,'events.db')
out=os.path.join(base,'pipeline_audit.json')
report=[]

if not os.path.exists(db):
    payload={'generated_at':datetime.now(timezone.utc).isoformat(),'status':'error','message':'events.db missing'}
    open(out,'w').write(json.dumps(payload,indent=2)); print(json.dumps(payload)); raise SystemExit(0)

con=sqlite3.connect(db); cur=con.cursor()
cur.execute('select count(*) from events'); total=cur.fetchone()[0]
cur.execute('select max(collected_at) from events'); last=cur.fetchone()[0]
cur.execute('select platform,count(*) from events group by platform'); byp=cur.fetchall()
con.close()

payload={
 'generated_at':datetime.now(timezone.utc).isoformat(),
 'status':'ok',
 'total_events':total,
 'last_collected_at':last,
 'by_platform':[{ 'platform':p, 'count':c } for p,c in byp],
 'recommended_upgrades':[
   'Add source-level decay weighting for stale feeds',
   'Add language detection and dedup by semantic similarity',
   'Add rolling z-score for narrative spikes (24h vs 7d baseline)',
   'Add confidence calibration from cross-source confirmation'
 ]
}
open(out,'w').write(json.dumps(payload,indent=2))
print(json.dumps(payload))