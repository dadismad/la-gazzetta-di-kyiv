#!/usr/bin/env python3
import subprocess, json, datetime, pathlib
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
ENV=pathlib.Path('/Users/alexstocchi/.hermes/.env')

def sh(cmd):
    p=subprocess.run(cmd,shell=True,cwd=ROOT,capture_output=True,text=True)
    return {'cmd':cmd,'code':p.returncode,'out':p.stdout[-1200:],'err':p.stderr[-1200:]}

def token():
    for l in ENV.read_text().splitlines():
        if l.startswith('GITHUB_TOKEN='): return l.split('=',1)[1].strip()
    return ''

steps=[]
for c in [
 'python3 ops/representation_curator.py',
 'python3 ops/channel_bundle_builder.py',
 'python3 ops/newsletter_builder.py',
 'python3 ops/brandbook_enforcer.py',
 'python3 ops/ui_contract_check.py',
 'python3 ops/claims_container_guard.py',
 'python3 ops/pages_watchdog_v2.py']:
    steps.append(sh(c))

ok = all(s['code']==0 for s in steps)

tok=token()
if ok and tok:
    remote=f"https://x-access-token:{tok}@github.com/pureciclismo/gazzetta-di-kyiv.git"
    steps.append(sh("git add -A"))
    steps.append(sh("git commit -m 'chore(auto): autonomous site content/gates refresh' || true"))
    steps.append(sh(f"git pull --rebase '{remote}' main"))
    steps.append(sh(f"git push '{remote}' main"))
    steps.append(sh("python3 ops/trigger_pages_redeploy.py"))

status={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ok':ok,'steps':steps}
(ROOT/'data'/'autonomous_site_update_status.json').write_text(json.dumps(status,indent=2))
print(json.dumps({'ok':ok}))