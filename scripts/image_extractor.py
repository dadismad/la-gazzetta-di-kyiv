#!/usr/bin/env python3
"""
Standalone Image Extractor for Gazzetta di Kyiv
================================================
Backfill images for existing stories in events_latest.json.

Tier 1: RSS feed media tags (<media:content>, <media:thumbnail>, <enclosure>)
Tier 2: Wikimedia Commons API search (named entities from headline)

Usage:
  # Backfill images for existing events_latest.json (reads raw RSS XML)
  python3 image_extractor.py

  # Process a specific events file
  python3 image_extractor.py --input /path/to/stories.json

  # Process all items, forcing Tier 2 even if Tier 1 found something
  python3 image_extractor.py --force-commons

  # Just show stats, don't modify
  python3 image_extractor.py --dry-run

  # Wikimedia-only mode (skip RSS media tag check, faster if RSS XML missing)
  python3 image_extractor.py --mode commons-only
"""
from __future__ import annotations
import json, os, re, sys, urllib.request, urllib.parse
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

# ── Paths ───────────────────────────────────────────────────────────────

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_INPUT = os.path.join(REPO, 'data', 'normalized', 'events_latest.json')
RAW_DIR = os.path.join(REPO, 'data', 'raw')
NORM_DIR = os.path.join(REPO, 'data', 'normalized')

RSS_NS = {
    'media': 'http://search.yahoo.com/mrss/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
}


# ── Tier 1: RSS media tag extraction ────────────────────────────────────

def extract_image_from_rss_item_et(item: ET.Element) -> str | None:
    """Extract image URL from a single RSS <item> using ElementTree.
       Priority: media:content (widest) > media:thumbnail > image enclosure."""
    mcs = item.findall('.//media:content', RSS_NS)
    if mcs:
        best, best_w = None, -1
        for mc in mcs:
            url = mc.get('url', '')
            typ = mc.get('type', '')
            if url and (not typ or typ.startswith('image/')):
                try:
                    w = int(mc.get('width', 0))
                except (ValueError, TypeError):
                    w = 0
                if w > best_w:
                    best_w, best = w, url
        if best:
            return best

    thumbs = item.findall('.//media:thumbnail', RSS_NS)
    if thumbs:
        url = thumbs[0].get('url', '')
        if url:
            return url

    for enc in item.findall('enclosure'):
        url = enc.get('url', '') or enc.get('href', '')
        if url and enc.get('type', '').startswith('image/'):
            return url
    return None


def find_raw_xml(source_id: str) -> str | None:
    """Find the most recent raw RSS XML for a given source_id."""
    pattern = f"rss_{source_id}_"
    candidates = []
    for f in os.listdir(RAW_DIR):
        if f.startswith(pattern) and f.endswith('.xml'):
            candidates.append(os.path.join(RAW_DIR, f))
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)


def build_url_to_image_map(source_id: str) -> dict[str, str]:
    """Build a {article_url: image_url} dict from raw RSS XML for a source."""
    xml_path = find_raw_xml(source_id)
    if not xml_path:
        return {}
    try:
        xml_text = open(xml_path, 'r', encoding='utf-8').read()
        root = ET.fromstring(xml_text)
    except Exception:
        return {}

    mapping: dict[str, str] = {}
    for item in root.findall('.//item'):
        link = (item.findtext('link') or '').strip()
        if not link:
            continue
        img = extract_image_from_rss_item_et(item)
        if img:
            mapping[link] = img
    return mapping


# ── Tier 2: Wikimedia Commons fallback ─────────────────────────────────

def _extract_entities(headline: str) -> list[str]:
    """Simple named-entity extraction: capitalized multi-word phrases first,
       then single capitalized words."""
    entities = []
    for m in re.finditer(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', headline):
        entities.append(m.group(1).strip())
    if not entities:
        for m in re.finditer(r'\b([A-Z][a-z]{3,})\b', headline):
            entities.append(m.group(1))
    return entities


def wikimedia_search(headline: str) -> str | None:
    """Search Wikimedia Commons for an image matching the headline entities."""
    entities = _extract_entities(headline)
    if not entities:
        return None

    search_terms = [entities[0]]
    words = headline.split()
    if len(words) >= 3:
        search_terms.append(' '.join(words[:3]))

    for term in search_terms:
        try:
            params = urllib.parse.urlencode({
                'action': 'query', 'list': 'search', 'srsearch': term,
                'srnamespace': '6', 'format': 'json', 'srlimit': '5',
            })
            url = f"https://commons.wikimedia.org/w/api.php?{params}"
            req = urllib.request.Request(url, headers={'User-Agent': 'GazzettaPipeline/2.3'})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode('utf-8'))
            for result in data.get('query', {}).get('search', []):
                title = result.get('title', '')
                if title.startswith('File:'):
                    filename = title[5:].replace(' ', '_')
                    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(filename)}"
        except Exception:
            continue
    return None


