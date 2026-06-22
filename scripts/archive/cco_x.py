#!/usr/bin/env python3
"""
cco_x.py — Chief Content Officer: X.com Draft Formatter

Formats curated stories as X.com threads (280 chars per tweet).
Voice register: THE CLAIM — direct, action-oriented, contempt for consensus.

Saves formatted drafts to GCS cco_drafts/x/ pending $5 API credit purchase.
When xurl CLI is posting-capable, will attempt live posting.

Format (3-5 tweet thread):
  Tweet 1: Contradiction headline + hook
  Tweet 2: They Say vs Reality
  Tweet 3: Source + link + $cashtags

Usage:
  python3 scripts/cco_x.py --story-id abc123 --headline "..." --they-say "..." --reality "..."
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone

try:
    from google.cloud import storage  # type: ignore
    HAS_GCP = True
except ImportError:
    HAS_GCP = False

BUCKET_NAME = os.environ.get("GCS_BUCKET", "www.lagazzettadikyiv.com")
DRAFTS_PATH = "cco_drafts/x"

SITE_URL = "lagazzettadikyiv.com"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def format_x_thread(story: dict) -> list[str]:
    """Format a story as an X.com thread. Returns list of tweet texts (<=280 chars)."""
    headline = (story.get("headline", "") or "Untitled").strip()
    they_say = (story.get("they_say", "") or "").strip()
    reality = (story.get("reality", "") or story.get("summary", "") or "").strip()
    source = (story.get("source", "") or "").strip()
    contradiction = story.get("contradiction_score", 0)
    confidence = story.get("confidence_pct", 0)

    # Determine cashtags from capital flow data
    capital_flow = story.get("capital_flow", {})
    asset = capital_flow.get("asset", "")
    cashtag = f"${asset.upper()}" if asset and asset.isalpha() and len(asset) <= 5 else ""

    tweets = []

    # Tweet 1: The hook — contradiction + headline
    t1 = headline
    if contradiction > 0.3:
        prefix = f"CONTRADICTION: "
        t1 = prefix + t1
    if len(t1) > 270:
        t1 = t1[:267] + "..."
    tweets.append(t1)

    # Tweet 2: They Say vs Reality
    t2_parts = []
    if they_say:
        t2_parts.append(f"They say: {they_say}")
    if reality:
        t2_parts.append(f"Reality: {reality}")
    if t2_parts:
        t2 = "\n".join(t2_parts)
        if len(t2) > 270:
            t2 = t2[:267] + "..."
        tweets.append(t2)

    # Tweet 3: Source + link + meta
    t3_parts = []
    if source:
        t3_parts.append(f"Source: {source}")
    if confidence:
        t3_parts.append(f"Confidence: {confidence:.0f}%")
    if cashtag:
        t3_parts.append(cashtag)
    t3_parts.append(SITE_URL)
    t3 = " | ".join(t3_parts)
    if len(t3) > 270:
        t3 = t3[:267] + "..."
    tweets.append(t3)

    return tweets


def save_draft(story_id: str, tweets: list[str]) -> bool:
    """Save formatted X thread to GCS drafts."""
    if not HAS_GCP:
        print(f"[{now()}] No GCP client — writing locally")
        from pathlib import Path
        Path(f"/tmp/cco_drafts/x/{story_id}.md").parent.mkdir(parents=True, exist_ok=True)
        Path(f"/tmp/cco_drafts/x/{story_id}.md").write_text("\n\n---\n\n".join(tweets))
        return False

    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{DRAFTS_PATH}/{story_id}.json")
        draft = {
            "story_id": story_id,
            "thread": tweets,
            "tweet_count": len(tweets),
            "formatted_at": now(),
            "status": "draft",
            "platform": "x"
        }
        blob.upload_from_string(json.dumps(draft, indent=2))
        print(f"[{now()}] X draft saved: {DRAFTS_PATH}/{story_id}.json")
        return True
    except Exception as e:
        print(f"[{now()}] X draft save failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="CCO X.com Draft Formatter")
    parser.add_argument("--story-id", type=str, required=True)
    parser.add_argument("--headline", type=str, default="Untitled")
    parser.add_argument("--they-say", type=str, default="")
    parser.add_argument("--reality", type=str, default="")
    parser.add_argument("--source", type=str, default="")
    parser.add_argument("--contradiction", type=float, default=0)
    parser.add_argument("--confidence", type=float, default=0)
    parser.add_argument("--asset", type=str, default="")
    parser.add_argument("--json", type=str, help="Full story JSON")
    args = parser.parse_args()

    if args.json:
        story = json.loads(args.json)
    else:
        story = {
            "story_id": args.story_id,
            "headline": args.headline,
            "they_say": args.they_say,
            "reality": args.reality,
            "source": args.source,
            "contradiction_score": args.contradiction,
            "confidence_pct": args.confidence,
            "capital_flow": {"asset": args.asset}
        }

    tweets = format_x_thread(story)
    save_draft(args.story_id, tweets)

    for i, tweet in enumerate(tweets):
        print(f"  Tweet {i+1} ({len(tweet)} chars): {tweet[:80]}...")
    print(f"DRAFT_SAVED:{args.story_id}")


if __name__ == "__main__":
    main()
