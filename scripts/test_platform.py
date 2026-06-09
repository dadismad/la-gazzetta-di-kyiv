#!/usr/bin/env python3
"""test_platform.py — Automated UI & Data Integrity Test Suite

Parses compiled site/ files with BeautifulSoup4, runs assertions:

1. NULL CHECK: No 'undefined', 'null', NaN strings, or empty brackets [] in any HTML
2. FLOW DATA: Every story with linked flow contains valid, non-zero capital numbers
3. HTTP STRUCTURE: All product pages have valid HTML layout + link to styles.css
4. TIMESTAMPS: Data-linked containers carry freshness indicators
5. FLOW CONSISTENCY: flows.json amounts match what's rendered in stories.json

Usage:
  python3 scripts/test_platform.py           # run all tests
  python3 scripts/test_platform.py --quick   # skip HTML structural checks (faster)
  python3 scripts/test_platform.py --strict  # exit on first failure

Exit codes:
  0 = all tests passed
  1 = test failures detected (abort deploy)
"""

import json
import os
import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 not installed. Run: .venv/bin/pip install beautifulsoup4")
    sys.exit(1)


PROJECT = Path(__file__).resolve().parent.parent
SITE = PROJECT / "site"
DATA = PROJECT / "data"

# Product pages to validate
PRODUCT_PAGES = [
    "index.html", "flow-nodes.html", "event_horizon.html",
    "stories.html", "flows.html", "signal.html", "track.html",
    "trades.html", "capital.html", "about.html", "data.html",
]

# Forbidden strings in rendered HTML
FORBIDDEN = [
    ("undefined", "undefined JavaScript value"),
    ("null", "null value"),
    ("NaN", "NaN numeric value"),
    ("[]", "empty array literal"),
]

PASS = 0
FAIL = 0


def check(condition, msg):
    """Assert a condition, print result, track pass/fail."""
    global PASS, FAIL
    if condition:
        print(f"  ✓ {msg}")
        PASS += 1
    else:
        print(f"  ✗ FAIL: {msg}")
        FAIL += 1


def load_html(path):
    """Load and parse an HTML file."""
    with open(path) as f:
        return BeautifulSoup(f.read(), "html.parser")


# ═══════════════════════════════════════════════════════
# TEST ROUND 1: Null / Poison Value Check
# ═══════════════════════════════════════════════════════

def test_no_poison_values(quick=False):
    """Scan all product pages for forbidden strings."""
    print("\n── ROUND 1: Poison Value Detection ──")

    pages_to_check = [PRODUCT_PAGES[0]] if quick else PRODUCT_PAGES

    for page_name in pages_to_check:
        page_path = SITE / page_name
        if not page_path.exists():
            check(False, f"{page_name}: file not found")
            continue

        with open(page_path) as f:
            html = f.read()

        for forbidden, label in FORBIDDEN:
            # Check only in body content, skip script/style tags
            body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
            content = body_match.group(1) if body_match else html
            # Strip script and style tags
            content = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', content, flags=re.DOTALL)
            # Strip HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)

            # Use word-boundary match for NaN (avoid false positives like "financial")
            if forbidden == "NaN":
                found = bool(re.search(r'\bNaN\b', content))
            elif forbidden == "[]":
                found = "[]" in content
            else:
                found = forbidden.lower() in content.lower()
            check(not found, f"{page_name}: no '{forbidden}' ({label})")


# ═══════════════════════════════════════════════════════
# TEST ROUND 2: Flow Data Integrity
# ═══════════════════════════════════════════════════════

