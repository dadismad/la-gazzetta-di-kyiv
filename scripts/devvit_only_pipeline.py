#!/usr/bin/env python3
"""Devvit-only pipeline: uses Devvit API for Reddit data, no OAuth/password flow needed."""
import subprocess, json, os
repo='/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv'

# Check if DEVVIT_API_URL is set
api_url = os.environ.get('DEVVIT_API_URL', '').strip()

steps = []
if api_url:
    steps.append(['python3','scripts/devvit_ingest.py','--limit','25','--sort','hot'])
else:
    # Without Devvit API URL, skip ingestion (no OAuth creds available)
    pass

steps.extend([
    ['python3','scripts/generate_candidates_fallback.py'],
    ['python3','scripts/phase2_scoring.py'],
    ['python3','scripts/reddit_to_gazzetta_draft.py'],
    ['python3','scripts/reddit_post_payload.py']
])

result={'ok':True,'steps':[],'notes':[]}
if not api_url:
    result['notes'].append('DEVVIT_API_URL not set — ingestion skipped. Set after deploying: devvit upload')

for i,cmd in enumerate(steps):
    p=subprocess.run(cmd,cwd=repo,text=True,capture_output=True)
    result['steps'].append({'cmd':' '.join(cmd),'exit':p.returncode,'stdout':p.stdout[-400:], 'stderr':p.stderr[-300:]})
    if p.returncode!=0:
      result['ok']=False
      break
print(json.dumps(result))
