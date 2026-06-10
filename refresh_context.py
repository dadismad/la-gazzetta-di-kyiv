#!/usr/bin/env python3
"""refresh_context.py — Grounding Protocol for Hermes
Checks git sync, data freshness, and live site parity.
Run at session start and after any significant change.
"""
import json
import os
import re
import sys
import subprocess
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests

PROJECT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(PROJECT, "data")
SITE_URL = "https://www.lagazzettadikyiv.com"

# ── State (populated by checks) ───────────────────
story_count = 0
flows_list: list = []
last_upd = "unknown"

# ── ANSI ──────────────────────────────────────────
GREEN  = "\033[0;32m"
YELLOW = "\033[0;33m"
RED    = "\033[0;31m"
BOLD   = "\033[1m"
NC     = "\033[0m"

def ok(s):   return f"{GREEN}{s}{NC}"
def warn(s): return f"{YELLOW}{s}{NC}"
def bad(s):  return f"{RED}{s}{NC}"
def hdr(s):  return f"{BOLD}{s}{NC}"

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=PROJECT)

# ── §0: TASKS — count open items in tasks.md ──────
tasks_path = os.path.join(PROJECT, "tasks.md")
open_tasks = 0
total_tasks = 0
if os.path.exists(tasks_path):
    with open(tasks_path) as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("- [ ]"):
                open_tasks += 1
                total_tasks += 1
            elif stripped.startswith("- [x]"):
                total_tasks += 1
    completed = total_tasks - open_tasks
    pct = int(completed / total_tasks * 100) if total_tasks else 0
    print(f"{hdr('§0  TASKS')}")
    print(f"    {completed}/{total_tasks} completed ({pct}%)  |  {ok(f'{open_tasks} open') if open_tasks == 0 else warn(f'{open_tasks} open')}")

