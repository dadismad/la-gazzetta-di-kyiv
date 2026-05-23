#!/usr/bin/env python3
import json, pathlib, datetime, urllib.request, subprocess
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
D=ROOT/'data'; D.mkdir(exist_ok=True)
STATE=D/'pages_watchdog_state.json'
OUT=D/'pages_watchdog_v2.json'

URLS={
 'main':'https://pureciclismo.github.io/gazzetta-di-kyiv/',
 'data':'https://pureciclismo.github.io/gazzetta-di-kyiv/data/narratives.json',
 'backup':'https://rawcdn.githack.com/pureciclismo/gazzetta-di-kyiv/main/site/index.html'
}

def fetch(u):
    try:
        with urllib.request.urlopen(u, timeout=20) as r:
            b=r.read().decode('utf-8','ignore')
            sig = "There isn't a GitHub Pages site here" in b
            return {'ok':200<=r.status<300 and not sig,'status':r.status,'sig404':sig,'size':len(b)}
    except Exception as e:
        return {'ok':False,'status':0,'error':str(e),'sig404':False,'size':0}

checks={k:fetch(v) for k,v in URLS.items()}
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
state={'fail_streak':0,'last_redeploy_at':None}
if STATE.exists():
    state.update(json.loads(STATE.read_text()))

critical_ok = checks['main']['ok'] and checks['data']['ok']
if critical_ok:
    state['fail_streak']=0
else:
    state['fail_streak']=int(state.get('fail_streak',0))+1

redeployed=False
if state['fail_streak']>=2:  # two consecutive failed probes
    try:
        subprocess.run('python3 ops/trigger_pages_redeploy.py', shell=True, cwd=ROOT, check=False, capture_output=True, text=True)
        redeployed=True
        state['last_redeploy_at']=now
        state['fail_streak']=0
    except Exception:
        pass

status='healthy' if critical_ok else ('degraded' if checks['backup']['ok'] else 'down')
out={
 'generated_at':now,
 'status':status,
 'checks':checks,
 'fail_streak':state['fail_streak'],
 'redeployed':redeployed,
 'canonical_url':URLS['main'],
 'fallback_url':URLS['backup']
}
OUT.write_text(json.dumps(out,indent=2))
STATE.write_text(json.dumps(state,indent=2))
print(json.dumps({'ok':True,'status':status,'redeployed':redeployed}))