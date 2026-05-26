#!/usr/bin/env python3
"""Phase 2: unified scoring for captivation/capital-flow/beneficiary signal."""
from __future__ import annotations
import json, os, time

SRC='data/reddit_candidates.json'
OUT='data/phase2_scores.json'

SECTOR_KEYWORDS={
  'AI & Semis':['ai','nvidia','chip','semiconductor','llm','gpu'],
  'Energy & Grid':['energy','oil','gas','power','grid','nuclear'],
  'Defense & Dual-use':['defense','drone','military','nato','security'],
  'Software & Cloud':['saas','cloud','software','openai','microsoft'],
  'Macro Rates & FX':['inflation','rates','fed','ecb','dollar','fx']
}

def infer_sector(text:str)->str:
  t=text.lower()
  for sec,keys in SECTOR_KEYWORDS.items():
    if any(k in t for k in keys):
      return sec
  return 'Broad Risk Basket'

def score(item:dict)->dict:
  title=item.get('title','')
  cap=min(100, int(item.get('hook_strength',0)*0.45 + item.get('actionability_score',0)*0.35 + item.get('credibility_signal',0)*0.20))
  flow=min(100, int(item.get('score',0)/25 + item.get('num_comments',0)/4 + item.get('upvote_ratio',0)*20))
  bene=min(100, int(flow*0.5 + cap*0.5))
  sector=infer_sector(title + ' ' + item.get('selftext',''))
  regime='risk-on' if flow>=60 else 'mixed'
  return {
    'post_id': item.get('post_id'),
    'title': title,
    'sector': sector,
    'regime': regime,
    'captivation_score': cap,
    'capital_flow_score': flow,
    'beneficiary_score': bene,
    'links': [item.get('url'), item.get('permalink')]
  }

if __name__=='__main__':
  if not os.path.exists(SRC):
    print(json.dumps({'ok':False,'error':f'missing {SRC}'})); raise SystemExit(1)
  with open(SRC,'r',encoding='utf-8') as f: data=json.load(f)
  items=[score(x) for x in data.get('items',[])]
  items.sort(key=lambda x: (x['beneficiary_score'],x['capital_flow_score']), reverse=True)
  out={'generated_at':int(time.time()), 'count':len(items), 'top':items[:25]}
  os.makedirs(os.path.dirname(OUT), exist_ok=True)
  with open(OUT,'w',encoding='utf-8') as f: json.dump(out,f,ensure_ascii=False,indent=2)
  print(json.dumps({'ok':True,'count':len(items),'output':OUT,'top_sector':(items[0]['sector'] if items else None)}))
