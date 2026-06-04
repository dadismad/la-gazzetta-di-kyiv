#!/usr/bin/env python3
"""Devvit-based Reddit ingestion.

Collects posts from target subreddits via the Devvit app's API endpoint.
The endpoint runs inside Reddit's Devvit environment; this script calls it
either via a configured public URL or deploys the app to trigger collection
through Reddit's scheduler/triggers.

Modes:
  1. DIRECT API (--api-url or DEVVIT_API_URL):
     Calls the deployed Devvit app's fetchSubredditPosts endpoint.
     URL format: https://<app-name>.devvit.net (if externally accessible)

  2. DEPLOY + TRIGGER (--deploy):
     Builds, uploads, and installs the Devvit app. The install triggers
     the onAppInstall hook which runs data collection + posting.
     NOTE: posts data TO Reddit but doesn't return data to local filesystem
     directly — this is useful for keeping the app updated.

  3. FALLBACK (documented):
     Uses the existing reddit_ingest.py with proper Reddit OAuth credentials
     (requires REDDIT_CLIENT_ID, etc. from .env.reddit.template).

Usage:
  python3 scripts/devvit_ingest.py --limit 25 --sort hot
  python3 scripts/devvit_ingest.py --deploy
  python3 scripts/devvit_ingest.py --list-subreddits
  export DEVVIT_API_URL=https://lagazzettadikyiv.devvit.net
  python3 scripts/devvit_ingest.py --subreddit investing
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
DEVVIT_APP_DIR = os.path.expanduser("~/lagazzettadikyiv")
DEFAULT_OUTPUT = os.path.join(REPO_DIR, "data", "reddit_ingest", "latest.json")

TARGET_SUBREDDITS = [
    "investing",
    "wallstreetbets",
    "geopolitics",
    "economics",
    "worldnews",
    "stocks",
    "cryptocurrency",
]

# ---- URL discovery ----


def discover_devvit_url() -> str | None:
    """Check env var for Devvit API URL."""
    url = os.environ.get("DEVVIT_API_URL", "").strip()
    if url:
        return url.rstrip("/")
    return None


def test_api_url(api_base: str) -> bool:
    """Test if a Devvit API URL is reachable by calling a simple health check."""
    try:
        req = urllib.request.Request(
            f"{api_base}/api/fetch-subreddit-posts?subreddit=investing&limit=1",
            method="GET",
        )
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False


# ---- API fetch ----


def fetch_posts_via_devvit(
    api_base: str,
    subreddit: str,
    limit: int = 25,
    sort: str = "hot",
) -> list[dict]:
    """Fetch posts from a subreddit via the Devvit app's API."""
    params = urllib.parse.urlencode({
        "subreddit": subreddit,
        "limit": str(limit),
        "sort": sort,
    })
    url = f"{api_base}/api/fetch-subreddit-posts?{params}"

    req = urllib.request.Request(url, method="GET")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        raise RuntimeError(
            f"HTTP {e.code} from Devvit API for r/{subreddit}: {body[:300]}"
        ) from e
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"Cannot reach Devvit API at {api_base}: {e.reason}"
        ) from e

    if data.get("status") == "error":
        raise RuntimeError(
            f"Devvit API error for r/{subreddit}: {data.get('message', 'unknown')}"
        )

    return data.get("posts", [])


# ---- Normalization ----


