#!/usr/bin/env python3
"""Devvit-only pipeline: no OAuth/password flow, generate publish-ready payloads."""
import subprocess, json
repo='/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv'
steps=[
 ['python3','scripts/reddit_ingest.py','--subreddit','Infographics','--limit','25'],
 ['python3','scripts/generate_candidates_fallback.py'],
 ['python3','scripts/phase2_scoring.py'],
 ['python3','scripts/reddit_to_gazzetta_draft.py'],
 ['python3','scripts/reddit_post_payload.py']
]

result={'ok':True,'steps':[]}
for i,cmd in enumerate(steps):
    p=subprocess.run(cmd,cwd=repo,text=True,capture_output=True)
    result['steps'].append({'cmd':' '.join(cmd),'exit':p.returncode,'stdout':p.stdout[-400:], 'stderr':p.stderr[-300:]})
    if p.returncode!=0 and i==0:
      # reddit ingest may fail when no creds; continue with fallback
      continue
    if p.returncode!=0:
      result['ok']=False
      break
print(json.dumps(result))
