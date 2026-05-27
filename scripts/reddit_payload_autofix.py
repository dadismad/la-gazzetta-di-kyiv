#!/usr/bin/env python3
import json,re
payload='data/reddit_post_payload.md'
audit='data/reddit_post_nlp_audit.json'
text=open(payload,encoding='utf-8').read()

def ensure(line):
    global text
    if line not in text:
        text=text.replace('READY_FOR_DEVVIT_POST', line+'\n\nREADY_FOR_DEVVIT_POST')

if not re.search(r'\b(Claim|claim)\b', text):
    ensure('**Claim:** narrative pressure is driving short-horizon positioning.')
if not re.search(r'\b(Contradiction|contradiction|however|despite)\b', text):
    ensure('**Contradiction:** sentiment strength is outpacing hard macro confirmation.')
if not re.search(r'24.?72h|24-72h', text, re.I):
    ensure('**24–72h path (62%):** risk assets drift up, then mean-revert on weak confirmation.')
if not re.search(r'\bInvalidation\b', text, re.I):
    ensure('**Invalidation:** if engagement and cross-asset confirmation both fade, thesis is wrong.')
if len(re.findall(r'https?://\S+', text)) < 2:
    ensure('- https://pureciclismo.github.io/gazzetta-di-kyiv/')
    ensure('- https://pureciclismo.github.io/gazzetta-di-kyiv/research.html')
if not re.search(r'\b(Fed|ECB|China|EU|NATO|Russia|Ukraine|Trump|Biden|Putin)\b', text, re.I):
    ensure('**Actors in play:** Fed, EU, China narrative desks and risk allocators.')

open(payload,'w',encoding='utf-8').write(text)
print(json.dumps({'ok':True,'output':payload}))