def normalize_post(post: dict, subreddit_name: str) -> dict:
    """Normalize a Devvit API post into the standard ingestion format."""
    title = post.get("title", "")
    selftext = post.get("selftext", "")
    score = int(post.get("score", 0) or 0)
    comments = int(post.get("num_comments", 0) or 0)

    hook_strength = min(
        100, len([c for c in title if c.isdigit()]) * 8 + (15 if "?" in title else 0)
    )
    actionability = 20 + (
        20 if any(k in title.lower() for k in ["how", "guide", "steps", "vs"]) else 0
    )
    contradiction = (
        25
        if any(k in title.lower() for k in ["but", "however", "despite", "vs"])
        else 10
    )
    credibility = min(
        100,
        (20 if post.get("url") and "reddit.com" not in post.get("url", "") else 10)
        + 20,
    )

    return {
        "post_id": post.get("id"),
        "subreddit": post.get("subreddit", subreddit_name),
        "title": title,
        "selftext": selftext,
        "url": post.get("url"),
        "permalink": post.get("permalink"),
        "score": score,
        "num_comments": comments,
        "upvote_ratio": float(post.get("upvote_ratio", 0) or 0),
        "created_utc": post.get("created_utc"),
        "fetched_at": int(time.time()),
        "hook_strength": hook_strength,
        "novelty_score": min(100, 15 + (comments // 20)),
        "contradiction_score": contradiction,
        "actionability_score": min(
            100, actionability + (10 if len(selftext) > 180 else 0)
        ),
        "credibility_signal": credibility,
    }


# ---- Deploy mode ----


def deploy_devvit_app() -> dict:
    """Build, upload, and install the Devvit app to make the new endpoint live."""
    results = {"steps": [], "ok": True}

    if not os.path.isdir(DEVVIT_APP_DIR):
        return {
            "ok": False,
            "error": f"Devvit app directory not found at {DEVVIT_APP_DIR}",
        }

    # Step 1: Type-check
    print("  [1/4] Running type-check...", file=sys.stderr)
    r1 = subprocess.run(
        ["npm", "run", "-s", "type-check"],
        cwd=DEVVIT_APP_DIR,
        text=True,
        capture_output=True,
        timeout=60,
    )
    results["steps"].append({
        "step": "type-check",
        "exit": r1.returncode,
        "stderr": r1.stderr[-200:],
    })
    if r1.returncode != 0:
        results["ok"] = False
        return results

    # Step 2: Build
    print("  [2/4] Building app...", file=sys.stderr)
    r2 = subprocess.run(
        ["npm", "run", "build"],
        cwd=DEVVIT_APP_DIR,
        text=True,
        capture_output=True,
        timeout=120,
    )
    results["steps"].append({
        "step": "build",
        "exit": r2.returncode,
        "stdout": r2.stdout[-200:],
        "stderr": r2.stderr[-200:],
    })
    if r2.returncode != 0:
        results["ok"] = False
        return results

    # Step 3: Upload
    print("  [3/4] Uploading app...", file=sys.stderr)
    devvit_bin = os.path.join(DEVVIT_APP_DIR, "node_modules", ".bin", "devvit")
    r3 = subprocess.run(
        [devvit_bin, "upload"],
        cwd=DEVVIT_APP_DIR,
        text=True,
        capture_output=True,
        timeout=180,
    )
    results["steps"].append({
        "step": "upload",
        "exit": r3.returncode,
        "stdout": r3.stdout[-300:],
        "stderr": r3.stderr[-200:],
    })
    if r3.returncode != 0:
        results["ok"] = False
        return results

    # Extract version from output
    version = "unknown"
    for line in r3.stdout.split("\n"):
        if "version" in line.lower() and "0." in line:
            version = line.split()[-1].strip()
            break

    # Step 4: Install
    print("  [4/4] Installing app to subreddit...", file=sys.stderr)
    r4 = subprocess.run(
        [devvit_bin, "install", "LaGazzettadiKyiv", f"lagazzettadikyiv@{version}"],
        cwd=DEVVIT_APP_DIR,
        text=True,
        capture_output=True,
        timeout=180,
    )
    results["steps"].append({
        "step": "install",
        "exit": r4.returncode,
        "stdout": r4.stdout[-300:],
        "stderr": r4.stderr[-200:],
    })
    if r4.returncode != 0:
        results["ok"] = False

    results["version"] = version
    return results


# ---- Main ----


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Devvit-based Reddit ingestion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--limit", type=int, default=25, help="Posts per subreddit (default: 25)"
    )
    parser.add_argument(
        "--sort",
        default="hot",
        choices=["hot", "new", "top", "rising", "controversial"],
        help="Sort order (default: hot)",
    )
    parser.add_argument(
        "--api-url",
        default=None,
        help="Devvit API base URL (overrides DEVVIT_API_URL env var)",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--subreddit",
        default=None,
        help="Single subreddit to fetch (default: all target subreddits)",
    )
    parser.add_argument(
        "--list-subreddits", action="store_true", help="List target subreddits and exit"
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Build, upload, and install the Devvit app (triggers data collection "
        "via the app's onAppInstall hook)",
    )
    args = parser.parse_args()

    if args.list_subreddits:
        print("Target subreddits for Devvit ingestion:")
        for sr in TARGET_SUBREDDITS:
            print(f"  r/{sr}")
        sys.exit(0)

    # ---- Deploy mode ----
    if args.deploy:
        print("Deploying Devvit app...", file=sys.stderr)
        result = deploy_devvit_app()
        if result["ok"]:
            version = result.get("version", "unknown")
            print(
                json.dumps({
                    "ok": True,
                    "mode": "deploy",
                    "version": version,
                    "steps": [
                        s["step"]
                        for s in result["steps"]
                        if s["exit"] == 0
                    ],
                    "message": (
                        f"App v{version} deployed and installed. "
                        "The onAppInstall trigger fired — data collection + "
                        "posting should have executed in the Reddit subreddit. "
                        "To run the API directly, set DEVVIT_API_URL "
                        "once the Devvit web gateway URL is known."
                    ),
                })
            )
        else:
            failed_steps = [
                s for s in result.get("steps", []) if s.get("exit", 0) != 0
            ]
            print(
                json.dumps({
                    "ok": False,
                    "mode": "deploy",
                    "error": f"Deploy failed at step(s): {[s['step'] for s in failed_steps]}",
                    "steps": result.get("steps", []),
                })
            )
        sys.exit(0 if result.get("ok") else 1)

    # ---- API mode ----
    api_url = args.api_url or discover_devvit_url()

    if not api_url:
        print(
            json.dumps({
                "ok": False,
                "error": (
                    "No Devvit API URL configured.\n\n"
                    "To use this script, either:\n"
                    "  1. Set DEVVIT_API_URL env var (if you know the Devvit app gateway URL)\n"
                    "  2. Pass --api-url <url>\n"
                    "  3. Run with --deploy to build, upload, and install the app\n\n"
                    "The fetchSubredditPosts endpoint IS deployed in v0.0.43+ but the\n"
                    "Devvit web server does not expose a simple public HTTP URL for external\n"
                    "API calls. The endpoint works when called from within Reddit (menu actions,\n"
                    "triggers, scheduler tasks, or the post IFrame).\n\n"
                    "For local testing, you can use:\n"
                    "  cd ~/lagazzettadikyiv && devvit playtest\n"
                    "This starts a local server that serves the API.\n\n"
                    "The existing reddit_ingest.py (OAuth-based) is also available if you\n"
                    "configure Reddit API credentials in .env.reddit (see .env.reddit.template)."
                ),
                "subreddits": TARGET_SUBREDDITS,
                "hint_deploy": f"python3 {sys.argv[0]} --deploy",
            })
        )
        sys.exit(1)

    api_url = api_url.rstrip("/")

    subreddits_to_fetch = [args.subreddit] if args.subreddit else TARGET_SUBREDDITS

    all_posts = []
    per_subreddit = {}
    errors = []

    for sub in subreddits_to_fetch:
        try:
            posts = fetch_posts_via_devvit(api_url, sub, args.limit, args.sort)
            normalized = [normalize_post(p, sub) for p in posts]
            normalized.sort(
                key=lambda x: (
                    x["hook_strength"]
                    + x["actionability_score"]
                    + x["credibility_signal"]
                ),
                reverse=True,
            )
            all_posts.extend(normalized)
            per_subreddit[sub] = {
                "count": len(normalized),
                "top_hook": normalized[0]["title"][:80] if normalized else None,
                "top_score": normalized[0]["score"] if normalized else 0,
            }
            print(f"  r/{sub}: {len(normalized)} posts fetched", file=sys.stderr)
        except Exception as e:
            errors.append({"subreddit": sub, "error": str(e)})
            print(f"  r/{sub}: ERROR - {e}", file=sys.stderr)

    all_posts.sort(
        key=lambda x: (
            x["hook_strength"] + x["actionability_score"] + x["credibility_signal"]
        ),
        reverse=True,
    )

    output_data = {
        "generated_at": int(time.time()),
        "generated_at_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "devvit-api",
        "api_url": api_url,
        "subreddits_fetched": subreddits_to_fetch,
        "per_subreddit": per_subreddit,
        "total_posts": len(all_posts),
        "errors": errors,
        "items": all_posts,
    }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    summary = {
        "ok": len(errors) < len(subreddits_to_fetch),
        "source": "devvit-api",
        "api_url": api_url,
        "subreddits_fetched": len(subreddits_to_fetch),
        "subreddits_ok": len(subreddits_to_fetch) - len(errors),
        "subreddits_errors": len(errors),
        "total_posts": len(all_posts),
        "output": args.output,
        "per_subreddit": per_subreddit,
        "errors": errors,
        "top_posts": [
            {
                "subreddit": p["subreddit"],
                "title": p["title"][:80],
                "score": p["score"],
                "comments": p["num_comments"],
                "hook": p["hook_strength"],
            }
            for p in all_posts[:5]
        ],
    }
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
