#!/usr/bin/env python3
"""Fallback generator when reddit source is paused/unavailable."""
import json, os, time
SRC='site/api/v1/home/setups.json'
OUT='data/reddit_candidates.json'
if not os.path.exists(SRC):
    print(json.dumps({'ok':False,'error':f'missing {SRC}'})); raise SystemExit(1)
with open(SRC,'r',encoding='utf-8') as f: data=json.load(f)
items=[]
for i,s in enumerate(data.get('items',[])[:20]):
    items.append({
        'post_id': s.get('setup_id',f'setup_{i}'),
        'title': s.get('title',''),
        'selftext': s.get('thesis',''),
        'url': 'https://pureciclismo.github.io/gazzetta-di-kyiv/',
        'permalink': 'https://pureciclismo.github.io/gazzetta-di-kyiv/data.html',
        'score': int((s.get('confidence',0)*1000)),
        'num_comments': int((s.get('probability_bull',0)+s.get('probability_bear',0))/2),
        'upvote_ratio': min(1.0,max(0.1,s.get('confidence',0))),
        'hook_strength': int(s.get('confidence',0)*100),
        'novelty_score': 40,
        'contradiction_score': 35,
        'actionability_score': 60,
        'credibility_signal': 65,
    })
os.makedirs('data',exist_ok=True)
with open(OUT,'w',encoding='utf-8') as f: json.dump({'generated_at':int(time.time()),'subreddit':'synthetic','items':items},f,indent=2)
print(json.dumps({'ok':True,'count':len(items),'output':OUT,'source':'setups-fallback'}))
