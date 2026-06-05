#!/usr/bin/env python3
"""UI contract check — validates site against current design system (v20.20+)"""
import re, json, pathlib, datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
css=(ROOT/'site/styles.css').read_text(errors='ignore')
js=(ROOT/'site/app.js').read_text(errors='ignore')
issues=[]

# v20.20+ design system tokens
required_tokens = ['#FFFFFF','#8EC8E8','#D4AF37','#2563EB','#059669','#DC2626','#111827','#E5E7EB']
for token in required_tokens:
    if token.lower() not in css.lower():
        issues.append(f'missing palette token {token}')

# Masthead: light blue name with gold stroke
if '#8EC8E8' not in css: issues.append('masthead name not light blue')
if 'text-stroke' not in css.lower() and '-webkit-text-stroke' not in css: 
    issues.append('masthead missing gold stroke')

# Hero: compressed
if 'padding: 16px' not in css and 'padding:16px' not in css:
    issues.append('hero padding not compressed to 16px')

# HTML structure check
html = (ROOT/'site/index.html').read_text(errors='ignore')
if 'What the capital is saying' not in html: issues.append('stories container missing')
if 'storiesContainer' not in html: issues.append('storiesContainer ID missing')
if 'Directional alignment' not in html: issues.append('confidence label missing')

ok = len(issues) == 0
out = {'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'ok': ok, 'issues': issues}
(ROOT/'data/ui_contract_check.json').write_text(json.dumps(out, indent=2))
print(json.dumps(out))
