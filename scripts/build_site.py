#!/usr/bin/env python3
import csv
import json
import os
import sqlite3
from collections import Counter
from datetime import datetime, timezone, timedelta

BASE = os.path.expanduser('~/.hermes/data/social_umbrella')
REPO = '/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv'
OUT_DATA = os.path.join(REPO, 'data')
OUT_SITE = os.path.join(REPO, 'site')

os.makedirs(OUT_DATA, exist_ok=True)
os.makedirs(OUT_SITE, exist_ok=True)

registry_json = os.path.join(BASE, 'source_registry_ranked.json')
events_db = os.path.join(BASE, 'events.db')

with open(registry_json, 'r') as f:
    registry = json.load(f)

# narrative extraction from recent titles
since = datetime.now(timezone.utc) - timedelta(hours=24)
keywords = ['ukraine','russia','nato','eu','inflation','rates','oil','gas','ai','china','sanctions','ceasefire','drone','crypto','election']
counts = Counter()
recent_items = 0

if os.path.exists(events_db):
    con = sqlite3.connect(events_db)
    cur = con.cursor()
    try:
        cur.execute("SELECT title, published_at, url FROM events")
        rows = cur.fetchall()
        for title, published_at, url in rows:
            if not title:
                continue
            t = title.lower()
            # best effort date parse
            in_window = True
            if published_at:
                try:
                    dt = datetime.fromisoformat(str(published_at).replace('Z','+00:00'))
                    in_window = dt >= since
                except Exception:
                    in_window = True
            if not in_window:
                continue
            recent_items += 1
            for k in keywords:
                if k in t:
                    counts[k] += 1
    finally:
        con.close()

narratives = [{'topic':k,'mentions_24h':v} for k,v in counts.most_common(15)]

narrative_reviews = []
for n in narratives:
    topic = n['topic']
    mentions = n['mentions_24h']
    intensity = round(min(100, mentions * 4.2), 1)
    momentum = 'high' if mentions >= 15 else ('medium' if mentions >= 6 else 'low')
    bias = 'risk-on' if topic in ['ai','crypto','technology'] else ('risk-off' if topic in ['war','sanctions','inflation','rates','oil','gas'] else 'mixed')
    review = (
        f"Signal strength {intensity}/100 with {momentum} momentum. "
        f"Regime bias appears {bias}. "
        f"Interpretation: short-term desks should treat this narrative as "
        f"{'position-relevant and timing-sensitive' if intensity >= 60 else 'context-relevant with selective execution'}; "
        f"cross-check with rates, energy, and policy headlines for confirmation before sizing."
    )
    narrative_reviews.append({
        'topic': topic,
        'mentions_24h': mentions,
        'intensity_score': intensity,
        'momentum': momentum,
        'review': review,
    })

summary = {
    'generated_at': datetime.now(timezone.utc).isoformat(),
    'recent_items_24h': recent_items,
    'top_narratives': narratives,
    'narrative_reviews': narrative_reviews,
}

with open(os.path.join(OUT_DATA,'narratives.json'),'w') as f:
    json.dump(summary,f,indent=2)

with open(os.path.join(OUT_DATA,'source_registry_ranked.json'),'w') as f:
    json.dump(registry,f,indent=2)

# csv refresh
with open(os.path.join(OUT_DATA,'source_registry_ranked.csv'),'w',newline='') as f:
    w=csv.DictWriter(f, fieldnames=['platform','source_id','name','url','popularity','engagement','score','access','description'])
    w.writeheader(); w.writerows(registry.get('sources',[]))

# load representation techniques snapshot
repr_path = os.path.join(OUT_DATA,'representation_techniques.json')
if not os.path.exists(repr_path):
    src_repr = '/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv/data/representation_techniques.json'
    if os.path.exists(src_repr):
        pass
repr_data = {'techniques': []}
try:
    with open('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv/data/representation_techniques.json','r') as rf:
        repr_data = json.load(rf)
except Exception:
    repr_data = {'techniques': []}

# render index
html = f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gazzetta di Kyiv — Narrative Monitor</title>
<style>body{{font-family:Arial,sans-serif;background:#0b1020;color:#e7ecff;margin:24px}}h1{{margin:0 0 8px}}.muted{{color:#a9b3d6}}table{{width:100%;border-collapse:collapse;margin-top:16px}}th,td{{border-bottom:1px solid #24305d;padding:8px;text-align:left}}a{{color:#8ec5ff}}</style></head><body>
<h1>Gazzetta di Kyiv</h1><div class="muted">Continuous source intelligence + narrative interpretation.</div>
<p>Updated: {summary['generated_at']}</p>
<h2>Top Narratives (24h)</h2>
<table><thead><tr><th>Narrative</th><th>Mentions(24h)</th><th>Intensity</th><th>Momentum</th><th>Analytical review</th></tr></thead><tbody>
{''.join([f"<tr><td>{n['topic']}</td><td>{n['mentions_24h']}</td><td>{n['intensity_score']}</td><td>{n['momentum']}</td><td>{n['review']}</td></tr>" for n in narrative_reviews]) or '<tr><td colspan="5">No data yet</td></tr>'}
</tbody></table>
<h2>Written Narrative Reviews</h2>
{''.join([f"<article style='margin:14px 0;padding:10px 12px;background:#121a33;border-radius:10px'><h3 style='margin:0 0 6px'>{n['topic'].upper()}</h3><p style='margin:0 0 4px;color:#c7d4ff'>Mentions: {n['mentions_24h']} | Intensity: {n['intensity_score']} | Momentum: {n['momentum']}</p><p style='margin:0'>{n['review']}</p></article>" for n in narrative_reviews]) or '<p>No written reviews yet.</p>'}
<h2>Top Sources</h2>
<table><thead><tr><th>Source</th><th>Platform</th><th>Score</th><th>Access</th><th>Description</th></tr></thead><tbody>
{''.join([f"<tr><td><a target='_blank' href='{s['url']}'>{s['name']}</a></td><td>{s['platform']}</td><td>{s['score']}</td><td>{s['access']}</td><td>{(s.get('description') or '')}</td></tr>" for s in sorted(registry.get('sources',[]), key=lambda x:(x.get('access',''), -(float(x.get('score',0) or 0))))[:60]])}
</tbody></table>
<h2>Representation Techniques Research</h2>
{''.join([f"<div style='margin:10px 0;padding:8px 10px;background:#11172c;border-radius:8px'><b>{t['technique']}</b> — evidence {t['evidence_count']}, priority {t['adoption_priority']}<br>{t['implementation_note']}</div>" for t in repr_data.get('techniques',[])[:10]]) or '<p>No techniques available yet.</p>'}
</body></html>'''

with open(os.path.join(OUT_SITE,'index.html'),'w') as f:
    f.write(html)

print(json.dumps({'ok':True,'narratives':len(narratives),'recent_items_24h':recent_items}))
