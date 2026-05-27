#!/usr/bin/env python3
import re
import sys
from urllib.request import urlopen, Request

URL = "https://pureciclismo.github.io/gazzetta-di-kyiv/"

INDEX_CHECKS = {
    "brand_title": r"La Gazzetta di Kyiv",
    "stories_heading": r"Stories in Play",
    "stories_container": r"id=\"stories-in-play\"",
    "lead_story_mount": r"id=\"leadStory\"",
    "focus_influence_mount": r"id=\"focusInfluence\"",
    "appjs_script_tag": r"<script\s+src=\"\./app\.js\"",
}

APPJS_CHECKS = {
    "boot_function": r"async\s+function\s+boot\s*\(",
    "story_body_renderer": r"function\s+storyBody\s*\(",
    "setups_feed": r"\./api/v1/home/setups\.json",
    "narratives_feed": r"\./data/narratives\.json",
    "focus_stakes_block": r"focusStakes",
    "focus_bet_block": r"focusBet",
}


def _fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": "gdk-smoke-check/1.0"})
    return urlopen(req, timeout=30).read().decode("utf-8", errors="ignore")


def main() -> int:
    html = _fetch(URL)
    appjs = _fetch(URL + "app.js")
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
