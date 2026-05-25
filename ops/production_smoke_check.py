#!/usr/bin/env python3
import re
import sys
from urllib.request import urlopen, Request

URL = "https://pureciclismo.github.io/gazzetta-di-kyiv/"

INDEX_CHECKS = {
    "stories_heading": r"Stories in Play",
    "build_strip": r"Build:\s*<b id=\"buildCommit\"",
    "cta": r"Get Daily Signal",
}

APPJS_CHECKS = {
    "actors_label": r"Actors:",
    "repricing_label": r"Repricing thesis",
    "story_card_renderer": r"storyCardForSetup",
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
