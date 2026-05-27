#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

APP = 'GazzettadiKyivX'

if len(sys.argv) < 2:
    print(json.dumps({'ok': False, 'error': 'usage: x_post_from_file.py <text_file>'}))
    sys.exit(2)

text_file = Path(sys.argv[1])
if not text_file.exists():
    print(json.dumps({'ok': False, 'error': f'missing file: {text_file}'}))
    sys.exit(2)

text = text_file.read_text(encoding='utf-8').strip()
if not text:
    print(json.dumps({'ok': False, 'error': 'empty text file'}))
    sys.exit(2)
if len(text) > 275:
    print(json.dumps({'ok': False, 'error': f'text too long ({len(text)} chars), max 275'}))
    sys.exit(2)

cmd = ['xurl', '--app', APP, 'post', text]
p = subprocess.run(cmd, capture_output=True, text=True)
out = (p.stdout or p.stderr).strip()

try:
    payload = json.loads(out)
except Exception:
    payload = {'raw': out}

if p.returncode != 0:
    print(json.dumps({'ok': False, 'error': 'post_failed', 'detail': payload}))
    sys.exit(1)

post_id = None
if isinstance(payload, dict):
    data_obj = payload.get('data')
    if isinstance(data_obj, dict):
        post_id = data_obj.get('id')

print(json.dumps({'ok': True, 'post_id': post_id, 'response': payload}))
