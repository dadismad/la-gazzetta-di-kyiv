#!/usr/bin/env python3
"""
auto_revert.py — Module 4: Autonomous Deployment Reversion & Alerting

Architect V2. When test_platform.py fails, this module:
1. Sends a Telegram alert to the C-Suite with failure details
2. Logs the failure to GCS for historical pattern analysis
3. Returns non-zero exit code to cloud_entrypoint.py (which blocks GCS sync)

Usage (called from cloud_entrypoint.py):
  python3 scripts/auto_revert.py --exit-code 1 --log "test_platform.py FAILED at ROUND 2"

Telegram Bot API token is read from TELEGRAM_BOT_TOKEN env var,
provisioned via GCP Secret Manager mount.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

# GCP clients — available in container
try:
    from google.cloud import storage  # type: ignore
    HAS_GCP = True
except ImportError:
    HAS_GCP = False


# ── Configuration ──────────────────────────────────────────────

PROJECT_ID = os.environ.get("GCP_PROJECT", "project-e5e0244c-b94d-41a1-810")
BUCKET_NAME = os.environ.get("GCS_BUCKET", "www.lagazzettadikyiv.com")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Default C-Suite chat: Stocchi Labs group
DEFAULT_CHAT_ID = "-1003796560949"

LOG_BLOB = "pipeline-run-log.jsonl"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def send_telegram_alert(message: str) -> bool:
    """Send a message via Telegram Bot API. Returns True on success."""
    if not TELEGRAM_BOT_TOKEN:
        print(f"[{now()}] WARNING: TELEGRAM_BOT_TOKEN not set — cannot send alert")
        return False

    chat_id = TELEGRAM_CHAT_ID or DEFAULT_CHAT_ID
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    import urllib.request
    import urllib.error

    payload = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode())
            if body.get("ok"):
                print(f"[{now()}] Telegram alert sent to {chat_id}")
                return True
            else:
                print(f"[{now()}] Telegram API error: {body}")
                return False
    except Exception as e:
        print(f"[{now()}] Telegram send failed: {e}")
        return False


def log_to_gcs(entry: dict) -> bool:
    """Append a JSON line to the pipeline run log in GCS."""
    if not HAS_GCP:
        print(f"[{now()}] WARNING: google.cloud.storage not available — cannot log to GCS")
        return False

    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(LOG_BLOB)

        # Read existing log
        existing = ""
        if blob.exists():
            existing = blob.download_as_text() or ""

        # Append new entry
        line = json.dumps(entry)
        updated = (existing.rstrip("\n") + "\n" + line + "\n").lstrip("\n")
        blob.upload_from_string(updated)
        print(f"[{now()}] Pipeline run logged to GCS ({len(updated)} bytes total)")
        return True
    except Exception as e:
        print(f"[{now()}] GCS log write failed: {e}")
        return False


def build_alert_message(exit_code: int, log_lines: str, dry_run: bool = False) -> str:
    """Build the Telegram alert message with pipeline failure details."""
    tag = "[DRY RUN] " if dry_run else ""

    # Extract key failure lines (last 5 non-empty lines of log)
    relevant = [l for l in log_lines.strip().split("\n") if l.strip()][-5:]
    log_excerpt = "\n".join(relevant) if relevant else "(no log output)"

    return (
        f"*{tag}ARCHITECT V2 — MODULE 4: AUTO-REVERT TRIGGERED*\n\n"
        f"*Status:* Pipeline FAILED (exit code {exit_code})\n"
        f"*Action:* GCS sync BLOCKED — live site preserved at last good state\n"
        f"*Time:* {now()}\n"
        f"*Project:* `{os.environ.get('GCP_PROJECT', '?')}`\n\n"
        f"*Last pipeline output:*\n```\n{log_excerpt}\n```\n\n"
        f"_No files deployed. Site at_ `lagazzettadikyiv.com` _unchanged._"
    )


def main():
    parser = argparse.ArgumentParser(description="Auto-revert: alert on pipeline failure")
    parser.add_argument("--exit-code", type=int, required=True, help="Pipeline exit code")
    parser.add_argument("--log", type=str, default="", help="Failure log excerpt")
    parser.add_argument("--dry-run", action="store_true", help="Test mode — don't send real alert")
    args = parser.parse_args()

    if args.exit_code == 0:
        print(f"[{now()}] Pipeline succeeded — no alert needed")
        # Still log success for Module 6 synthesis
        log_to_gcs({
            "timestamp": now(),
            "exit_code": 0,
            "status": "success",
            "project": PROJECT_ID,
        })
        sys.exit(0)

    # Build alert
    message = build_alert_message(args.exit_code, args.log, dry_run=args.dry_run)

    # Log to GCS
    log_to_gcs({
        "timestamp": now(),
        "exit_code": args.exit_code,
        "status": "failed",
        "project": PROJECT_ID,
        "log_excerpt": args.log[-500:] if args.log else "",
    })

    # Send Telegram alert
    if args.dry_run:
        print(f"[{now()}] DRY RUN — would send alert:\n{message}")
    else:
        sent = send_telegram_alert(message)
        if not sent:
            print(f"[{now()}] WARNING: Telegram alert failed — pipeline halted but C-Suite NOT notified")
            # Non-fatal: pipeline still halted, GCS sync still blocked

    # Always return failure exit code so cloud_entrypoint.py knows to block
    sys.exit(1)


if __name__ == "__main__":
    main()
