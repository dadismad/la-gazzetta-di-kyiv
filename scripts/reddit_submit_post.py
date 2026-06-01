#!/usr/bin/env python3
"""Submit generated payload to subreddit via Reddit OAuth API (unattended bridge)."""
from __future__ import annotations
import base64, json, os, urllib.parse, urllib.request

TOKEN_URL='https://www.reddit.com/api/v1/access_token'
POST_URL='https://oauth.reddit.com/api/submit'
PAYLOAD=os.getenv('REDDIT_POST_PAYLOAD','data/reddit_post_payload.md')
LOCK='data/.last_reddit_payload_hash'

def env(k:str)->str:
    v=os.getenv(k,'').strip()
    if not v: raise RuntimeError(f'Missing env var: {k}')
    return v

def token()->str:
    cid=env('REDDIT_CLIENT_ID'); sec=env('REDDIT_CLIENT_SECRET')
    usr=env('REDDIT_USERNAME'); pwd=env('REDDIT_PASSWORD'); ua=env('REDDIT_USER_AGENT')
    basic=base64.b64encode(f'{cid}:{sec}'.encode()).decode()
    body=urllib.parse.urlencode({'grant_type':'password','username':usr,'password':pwd}).encode()
    req=urllib.request.Request(TOKEN_URL,data=body,headers={'Authorization':f'Basic {basic}','User-Agent':ua,'Content-Type':'application/x-www-form-urlencoded'},method='POST')
    with urllib.request.urlopen(req, timeout=30) as r: j=json.loads(r.read().decode())
    if 'access_token' not in j: raise RuntimeError(f'token missing: {j}')
    return j['access_token']

def content_hash(s:str)->str:
    import hashlib
    return hashlib.sha256(s.encode()).hexdigest()

if __name__=='__main__':
    sub=os.getenv('REDDIT_TARGET_SUBREDDIT','lagazzettadikyiv')
    if not os.path.exists(PAYLOAD): raise SystemExit(f'missing {PAYLOAD}')
    text=open(PAYLOAD,encoding='utf-8').read().strip()
    h=content_hash(text)
    last=open(LOCK).read().strip() if os.path.exists(LOCK) else ''
    if h==last:
        print(json.dumps({'ok':True,'skipped':'duplicate_payload_hash'})); raise SystemExit(0)
    lines=[x.strip() for x in text.splitlines() if x.strip()]
    title=next((l for l in lines if not l.startswith('#') and not l.startswith('**') and 'READY_FOR_DEVVIT_POST' not in l), 'La Gazzetta di Kyiv — Capital Flow Brief')
    title=title[:290]
    required=['REDDIT_CLIENT_ID','REDDIT_CLIENT_SECRET','REDDIT_USERNAME','REDDIT_PASSWORD','REDDIT_USER_AGENT']
    missing=[k for k in required if not os.getenv(k,'').strip()]
    if missing:
        print(json.dumps({'ok':False,'skipped':'missing_credentials','missing':missing,'payload_ready':PAYLOAD}))
        raise SystemExit(0)
    tok=token(); ua=env('REDDIT_USER_AGENT')
    body=urllib.parse.urlencode({'sr':sub,'kind':'self','title':title,'text':text,'resubmit':'true'}).encode()
    req=urllib.request.Request(POST_URL,data=body,headers={'Authorization':f'bearer {tok}','User-Agent':ua,'Content-Type':'application/x-www-form-urlencoded'},method='POST')
    with urllib.request.urlopen(req, timeout=30) as r: resp=json.loads(r.read().decode())
    errs=((resp.get('json') or {}).get('errors') or [])
    if errs: raise RuntimeError(f'reddit submit errors: {errs}')
    with open(LOCK,'w',encoding='utf-8') as f: f.write(h)
    print(json.dumps({'ok':True,'subreddit':sub,'title':title}))
