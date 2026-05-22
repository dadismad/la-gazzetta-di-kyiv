#!/usr/bin/env python3
import json, pathlib, subprocess, datetime, urllib.request

ROOT = pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
OUT = ROOT / 'data' / 'pages_watchdog.json'
ENV = pathlib.Path('/Users/alexstocchi/.hermes/.env')

PRIMARY = [
    'https://pureciclismo.github.io/gazzetta-di-kyiv/',
    'https://pureciclismo.github.io/gazzetta-di-kyiv/data/narratives.json'
]
MIRRORS = [
    'https://rawcdn.githack.com/pureciclismo/gazzetta-di-kyiv/main/site/index.html',
    'https://cdn.jsdelivr.net/gh/pureciclismo/gazzetta-di-kyiv@main/site/index.html'
]


def check(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read(3000).decode('utf-8', errors='ignore')
            code = r.getcode()
        bad_404 = "There isn't a GitHub Pages site here" in body
        return {'url': url, 'ok': code == 200 and not bad_404, 'code': code, 'bad_404': bad_404}
    except Exception as e:
        return {'url': url, 'ok': False, 'code': None, 'bad_404': False, 'error': str(e)}


def run(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {'ok': p.returncode == 0, 'code': p.returncode, 'out': p.stdout[-800:], 'err': p.stderr[-800:]}


def get_token():
    if not ENV.exists():
        return None
    for line in ENV.read_text().splitlines():
        if line.startswith('GITHUB_TOKEN='):
            return line.split('=', 1)[1].strip()
    return None


primary_results = [check(u) for u in PRIMARY]
mirror_results = [check(u) for u in MIRRORS]
primary_healthy = all(r['ok'] for r in primary_results)
mirror_healthy = any(r['ok'] for r in mirror_results)
healthy = primary_healthy

actions = []
if not primary_healthy:
    token = get_token()
    if token:
        actions.append({'action': 'dispatch_pages_deploy'})
        cmd = (
            "curl -s -o /tmp/dispatch.out -w '%{http_code}' -X POST "
            f"-H 'Authorization: Bearer {token}' "
            "-H 'Accept: application/vnd.github+json' "
            "https://api.github.com/repos/pureciclismo/gazzetta-di-kyiv/actions/workflows/refresh-and-deploy.yml/dispatches "
            "-d '{\"ref\":\"main\"}'"
        )
        actions.append(run(cmd))

recommended_url = PRIMARY[0] if primary_healthy else next((r['url'] for r in mirror_results if r['ok']), None)

payload = {
    'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'healthy': healthy,
    'primary_healthy': primary_healthy,
    'mirror_healthy': mirror_healthy,
    'recommended_url': recommended_url,
    'checks': {'primary': primary_results, 'mirrors': mirror_results},
    'actions': actions,
}
OUT.write_text(json.dumps(payload, indent=2))
print(json.dumps({'ok': True, 'healthy': healthy, 'recommended_url': recommended_url, 'file': str(OUT)}))