# ── §1: GIT CHECK ─────────────────────────────────
print(f"\n{hdr('═══ GROUNDING PROTOCOL ═══')}")
print(f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
print()

run("git fetch origin main 2>/dev/null")
behind = run("git rev-list --count HEAD..origin/main 2>/dev/null").stdout.strip()
ahead  = run("git rev-list --count origin/main..HEAD 2>/dev/null").stdout.strip()
branch = run("git branch --show-current").stdout.strip()
commit = run("git rev-parse --short HEAD").stdout.strip()

print(f"{hdr('§1  GIT')}")
print(f"    branch : {branch}")
print(f"    commit : {commit}")
if behind and behind != "0":
    print(f"    remote : {bad(f'{behind} commits BEHIND origin/main — PULL NEEDED')}")
elif ahead and ahead != "0":
    print(f"    remote : {warn(f'{ahead} commits AHEAD of origin/main')}")
else:
    print(f"    remote : {ok('in sync with origin/main')}")

# ── §2: DATA CHECK ────────────────────────────────
print(f"\n{hdr('§2  DATA')}")
stories_path = os.path.join(DATA, "stories.json")
flows_path   = os.path.join(DATA, "flows.json")

if os.path.exists(stories_path):
    with open(stories_path) as f:
        stories_doc = json.load(f)
    stories_list = stories_doc.get("stories", [])
    story_count = len(stories_list)
    last_upd = stories_doc.get("last_updated") or stories_doc.get("generated_at") or "unknown"
    # Get most recent story timestamp
    max_ts = None
    for s in stories_list:
        ts = s.get("generated_at") or s.get("timestamp") or s.get("date")
        if ts:
            if max_ts is None or ts > max_ts:
                max_ts = ts
    print(f"    stories         : {story_count}")
    print(f"    last_updated    : {last_upd}")
    print(f"    newest story    : {max_ts or 'unknown'}")
else:
    print(f"    {bad('stories.json NOT FOUND')}")

if os.path.exists(flows_path):
    with open(flows_path) as f:
        flows_doc = json.load(f)
    flows_list = flows_doc.get("flows", [])
    inflows = sum(1 for fl in flows_list if fl.get("direction") == "in")
    outflows = sum(1 for fl in flows_list if fl.get("direction") == "out")
    print(f"    flows           : {len(flows_list)} ({inflows} in, {outflows} out)")
else:
    print(f"    {bad('flows.json NOT FOUND')}")

# ── §3: LIVE SITE CHECK ───────────────────────────
print(f"\n{hdr('§3  LIVE SITE')}")
try:
    resp = requests.head(SITE_URL, timeout=10, allow_redirects=True)
    live_status = resp.status_code
    live_last_mod = resp.headers.get("Last-Modified", "missing")
    live_etag = resp.headers.get("ETag", "missing")
    live_cc = resp.headers.get("Cache-Control", "missing")

    print(f"    status          : {ok(str(live_status)) if live_status == 200 else bad(str(live_status))}")
    print(f"    Last-Modified   : {live_last_mod}")
    print(f"    ETag            : {live_etag}")
    print(f"    Cache-Control   : {live_cc}")
except Exception as e:
    live_status = None
    live_etag = None
    live_last_mod = None
    print(f"    {bad(f'FETCH FAILED: {e}')}")

# ── §4: DRIFT DETECTION ───────────────────────────
print(f"\n{hdr('§4  DRIFT DETECTION')}")
drift = False

# Check if local last_updated matches live Last-Modified
if live_last_mod and live_last_mod != "missing" and last_upd != "unknown":
    try:
        live_dt = parsedate_to_datetime(live_last_mod)
        local_dt = datetime.fromisoformat(last_upd.replace("Z", "+00:00"))

        delta = abs((live_dt - local_dt).total_seconds())
        if delta > 300:  # >5 min drift
            drift = True
            print(f"    {bad('CONTEXT DRIFT DETECTED: Local version is not live.')}")
            print(f"    local  : {local_dt.isoformat()}")
            print(f"    live   : {live_dt.isoformat()}")
            print(f"    delta  : {delta:.0f}s")
        else:
            print(f"    {ok('Local ↔ Live timestamps match (within 5min)')}")
    except Exception as e:
        print(f"    {warn(f'Could not compare timestamps: {e}')}")
elif live_last_mod is None:
    print(f"    {warn('Skipped — live fetch failed')}")
else:
    print(f"    {warn('Skipped — missing local or live timestamp')}")

# Check if local ETag is stale
if not drift and live_etag and live_etag != "missing":
    build_manifest = os.path.join(PROJECT, "site", "build-manifest.json")
    if os.path.exists(build_manifest):
        with open(build_manifest) as f:
            manifest = json.load(f)
        manifest_age = os.path.getmtime(build_manifest)
        manifest_dt = datetime.fromtimestamp(manifest_age, tz=timezone.utc)
        age_s = time.time() - manifest_age
        if age_s > 3600:
            print(f"    {warn(f'Build manifest is {age_s/60:.0f}min old — may need rebuild')}")
    else:
        print(f"    {warn('No build-manifest.json — site/ may not be built')}")

# ── §4.5: PRE-DEPLOY STRUCTURAL CHECK ──────────────
print(f"\n{hdr('§4.5 PRE-DEPLOY CHECK')}")

# 4.5a: Uncommitted changes warning
dirty = run("git status --porcelain").stdout.strip()
if dirty:
    dirty_count = len(dirty.split("\n"))
    print(f"    {warn(f'{dirty_count} uncommitted file(s) — run scripts/safe_git.py before destructive git ops')}")
else:
    print(f"    {ok('working tree clean')}")

# 4.5b: Structural integrity of compiled HTML
site_dir = os.path.join(PROJECT, "site")
critical_elements = {
    "index.html": [
        ("hero section", r'<section[^>]*class="[^"]*hero[^"]*"'),
        ("product nav", r'class="[^"]*product-nav[^"]*"'),
        ("container collapsible (Stories)", r'id="storiesTeaser"'),
        ("heroProductCount span", r'id="heroProductCount"'),
        ("storyFreshness span", r'id="storyFreshness"'),
        ("flowFreshness span", r'id="flowFreshness"'),
    ],
    "flow-nodes.html": [
        ("flow-nodes page", r'flow-nodes'),
    ],
}
pages_ok = 0
pages_warn = 0
for page, checks in critical_elements.items():
    page_path = os.path.join(site_dir, page)
    if not os.path.exists(page_path):
        print(f"    {bad(f'MISSING PAGE: {page}')}")
        pages_warn += 1
        continue
    with open(page_path) as f:
        html = f.read()
    page_ok = True
    for name, pattern in checks:
        if not re.search(pattern, html):
            print(f"    {bad(f'MISSING in {page}: {name}')}")
            pages_warn += 1
            page_ok = False
    if page_ok:
        print(f"    {ok(f'{page}: all elements present')}")
        pages_ok += 1

# 4.5c: Orphan detection — no stories without linked flows
orphan_warn = 0
try:
    stories_file = os.path.join(PROJECT, "data", "stories.json")
    flows_file = os.path.join(PROJECT, "data", "flows.json")
    if os.path.exists(stories_file) and os.path.exists(flows_file):
        import json as _json
        with open(stories_file) as f: stories_d = _json.load(f)
        with open(flows_file) as f: flows_d = _json.load(f)
        flow_ids = {f.get("id", "") for f in flows_d.get("flows", [])}
        flow_ids.update({f.get("story_id", "") for f in flows_d.get("flows", [])})
        orphan_stories = []
        for s in stories_d.get("stories", []):
            impacted = s.get("impacted_flows", [])
            sid = s.get("story_id", "")
            if not impacted:
                # Check if there's a flow with matching story_id
                flow_match = f"flow_{sid}" in flow_ids
                if not flow_match:
                    orphan_stories.append(sid)
        if orphan_stories:
            print(f"    {warn(f'{len(orphan_stories)} orphaned stories (no linked flows)')}")
            orphan_warn = len(orphan_stories)
        else:
            print(f"    {ok('zero orphaned stories')}")
except Exception as e:
    print(f"    {warn(f'Orphan check skipped: {e}')}")

# 4.5d: Live product page 200 check
import urllib.request
product_pages = [
    "flow-nodes.html",
    "event_horizon.html",
    "stories.html",
    "flows.html",
    "signal.html",
    "track.html",
    "trades.html",
]
for pp in product_pages:
    try:
        req = urllib.request.Request(f"{SITE_URL}/{pp}", method="HEAD")
        resp = urllib.request.urlopen(req, timeout=10)
        if resp.status == 200:
            print(f"    {ok(f'{pp}: 200')}")
            pages_ok += 1
        else:
            print(f"    {bad(f'{pp}: {resp.status}')}")
            pages_warn += 1
    except Exception as e:
        print(f"    {bad(f'{pp}: FAILED — {e}')}")
        pages_warn += 1

if pages_warn > 0:
    print(f"\n    {bad(f'PRE-DEPLOY BLOCKED: {pages_warn} issue(s). Fix before deploying.')}")
    drift = True  # Block deploy
else:
    print(f"    {ok('All critical elements + product pages verified — deploy safe')}")

# ── §5: SYSTEM TRUTH ───────────────────────────────
print(f"\n{hdr('═══ CURRENT SYSTEM TRUTH ═══')}")
print(f"  Git         : {branch} @ {commit}  {'⚠ BEHIND' if (behind and behind != '0') else '✓'}")
print(f"  Stories     : {story_count if os.path.exists(stories_path) else 'N/A'}")
print(f"  Flows       : {len(flows_list) if os.path.exists(flows_path) else 'N/A'}")
print(f"  Live site   : {live_status or 'N/A'}")
print(f"  Drift       : {'⚠ YES — run shipit.sh' if drift else '✓ in sync'}")
print(f"  Checked     : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
print()

sys.exit(1 if drift else 0)
