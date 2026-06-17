#!/usr/bin/env python3
"""
cco_reddit.py — Chief Content Officer: Reddit Draft Formatter

Formats curated stories for Reddit posts (r/LaGazzettadiKyiv).
Voice register: THE DISPATCH — dense, confident, institutional-adjacent.

Saves formatted drafts to GCS cco_drafts/reddit/ pending OAuth credential provisioning.
When REDDIT_CLIENT_ID env var is set, will attempt live posting via PRAW.

Format:
  Title: [CONTRADICTION] Headline
  Body: They Say / Reality / Source / Analysis / link

Usage:
  python3 scripts/cco_reddit.py --story-id abc123 --headline "..." --they-say "..." --reality "..."
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
DRAFTS_PATH = "cco_drafts/reddit"

SITE_URL = "https://www.lagazzettadikyiv.com"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def format_reddit_post(story: dict) -> tuple[str, str]:
    """Format a story as a Reddit post. Returns (title, body)."""
    headline = (story.get("headline", "") or "Untitled").strip()
    they_say = (story.get("they_say", "") or "").strip()
    reality = (story.get("reality", "") or story.get("summary", "") or "").strip()
    source = (story.get("source", "") or "").strip()
    confidence = story.get("confidence_pct", 0)
    contradiction = story.get("contradiction_score", 0)
    body_text = story.get("body", "") or story.get("full_story", "") or reality

    # Title: contradiction + headline
    title = f"{headline}"
    if contradiction > 0.3:
        title = f"[CONTRADICTION {contradiction:.0%}] {headline}"

    # Body: THE DISPATCH format
    body_lines = [
        f"## {headline}",
        "",
        f"**They Say:** {they_say}",
        "",
        f"**Reality:** {reality}",
        "",
    ]

    if body_text and body_text != reality:
        body_lines.append(body_text)
        body_lines.append("")

    # Meta
    meta = []
    if confidence:
        meta.append(f"Model Confidence: {confidence:.0f}%")
    if source:
        meta.append(f"Source: {source}")
    body_lines.append(" | ".join(meta))
    body_lines.append("")

    # Footer
    body_lines.extend([
        "---",
        f"*La Gazzetta di Kyiv — Contradiction-First Capital Flow Intelligence*",
        f"[{SITE_URL}]({SITE_URL}) | [Methodology]({SITE_URL}/capital.html)",
    ])

    body = "\n".join(body_lines)

    # Truncate to Reddit's 40K char limit
    if len(body) > 39000:
        body = body[:38997] + "\n\n*[truncated]*"

    return title, body


def save_draft(story_id: str, title: str, body: str) -> bool:
    """Save formatted Reddit post to GCS drafts."""
    if not HAS_GCP:
        print(f"[{now()}] No GCP client — writing locally")
        Path(f"/tmp/cco_drafts/reddit/{story_id}.md").parent.mkdir(parents=True, exist_ok=True)
        Path(f"/tmp/cco_drafts/reddit/{story_id}.md").write_text(
            f"# {title}\n\n{body}"
        )
        return False

    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{DRAFTS_PATH}/{story_id}.json")
        draft = {
            "story_id": story_id,
            "title": title,
            "body": body,
            "formatted_at": now(),
            "status": "draft",
            "platform": "reddit"
        }
        blob.upload_from_string(json.dumps(draft, indent=2))
        print(f"[{now()}] Reddit draft saved: {DRAFTS_PATH}/{story_id}.json")
        return True
    except Exception as e:
        print(f"[{now()}] Reddit draft save failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="CCO Reddit Draft Formatter")
    parser.add_argument("--story-id", type=str, required=True)
    parser.add_argument("--headline", type=str, required=True)
    parser.add_argument("--they-say", type=str, default="")
    parser.add_argument("--reality", type=str, default="")
    parser.add_argument("--source", type=str, default="")
    parser.add_argument("--body", type=str, default="")
    parser.add_argument("--contradiction", type=float, default=0)
    parser.add_argument("--confidence", type=float, default=0)
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
            "body": args.body,
            "contradiction_score": args.contradiction,
            "confidence_pct": args.confidence,
        }

    title, body = format_reddit_post(story)
    save_draft(args.story_id, title, body)

    print(f"DRAFT_SAVED:{args.story_id}")


if __name__ == "__main__":
    from pathlib import Path
    main()
