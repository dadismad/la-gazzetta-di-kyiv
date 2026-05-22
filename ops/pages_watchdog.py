#!/usr/bin/env python3
import json, pathlib, subprocess, datetime, urllib.request

ROOT = pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
OUT = ROOT / 'data' / 'pages_watchdog.json'
URLS = [
    'https://pureciclismo.github.io/gazzetta-di-kyiv/',
    'https://pureciclismo.github.io/gazzetta-di-kyiv/data/narratives.json'
]


def check(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read(2500).decode('utf-8', errors='ignore')
            code = r.getcode()
        bad_404 = "There isn't a GitHub Pages site here" in body
        return {'url': url, 'ok': code == 200 and not bad_404, 'code': code, 'bad_404': bad_404}
    except Exception as e:
        return {'url': url, 'ok': False, 'code': None, 'bad_404': False, 'error': str(e)}


def run(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {'ok': p.returncode == 0, 'code': p.returncode, 'out': p.stdout[-800:], 'err': p.stderr[-800:]}


results = [check(u) for u in URLS]
healthy = all(r['ok'] for r in results)
actions = []

if not healthy:
    actions.append('dispatch_pages_deploy')
    token = None
    env = pathlib.Path('/Users/alexstocchi/.hermes/.env')
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith('GITHUB_TOKEN='):
                token = line.split('=', 1)[1].strip()
                break
    if token:
        cmd = (
            "curl -s -o /tmp/dispatch.out -w '%{http_code}' -X POST "
            f"-H 'Authorization: Bearer {token}' "
            "-H 'Accept: application/vnd.github+json' "
            "https://api.github.com/repos/pureciclismo/gazzetta-di-kyiv/actions/workflows/refresh-and-deploy.yml/dispatches "
            "-d '{\"ref\":\"main\"}'"
        )
        actions.append(run(cmd))

payload = {
    'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'healthy': healthy,
    'checks': results,
    'actions': actions,
}
OUT.write_text(json.dumps(payload, indent=2))
print(json.dumps({'ok': True, 'healthy': healthy, 'file': str(OUT)}))
