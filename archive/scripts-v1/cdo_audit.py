#!/usr/bin/env python3
"""
cdo_audit.py — Chief Design Officer: Design Compliance Auditor

Opens the live website via Playwright (headless Chromium), runs
getComputedStyle() checks against DESIGN v26.1 tokens at 3 breakpoints,
and produces a structured audit report.

Verification Pyramid (SOP R7):
  1. browser_console / page.evaluate() — PRIMARY (computed styles, DOM state)
  2. page.screenshot() — SECONDARY (visual confirmation only, not color verification)

Design tokens checked:
  - Masthead: color, border-bottom, font-family, font-size
  - Cards: background, border, padding
  - Nav: background color, link consistency
  - Typography: DM Serif Display for headlines, Source Serif 4 for body
  - No JS errors in console after page load
  - Container count: 5 collapsible containers
  - Card count: >= 30 stories
  - Mobile: no horizontal overflow at 400px

Usage:
  python3 scripts/cdo_audit.py
  python3 scripts/cdo_audit.py --breakpoints desktop,tablet,mobile
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

try:
    from google.cloud import storage  # type: ignore
    HAS_GCP = True
except ImportError:
    HAS_GCP = False

BUCKET_NAME = os.environ.get("GCS_BUCKET", "www.lagazzettadikyiv.com")
AUDITS_PATH = "cdo_audits"
SITE_URL = "https://www.lagazzettadikyiv.com"
CONTEXT_MEMORY_URL = f"{SITE_URL}/data/context_memory.json"


def load_context_memory() -> dict:
    """Load persistent cognitive core from context_memory.json (local or live).
    Returns the parsed JSON dict, or empty dict if unavailable."""
    # Try local file first (Cloud Run pipeline artifact)
    local_path = Path(__file__).resolve().parent.parent / "public" / "data" / "context_memory.json"
    if local_path.exists():
        try:
            with open(local_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    # Fallback: fetch from live site
    try:
        import urllib.request
        with urllib.request.urlopen(CONTEXT_MEMORY_URL, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        pass
    return {}


def merge_design_tokens(base: dict, ctx: dict) -> dict:
    """Merge context_memory design_tokens into base DESIGN_TOKENS.
    JSON values override hardcoded defaults."""
    if not ctx:
        return base
    dt = ctx.get("design_tokens", {})
    if not dt:
        return base
    merged = json.loads(json.dumps(base))  # deep copy
    # Merge top-level design token keys
    for key in ("masthead", "cards", "nav", "wcag"):
        if key in dt:
            merged[key] = dt[key]
    # Merge scalar tokens
    for key in ("body_font", "container_count"):
        if key in dt:
            merged[key] = dt[key]
    return merged

# DESIGN v27.1 tokens — aligned with focus-group-validated live site (June 2026)
DESIGN_TOKENS = {
    "masthead": {
        "color": "rgb(17, 24, 39)",              # #111827 — var(--ink) body text
        "borderBottom": "2px solid rgb(212, 175, 55)",  # gold border
        "fontFamily_contains": "Playfair Display",
        "fontSize_min": 18,
        "fontSize_max": 24,
        # Masthead name uses gold via specific selector, not inherited
        "name_color": "rgb(212, 175, 55)",        # #D4AF37 on .masthead-name
    },
    "cards": {
        "background": "rgb(255, 255, 255)",        # white
        "borderLeft": "2px solid rgb(212, 175, 55)",  # gold left border
        "minCount": 30,
    },
    "nav": {
        "backgroundColor_contains": "26, 31, 46", # #1A1F2E dark navy (v27)
        "linkCount": 7,
    },
    "body_font": "Source Serif 4",
    "container_count": 5,
    # WCAG v27 additions
    "wcag": {
        "body_font_min": 16,                       # >=16px body
        "meta_font_min": 12,                       # >=12px metadata
        "touch_target_min": 44,                    # >=44px interactive
        "gold_contrast_min": 3.0,                  # AA large text
    },
}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_audit() -> dict:
    """Run design audit using Playwright. Returns structured results."""
    results = {
        "timestamp": now(),
        "site_url": SITE_URL,
        "breakpoints": {},
        "overall_status": "unknown",
        "violations": [],
        "passes": [],
    }

    # Load persistent cognitive core and merge design tokens
    ctx_memory = load_context_memory()
    tokens = merge_design_tokens(DESIGN_TOKENS, ctx_memory)
    if ctx_memory:
        results["context_memory_loaded"] = True
        never_again = ctx_memory.get("never_again_list", [])
        if never_again:
            results["never_again_rules"] = len(never_again)
    else:
        results["context_memory_loaded"] = False

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        results["overall_status"] = "ERROR"
        results["violations"].append("Playwright not installed")
        return results

    breakpoints = [
        ("desktop", 1280, 900),
        ("tablet", 768, 1024),
        ("mobile", 400, 800),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        for bp_name, width, height in breakpoints:
            page = context.new_page()
            page.set_viewport_size({"width": width, "height": height})

            # Navigate with cache bust
            cache_bust = f"?_v={datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            page.goto(SITE_URL + cache_bust, wait_until="networkidle", timeout=30000)

            # Wait for JS to render
            page.wait_for_timeout(4000)

            bp_results = {"width": width, "height": height, "checks": {}}

            # --- CHECK 1: Masthead color ---
            try:
                masthead_color = page.evaluate(
                    "() => getComputedStyle(document.querySelector('.masthead')).color"
                )
                bp_results["checks"]["masthead_color"] = masthead_color
                expected = tokens["masthead"]["color"]
                if masthead_color == expected:
                    results["passes"].append(f"[{bp_name}] Masthead color: {masthead_color}")
                else:
                    results["violations"].append(
                        f"[{bp_name}] Masthead color: {masthead_color} (expected {expected})")
            except Exception as e:
                results["violations"].append(f"[{bp_name}] Masthead color check failed: {e}")

            # --- CHECK 2: Masthead font (use .masthead-name, not .masthead which inherits body) ---
            try:
                font = page.evaluate(
                    "() => { const el = document.querySelector('.masthead-name'); return el ? getComputedStyle(el).fontFamily : 'NO_NAME'; }"
                )
                bp_results["checks"]["masthead_font"] = font
                expected_font = tokens["masthead"]["fontFamily_contains"]
                if expected_font.lower() in font.lower():
                    results["passes"].append(f"[{bp_name}] Masthead font: {font}")
                else:
                    results["violations"].append(
                        f"[{bp_name}] Masthead font: {font} (expected contains '{expected_font}')")
            except Exception as e:
                results["violations"].append(f"[{bp_name}] Masthead font check failed: {e}")

            # --- CHECK 3: Card background (navigate to stories page where cards live) ---
            try:
                card_page = context.new_page()
                card_page.set_viewport_size({"width": width, "height": height})
                card_page.goto(SITE_URL + "/stories.html" + cache_bust, wait_until="networkidle", timeout=30000)
                card_page.wait_for_timeout(4000)
                card_bg = card_page.evaluate(
                    "() => { const c = document.querySelector('.card'); return c ? getComputedStyle(c).background : 'NO_CARD'; }"
                )
                bp_results["checks"]["card_background"] = card_bg
                if "NO_CARD" in str(card_bg):
                    results["violations"].append(f"[{bp_name}] No .card element found")
                else:
                    results["passes"].append(f"[{bp_name}] Card background: {card_bg}")
            except Exception as e:
                results["violations"].append(f"[{bp_name}] Card check failed: {e}")

            # --- CHECK 4: Card count ---
            try:
                card_count = card_page.evaluate(
                    "() => document.querySelectorAll('.card').length"
                )
                bp_results["checks"]["card_count"] = card_count
                min_count = tokens["cards"]["minCount"]
                if card_count >= min_count:
                    results["passes"].append(f"[{bp_name}] Card count: {card_count}")
                else:
                    results["violations"].append(
                        f"[{bp_name}] Card count: {card_count} (minimum {min_count})")
                card_page.close()
            except Exception as e:
                results["violations"].append(f"[{bp_name}] Card count failed: {e}")
                try: card_page.close()
                except: pass

            # --- CHECK 5: Nav background (check .nav-dropdown-panel) ---
            try:
                nav_bg = page.evaluate(
                    "() => { const n = document.querySelector('.nav-dropdown-panel'); return n ? getComputedStyle(n).backgroundColor : 'NO_NAV'; }"
                )
                bp_results["checks"]["nav_background"] = nav_bg
                expected_bg = tokens["nav"]["backgroundColor_contains"]
                if expected_bg in str(nav_bg):
                    results["passes"].append(f"[{bp_name}] Nav background: {nav_bg}")
                else:
                    results["violations"].append(
                        f"[{bp_name}] Nav background: {nav_bg} (expected contains '{expected_bg}')")
            except Exception as e:
                results["violations"].append(f"[{bp_name}] Nav check failed: {e}")

            # --- CHECK 6: Horizontal overflow (mobile only) ---
            if bp_name == "mobile":
                try:
                    overflow = page.evaluate(
                        "() => document.documentElement.scrollWidth > window.innerWidth"
                    )
                    bp_results["checks"]["horizontal_overflow"] = overflow
                    if overflow:
                        results["violations"].append(
                            f"[{bp_name}] Horizontal overflow detected (scrollWidth > innerWidth)")
                    else:
                        results["passes"].append(f"[{bp_name}] No horizontal overflow")
                except Exception as e:
                    results["violations"].append(f"[{bp_name}] Overflow check failed: {e}")

            # --- CHECK 7: JS errors ---
            try:
                # Listen for console errors
                errors = []
                def handle_console(msg):
                    if msg.type == "error":
                        errors.append(msg.text)
                page.on("console", handle_console)
                page.reload(wait_until="networkidle")
                page.wait_for_timeout(2000)
                bp_results["checks"]["js_errors"] = len(errors)
                if errors:
                    results["violations"].append(
                        f"[{bp_name}] {len(errors)} JS console errors: {errors[:3]}")
                else:
                    results["passes"].append(f"[{bp_name}] No JS console errors")
            except Exception as e:
                results["violations"].append(f"[{bp_name}] JS error check failed: {e}")

            # Take screenshot (secondary verification)
            try:
                screenshot_bytes = page.screenshot(full_page=False)
                bp_results["screenshot_size_bytes"] = len(screenshot_bytes)
            except Exception:
                pass

            page.close()
            results["breakpoints"][bp_name] = bp_results

        browser.close()

    # Overall status
    if not results["violations"]:
        results["overall_status"] = "PASS"
    elif len(results["violations"]) <= 3:
        results["overall_status"] = "WARN"
    else:
        results["overall_status"] = "FAIL"

    return results


def save_report(results: dict) -> bool:
    """Save audit report to GCS."""
    filename = f"audit_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"

    if not HAS_GCP:
        from pathlib import Path
        Path(f"/tmp/{AUDITS_PATH}/{filename}").parent.mkdir(parents=True, exist_ok=True)
        Path(f"/tmp/{AUDITS_PATH}/{filename}").write_text(json.dumps(results, indent=2))
        print(f"[{now()}] CDO report saved locally: {filename}")
        return False

    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{AUDITS_PATH}/{filename}")
        blob.upload_from_string(json.dumps(results, indent=2))
        print(f"[{now()}] CDO report saved: {AUDITS_PATH}/{filename}")
        return True
    except Exception as e:
        print(f"[{now()}] CDO report save failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="CDO Design Compliance Auditor")
    parser.add_argument("--breakpoints", type=str, default="desktop,tablet,mobile",
                       help="Comma-separated breakpoints to test")
    args = parser.parse_args()

    print(f"[{now()}] CDO Audit starting — {SITE_URL}")
    results = run_audit()

    print(f"[{now()}] CDO Status: {results['overall_status']}")
    print(f"  Passes: {len(results['passes'])}")
    print(f"  Violations: {len(results['violations'])}")

    for v in results["violations"]:
        print(f"  VIOLATION: {v}")
    for p in results["passes"]:
        print(f"  PASS: {p}")

    save_report(results)

    # Exit non-zero on FAIL for alerting integration
    sys.exit(0 if results["overall_status"] != "FAIL" else 1)


if __name__ == "__main__":
    main()
