#!/usr/bin/env python3
import json, os, urllib.request
from datetime import datetime, timezone

cfg = os.path.expanduser('~/.hermes/data/social_umbrella/sources.json')
os.makedirs(os.path.dirname(cfg), exist_ok=True)
if os.path.exists(cfg):
    with open(cfg) as f: data=json.load(f)
else:
    data={'sources':[]}

existing={s.get('id'):s for s in data.get('sources',[])}

def add(src):
    existing[src['id']]=src

# Hedge-fund style tactical short-term signal mix
seed=[
 {'id':'reddit_worldnews','type':'reddit_json','enabled':True,'category':'geopolitics','url':'https://www.reddit.com/r/worldnews/new.json?limit=100'},
 {'id':'reddit_stocks','type':'reddit_json','enabled':True,'category':'markets','url':'https://www.reddit.com/r/stocks/new.json?limit=100'},
 {'id':'reddit_economics','type':'reddit_json','enabled':True,'category':'macro','url':'https://www.reddit.com/r/economics/new.json?limit=100'},
 {'id':'reuters_world','type':'rss','enabled':True,'category':'geopolitics','url':'https://feeds.reuters.com/Reuters/worldNews'},
 {'id':'bloomberg_markets','type':'rss','enabled':True,'category':'markets','url':'https://feeds.bloomberg.com/markets/news.rss'},
 {'id':'ft_world','type':'rss','enabled':True,'category':'macro','url':'https://www.ft.com/world?format=rss'},
 {'id':'guardian_world','type':'rss','enabled':True,'category':'geopolitics','url':'https://www.theguardian.com/world/rss'},
 {'id':'hn_front','type':'rss','enabled':True,'category':'tech','url':'https://hnrss.org/frontpage'},
]
for s in seed: add(s)

# validate urls lightly
ok=[]; bad=[]
ua={'User-Agent':'Mozilla/5.0 HermesSourceUpdater/1.0'}
for s in existing.values():
    try:
        req=urllib.request.Request(s['url'], headers=ua)
        with urllib.request.urlopen(req, timeout=20) as r:
            code=getattr(r,'status',200)
        s['last_validation_status']=int(code)
        s['last_validated_at']=datetime.now(timezone.utc).isoformat()
        ok.append(s['id'])
    except Exception as e:
        s['last_validation_status']='error'
        s['last_validation_error']=str(e)[:180]
        s['last_validated_at']=datetime.now(timezone.utc).isoformat()
        bad.append(s['id'])

out={'updated_at':datetime.now(timezone.utc).isoformat(),'sources':sorted(existing.values(), key=lambda x:x['id'])}
with open(cfg,'w') as f: json.dump(out,f,indent=2)
print(json.dumps({'updated_sources':len(out['sources']),'validated_ok':len(ok),'validated_bad':len(bad),'bad':bad}))