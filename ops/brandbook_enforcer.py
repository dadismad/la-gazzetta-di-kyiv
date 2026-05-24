#!/usr/bin/env python3
import json, pathlib, datetime, re
ROOT=pathlib.Path(__file__).resolve().parents[1]
SITE=ROOT/'site'; DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
css=(SITE/'styles.css').read_text(errors='ignore')
js=(SITE/'app.js').read_text(errors='ignore')
index=(SITE/'index.html').read_text(errors='ignore')
nar_path=SITE/'data'/'narratives.json'
issues=[]; checks={}

# Visual brand checks
palette=['#F7FAFF','#3E6FAE','#10233F','#6BB6FF']
checks['palette_tokens']={t:(t.lower() in css.lower()) for t in palette}
for t,ok in checks['palette_tokens'].items():
    if not ok: issues.append(f'missing palette {t}')

checks['compact_typography']=('font-size:10px' in css.lower() or 'font-size:9px' in css.lower() or 'font-size:8px' in css.lower())
if not checks['compact_typography']: issues.append('missing compact typography scale')

# Content schema checks in UI logic
for key,msg in [('flow 3d','missing 3-day flow metric'),('projection 3d','missing 3-day projection metric'),('invalidation','missing invalidation logic')]:
    present = key in js.lower() or key in index.lower()
    checks[key]=present
    if not present: issues.append(msg)

# Narrative dataset checks
narr=[]
if not nar_path.exists():
    issues.append('missing site/data/narratives.json')
else:
    obj=json.loads(nar_path.read_text())
    narr=obj.get('narrative_reviews',[])
    checks['narrative_count']=len(narr)
    if len(narr)<8: issues.append('too few narrative reviews (<8)')

    # uniqueness: headline duplicates
    heads=[(x.get('headline') or '').strip().lower() for x in narr if (x.get('headline') or '').strip()]
    dup=len(heads)-len(set(heads))
    checks['duplicate_headlines']=dup
    if dup>0: issues.append(f'duplicate headlines: {dup}')

    # required fields per item
    missing_fields=0
    generic=0
    banned=['narrative drift requires tactical adaptation']
    for x in narr:
        if not x.get('topic') or not x.get('review'): missing_fields+=1
        h=(x.get('headline') or '').lower()
        r=(x.get('review') or '').lower()
        if any(b in h or b in r for b in banned): generic+=1
    checks['items_missing_required_fields']=missing_fields
    checks['generic_phrase_hits']=generic
    if missing_fields>0: issues.append(f'items missing required fields: {missing_fields}')
    if generic>0: issues.append(f'generic wording still present: {generic}')

# Layout intent checks
checks['focus_panel_present']=('economic regime overlap' in index.lower() and 'selectednarrative' in index.lower())
if not checks['focus_panel_present']: issues.append('missing narrative focus panel')

ok=len(issues)==0
out={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ok':ok,'issues':issues,'checks':checks}
(DATA/'brandbook_enforcement.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))