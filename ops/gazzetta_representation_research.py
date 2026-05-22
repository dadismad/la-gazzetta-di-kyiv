#!/usr/bin/env python3
import json, os, re, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone

feeds = [
    ('nngroup', 'https://www.nngroup.com/feed/rss/'),
    ('smashing', 'https://www.smashingmagazine.com/feed/'),
    ('uxcollective', 'https://uxdesign.cc/feed'),
    ('a_list_apart', 'https://alistapart.com/main/feed/'),
]

keywords = {
    'scrollytelling': ['scrollytelling','storytelling'],
    'small_multiples': ['small multiples','facet'],
    'sparklines': ['sparkline','microchart'],
    'confidence_bands': ['uncertainty','confidence interval','band'],
    'annotation_layers': ['annotation','callout','note layer'],
    'narrative_cards': ['cards','modular content'],
    'progressive_disclosure': ['progressive disclosure','drill-down'],
    'color_semantics': ['color semantics','semantic color','palette'],
    'information_density': ['information density','dashboard density'],
    'mobile_first_summaries': ['mobile first','summary cards'],
}

ua = {'User-Agent':'Mozilla/5.0 GazzettaResearchBot/1.0'}
items = []
for src, url in feeds:
    try:
        req = urllib.request.Request(url, headers=ua)
        txt = urllib.request.urlopen(req, timeout=25).read().decode('utf-8','ignore')
        root = ET.fromstring(txt)
        for it in root.findall('.//item')[:40]:
            title = (it.findtext('title') or '').strip()
            link = (it.findtext('link') or '').strip()
            desc = (it.findtext('description') or '').strip()
            blob = (title + ' ' + re.sub('<[^>]+>',' ',desc)).lower()
            matched=[]
            for k, kws in keywords.items():
                if any(kw in blob for kw in kws):
                    matched.append(k)
            if matched:
                items.append({'source':src,'title':title,'link':link,'matched':matched})
    except Exception:
        continue

score = {k:0 for k in keywords}
examples = {k:[] for k in keywords}
for it in items:
    for m in it['matched']:
        score[m]+=1
        if len(examples[m])<3:
            examples[m].append({'title':it['title'],'link':it['link'],'source':it['source']})

techniques=[]
for k,v in sorted(score.items(), key=lambda x:x[1], reverse=True):
    if v==0: continue
    techniques.append({
        'technique':k,
        'evidence_count':v,
        'adoption_priority':'high' if v>=6 else ('medium' if v>=3 else 'low'),
        'implementation_note':{
            'scrollytelling':'Use scroll-linked narrative transitions from macro to micro evidence.',
            'small_multiples':'Show side-by-side regime slices for time or region comparisons.',
            'sparklines':'Add inline 7d/30d sparkline microcharts next to each narrative.',
            'confidence_bands':'Display confidence range around narrative intensity score.',
            'annotation_layers':'Add short callouts for shock events causing spikes.',
            'narrative_cards':'Use card stacks for each storyline with source snippets.',
            'progressive_disclosure':'Default concise view, click to expand analytical depth.',
            'color_semantics':'Use semantic color mapping for risk-on/risk-off conditions.',
            'information_density':'Keep data-dense summary while preserving whitespace.',
            'mobile_first_summaries':'Expose concise hook lines first for mobile readers.',
        }.get(k,'Adopt as standard representation pattern.'),
        'examples': examples[k]
    })

out = {
    'generated_at': datetime.now(timezone.utc).isoformat(),
    'sources_scanned': [u for _,u in feeds],
    'articles_matched': len(items),
    'techniques': techniques,
}

path='/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv/data/representation_techniques.json'
os.makedirs(os.path.dirname(path), exist_ok=True)
json.dump(out, open(path,'w'), indent=2)
print(json.dumps({'ok':True,'techniques':len(techniques),'matched':len(items)}))
