#!/usr/bin/env python3

"""
Multi-source collector v2.2 — pulls from RSS & Reddit sources configured in
data/config/data_sources_v2.json (category grouping) and data/source_registry_ranked.json
(operational feed URLs). Includes Tier 1 (RSS media tags) + Tier 2 (Wikimedia Commons)
image extraction.

Image extraction priority:
  Tier 1a: <media:content> from RSS item (pick largest width)
  Tier 1b: <media:thumbnail> from RSS item
  Tier 1c: <enclosure type="image/*"> from RSS item
  Tier 2:  Wikimedia Commons API search for named entities in headline
"""
from __future__ import annotations
import json, os, re, time, urllib.request, urllib.parse
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(REPO, 'data', 'config', 'data_sources_v2.json')
REGISTRY = os.path.join(REPO, 'data', 'source_registry_ranked.json')
RAW_DIR = os.path.join(REPO, 'data', 'raw')
NORM_DIR = os.path.join(REPO, 'data', 'normalized')
OUT = os.path.join(NORM_DIR, 'events_latest.json')

# Namespace map for ElementTree-based RSS image extraction
RSS_NS = {
    'media': 'http://search.yahoo.com/mrss/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'dc': 'http://purl.org/dc/elements/1.1/',
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (gazzetta-pipeline/2.2)'})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode('utf-8', errors='replace')


# ── Tier 1: RSS image extraction ────────────────────────────────────────

def extract_rss_image_et(item: ET.Element) -> str | None:
    """Extract image URL from a single RSS <item> using ElementTree.
       Priority: media:content (widest) > media:thumbnail > image enclosure."""
    # 1) media:content — pick largest by width
    mcs = item.findall('.//media:content', RSS_NS)
    if mcs:
        best = None
        best_w = -1
        for mc in mcs:
            url = mc.get('url', '')
            typ = mc.get('type', '')
            if url and (not typ or typ.startswith('image/')):
                try:
                    w = int(mc.get('width', 0))
                except (ValueError, TypeError):
                    w = 0
                if w > best_w:
                    best_w = w
                    best = url
        if best:
            return best

    # 2) media:thumbnail
    thumbs = item.findall('.//media:thumbnail', RSS_NS)
    if thumbs:
        url = thumbs[0].get('url', '')
        if url:
            return url

    # 3) enclosure with image type
    for enc in item.findall('enclosure'):
        url = enc.get('url', '') or enc.get('href', '')
        typ = enc.get('type', '')
        if url and typ.startswith('image/'):
            return url

    return None


def extract_rss_image_feedparser(entry) -> str | None:
    """Extract image from a feedparser entry. Priority: media_content (widest)
       > media_thumbnail > enclosures."""
    # 1) media_content — pick largest by width
    mc_list = getattr(entry, 'media_content', None) or []
    if mc_list:
        best = None
        best_w = -1
        for mc in mc_list:
            url = mc.get('url', '')
            typ = mc.get('type', '')
            if url and (not typ or typ.startswith('image/')):
                try:
                    w = int(mc.get('width', 0))
                except (ValueError, TypeError):
                    w = 0
                if w > best_w:
                    best_w = w
                    best = url
        if best:
            return best

    # 2) media_thumbnail
    thumbs = getattr(entry, 'media_thumbnail', None) or []
    if thumbs:
        url = thumbs[0].get('url', '')
        if url:
            return url

    # 3) enclosures with image type
    encs = getattr(entry, 'enclosures', None) or []
    for enc in encs:
        url = enc.get('href', '') or enc.get('url', '')
        typ = enc.get('type', '') or enc.get('mimeType', '')
        if url and typ.startswith('image/'):
            return url

    return None


def extract_image_from_rss_item(item: ET.Element) -> str | None:
    """Top-level Tier 1 extraction — tries feedparser first, falls back to raw ET."""
    try:
        import feedparser
        xml = ET.tostring(item, encoding='unicode')
        # Wrap a single item as a minimal RSS doc so feedparser can parse it
        feed = feedparser.parse(f"<rss version='2.0'><channel>{xml}</channel></rss>")
        if feed.entries:
            img = extract_rss_image_feedparser(feed.entries[0])
            if img:
                return img
    except Exception:
        pass
    return extract_rss_image_et(item)


# ── Tier 2: Wikimedia Commons fallback ──────────────────────────────────

def _extract_entities(headline: str) -> list[str]:
    """Simple named-entity extraction from a headline: grab capitalized phrases."""
    entities = []
    # Multi-word capitalized phrases (preferred)
    for m in re.finditer(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', headline):
        entities.append(m.group(1).strip())
    # Single-word capitalized nouns (fallback)
    if not entities:
        for m in re.finditer(r'\b([A-Z][a-z]{3,})\b', headline):
            entities.append(m.group(1))
    return entities


def wikimedia_fallback(headline: str) -> str | None:
    """Tier 2 — search Wikimedia Commons for an image matching named entities
       in the headline. Returns the first image URL found, or None."""
    entities = _extract_entities(headline)
    if not entities:
        return None

    # Try the best entity first, then the first few words of the headline
    search_terms = [entities[0]]
    words = headline.split()
    if len(words) >= 3:
        search_terms.append(' '.join(words[:3]))

    for term in search_terms:
        try:
            params = urllib.parse.urlencode({
                'action': 'query',
                'list': 'search',
                'srsearch': term,
                'srnamespace': '6',  # File: namespace
                'format': 'json',
                'srlimit': '5',
            })
            url = f"https://commons.wikimedia.org/w/api.php?{params}"
            req = urllib.request.Request(url, headers={'User-Agent': 'GazzettaPipeline/2.2'})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode('utf-8'))

            for result in data.get('query', {}).get('search', []):
                title = result.get('title', '')
                if title.startswith('File:'):
                    filename = title[5:].replace(' ', '_')
                    img_url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(filename)}"
                    return img_url
        except Exception:
            continue
    return None


