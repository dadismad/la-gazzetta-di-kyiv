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
    review = f"Intensity {intensity}/100; momentum {momentum}; tactical relevance {'high' if topic in ['rates','inflation','oil','gas','ukraine','china','sanctions'] else 'medium'}."
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

# render index
html = f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gazzetta di Kyiv — Narrative Monitor</title>
<style>body{{font-family:Arial,sans-serif;background:#0b1020;color:#e7ecff;margin:24px}}h1{{margin:0 0 8px}}.muted{{color:#a9b3d6}}table{{width:100%;border-collapse:collapse;margin-top:16px}}th,td{{border-bottom:1px solid #24305d;padding:8px;text-align:left}}a{{color:#8ec5ff}}</style></head><body>
<h1>Gazzetta di Kyiv</h1><div class="muted">Continuous source intelligence + narrative interpretation.</div>
<p>Updated: {summary['generated_at']}</p>
<h2>Top Narratives (24h)</h2>
<table><thead><tr><th>Narrative</th><th>Mentions(24h)</th><th>Intensity</th><th>Momentum</th><th>Analytical review</th></tr></thead><tbody>
{''.join([f"<tr><td>{n['topic']}</td><td>{n['mentions_24h']}</td><td>{n['intensity_score']}</td><td>{n['momentum']}</td><td>{n['review']}</td></tr>" for n in narrative_reviews]) or '<tr><td colspan="5">No data yet</td></tr>'}
</tbody></table>
<h2>Top Sources</h2>
<table><thead><tr><th>Source</th><th>Platform</th><th>Score</th><th>Access</th><th>Description</th></tr></thead><tbody>
{''.join([f"<tr><td><a target='_blank' href='{s['url']}'>{s['name']}</a></td><td>{s['platform']}</td><td>{s['score']}</td><td>{s['access']}</td><td>{(s.get('description') or '')}</td></tr>" for s in sorted(registry.get('sources',[]), key=lambda x:(x.get('access',''), -(float(x.get('score',0) or 0))))[:60]])}
</tbody></table>
</body></html>'''

with open(os.path.join(OUT_SITE,'index.html'),'w') as f:
    f.write(html)

print(json.dumps({'ok':True,'narratives':len(narratives),'recent_items_24h':recent_items}))
