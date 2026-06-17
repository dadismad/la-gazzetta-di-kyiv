#!/usr/bin/env python3
"""
cco_entrypoint.py — Chief Content Officer: Cloud Run Entrypoint

Orchestrates the full CCO workflow:
1. Curate stories for all platforms (cco_curate.py)
2. Post to Telegram (LIVE — cco_telegram.py)
3. Format and save drafts for Reddit, X, Newsletter (DRAFT MODE)
4. Log posted story IDs for idempotency (cco_drafts/posted_stories.jsonl)

Runs as a Cloud Run Job every 30 minutes via Cloud Scheduler.

Usage:
  python3 scripts/cco_entrypoint.py
  python3 scripts/cco_entrypoint.py --platform telegram  # single platform
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timezone

try:
    from google.cloud import storage  # type: ignore
    HAS_GCP = True
except ImportError:
    HAS_GCP = False

BUCKET_NAME = os.environ.get("GCS_BUCKET", "www.lagazzettadikyiv.com")
POSTED_LOG = "cco_drafts/posted_stories.jsonl"
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_script(script_name: str, args: list[str] = None) -> tuple[int, str]:
    """Run a CCO script and return exit code + stdout."""
    cmd = [sys.executable, os.path.join(SCRIPTS_DIR, script_name)]
    if args:
        cmd.extend(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return result.returncode, result.stdout


def log_posted(story_id: str, platform: str):
    """Append posted story ID to GCS idempotency log."""
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
        print(f"[{now()}] Idempotency: logged {story_id} -> {platform}")
    except Exception as e:
        print(f"[{now()}] Idempotency log failed: {e}")


def process_telegram(stories: list[dict]) -> int:
    """Post top stories to Telegram. Returns count of successfully posted."""
    posted = 0
    for story in stories:
        sid = story.get("story_id", "")
        headline = story.get("headline", "")
        if not sid or not headline:
            continue

        args = [
            "--story-id", sid,
            "--headline", headline,
            "--they-say", story.get("they_say", "") or "",
            "--reality", story.get("reality", "") or story.get("summary", "") or "",
            "--source", story.get("source", "") or "",
            "--contradiction", str(story.get("contradiction_score", 0) or 0),
            "--confidence", str(story.get("confidence_pct", 0) or 0),
            "--direction", (story.get("capital_flow", {}) or {}).get("direction", "") or "",
        ]

        exit_code, stdout = run_script("cco_telegram.py", args)
        if exit_code == 0 and "POSTED:" in stdout:
            log_posted(sid, "telegram")
            posted += 1
        else:
            print(f"[{now()}] Telegram post failed for {sid}: {stdout[-200:]}")
    return posted


def process_drafts(stories: list[dict], platform: str) -> int:
    """Format and save draft posts for a platform. Returns count saved."""
    script_map = {
        "reddit": "cco_reddit.py",
        "x": "cco_x.py",
    }
    script = script_map.get(platform)
    if not script:
        return 0

    saved = 0
    for story in stories:
        sid = story.get("story_id", "")
        headline = story.get("headline", "")
        if not sid or not headline:
            continue

        args = [
            "--story-id", sid,
            "--headline", headline,
            "--they-say", story.get("they_say", "") or "",
            "--reality", story.get("reality", "") or story.get("summary", "") or "",
            "--source", story.get("source", "") or "",
            "--contradiction", str(story.get("contradiction_score", 0) or 0),
            "--confidence", str(story.get("confidence_pct", 0) or 0),
        ]

        # Platform-specific args
        if platform == "x":
            asset = (story.get("capital_flow", {}) or {}).get("asset", "") or ""
            if asset:
                args.extend(["--asset", asset])
        else:
            args.extend(["--body", story.get("body", "") or ""])

        exit_code, stdout = run_script(script, args)
        if exit_code == 0:
            log_posted(sid, platform)
            saved += 1
        else:
            print(f"[{now()}] {platform} draft failed for {sid}: {stdout[-200:]}")

    return saved


def main():
    print(f"[{now()}] CCO Entrypoint starting")

    # 1. Curate stories
    print(f"[{now()}] Stage 1: Curation")
    exit_code, stdout = run_script("cco_curate.py")
    if exit_code != 0:
        print(f"[{now()}] Curation failed: {stdout[-500:]}")
        sys.exit(1)

    # Parse curation output to get selected stories per platform
    # Re-run curation programmatically for structured data
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "cco_curate", os.path.join(SCRIPTS_DIR, "cco_curate.py"))
    cco_curate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cco_curate)

    stories = cco_curate.fetch_stories()
    posted_ids = cco_curate.load_posted_ids()
    curated = cco_curate.curate_all(stories, posted_ids)

    total_posted = 0
    total_drafted = 0

    # 2. Telegram — LIVE POSTING
    telegram_stories = curated.get("telegram", [])
    print(f"[{now()}] Stage 2: Telegram — {len(telegram_stories)} candidates")
    if telegram_stories:
        posted = process_telegram(telegram_stories)
        total_posted += posted
        print(f"[{now()}] Telegram: {posted}/{len(telegram_stories)} posted")

    # 3. Reddit — DRAFT MODE
    reddit_stories = curated.get("reddit", [])
    print(f"[{now()}] Stage 3: Reddit drafts — {len(reddit_stories)} candidates")
    if reddit_stories:
        drafted = process_drafts(reddit_stories, "reddit")
        total_drafted += drafted

    # 4. X.com — DRAFT MODE
    x_stories = curated.get("x", [])
    print(f"[{now()}] Stage 4: X drafts — {len(x_stories)} candidates")
    if x_stories:
        drafted = process_drafts(x_stories, "x")
        total_drafted += drafted

    # 5. Newsletter — separate entrypoint, runs on its own schedule
    # (Triggered by separate Cloud Scheduler: cco-newsletter-daily / cco-newsletter-weekly)
    newsletter_stories = curated.get("newsletter", [])
    print(f"[{now()}] Stage 5: Newsletter — {len(newsletter_stories)} candidates (separate job)")

    print(f"[{now()}] CCO complete — {total_posted} posted, {total_drafted} drafted")
    sys.exit(0)


if __name__ == "__main__":
    main()
