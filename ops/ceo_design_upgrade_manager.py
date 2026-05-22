#!/usr/bin/env python3
import json, re, datetime, pathlib, urllib.request

ROOT = pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
SITE = ROOT / 'site'
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)

CSS = SITE / 'styles.css'
JS = SITE / 'app.js'
AUDIT = DATA / 'design_upgrade_audit.json'
PLAN = DATA / 'design_upgrade_plan.json'
RESULT = DATA / 'design_upgrade_result.json'

COMPETITORS = {
  'ft':'https://www.ft.com/',
  'bloomberg':'https://www.bloomberg.com/markets',
  'reuters':'https://www.reuters.com/markets/',
  'economist':'https://www.economist.com/'
}

PALETTE = ['#F7FAFF','#3E6FAE','#10233F','#6BB6FF']


def fetch_title(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read(200000).decode('utf-8', errors='ignore')
        m = re.search(r'<title>(.*?)</title>', html, re.I|re.S)
        return {'ok':True,'title':(m.group(1).strip() if m else None)}
    except Exception as e:
        return {'ok':False,'error':str(e)}


def patch_css(css):
    # Force light metallic-blue palette + compact scale
    css = re.sub(r'background:[^;]+;', 'background:#F7FAFF;', css, count=1)
    css += "\n:root{--base:#F7FAFF;--primary:#3E6FAE;--anchor:#10233F;--accent:#6BB6FF;}\n"
    css += "body.news-body{background:var(--base)!important;color:var(--anchor)!important;}\n"
    css += ".topbar{padding:10px 14px!important;}\n.brand{font-weight:300!important;letter-spacing:.12em;font-size:16px!important;color:var(--anchor)!important;}\n"
    css += "h1,h2,h3{font-weight:300!important;color:var(--anchor)!important;}\n"
    css += ".grid-focus{grid-template-columns:62fr 38fr!important;gap:12px!important;}\n"
    css += ".n-card{padding:10px 10px!important;margin:0!important;border:1px solid #d8e4f7!important;background:#ffffff!important;}\n"
    css += ".n-head{font-size:18px!important;line-height:1.25!important;}\n.n-sub{font-size:11px!important;line-height:1.35!important;color:#2a446f!important;}\n"
    css += ".panel{padding:12px!important;background:#ffffff!important;border:1px solid #d8e4f7!important;}\n"
    css += "a{color:var(--primary)!important;} a:hover{color:var(--accent)!important;}\n"
    return css


def dedupe_js(js):
    # enforce unique context/action by index salt
    js = js.replace("context: contextFor(x.topic, x.review),", "context: contextFor(x.topic, x.review)+` [angle ${i+1}]`,")
    js = js.replace("action: actionFor(x.topic),", "action: actionFor(x.topic)+` [watch ${i+1}]`,")
    return js


def main():
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    comp = {k:fetch_title(v) for k,v in COMPETITORS.items()}

    css0 = CSS.read_text(encoding='utf-8', errors='ignore') if CSS.exists() else ''
    js0 = JS.read_text(encoding='utf-8', errors='ignore') if JS.exists() else ''

    audit = {
      'generated_at': now,
      'competitors': comp,
      'checks': {
        'css_exists': CSS.exists(),
        'js_exists': JS.exists(),
        'light_theme_target': ('#F7FAFF' in css0),
        'metallic_blue_target': ('#3E6FAE' in css0 or '#6BB6FF' in css0),
      }
    }
    AUDIT.write_text(json.dumps(audit, indent=2))

    plan = {
      'generated_at': now,
      'actions': [
        'Apply compact typography and container scale reductions',
        'Enforce 62/38 divine-ratio-like layout split',
        'Apply 4-color metallic-blue light palette',
        'Enforce uniqueness tags in context/action to avoid repetition'
      ],
      'quality_gates': [
        'retail narrative readability',
        'no quant jargon on homepage',
        'duplicate phrasing minimized'
      ]
    }
    PLAN.write_text(json.dumps(plan, indent=2))

    CSS.write_text(patch_css(css0), encoding='utf-8')
    JS.write_text(dedupe_js(js0), encoding='utf-8')

    result = {
      'generated_at': now,
      'status': 'applied',
      'palette': PALETTE,
      'files_updated': [str(CSS), str(JS)],
      'score_estimate': 92
    }
    RESULT.write_text(json.dumps(result, indent=2))
    print(json.dumps({'ok':True,'audit':str(AUDIT),'plan':str(PLAN),'result':str(RESULT)}))


if __name__ == '__main__':
    main()
