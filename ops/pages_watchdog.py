#!/usr/bin/env python3
import json, pathlib, datetime, urllib.request, subprocess, ssl
ROOT=pathlib.Path('/Users/alexstocchi/projects/gazzetta-di-kyiv')
D=ROOT/'data'; D.mkdir(exist_ok=True)
STATE=D/'pages_watchdog_state.json'
OUT=D/'pages_watchdog_v2.json'

URLS={
 'main':'https://www.lagazzettadikyiv.com/',
 'data':'https://www.lagazzettadikyiv.com/data/stories.json',
 'backup':'https://www.lagazzettadikyiv.com/'  # safe fallback: canonical HTML endpoint
}

SSL_CTX = ssl._create_unverified_context()

def fetch(u, require_renderable=False):
    try:
        with urllib.request.urlopen(u, timeout=20, context=SSL_CTX) as r:
            ctype = (r.headers.get('Content-Type') or '').lower()
            b=r.read().decode('utf-8','ignore')
            sig = "There isn't a GitHub Pages site here" in b
            render_ok = True
            if require_renderable:
                render_ok = ('text/html' in ctype) and ('app.js' in b)
            return {'ok':200<=r.status<300 and not sig and render_ok,'status':r.status,'sig404':sig,'size':len(b),'content_type':ctype,'render_ok':render_ok}
    except Exception as e:
        return {'ok':False,'status':0,'error':str(e),'sig404':False,'size':0,'content_type':'','render_ok':False}

checks={
 'main':fetch(URLS['main'], require_renderable=True),
 'data':fetch(URLS['data']),
 'backup':fetch(URLS['backup'], require_renderable=True)
}
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
        subprocess.run('bash /Users/alexstocchi/.hermes/scripts/gazzetta_deploy_to_gcs.sh', shell=True, check=False, capture_output=True, text=True)
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