# ── RSS parsing ─────────────────────────────────────────────────────────

def parse_rss(xml_text: str, source_id: str, topic: str):
    """Parse RSS XML and extract articles with images.
       Tier 1 extracts images from RSS media tags; Tier 2 falls back to
       Wikimedia Commons for items missing an image."""
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

            # Tier 1: extract image from RSS media tags
            image_url = extract_image_from_rss_item(it)

            # Tier 2: Wikimedia Commons fallback
            if not image_url:
                image_url = wikimedia_fallback(title)

            out.append({
                'source_type': 'rss', 'source_id': source_id, 'topic': topic,
                'title': title, 'url': link, 'published_at': pub,
                'text': title,
                'image_url': image_url or None,
            })
    except Exception:
        pass
    return out


# ── Reddit parsing ──────────────────────────────────────────────────────

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
                'text': f"{title}\n{(d.get('selftext') or '')[:500]}",
                'image_url': None,
            })
    except Exception:
        pass
    return out


# ── Tagging ─────────────────────────────────────────────────────────────

def infer_tags(text: str):
    t = text.lower()
    tags = []
    for k in ['inflation','rates','oil','gas','ai','nato','ukraine','russia','china','election','crypto']:
        if re.search(rf'\\b{k}\\b', t):
            tags.append(k)
    return tags


# ── Main ────────────────────────────────────────────────────────────────

def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(NORM_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

    # Load operational source registry (has actual RSS feed URLs)
    reg = json.load(open(REGISTRY, 'r', encoding='utf-8'))

    events, failures = [], []

    # Iterate RSS sources from the operational registry
    for src in reg.get('sources', []):
        if src.get('platform') != 'rss':
            continue
        sid = src['source_id']
        feed_url = src['url']
        try:
            body = fetch(feed_url)
            raw_path = os.path.join(RAW_DIR, f"rss_{sid}_{ts}.xml")
            with open(raw_path, 'w', encoding='utf-8') as f:
                f.write(body)
            events.extend(parse_rss(body, sid, 'macro'))
        except Exception as e:
            failures.append({'source': sid, 'type': 'rss', 'error': str(e)[:180]})

    # Iterate Reddit sources
    for src in reg.get('sources', []):
        if src.get('platform') != 'reddit':
            continue
        sid = src['source_id']
        feed_url = src['url']
        try:
            body = fetch(feed_url)
            raw_path = os.path.join(RAW_DIR, f"reddit_{sid}_{ts}.json")
            with open(raw_path, 'w', encoding='utf-8') as f:
                f.write(body)
            events.extend(parse_reddit(body, sid, 'macro'))
        except Exception as e:
            failures.append({'source': sid, 'type': 'reddit', 'error': str(e)[:180]})

    # Apply tags
    for ev in events:
        ev['tags'] = infer_tags(f"{ev.get('title','')} {ev.get('text','')}")

    out = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'event_count': len(events),
        'failures': failures,
        'stale': len(events) == 0,
        'items': events[:300],
    }
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(json.dumps({'ok': True, 'events': len(events), 'failures': len(failures), 'output': OUT}))


if __name__ == '__main__':
    main()
