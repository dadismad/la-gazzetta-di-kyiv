#!/usr/bin/env python3
"""devvit_ingest.py — Fetch Reddit posts via Devvit API for Gazzetta di Kyiv.

Supports --deploy flag to trigger Devvit app deploy before ingestion.
Targets: investing, wallstreetbets, geopolitics, economics, worldnews, stocks, cryptocurrency

Usage:
  python3 scripts/devvit_ingest.py                    # Direct API mode
  python3 scripts/devvit_ingest.py --deploy           # Deploy Devvit app first, then ingest
  python3 scripts/devvit_ingest.py --limit 25         # Set post limit per subreddit
  python3 scripts/devvit_ingest.py --list-subreddits   # Show target subreddits

Output: data/reddit_ingest/latest.json
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(PROJECT, "data")
INGEST_DIR = os.path.join(DATA, "reddit_ingest")
DEVVIT_PROJECT = os.path.expanduser("~/lagazzettadikyiv")
DEVVIT_API_URL = os.environ.get("DEVVIT_API_URL", "https://lagazzettadikyiv.devvit.zone")

TARGET_SUBREDDITS = [
    "investing",
    "wallstreetbets",
    "geopolitics",
    "economics",
    "worldnews",
    "stocks",
    "cryptocurrency",
]

HOOK_SIGNALS = [
    "crash", "surge", "plunge", "rally", "sell-off", "breakout",
    "breaking", "alert", "urgent", "crisis", "collapse", "boom",
    "fed", "ecb", "rate hike", "rate cut", "inflation", "recession",
    "war", "sanctions", "tariff", "supply chain", "shortage",
]


def deploy_devvit():
    """Deploy the Devvit app to Reddit."""
    if not os.path.exists(DEVVIT_PROJECT):
        return False, f"Devvit project not found at {DEVVIT_PROJECT}"

    try:
        # Type check
        subprocess.run(
            ["npm", "run", "-s", "type-check"],
            cwd=DEVVIT_PROJECT, capture_output=True, timeout=60
        )
        # Upload
        subprocess.run(
            ["./node_modules/.bin/devvit", "upload"],
            cwd=DEVVIT_PROJECT, capture_output=True, timeout=60
        )
        # Install
        subprocess.run(
            ["./node_modules/.bin/devvit", "install", "LaGazzettadiKyiv", "lagazzettadikyiv@latest"],
            cwd=DEVVIT_PROJECT, capture_output=True, timeout=60
        )
        return True, "deployed"
    except Exception as e:
        return False, str(e)


def fetch_via_api(subreddit, limit=25, sort="hot"):
    """Fetch posts via Devvit HTTP API."""
    import urllib.request
    import urllib.error

    url = (
        f"{DEVVIT_API_URL}/api/fetch-subreddit-posts"
        f"?subreddit={subreddit}&limit={limit}&sort={sort}"
    )
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("posts", data.get("data", {}).get("posts", []))
    except urllib.error.URLError as e:
        return []
    except Exception:
        return []


def normalize_post(post, subreddit):
    """Normalize a Reddit post for Gazzetta scoring."""
    title = post.get("title", "")
    body = post.get("selftext", "")
    text = f"{title} {body}".lower()

    hook_strength = sum(1 for s in HOOK_SIGNALS if s in text)
    actionability = min(10, len(body.split()) // 20)
    contradiction = 1 if any(w in text for w in ["but", "however", "despite"]) else 0
    credibility = 2 if any(w in text for w in ["data", "report", "%", "bps"]) else 0

    return {
        "id": post.get("id", ""),
        "title": title,
        "selftext": body[:500],
        "url": post.get("url", ""),
        "permalink": post.get("permalink", ""),
        "score": post.get("score", 0),
        "num_comments": post.get("num_comments", 0),
        "author": post.get("author", ""),
        "subreddit": subreddit,
        "created_utc": post.get("created_utc", ""),
        "hook_strength": hook_strength,
        "actionability": actionability,
        "contradiction": contradiction,
        "credibility": credibility,
    }


def main():
    parser = argparse.ArgumentParser(description="Devvit Reddit ingestion for Gazzetta di Kyiv")
    parser.add_argument("--deploy", action="store_true", help="Deploy Devvit app before ingestion")
    parser.add_argument("--limit", type=int, default=25, help="Posts per subreddit")
    parser.add_argument("--sort", default="hot", choices=["hot", "new", "top", "rising"])
    parser.add_argument("--list-subreddits", action="store_true", help="List target subreddits")
    parser.add_argument("--api-url", help="Devvit API base URL")
    args = parser.parse_args()

    if args.list_subreddits:
        print(json.dumps({"target_subreddits": TARGET_SUBREDDITS}, indent=2))
        return

    if args.api_url:
        global DEVVIT_API_URL
        DEVVIT_API_URL = args.api_url

    os.makedirs(INGEST_DIR, exist_ok=True)

    if args.deploy:
        ok, msg = deploy_devvit()
        if not ok:
            print(json.dumps({"ok": False, "error": f"deploy_failed: {msg}"}, indent=2))

    all_posts = []
    per_subreddit = {}

    for sub in TARGET_SUBREDDITS:
        posts = fetch_via_api(sub, args.limit, args.sort)
        normalized = [normalize_post(p, sub) for p in posts]
        all_posts.extend(normalized)
        per_subreddit[sub] = len(normalized)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_posts": len(all_posts),
        "per_subreddit": per_subreddit,
        "api_url": DEVVIT_API_URL,
        "posts": all_posts,
    }

    out_path = os.path.join(INGEST_DIR, "latest.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(json.dumps({
        "ok": True,
        "total": len(all_posts),
        "per_subreddit": per_subreddit,
        "output": out_path,
    }, indent=2))


if __name__ == "__main__":
    main()
