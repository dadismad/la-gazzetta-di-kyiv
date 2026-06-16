#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_site.py — Static site generator for Gazzetta di Kyiv.

Three responsibilities:
  1. Sync data artifacts from data/ → public/data/
  2. Generate API endpoints (setups, contradictions, regime, divergences, aftershocks)
  3. INJECT shared components (header, footer) into all public/*.html templates

Called by: shipit.sh Stage 2
Side effects: writes to public/data/*.json, public/api/v1/home/*.json, public/*.html
"""

import json
import os
import re
import shutil
from datetime import datetime, timezone

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(PROJECT, "data")
PUBLIC = os.path.join(PROJECT, "public")
SITE_DATA = os.path.join(PROJECT, "public", "data")
API_HOME = os.path.join(PROJECT, "public", "api", "v1", "home")
TEMPLATES = os.path.join(PROJECT, "templates")

SYNC_FILES = [
    "narratives.json",
    "stories.json",
    "stories_in_play.json",
    "living_stories.json",
    "story_registry.json",
    "intelligence_objects.json",
    "asset_claims_latest.json",
    "representation_techniques.json",
    "source_registry_ranked.json",
    "ops_status.json",
    "publish_manifest.json",
    "flows.json",
    "website_stories_latest.json",
    "event_horizon.json",
    "flow_nodes.json",
]

# ── Component injection ──────────────────────────────────────────
# Sentinel markers in HTML files. build_site.py replaces the content
# between these markers with the shared template file.

HEADER_START = "<!-- COMPONENT:HEADER:START -->"
HEADER_END   = "<!-- COMPONENT:HEADER:END -->"
FOOTER_START = "<!-- COMPONENT:FOOTER:START -->"
FOOTER_END   = "<!-- COMPONENT:FOOTER:END -->"


def inject_components():
    """Inject shared header/footer templates into all HTML files.

    For each public/*.html file:
      1. Find HEADER_START...HEADER_END sentinel block
      2. Replace content between them with templates/header.html
      3. Find FOOTER_START...FOOTER_END sentinel block
      4. Replace content between them with templates/footer.html

    Files WITHOUT sentinel markers are SKIPPED (no injection).
    This allows gradual adoption — only pages with markers get injected.
    """
    header_tmpl = os.path.join(TEMPLATES, "header.html")
    footer_tmpl = os.path.join(TEMPLATES, "footer.html")

    if not os.path.exists(header_tmpl) or not os.path.exists(footer_tmpl):
        print("  ⚠ Templates missing — skipping component injection")
        return 0

    with open(header_tmpl) as f:
        header_html = f.read().strip()
    with open(footer_tmpl) as f:
        footer_html = f.read().strip()

    injected = 0
    html_files = [f for f in os.listdir(PUBLIC) if f.endswith(".html")]

    for fname in html_files:
        fpath = os.path.join(PUBLIC, fname)
        with open(fpath) as f:
            html = f.read()

        original = html
        modified = False

        # Inject header
        if HEADER_START in html and HEADER_END in html:
            pattern = re.compile(
                re.escape(HEADER_START) + r".*?" + re.escape(HEADER_END),
                re.DOTALL
            )
            replacement = HEADER_START + "\n" + header_html + "\n" + HEADER_END
            html = pattern.sub(replacement, html)
            if html != original:
                modified = True

        # Inject footer
        if FOOTER_START in html and FOOTER_END in html:
            pattern = re.compile(
                re.escape(FOOTER_START) + r".*?" + re.escape(FOOTER_END),
                re.DOTALL
            )
            replacement = FOOTER_START + "\n" + footer_html + "\n" + FOOTER_END
            html = pattern.sub(replacement, html)
            if html != original:
                modified = True

        if modified:
            with open(fpath, "w") as f:
                f.write(html)
            injected += 1

    if injected > 0:
        print(f"  ✓ Components injected into {injected}/{len(html_files)} HTML files")
    else:
        print(f"  ⚠ No HTML files had sentinel markers — add {HEADER_START}...{HEADER_END} to enable")
    return injected


def cache_bust_assets():
    """Append Unix timestamp (?t=N) to all script and style imports in every HTML file.

    This guarantees CDN cache bypass on every build — when you push a design change,
    users see it instantly instead of waiting for CDN TTL to expire.

    Modifies files in-place in public/.
    """
    import time
    ts = str(int(time.time()))
    modified = 0

    html_files = [f for f in os.listdir(PUBLIC) if f.endswith(".html")]

    for fname in html_files:
        fpath = os.path.join(PUBLIC, fname)
        with open(fpath) as f:
            html = f.read()

        original = html

        # Append ?t=TS to <link rel="stylesheet" href="...">
        html = re.sub(
            r'(<link\s+[^>]*href=")([^"]+\.css)(")',
            rf'\1\2?t={ts}\3',
            html
        )

        # Append ?t=TS to <script src="...">
        html = re.sub(
            r'(<script\s+[^>]*src=")([^"]+\.js)(")',
            rf'\1\2?t={ts}\3',
            html
        )

        if html != original:
            with open(fpath, "w") as f:
                f.write(html)
            modified += 1

    if modified > 0:
        print(f"  ✓ Cache bust (?t={ts}) applied to {modified} HTML files")
    return modified


def sync_data():
    """Sync data/ → public/data/ with smart merge for stories.json."""
    os.makedirs(SITE_DATA, exist_ok=True)
    os.makedirs(API_HOME, exist_ok=True)

    synced = 0
    for fname in SYNC_FILES:
        src = os.path.join(DATA, fname)
        dst = os.path.join(SITE_DATA, fname)
        if os.path.exists(src):
            if fname == "stories.json" and os.path.exists(dst):
                with open(src) as fs:
                    data_stories = json.load(fs).get("stories", [])
                with open(dst) as fd:
                    site_stories = json.load(fd).get("stories", [])
                data_ids = {s.get("story_id") for s in data_stories}
                site_only = [s for s in site_stories if s.get("story_id") not in data_ids]
                if site_only:
                    merged = data_stories + site_only
                    with open(dst) as fd:
                        site_doc = json.load(fd)
                    site_doc["stories"] = merged
                    with open(dst, "w") as fd:
                        json.dump(site_doc, fd, indent=2)
                    synced += 1
                    continue
            shutil.copy2(src, dst)
            synced += 1

    return synced


def generate_apis():
    """Generate API endpoint JSON files."""
    now = datetime.now(timezone.utc).isoformat()

    flows_path = os.path.join(DATA, "flows.json")
    setups_count = 0
    contradictions_count = 0

    if os.path.exists(flows_path):
        with open(flows_path) as f:
            flows = json.load(f)
        setups_count = len(flows.get("flows", []))
        for flow in flows.get("flows", []):
            if flow.get("confidence_level") == "medium" or flow.get("confidence_pct", 100) < 70:
                contradictions_count += 1
    contradictions_count = max(contradictions_count, 1)

    api_files = {
        "setups.json": {"generated_at": now, "count": setups_count, "setups": []},
        "contradictions.json": {"generated_at": now, "count": contradictions_count, "contradictions": []},
        "regime.json": {"generated_at": now, "regime": "mixed", "confidence": 78},
        "divergences.json": {"generated_at": now, "count": 0, "divergences": []},
        "aftershocks.json": {"generated_at": now, "count": 0, "aftershocks": []},
    }

    for fname, data in api_files.items():
        dst = os.path.join(API_HOME, fname)
        with open(dst, "w") as f:
            json.dump(data, f, indent=2)

    return setups_count, contradictions_count


def main():
    print("── build_site.py ──")

    # 1. Sync data
    synced = sync_data()
    print(f"  ✓ Data synced: {synced}/{len(SYNC_FILES)} files")

    # 2. Inject shared components
    injected = inject_components()

    # 3. Cache-bust all asset references (CDN bypass)
    busted = cache_bust_assets()

    # 4. Generate APIs
    setups_count, contradictions_count = generate_apis()
    print(f"  ✓ API endpoints: {setups_count} setups, {contradictions_count} contradictions")

    now = datetime.now(timezone.utc).isoformat()
    result = {
        "ok": True,
        "synced_at": now,
        "synced_files": synced,
        "components_injected": injected,
        "cache_busted": busted,
        "setups": setups_count,
        "contradictions": contradictions_count,
        "website_stories": os.path.exists(os.path.join(SITE_DATA, "website_stories_latest.json")),
        "concrete_stories": os.path.exists(os.path.join(SITE_DATA, "stories.json")),
        "living_stories": os.path.exists(os.path.join(SITE_DATA, "living_stories.json")),
        "story_registry": os.path.exists(os.path.join(SITE_DATA, "story_registry.json")),
    }

    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
