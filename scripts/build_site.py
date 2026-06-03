#!/usr/bin/env python3
"""build_site.py — Sync pipeline outputs to GitHub Pages site directory.
Run after each editorial cycle to push fresh data to the static site.
"""
import json, os, shutil
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, 'data')
SITE = os.path.join(REPO, 'site')

os.makedirs(os.path.join(SITE, 'api', 'v1', 'home'), exist_ok=True)
os.makedirs(os.path.join(SITE, 'data'), exist_ok=True)

# 1. Sync narrative intelligence → API endpoints
ni_path = os.path.join(DATA, 'processed', 'narrative_intelligence_latest.json')
setups = []
contradictions = []
if os.path.exists(ni_path):
    ni = json.load(open(ni_path))
    api_dir = os.path.join(SITE, 'api', 'v1', 'home')
    
    setups = ni.get('setups', [])
    contradictions = ni.get('contradictions', [])
    regime = ni.get('regime', {})
    
    json.dump({'generated_at': ni.get('generated_at'), 'data_freshness_seconds': 3600,
               'source_count': regime.get('source_count', 4), 'items': setups},
              open(os.path.join(api_dir, 'setups.json'), 'w'), indent=2)
    json.dump({'generated_at': ni.get('generated_at'), 'data_freshness_seconds': 3600,
               'source_count': regime.get('source_count', 4), 'items': contradictions},
              open(os.path.join(api_dir, 'contradictions.json'), 'w'), indent=2)
    json.dump(regime, open(os.path.join(api_dir, 'regime.json'), 'w'), indent=2)

# 2. Sync publish content files (stories, living stories, website blurbs, manifests)
publish_srcs = [
    'website_stories_latest.json',
    'stories.json',
    'living_stories.json',
    'asset_claims_latest.json',
    'publish_manifest.json',
]
for fname in publish_srcs:
    src = os.path.join(DATA, 'publish', fname)
    dst = os.path.join(SITE, 'data', fname)
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

# 3. Sync story registry (lives at data/story_registry.json, not data/publish/)
registry_src = os.path.join(DATA, 'story_registry.json')
registry_dst = os.path.join(SITE, 'data', 'story_registry.json')
if os.path.exists(registry_src):
    shutil.copy2(registry_src, registry_dst)

# 4. Sync Telegram/Reddit latest
for fname in ['telegram_latest.md', 'reddit_latest.md']:
    src = os.path.join(DATA, 'publish', fname)
    dst = os.path.join(SITE, 'data', fname)
    if os.path.exists(src):
        shutil.copy2(src, dst)

print(json.dumps({
    'ok': True,
    'synced_at': datetime.now(timezone.utc).isoformat(),
    'setups': len(setups) if os.path.exists(ni_path) else 0,
    'contradictions': len(contradictions) if os.path.exists(ni_path) else 0,
    'website_stories': os.path.exists(os.path.join(SITE, 'data', 'website_stories_latest.json')),
    'concrete_stories': os.path.exists(os.path.join(SITE, 'data', 'stories.json')),
    'living_stories': os.path.exists(os.path.join(SITE, 'data', 'living_stories.json')),
    'story_registry': os.path.exists(os.path.join(SITE, 'data', 'story_registry.json')),
}))
