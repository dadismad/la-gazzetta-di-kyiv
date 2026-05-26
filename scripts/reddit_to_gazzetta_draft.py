#!/usr/bin/env python3
"""Convert reddit_candidates.json into Gazzetta-ready draft cards."""
from __future__ import annotations
import json, os, time

INP='data/reddit_candidates.json'
OUT='data/reddit_gazzetta_drafts.json'

def choose_direction(item):
    s=item.get('score',0); c=item.get('num_comments',0)
    return 'risk-on continuation' if s>500 and c>50 else 'two-way / fade spikes'

def projection(item):
    hs=item.get('hook_strength',0)
    return '+1.0% to +3.2%' if hs>=40 else '-0.8% to +1.5%'

def convert(item, i):
    title=item.get('title','Untitled signal')
    return {
      'rank': i+1,
      'headline_hook': title,
      'core_claim': 'Narrative momentum and engagement suggest near-term repricing attention.',
      'actors': ['Retail flow','Narrative amplifiers','Cross-platform curators'],
      'contradiction_map': {
        'consensus':'Viral = noise',
        'evidence':'Sustained score + comment depth indicates durable positioning narrative',
        'implication':'Short horizon assets can reprice before fundamentals catch up'
      },
      'bet_snippet_24_72h': {
        'instrument':'NASDAQ-100 proxy',
        'direction': choose_direction(item),
        'probability_pct': min(78, 45 + int(item.get('hook_strength',0)/3)),
        'projection_pct': projection(item),
        'invalidation':'Engagement decay >50% vs first 12h baseline'
      },
      'links':[item.get('url'), item.get('permalink')]
    }

if __name__=='__main__':
    if not os.path.exists(INP):
        print(json.dumps({'ok':False,'error':f'missing {INP}'})); raise SystemExit(1)
    with open(INP,'r',encoding='utf-8') as f: data=json.load(f)
    items=data.get('items',[])[:10]
    out={'generated_at':int(time.time()), 'items':[convert(x,i) for i,x in enumerate(items)]}
    os.makedirs(os.path.dirname(OUT),exist_ok=True)
    with open(OUT,'w',encoding='utf-8') as f: json.dump(out,f,ensure_ascii=False,indent=2)
    print(json.dumps({'ok':True,'count':len(out['items']),'output':OUT}))
