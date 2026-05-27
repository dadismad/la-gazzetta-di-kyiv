#!/usr/bin/env python3
import json,re,os
p='/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv/data/reddit_post_payload.md'
text=open(p,encoding='utf-8').read() if os.path.exists(p) else ''
checks={}
checks['len_chars']=len(text)
checks['len_words']=len(re.findall(r"\b\w+\b",text))
checks['has_actors']=bool(re.search(r'\b(Trump|Putin|EU|China|Fed|ECB|Biden|NATO|Russia|Ukraine)\b',text,re.I))
checks['has_claim']=bool(re.search(r'\b(claim|thesis|we think|base case|likely)\b',text,re.I))
checks['has_contradiction']=bool(re.search(r'\b(contradiction|however|but|yet|despite)\b',text,re.I))
checks['has_2472h']=bool(re.search(r'24.?72h|24-72h',text,re.I))
checks['has_invalidation']=bool(re.search(r'\binvalidation\b',text,re.I))
checks['has_links']=len(re.findall(r'https?://\S+',text))
checks['readability_sentence_count']=max(1,len(re.findall(r'[.!?]+',text)))
checks['avg_words_per_sentence']=round(checks['len_words']/checks['readability_sentence_count'],2)
checks['pass']=all([
  checks['has_actors'],checks['has_claim'],checks['has_contradiction'],checks['has_2472h'],checks['has_invalidation'],checks['has_links']>=2
])
out='/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv/data/reddit_post_nlp_audit.json'
open(out,'w',encoding='utf-8').write(json.dumps(checks,indent=2))
print(json.dumps({'ok':True,'audit':out,'pass':checks['pass']}))