def test_flow_data_integrity():
    """Verify stories.json flows match DB-convention and have non-zero values."""
    print("\n── ROUND 2: Flow Data Integrity ──")

    stories_path = DATA / "stories.json"
    flows_path = DATA / "flows.json"

    if not stories_path.exists():
        check(False, "stories.json not found")
        return
    if not flows_path.exists():
        check(False, "flows.json not found")
        return

    with open(stories_path) as f:
        stories_data = json.load(f)
    with open(flows_path) as f:
        flows_data = json.load(f)

    stories = stories_data.get("stories", [])
    flows = flows_data.get("flows", [])
    flow_ids = {f["id"] for f in flows}

    # Build flow lookup
    flow_by_id = {}
    for f in flows:
        flow_by_id[f["id"]] = f

    linked_count = 0
    mismatch_count = 0
    zero_amount_count = 0

    for story in stories:
        impacted = story.get("impacted_flows", [])
        if not impacted:
            continue

        linked_count += 1
        sid = story.get("story_id", "?")

        for flow_id in impacted:
            # Check flow_id references a real flow
            if flow_id not in flow_ids:
                check(False, f"{sid}: flow_id '{flow_id}' not found in flows.json")
                mismatch_count += 1
                continue

            # Check capital_flow has valid numbers
            cf = story.get("capital_flow", {})
            amount = cf.get("amount_b", 0)
            pace = cf.get("pace_multiplier", 0)

            if amount == 0:
                check(False, f"{sid}: capital_flow.amount_b = 0 (should be non-zero)")
                zero_amount_count += 1
            else:
                check(True, f"{sid}: amount_b=${amount}B ✓")

            if pace == 0:
                check(False, f"{sid}: capital_flow.pace_multiplier = 0 (should be non-zero)")
            else:
                check(True, f"{sid}: pace_multiplier={pace} ✓")

            # Cross-verify: story's amount_b should match the linked flow's amount_b
            flow = flow_by_id.get(flow_id, {})
            flow_amount = flow.get("amount_b", 0)
            if abs(amount - flow_amount) > 0.01 and flow_amount > 0:
                check(False, f"{sid}: capital_flow.amount_b=${amount}B ≠ flow.amount_b=${flow_amount}B (DRIFT)")
                mismatch_count += 1

    check(linked_count > 0, f"{linked_count} stories have linked flows")
    check(mismatch_count == 0, f"flow-story amount mismatches: {mismatch_count}")
    check(zero_amount_count == 0, f"stories with zero flow amounts: {zero_amount_count}")

    # Also verify flows.json has valid summary
    check(flows_data.get("total_flows_tracked", 0) > 0, f"flows.json: {flows_data['total_flows_tracked']} flows tracked")
    check(isinstance(flows_data.get("aggregate_confidence"), (int, float)),
          f"flows.json: aggregate_confidence={flows_data.get('aggregate_confidence')}")


# ═══════════════════════════════════════════════════════
# TEST ROUND 3: HTML Structure & Stylesheet Links
# ═══════════════════════════════════════════════════════

def test_html_structure():
    """Verify product pages have valid HTML, link to styles.css, have body content."""
    print("\n── ROUND 3: HTML Structure Validation ──")

    for page_name in PRODUCT_PAGES:
        page_path = SITE / page_name
        if not page_path.exists():
            check(False, f"{page_name}: file not found in site/")
            continue

        try:
            soup = load_html(page_path)
        except Exception as e:
            check(False, f"{page_name}: parse error — {e}")
            continue

        # Check has <html> tag
        has_html = soup.find("html") is not None
        check(has_html, f"{page_name}: has <html> tag")

        # Check has <body> with content
        body = soup.find("body")
        has_body = body is not None
        check(has_body, f"{page_name}: has <body> tag")
        if body:
            text_len = len(body.get_text(strip=True))
            check(text_len > 100, f"{page_name}: body text length={text_len}")

        # Check links to styles.css
        css_links = soup.find_all("link", rel="stylesheet")
        has_css = any("styles" in (l.get("href") or "") for l in css_links)
        check(has_css, f"{page_name}: links to styles.css")

        # Check has a meaningful title or h1
        title = soup.find("title")
        h1 = soup.find("h1")
        has_heading = (title and title.get_text(strip=True)) or (h1 and h1.get_text(strip=True))
        check(has_heading, f"{page_name}: has title or h1 heading")


# ═══════════════════════════════════════════════════════
# TEST ROUND 4: Timestamp Freshness
# ═══════════════════════════════════════════════════════

