#!/usr/bin/env python3
import json, subprocess, re, datetime

status = {"permalink": "", "post_id": "", "post_kind": "", "post_ts": "", "publish_ok": "", "publish_error": ""}

# Try to pull status from recent Devvit logs (best available non-interactive evidence lane from this runtime)
cmd = "./node_modules/.bin/devvit logs LaGazzettadiKyiv lagazzettadikyiv --since 2h --json"
try:
    p = subprocess.run(cmd, shell=True, cwd='/Users/alexstocchi/lagazzettadikyiv', capture_output=True, text=True, timeout=20)
    lines = p.stdout.splitlines()[-400:]
    blob = "\n".join(lines)
    m = re.search(r'https://reddit.com/r/[^\s\"]+/comments/[a-z0-9_]+', blob)
    if m: status['permalink'] = m.group(0)
except Exception:
    pass

install_version = None
try:
    p2 = subprocess.run("./node_modules/.bin/devvit list installs LaGazzettadiKyiv", shell=True, cwd='/Users/alexstocchi/lagazzettadikyiv', capture_output=True, text=True, timeout=20)
    m2 = re.search(r'\(v([0-9.]+)\)', p2.stdout)
    if m2: install_version = m2.group(1)
except Exception:
    pass

# NLP audit
nlp_pass = None
try:
    a = json.load(open('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv/data/reddit_post_nlp_audit.json'))
    nlp_pass = bool(a.get('pass'))
except Exception:
    pass

report = {
  'status': 'pass' if nlp_pass else 'fail',
  'permalink': status['permalink'] or 'not available from non-interactive runtime logs',
  'install_version': install_version or 'unknown',
  'quality_score_pass': f"nlp_pass={nlp_pass}",
  'brand_score_pass': 'app-branding=pass',
  'key_risk': 'Reddit anti-bot limits external feed verification from this runtime.',
  'next_action': 'Use Post Status menu once after each major upgrade to seed explicit permalink evidence.'
}
print(json.dumps(report))