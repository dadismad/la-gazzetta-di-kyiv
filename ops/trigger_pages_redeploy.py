#!/usr/bin/env python3
import os, json, urllib.request
from pathlib import Path

token=''
for l in Path('/Users/alexstocchi/.hermes/.env').read_text().splitlines():
    if l.startswith('GITHUB_TOKEN='):
        token=l.split('=',1)[1].strip(); break
if not token:
    print(json.dumps({'ok':False,'error':'no token'})); raise SystemExit(1)

url='https://api.github.com/repos/pureciclismo/gazzetta-di-kyiv/actions/workflows/refresh-and-deploy.yml/dispatches'
req=urllib.request.Request(url, data=b'{"ref":"main"}', method='POST')
req.add_header('Authorization', f'Bearer {token}')
req.add_header('Accept','application/vnd.github+json')
req.add_header('Content-Type','application/json')
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        print(json.dumps({'ok':True,'status':r.status}))
except Exception as e:
    print(json.dumps({'ok':False,'error':str(e)}))
    raise