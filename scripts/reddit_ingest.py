#!/usr/bin/env python3
"""Compliant Reddit ingestion scaffold (OAuth API, no ban-evasion).

Env vars:
  REDDIT_CLIENT_ID
  REDDIT_CLIENT_SECRET
  REDDIT_USERNAME
  REDDIT_PASSWORD
  REDDIT_USER_AGENT   (e.g. gazzetta-kyiv-bot/1.0 by u/yourname)

Usage:
  python3 scripts/reddit_ingest.py --subreddit Infographics --limit 15
"""

from __future__ import annotations
import argparse
import base64
import json
import os
import time
import urllib.parse
import urllib.request

TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API_BASE = "https://oauth.reddit.com"


def env(name: str) -> str:
    v = os.getenv(name, "").strip()
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v


def get_token() -> str:
    cid = env("REDDIT_CLIENT_ID")
    secret = env("REDDIT_CLIENT_SECRET")
    username = env("REDDIT_USERNAME")
    password = env("REDDIT_PASSWORD")
    ua = env("REDDIT_USER_AGENT")

    basic = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    body = urllib.parse.urlencode({
        "grant_type": "password",
        "username": username,
        "password": password,
    }).encode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=body,
        headers={
            "Authorization": f"Basic {basic}",
            "User-Agent": ua,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.loads(r.read().decode())
    tok = payload.get("access_token")
    if not tok:
        raise RuntimeError(f"Token response missing access_token: {payload}")
    return tok


def api_get(path: str, token: str, ua: str) -> dict:
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        headers={"Authorization": f"bearer {token}", "User-Agent": ua},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def normalize(post: dict) -> dict:
    d = post.get("data", {})
    title = d.get("title", "")
    selftext = d.get("selftext", "")
    score = int(d.get("score", 0) or 0)
    comments = int(d.get("num_comments", 0) or 0)
    upvote_ratio = float(d.get("upvote_ratio", 0) or 0)

    hook_strength = min(100, len([c for c in title if c.isdigit()]) * 8 + (15 if "?" in title else 0))
    actionability = 20 + (20 if any(k in title.lower() for k in ["how", "guide", "steps", "vs"]) else 0)
    contradiction = 25 if any(k in title.lower() for k in ["but", "however", "despite", "vs"]) else 10
    credibility = min(100, (20 if d.get("domain") and d.get("domain") != "self." + d.get("subreddit", "") else 10) + int(upvote_ratio * 30))

    return {
        "post_id": d.get("id"),
        "subreddit": d.get("subreddit"),
        "title": title,
        "selftext": selftext,
        "url": d.get("url"),
        "permalink": f"https://reddit.com{d.get('permalink', '')}",
        "score": score,
        "num_comments": comments,
        "upvote_ratio": upvote_ratio,
        "created_utc": d.get("created_utc"),
        "fetched_at": int(time.time()),
        "hook_strength": hook_strength,
        "novelty_score": min(100, 15 + (comments // 20)),
        "contradiction_score": contradiction,
        "actionability_score": min(100, actionability + (10 if len(selftext) > 180 else 0)),
        "credibility_signal": credibility,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subreddit", default="Infographics")
    ap.add_argument("--limit", type=int, default=15)
    ap.add_argument("--sort", default="hot", choices=["hot", "new", "top"])
    ap.add_argument("--output", default="data/reddit_candidates.json")
    args = ap.parse_args()

    ua = env("REDDIT_USER_AGENT")
    token = get_token()
    payload = api_get(f"/r/{args.subreddit}/{args.sort}.json?limit={args.limit}", token, ua)
    items = payload.get("data", {}).get("children", [])
    normalized = [normalize(x) for x in items]
    normalized.sort(key=lambda x: (x["hook_strength"] + x["actionability_score"] + x["credibility_signal"]), reverse=True)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"generated_at": int(time.time()), "subreddit": args.subreddit, "items": normalized}, f, ensure_ascii=False, indent=2)

    print(json.dumps({"ok": True, "count": len(normalized), "output": args.output}))


if __name__ == "__main__":
    main()
