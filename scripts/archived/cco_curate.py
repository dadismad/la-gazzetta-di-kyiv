#!/usr/bin/env python3
"""
cco_curate.py — Chief Content Officer: Content Curation Engine

Reads stories.json from GCS, ranks stories by contradiction impact score,
selects top N for each distribution platform.

Curation formula: impact_score = contradiction_score * (confidence_pct / 100)
Higher score = bigger gap between consensus and reality = more newsworthy.

Platform thresholds:
- Telegram: top 3 stories, impact_score >= 0.15
- Reddit: top 1 story, impact_score >= 0.25
- X.com: top 3 stories, impact_score >= 0.10
- Newsletter: top 5 stories, impact_score >= 0.10

Usage:
  python3 scripts/cco_curate.py            # full curation for all platforms
  python3 scripts/cco_curate.py --dry-run  # print selections only
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

try:
    from google.cloud import storage  # type: ignore
    HAS_GCP = True
except ImportError:
    HAS_GCP = False

BUCKET_NAME = os.environ.get("GCS_BUCKET", "www.lagazzettadikyiv.com")
STORIES_BLOB = "data/stories.json"
DRAFTS_DIR = "cco_drafts"
POSTED_LOG = os.path.join(DRAFTS_DIR, "posted_stories.jsonl")

PLATFORM_CONFIG = {
    "telegram": {"top_n": 3, "min_score": 0.15, "max_age_hours": 24},
    "reddit":   {"top_n": 1, "min_score": 0.25, "max_age_hours": 24},
    "x":        {"top_n": 3, "min_score": 0.10, "max_age_hours": 12},
    "newsletter": {"top_n": 5, "min_score": 0.10, "max_age_hours": 24},
}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_posted_ids() -> set:
    """Load already-posted story IDs from GCS for idempotency."""
    if not HAS_GCP:
        return set()
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(POSTED_LOG)
        if not blob.exists():
            return set()
        posted = set()
        for line in blob.download_as_text().strip().split("\n"):
            if line.strip():
                try:
                    entry = json.loads(line)
                    posted.add(entry.get("story_id", ""))
                except json.JSONDecodeError:
                    continue
        return posted
    except Exception:
        return set()


def save_posted_id(story_id: str, platform: str):
    """Log a posted story ID to prevent duplicate posting."""
    if not HAS_GCP:
        return
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(POSTED_LOG)
        existing = blob.download_as_text() if blob.exists() else ""
        entry = json.dumps({
            "story_id": story_id,
            "platform": platform,
            "posted_at": now()
        })
        blob.upload_from_string((existing.rstrip() + "\n" + entry + "\n").lstrip())
    except Exception:
        pass


def fetch_stories() -> list[dict]:
    """Download stories.json from GCS."""
    if HAS_GCP:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(STORIES_BLOB)
        if blob.exists():
            return json.loads(blob.download_as_text()).get("stories", [])
    # Fallback: try local file
    local_path = Path("data/stories.json")
    if local_path.exists():
        return json.loads(local_path.read_text()).get("stories", [])
    return []


def compute_impact(story: dict) -> float:
    """Compute contradiction impact score for a story."""
    cs = story.get("contradiction_score", 0)
    if isinstance(cs, str):
        try:
            cs = float(cs)
        except (ValueError, TypeError):
            cs = 0
    # Normalize: if score is on 0-100 scale (common in DB), convert to 0-1
    if cs > 1:
        cs = cs / 100.0

    # Try multiple confidence field names
    cp = story.get("confidence_pct", None)
    if cp is None:
        cp = story.get("confidence", 0)
    if isinstance(cp, str):
        # Qualitative confidence: map to numeric
        cp_lower = cp.lower().rstrip("%")
        QUALITATIVE_MAP = {
            "high": 85, "medium_high": 75, "medium": 65,
            "medium_low": 50, "low": 35, "very_low": 15, "none": 5,
        }
        if cp_lower in QUALITATIVE_MAP:
            cp = QUALITATIVE_MAP[cp_lower]
        else:
            try:
                cp = float(cp_lower)
            except (ValueError, TypeError):
                cp = 50  # default if unparseable
    if isinstance(cp, (int, float)):
        if cp > 1 and cp <= 100:
            cp = cp  # already percent
        elif cp <= 1:
            cp = cp * 100  # convert 0-1 to percent
    else:
        cp = 50

    return cs * (cp / 100.0)


def is_fresh(story: dict, max_hours: int) -> bool:
    """Check if story is within the freshness window."""
    pub = story.get("published_at", "") or story.get("created_at", "")
    if not pub:
        return True  # no timestamp = assume fresh
    try:
        ts = datetime.fromisoformat(pub.replace("Z", "+00:00"))
        age = datetime.now(timezone.utc) - ts
        return age < timedelta(hours=max_hours)
    except (ValueError, TypeError):
        return True


def curate(platform: str, stories: list[dict], posted_ids: set) -> list[dict]:
    """Select top stories for a platform."""
    config = PLATFORM_CONFIG.get(platform, PLATFORM_CONFIG["telegram"])

    candidates = []
    for story in stories:
        sid = story.get("story_id", "")
        if sid in posted_ids:
            continue
        if not is_fresh(story, config["max_age_hours"]):
            continue
        score = compute_impact(story)
        if score < config["min_score"]:
            continue
        candidates.append((score, story))

    candidates.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in candidates[:config["top_n"]]]


def curate_all(stories: list[dict], posted_ids: set) -> dict:
    """Curate for all platforms."""
    return {
        platform: curate(platform, stories, posted_ids)
        for platform in PLATFORM_CONFIG
    }


def main():
    parser = argparse.ArgumentParser(description="CCO Curation Engine")
    parser.add_argument("--dry-run", action="store_true", help="Print selections without posting")
    parser.add_argument("--platform", type=str, help="Curate for specific platform only")
    args = parser.parse_args()

    print(f"[{now()}] CCO: Fetching stories from GCS...")
    stories = fetch_stories()
    print(f"[{now()}] CCO: Loaded {len(stories)} stories")

    posted_ids = load_posted_ids()
    print(f"[{now()}] CCO: {len(posted_ids)} previously posted story IDs")

    platforms = [args.platform] if args.platform else list(PLATFORM_CONFIG.keys())
    results = {}

    for platform in platforms:
        selected = curate(platform, stories, posted_ids)
        results[platform] = selected
        config = PLATFORM_CONFIG.get(platform, {})
        print(f"[{now()}] CCO: {platform} — {len(selected)} stories "
              f"(threshold: {config.get('min_score', 0)}, top {config.get('top_n', 0)})")
        for i, s in enumerate(selected):
            score = compute_impact(s)
            headline = (s.get("headline", "") or "")[:80]
            print(f"  [{i+1}] {score:.2f} | {headline}")

    if not args.dry_run:
        # Return results for downstream processing
        return results

    return results


if __name__ == "__main__":
    main()
