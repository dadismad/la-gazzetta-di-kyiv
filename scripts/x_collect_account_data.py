#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

OUT_DIR = Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv/data/x')
OUT_DIR.mkdir(parents=True, exist_ok=True)

APP = 'GazzettadiKyivX'
HANDLE = 'GazzettadiKyiv'


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def parse_json(text):
    try:
        return json.loads(text)
    except Exception:
        return {'raw': text}


now = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
status = {
    'ts': now,
    'app': APP,
    'handle': HANDLE,
    'collection': {},
}

cmd_user = ['xurl', '--app', APP, '--auth', 'app', 'user', HANDLE]
rc, out, err = run(cmd_user)
status['collection']['user_lookup_rc'] = rc
status['collection']['user_lookup'] = parse_json(out if out else err)

if rc != 0:
    blob = status['collection']['user_lookup']
    title = blob.get('title', '') if isinstance(blob, dict) else ''
    detail = blob.get('detail', '') if isinstance(blob, dict) else ''
    if title == 'CreditsDepleted' or 'credits' in str(detail).lower():
        status['state'] = 'blocked_credits'
    else:
        status['state'] = 'blocked_auth_or_api'
else:
    cmd_search = ['xurl', '--app', APP, '--auth', 'app', 'search', f'from:{HANDLE} -is:retweet', '-n', '10']
    rc2, out2, err2 = run(cmd_search)
    status['collection']['recent_posts_rc'] = rc2
    status['collection']['recent_posts'] = parse_json(out2 if out2 else err2)
    status['state'] = 'ok' if rc2 == 0 else 'partial_error'

out_file = OUT_DIR / f'x_collection_status_{now}.json'
out_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')

print(json.dumps({'ok': True, 'state': status['state'], 'file': str(out_file)}))
if status['state'] != 'ok':
    sys.exit(1)
