#!/usr/bin/env python3
import json, datetime, pathlib, urllib.request, subprocess
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
D=ROOT/'data'; D.mkdir(exist_ok=True)

def get(url):
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            body=r.read().decode('utf-8','ignore')
            return {'ok':200<=r.status<300,'status':r.status,'size':len(body),'body':body[:500]}
    except Exception as e:
        return {'ok':False,'status':0,'error':str(e)}

checks={
 'home':get('https://pureciclismo.github.io/gazzetta-di-kyiv/'),
 'narratives':get('https://pureciclismo.github.io/gazzetta-di-kyiv/data/narratives.json')
}
blocked=[]
if not checks['home']['ok']: blocked.append('homepage_down')
if not checks['narratives']['ok']: blocked.append('narratives_down')

# local quality checks
qa=[]
for cmd in ['python3 ops/ui_contract_check.py','python3 ops/brandbook_enforcer.py','python3 ops/claims_container_guard.py']:
    p=subprocess.run(cmd,shell=True,capture_output=True,text=True,cwd=ROOT)
    qa.append({'cmd':cmd,'code':p.returncode})
    if p.returncode!=0: blocked.append(f'qa_fail:{cmd}')

now=datetime.datetime.now(datetime.timezone.utc).isoformat()
slo={'generated_at':now,'sli':{'home_uptime':1 if checks['home']['ok'] else 0,'data_uptime':1 if checks['narratives']['ok'] else 0},'slo_target':0.99,'status':'pass' if not blocked else 'fail'}
incident={'generated_at':now,'open_incidents':[{'id':'site-availability','severity':'high','cause':','.join(blocked)}] if blocked else []}
canary={'generated_at':now,'checks':checks,'passed':not blocked}
actions=[
 {'owner':'CEO','priority':'P0' if blocked else 'P2','task':'Restore live endpoint + re-verify external URLs','eta':'30m' if blocked else 'monitoring'},
 {'owner':'DataOps','priority':'P1','task':'Maintain narrative freshness and non-empty claims container','eta':'today'},
 {'owner':'DesignOps','priority':'P1','task':'Maintain brandbook/UI contract compliance','eta':'today'}
]
status={'generated_at':now,'state':'blocked' if blocked else 'running','blocked_reasons':blocked,'external_checks':checks,'qa':qa}

(D/'slo_report.json').write_text(json.dumps(slo,indent=2))
(D/'incident_log.json').write_text(json.dumps(incident,indent=2))
(D/'deploy_canary_report.json').write_text(json.dumps(canary,indent=2))
(D/'action_queue.json').write_text(json.dumps(actions,indent=2))
(D/'ceo_status.json').write_text(json.dumps(status,indent=2))
print(json.dumps({'ok':not blocked,'blocked':blocked}))