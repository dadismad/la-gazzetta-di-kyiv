#!/usr/bin/env python3
import re
import sys
from urllib.request import urlopen, Request

URL = "https://pureciclismo.github.io/gazzetta-di-kyiv/"

INDEX_CHECKS = {
    "brand_title": r"La Gazzetta di Kyiv",
    "stories_container": r"STORIES IN PLAY",
    "anchor_container": r"THE ANCHOR",
    "capital_flows_container": r"CAPITAL FLOWS REPORT",
    "collapsible_class": r"container\.collapsible",
    "appjs_script_tag": r"<script\s+src=\"./app\.js\?v=19\"",
}

APPJS_CHECKS = {
    "boot_function": r"async\s+function\s+boot\s*\(",
    "story_renderer": r"appendStoryCard",
    "capital_flow_renderer": r"renderCapitalFlows",
    "collapsible_wiring": r"wireCollapsibleContainers",
    "anchor_expanded": r"ANCHOR_ASSETS",
    "deduplication": r"filter\(s\s=>\s+s\.story_id\s*!==\s*leadId\)",
}


def _fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": "gdk-smoke-check/1.0"})
    return urlopen(req, timeout=30).read().decode("utf-8", errors="ignore")


def main() -> int:
    html = _fetch(URL)
    appjs = _fetch(URL + "app.js?v=19")
    failed = []

    for name, pattern in INDEX_CHECKS.items():
        if not re.search(pattern, html, flags=re.IGNORECASE):
            failed.append(name)

    for name, pattern in APPJS_CHECKS.items():
        if not re.search(pattern, appjs, flags=re.IGNORECASE):
            failed.append(name)

    if failed:
        print("SMOKE CHECK FAILED")
        print("Missing:", ", ".join(failed))
        return 1

    print("SMOKE CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
