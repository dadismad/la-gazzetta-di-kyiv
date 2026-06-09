#!/usr/bin/env python3
"""sync_publish_to_site.py — Copy editorial writer output (data/publish/) to canonical data/ paths.
Runs as step 0.5 in the pipeline chain before generate_flows.
Ensures the website always serves the freshest editorial content.
"""
import json, shutil, os
from datetime import datetime, timezone

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT, 'data')
PUBLISH_DIR = os.path.join(DATA_DIR, 'publish')

def copy_if_newer(src_name, dst_name):
    """Copy publish/src → data/dst if publish version is newer or missing."""
    src = os.path.join(PUBLISH_DIR, src_name)
    dst = os.path.join(DATA_DIR, dst_name)
    if not os.path.exists(src):
        print(f"  SKIP {src_name}: not found in publish/")
        return False
    if os.path.exists(dst):
        src_mtime = os.path.getmtime(src)
        dst_mtime = os.path.getmtime(dst)
        if src_mtime <= dst_mtime:
            print(f"  SKIP {src_name}: data/ version is same age or newer")
            return False
    shutil.copy2(src, dst)
    print(f"  COPY {src_name} → data/{dst_name}")
    return True

def main():
    print(f"=== SYNC PUBLISH → DATA {datetime.now(timezone.utc).isoformat()} ===")
    synced = 0
    
    # Stories — the critical one
    if copy_if_newer('stories.json', 'stories.json'):
        synced += 1
    
    # Living stories
    if copy_if_newer('living_stories.json', 'living_stories.json'):
        synced += 1
    
    # Asset claims
    if copy_if_newer('asset_claims_latest.json', 'asset_claims_latest.json'):
        synced += 1
    
    # Publish manifest
    if copy_if_newer('publish_manifest.json', 'publish_manifest.json'):
        synced += 1
    
    print(f"  Synced: {synced} files")
    return {'ok': True, 'synced': synced}

if __name__ == '__main__':
    import json as _j
    print(_j.dumps(main()))
