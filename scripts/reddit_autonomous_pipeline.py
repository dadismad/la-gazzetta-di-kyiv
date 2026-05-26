#!/usr/bin/env python3
import os, subprocess, sys
repo='/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv'

def run(cmd):
    p=subprocess.run(cmd,cwd=repo,text=True,capture_output=True)
    if p.returncode!=0:
        print(p.stdout); print(p.stderr); raise SystemExit(p.returncode)
    print(p.stdout.strip())

# Build payload from best available source (Reddit API if creds; otherwise fallback)
try:
    run([sys.executable,'scripts/reddit_ingest.py','--subreddit',os.getenv('REDDIT_SOURCE_SUBREDDIT','Infographics'),'--limit','25'])
except SystemExit:
    run([sys.executable,'scripts/generate_candidates_fallback.py'])
run([sys.executable,'scripts/phase2_scoring.py'])
run([sys.executable,'scripts/reddit_to_gazzetta_draft.py'])
run([sys.executable,'scripts/reddit_post_payload.py'])
# Submit unattended to target subreddit
run([sys.executable,'scripts/reddit_submit_post.py'])
print('OK: autonomous reddit workflow complete')
