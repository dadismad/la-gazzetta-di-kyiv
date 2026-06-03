#!/usr/bin/env python3
"""
Multi-source collector v2.1 — pulls from RSS, Reddit, and (future) API sources
configured in data/config/data_sources_v2.json. Expanded source registry covers:
- China tech execution (Nikkei Asia, SCMP, ASPI, ITIF, WIPO, 5YP documents)
- Dollar architecture (IMF COFER, BIS, SWIFT, BRICS communiqués)
- EU structural (Eurostat, YouGov, Eurobarometer, Frontex)
- Abundance tech (Fusion Industry Assoc, BryceTech, Longevity.Technology, NASA/ESA)
- Blockchain/agentic (RWA.xyz, DefiLlama, Dune)
- Positive breakthroughs (ScienceDaily, MIT Tech Review, ARK, Epoch AI)
- Geopolitics events (Telegram intel monitor, Reuters, Al Jazeera)

To add a new ingestion method (API, structured scrape), add a function below
and register it in main() with the appropriate source type from the config.
"""
from __future__ import annotations
import json, os, re, time, urllib.request
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(REPO, 'data', 'config', 'data_sources_v2.json')
RAW_DIR = os.path.join(REPO, 'data', 'raw')
NORM_DIR = os.path.join(REPO, 'data', 'normalized')
OUT = os.path.join(NORM_DIR, 'events_latest.json')


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (gazzetta-pipeline/1.0)'})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode('utf-8', errors='replace')


def parse_rss(xml_text: str, source_id: str, topic: str):
    out = []
    try:
        root = ET.fromstring(xml_text)
        items = root.findall('.//item')[:25]
        for it in items:
            title = (it.findtext('title') or '').strip()
            link = (it.findtext('link') or '').strip()
            pub = (it.findtext('pubDate') or '').strip()
            if not title:
                continue
            out.append({
                'source_type': 'rss', 'source_id': source_id, 'topic': topic,
                'title': title, 'url': link, 'published_at': pub,
                'text': title
            })
    except Exception:
        pass
    return out


def parse_reddit(json_text: str, source_id: str, topic: str):
    out = []
    try:
        j = json.loads(json_text)
        for child in (j.get('data', {}).get('children', []) or [])[:25]:
            d = child.get('data', {})
            title = (d.get('title') or '').strip()
            if not title:
                continue
            out.append({
                'source_type': 'reddit', 'source_id': source_id, 'topic': topic,
                'title': title,
                'url': d.get('url_overridden_by_dest') or d.get('url') or '',
                'published_at': d.get('created_utc'),
                'text': f"{title}\n{(d.get('selftext') or '')[:500]}"
            })
    except Exception:
        pass
    return out


def infer_tags(text: str):
    t = text.lower()
    tags = []
    for k in ['inflation','rates','oil','gas','ai','nato','ukraine','russia','china','election','crypto']:
        if re.search(rf'\\b{k}\\b', t):
            tags.append(k)
    return tags


def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(NORM_DIR, exist_ok=True)
    cfg = json.load(open(CFG, 'r', encoding='utf-8'))
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

    events, failures = [], []
    for src in cfg.get('rss', []):
        try:
            body = fetch(src['url'])
            open(os.path.join(RAW_DIR, f"rss_{src['id']}_{ts}.xml"), 'w', encoding='utf-8').write(body)
            events.extend(parse_rss(body, src['id'], src.get('topic', 'macro')))
        except Exception as e:
            failures.append({'source': src['id'], 'type': 'rss', 'error': str(e)[:180]})

    for src in cfg.get('reddit', []):
        try:
            body = fetch(src['url'])
            open(os.path.join(RAW_DIR, f"reddit_{src['id']}_{ts}.json"), 'w', encoding='utf-8').write(body)
            events.extend(parse_reddit(body, src['id'], src.get('topic', 'macro')))
        except Exception as e:
            failures.append({'source': src['id'], 'type': 'reddit', 'error': str(e)[:180]})

    for ev in events:
        ev['tags'] = infer_tags(f"{ev.get('title','')} {ev.get('text','')}")

    out = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'event_count': len(events),
        'failures': failures,
        'stale': len(events) == 0,
        'items': events[:300]
    }
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(json.dumps({'ok': True, 'events': len(events), 'failures': len(failures), 'output': OUT}))


if __name__ == '__main__':
    main()
