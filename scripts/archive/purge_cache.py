#!/usr/bin/env python3
"""
Gazzetta di Kyiv — CDN Cache Purge Script
Invalidates CDN cache for critical data files when CRITICAL stories are published.

Usage:
    .venv/bin/python scripts/purge_cache.py              # Purge stories.json + flows.json
    .venv/bin/python scripts/purge_cache.py --all        # Purge all .json and .html
    .venv/bin/python scripts/purge_cache.py --file data/stories.json  # Purge specific file

Requires: gcloud SDK authenticated with CDN admin permissions.
Always Free note: Cache invalidation is free, but limited to 6 paths/minute per host.
"""

import os, sys, subprocess, json
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
GCLOUD_DIR = os.environ.get('GCLOUD_DIR', os.path.expanduser('~/lagazzettadikyiv/google-cloud-sdk'))
GSUTIL = os.path.join(GCLOUD_DIR, 'bin', 'gsutil')

# Critical data files that must always be fresh
CRITICAL_FILES = [
    'data/stories.json',
    'data/flows.json',
    'data/stories_ru.json',
    'data/flows_ru.json',
    'data/narratives.json',
    'data/signal.json',
]

BUCKET = 'gs://www.lagazzettadikyiv.com'


def purge_by_gsutil_reset(files):
    """Purge CDN cache by resetting Cache-Control metadata on GCS objects.
    
    Google Cloud CDN doesn't support explicit invalidation via gsutil.
    Instead, we force cache refresh by touching the object metadata.
    """
    results = []
    for f in files:
        path = f'{BUCKET}/{f}'
        try:
            # Reset metadata to force CDN to revalidate
            subprocess.run(
                [GSUTIL, 'setmeta', '-h', 'Cache-Control:public, max-age=0, must-revalidate', path],
                check=True, capture_output=True, timeout=30
            )
            # Touch the object to change its generation number
            subprocess.run(
                [GSUTIL, 'cp', path, path],
                check=True, capture_output=True, timeout=30
            )
            results.append({'file': f, 'status': 'purged'})
        except Exception as e:
            results.append({'file': f, 'status': 'failed', 'error': str(e)[:100]})
    
    return results


def detect_critical_stories():
    """Check if any recent CRITICAL CONTRADICTION stories were published."""
    stories_path = PROJECT / 'data' / 'stories.json'
    if not stories_path.exists():
        return False
    
    with open(stories_path) as f:
        data = json.load(f)
    
    stories = [data.get('lead')] + data.get('stories', [])
    for s in stories:
        if not s:
            continue
        headline = (s.get('headline') or '')
        cs = s.get('contradiction_score', 0)
        if 'CRITICAL CONTRADICTION' in headline or cs >= 70:
            return True
    
    return False


def main():
    files_to_purge = CRITICAL_FILES.copy()
    
    if '--all' in sys.argv:
        files_to_purge = [
            'data/stories.json', 'data/flows.json', 'data/stories_ru.json',
            'data/flows_ru.json', 'data/narratives.json', 'data/signal.json',
            'data/market_prices.json', 'data/correlation_matrix.json',
            'index.html', 'ru/index.html', 'stories.html', 'flows.html',
            'signal.html', 'track.html', 'trades.html', 'story.html',
            'flow-nodes.html', 'event_horizon.html',
        ]
    elif '--file' in sys.argv:
        idx = sys.argv.index('--file')
        files_to_purge = [sys.argv[idx + 1]]
    
    print(f"CDN Cache Purge — {datetime.now(timezone.utc).isoformat()}")
    print(f"  Files: {len(files_to_purge)}")
    
    # Check for critical stories
    if detect_critical_stories():
        print("  ⚡ CRITICAL story detected — forcing full data purge")
        if 'data/stories.json' not in files_to_purge:
            files_to_purge.append('data/stories.json')
        if 'data/flows.json' not in files_to_purge:
            files_to_purge.append('data/flows.json')
    
    # Verify gsutil
    if not os.path.exists(GSUTIL):
        print(f"  ⚠ gsutil not found at {GSUTIL}")
        print("  Purge skipped — deploy will handle cache via setmeta")
        return
    
    results = purge_by_gsutil_reset(files_to_purge)
    
    ok = sum(1 for r in results if r['status'] == 'purged')
    failed = sum(1 for r in results if r['status'] == 'failed')
    
    print(f"  Results: {ok} purged, {failed} failed")
    
    if failed:
        for r in results:
            if r['status'] == 'failed':
                print(f"    ✗ {r['file']}: {r.get('error', 'unknown')}")
    
    print(f"  ✓ Purge complete — CDN will revalidate on next request")


if __name__ == '__main__':
    main()
