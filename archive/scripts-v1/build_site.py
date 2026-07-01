#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_site.py v2.0 — Inject shared components + cache-bust assets.

Two responsibilities:
  1. Inject masthead/footer from templates/ into all public/*.html
  2. Add cache-bust timestamps (?t=...) to unhashed asset references

No longer: syncs data/ → public/data/ (db_to_json.py v2 does this directly).
No longer: generates API endpoints (removed — no Signal/Trades/Track).

Usage: python3 scripts/build_site.py
"""

import json, os, re
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
PUBLIC = PROJECT / "public"
TEMPLATES = PROJECT / "templates"

# ── Component injection markers ──
HEADER_START = "<!-- COMPONENT:HEADER:START -->"
HEADER_END   = "<!-- COMPONENT:HEADER:END -->"
FOOTER_START = "<!-- COMPONENT:FOOTER:START -->"
FOOTER_END   = "<!-- COMPONENT:FOOTER:END -->"


def inject_components():
    """Inject shared header/footer from templates/ into all public/*.html files."""
    header_path = TEMPLATES / "header.html"
    footer_path = TEMPLATES / "footer.html"
    
    if not header_path.exists() or not footer_path.exists():
        print("  ⚠ Templates missing — skipping component injection")
        return 0
    
    header_html = header_path.read_text().strip()
    footer_html = footer_path.read_text().strip()
    
    html_files = sorted(PUBLIC.glob("*.html"))
    injected = 0
    
    for html_path in html_files:
        html = html_path.read_text()
        modified = False
        
        # Inject header
        if HEADER_START in html and HEADER_END in html:
            pattern = re.escape(HEADER_START) + r".*?" + re.escape(HEADER_END)
            replacement = HEADER_START + "\n" + header_html + "\n" + HEADER_END
            html = re.sub(pattern, replacement, html, flags=re.DOTALL)
            modified = True
        
        # Inject footer
        if FOOTER_START in html and FOOTER_END in html:
            pattern = re.escape(FOOTER_START) + r".*?" + re.escape(FOOTER_END)
            replacement = FOOTER_START + "\n" + footer_html + "\n" + FOOTER_END
            html = re.sub(pattern, replacement, html, flags=re.DOTALL)
            modified = True
        
        if modified:
            html_path.write_text(html)
            injected += 1
    
    if injected > 0:
        print(f"  ✓ Components injected into {injected}/{len(html_files)} HTML files")
    else:
        print(f"  ⚠ No HTML files had sentinel markers")
    return injected


def cache_bust_assets():
    """DEPRECATED: build_hashed_assets.py handles immutability via content hashing.
    This function was a no-op (replacer always returned original match unchanged).
    Kept as stub for backward compatibility — always returns 0."""
    print("  ⚠ cache_bust_assets() is deprecated — build_hashed_assets.py handles this")
    return 0


def main():
    print("── build_site.py v2.0 ──")
    
    # 1. Inject shared components (masthead + footer)
    injected = inject_components()
    
    # 2. Cache-bust asset references
    busted = cache_bust_assets()
    
    now = datetime.now(timezone.utc).isoformat()
    result = {
        "ok": True,
        "built_at": now,
        "components_injected": injected,
        "cache_busted": busted,
    }
    
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
