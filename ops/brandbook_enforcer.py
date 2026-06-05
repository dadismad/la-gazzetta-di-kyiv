#!/usr/bin/env python3
"""Brandbook enforcer — validates site against v20.20 design system"""
import json, pathlib, datetime, re
ROOT=pathlib.Path(__file__).resolve().parents[1]
SITE=ROOT/'site'; DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
css=(SITE/'styles.css').read_text(errors='ignore')
js=(SITE/'app.js').read_text(errors='ignore')
index=(SITE/'index.html').read_text(errors='ignore')
issues=[]; checks={}

# Visual brand checks — v20.20 palette
palette=['#FFFFFF','#8EC8E8','#D4AF37','#2563EB','#059669','#DC2626','#111827','#E5E7EB','#6B7280','#9CA3AF']
checks['palette_tokens']={t:(t.lower() in css.lower()) for t in palette}
for t,ok in checks['palette_tokens'].items():
    if not ok: issues.append(f'missing palette {t}')

# Masthead: light blue name + gold stroke
checks['masthead_blue'] = ('#8EC8E8' in css)
checks['masthead_stroke'] = ('text-stroke' in css.lower() or '-webkit-text-stroke' in css)
if not checks['masthead_blue']: issues.append('masthead name not light blue')
if not checks['masthead_stroke']: issues.append('masthead missing gold stroke')

# Container structure
containers = ['storiesContainer','capitalFlowsContainer','anchorContainer','triangulationContainer','trackRecordContainer']
checks['container_count'] = sum(1 for c in containers if c in index)
if checks['container_count'] < 5: issues.append(f'missing containers: {checks["container_count"]}/5')

# Share buttons (v20.20: visible row, not dropdown)
checks['share_visible'] = 'shareToX' in js and 'shareToFacebook' in js
if not checks['share_visible']: issues.append('share buttons not visible row format')

# Timestamps
checks['story_timestamps'] = 'story-date' in js or '<time' in js.lower()
if not checks['story_timestamps']: issues.append('missing story timestamps')

# Hero
checks['hero_descriptive'] = 'before they move prices' in index.lower()
if not checks['hero_descriptive']: issues.append('hero headline not benefit-focused')

# Narrative dataset checks
nar_path=SITE/'data'/'narratives.json'
if not nar_path.exists():
    issues.append('missing site/data/narratives.json')
else:
    obj=json.loads(nar_path.read_text())
    narr=obj.get('narrative_reviews',[])
    checks['narrative_count']=len(narr)
    if len(narr)<8: issues.append('too few narrative reviews (<8)')
    heads=[(x.get('headline') or '').strip().lower() for x in narr if (x.get('headline') or '').strip()]
    dup=len(heads)-len(set(heads))
    checks['duplicate_headlines']=dup
    if dup>0: issues.append(f'duplicate headlines: {dup}')

ok = len(issues)==0
out={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ok':ok,'issues':issues,'checks':checks}
(DATA/'brandbook_enforcer.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
