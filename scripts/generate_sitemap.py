#!/usr/bin/env python3
"""Generate sitemap.xml from current site state. Run in pipeline chain."""
import json, os
from datetime import datetime
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DOMAIN = "https://www.lagazzettadikyiv.com"
NOW = datetime.utcnow().strftime("%Y-%m-%d")

PRODUCTS = [
    ("", "hourly", "1.0"),
    ("stories.html", "hourly", "0.9"),
    ("flows.html", "hourly", "0.9"),
    ("trades.html", "hourly", "0.9"),
    ("signal.html", "hourly", "0.8"),
    ("track.html", "daily", "0.7"),
    ("story.html", "hourly", "0.8"),
    ("capital.html", "weekly", "0.6"),
    ("about.html", "monthly", "0.4"),
]

def main():
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
    sitemap += '  xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    
    for path, freq, pri in PRODUCTS:
        url = f"{DOMAIN}/{path}" if path else DOMAIN
        sitemap += f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{NOW}</lastmod>\n"
        sitemap += f"    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n"
        if path:
            sitemap += f'    <xhtml:link rel="alternate" hreflang="en" href="{url}"/>\n'
            sitemap += f'    <xhtml:link rel="alternate" hreflang="ru" href="{DOMAIN}/ru/{path.replace(".html","/")}"/>\n'
        sitemap += "  </url>\n"
    
    # Story pages from stories.json
    stories_path = PROJECT / "data" / "stories.json"
    if stories_path.exists():
        with open(stories_path) as f:
            data = json.load(f)
        seen = set()
        for s in [data.get('lead')] + data.get('stories', []):
            if not s: continue
            sid = s.get('story_id') or s.get('id', '')
            if sid and sid not in seen:
                seen.add(sid)
                sitemap += f"  <url>\n    <loc>{DOMAIN}/story.html?id={sid}</loc>\n"
                sitemap += f"    <lastmod>{NOW}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>0.6</priority>\n  </url>\n"
    
    sitemap += "</urlset>\n"
    
    out = PROJECT / "site" / "sitemap.xml"
    out.write_text(sitemap)
    print(f"sitemap.xml: {len(PRODUCTS)} pages + {len(seen)} stories -> {out}")

if __name__ == "__main__":
    main()