# ── Backfill engine ────────────────────────────────────────────────────

def backfill_images(items: list[dict], mode: str = 'auto', dry_run: bool = False) -> tuple[int, int, list[str]]:
    """
    Backfill image_url for a list of event items.
    
    Args:
        items: List of event dicts (must have title, source_id, url)
        mode: 'auto' (Tier 1 then Tier 2), 'commons-only' (Tier 2 only)
        dry_run: If True, don't modify items, just report
    
    Returns:
        (tier1_found, tier2_found, logs)
    """
    tier1_count = 0
    tier2_count = 0
    logs = []

    # Group items by source_id for efficient RSS XML lookup
    items_by_source: dict[str, list[dict]] = {}
    for ev in items:
        sid = ev.get('source_id', '')
        if sid:
            items_by_source.setdefault(sid, []).append(ev)

    # Tier 1: Pre-build URL→image maps per source
    source_maps: dict[str, dict[str, str]] = {}
    if mode != 'commons-only':
        for sid in items_by_source:
            source_maps[sid] = build_url_to_image_map(sid)

    for ev in items:
        title = ev.get('title', '')
        sid = ev.get('source_id', '')
        url = ev.get('url', '')

        if ev.get('image_url'):
            continue  # already has an image

        found = False

        # Tier 1
        if mode != 'commons-only' and sid in source_maps:
            img = source_maps[sid].get(url)
            if img:
                if not dry_run:
                    ev['image_url'] = img
                tier1_count += 1
                found = True
                logs.append(f"[Tier1] {sid}: {title[:50]}...")

        # Tier 2
        if not found:
            img = wikimedia_search(title)
            if img:
                if not dry_run:
                    ev['image_url'] = img
                tier2_count += 1
                found = True
                logs.append(f"[Tier2] {sid}: {title[:50]}... -> commons")
            else:
                logs.append(f"[NONE]  {sid}: {title[:50]}...")

    return tier1_count, tier2_count, logs


# ── CLI ─────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Backfill images for Gazzetta di Kyiv stories')
    parser.add_argument('--input', default=DEFAULT_INPUT,
                        help=f'Input JSON file (default: {DEFAULT_INPUT})')
    parser.add_argument('--output', default=None,
                        help='Output JSON file (default: overwrite input)')
    parser.add_argument('--mode', choices=['auto', 'commons-only'], default='auto',
                        help='Extraction mode (default: auto = Tier 1 + Tier 2)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without modifying files')
    parser.add_argument('--stats', action='store_true',
                        help='Just show stats, skip processing')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(json.dumps({'ok': False, 'error': f'Input not found: {args.input}'}))
        sys.exit(1)

    data = json.load(open(args.input, 'r', encoding='utf-8'))
    items = data.get('items', [])

    existing = sum(1 for ev in items if ev.get('image_url'))
    print(f"Input: {args.input}")
    print(f"Total items: {len(items)}")
    print(f"Already have images: {existing}")
    print(f"Mode: {args.mode}")
    print(f"Dry run: {args.dry_run}")
    print()

    if args.stats:
        by_source = {}
        for ev in items:
            sid = ev.get('source_id', 'unknown')
            by_source.setdefault(sid, {'total': 0, 'with_img': 0})
            by_source[sid]['total'] += 1
            if ev.get('image_url'):
                by_source[sid]['with_img'] += 1
        print(f"{'Source':<25} {'Total':>6} {'With Img':>9} {'Coverage':>8}")
        print("-" * 50)
        for sid in sorted(by_source):
            s = by_source[sid]
            pct = s['with_img'] / max(s['total'], 1) * 100
            print(f"{sid:<25} {s['total']:>6} {s['with_img']:>9} {pct:>7.0f}%")
        return

    tier1, tier2, logs = backfill_images(items, mode=args.mode, dry_run=args.dry_run)

    after = sum(1 for ev in items if ev.get('image_url'))
    print(f"Tier 1 (RSS media tags): {tier1} new images")
    print(f"Tier 2 (Wikimedia Commons): {tier2} new images")
    print(f"Total with images: {existing} → {after}")
    print(f"Coverage: {after}/{len(items)} ({after/max(len(items),1)*100:.0f}%)")
    print()

    if not args.dry_run:
        out_path = args.output or args.input
        data['image_extraction'] = {
            'tier1_found': tier1,
            'tier2_found': tier2,
            'total_with_images': after,
            'coverage_pct': round(after / max(len(items), 1) * 100, 1),
            'mode': args.mode,
            'run_at': datetime.now(timezone.utc).isoformat(),
        }
        json.dump(data, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f"Written to: {out_path}")
        print(json.dumps({'ok': True, 'tier1': tier1, 'tier2': tier2, 'total': after}))


if __name__ == '__main__':
    main()
