#!/usr/bin/env python3
"""Pull latest tweets from all 33 mapped X.com accounts for Gazzetta di Kyiv.

Usage:
  python3 scripts/xcom_collector.py [--app APP_NAME] [--max-per-account N]

Output:
  data/xcom_intel/latest.json — full tweet data + metadata
  data/xcom_intel/summary.json — thematic summary (1-paragraph synthesis)

Prerequisites:
  - xurl CLI installed and app registered with OAuth user context
  - Active X.com developer project with credits
  - Account map at data/xcom_intel/account_map.json
"""

import json, os, sys, subprocess
from datetime import datetime, timezone

ACCOUNT_MAP_PATH = "data/xcom_intel/account_map.json"
OUTPUT_PATH = "data/xcom_intel/latest.json"
SUMMARY_PATH = "data/xcom_intel/summary.json"
DEFAULT_APP = "GazzettadiKyivX"
MAX_PER_ACCOUNT = 5

def load_account_map():
    with open(ACCOUNT_MAP_PATH) as f:
        return json.load(f)

def pull_tweets(username, uid, app, max_results):
    """Pull tweets from a single user, excluding retweets and replies."""
    url = f"/2/users/{uid}/tweets?max_results={max_results}&tweet.fields=created_at,public_metrics&exclude=retweets,replies"
    result = subprocess.run(
        ["xurl", "--app", app, url],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"  ✗ {username}: API error", file=sys.stderr)
        return []
    
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  ✗ {username}: JSON parse error", file=sys.stderr)
        return []

    if "data" not in data:
        error = data.get("title", data.get("detail", "unknown"))
        print(f"  ✗ {username}: {error}", file=sys.stderr)
        return []

    tweets = []
    for t in data["data"]:
        tweets.append({
            "id": t["id"],
            "text": t["text"],
            "created_at": t["created_at"],
            "likes": t["public_metrics"]["like_count"],
            "retweets": t["public_metrics"]["retweet_count"],
            "impressions": t["public_metrics"].get("impression_count", 0),
            "replies": t["public_metrics"].get("reply_count", 0),
            "bookmarks": t["public_metrics"].get("bookmark_count", 0),
        })
    return tweets

def collect_all(accounts, app, max_per):
    """Pull tweets from all accounts sequentially."""
    results = {}
    total = len(accounts)
    
    for i, (username, uid) in enumerate(accounts.items(), 1):
        print(f"[{i}/{total}] {username}...", end=" ", flush=True)
        tweets = pull_tweets(username, uid, app, max_per)
        if tweets:
            results[username] = tweets
            print(f"✓ {len(tweets)} tweets")
        else:
            print("✗")
    
    return results

def save_output(results):
    """Save raw results to latest.json."""
    output = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "accounts_polled": len(results),
        "total_tweets": sum(len(t) for t in results.values()),
        "accounts": results,
    }
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nSaved: {output['accounts_polled']} accounts, {output['total_tweets']} tweets → {OUTPUT_PATH}")
    return output

def main():
    app = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--app" else DEFAULT_APP
    max_per = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == "--max-per-account" else MAX_PER_ACCOUNT
    
    accounts = load_account_map()
    print(f"Pulling {max_per} tweets each from {len(accounts)} accounts (app: {app})...\n")
    
    results = collect_all(accounts, app, max_per)
    output = save_output(results)
    
    print(f"\nDone. {output['accounts_polled']}/{len(accounts)} accounts returned tweets.")

if __name__ == "__main__":
    main()