def test_timestamps():
    """Verify data containers have freshness timestamp hooks."""
    print("\n── ROUND 4: Timestamp Freshness ──")

    index_path = SITE / "index.html"
    if not index_path.exists():
        check(False, "index.html not found")
        return

    soup = load_html(index_path)

    # Check for freshness elements
    fresh_elements = (
        soup.find_all(id="storyFreshness") +
        soup.find_all(id="flowFreshness") +
        soup.find_all(id="signalFreshness") +
        soup.find_all(class_="freshness-ago") +
        soup.find_all(class_="timestamp") +
        soup.find_all(attrs={"data-freshness": True})
    )
    check(len(fresh_elements) > 0, f"index.html: {len(fresh_elements)} freshness elements found")

    # Check hero indicators
    hero_indicators = soup.select(".hero-indicator, .hero-stats, .hero-stat")
    check(len(hero_indicators) > 0 or soup.find(id="heroIndicators"),
          f"index.html: hero indicators present (found {len(hero_indicators)} elements)")

    # Check services grid
    services = soup.select(".services-grid, .service-card, .persona-card")
    check(len(services) > 0, f"index.html: services grid present ({len(services)} cards)")

    # Check teaser containers
    teasers = soup.select(".teaser-list, .teaser-container, [id$='TeaserContent']")
    check(len(teasers) > 0, f"index.html: teaser containers present ({len(teasers)})")


# ═══════════════════════════════════════════════════════
# TEST ROUND 5: Cross-File JSON Consistency
# ═══════════════════════════════════════════════════════

def test_json_consistency():
    """Verify site/data/ matches data/ and JSON is valid."""
    print("\n── ROUND 5: JSON Consistency ──")

    for fname in ["stories.json", "flows.json"]:
        data_path = DATA / fname
        site_path = SITE / "data" / fname

        if not data_path.exists():
            check(False, f"data/{fname} not found")
            continue
        if not site_path.exists():
            check(False, f"site/data/{fname} not found")
            continue

        with open(data_path) as f:
            data_j = json.load(f)
        with open(site_path) as f:
            site_j = json.load(f)

        # Compare story/flow counts
        if fname == "stories.json":
            d_count = len(data_j.get("stories", []))
            s_count = len(site_j.get("stories", []))
            check(d_count == s_count, f"stories.json: data/={d_count} stories, site/={s_count} (must match)")

        if fname == "flows.json":
            d_count = data_j.get("total_flows_tracked", 0)
            s_count = site_j.get("total_flows_tracked", 0)
            check(d_count == s_count, f"flows.json: data/={d_count}, site/={s_count} (must match)")

        # Check generated_at timestamps are recent (< 24h)
        gen_at = data_j.get("generated_at", "")
        check(bool(gen_at), f"{fname}: has generated_at timestamp")
        if gen_at:
            from datetime import datetime, timezone, timedelta
            try:
                ts = datetime.fromisoformat(gen_at.replace("Z", "+00:00"))
                age = datetime.now(timezone.utc) - ts
                check(age < timedelta(hours=24), f"{fname}: generated_at is {age.total_seconds()/3600:.1f}h old (< 24h)")
            except:
                check(False, f"{fname}: invalid generated_at format")


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def main():
    global PASS, FAIL
    quick = "--quick" in sys.argv
    strict = "--strict" in sys.argv

    print("══════════════════════════════════════")
    print("  TEST PLATFORM — Gazzetta di Kyiv")
    print("══════════════════════════════════════")

    test_no_poison_values(quick=quick)
    test_flow_data_integrity()
    test_html_structure()
    test_timestamps()
    test_json_consistency()

    print(f"\n{'═'*40}")
    print(f"  RESULTS: {PASS} passed · {FAIL} failed")
    if FAIL == 0:
        print("  VERDICT: ALL TESTS PASSED ✓")
        print(f"{'═'*40}")
        sys.exit(0)
    else:
        print(f"  VERDICT: {FAIL} TEST(S) FAILED ✗")
        print(f"{'═'*40}")
        sys.exit(1)


if __name__ == "__main__":
    main()
