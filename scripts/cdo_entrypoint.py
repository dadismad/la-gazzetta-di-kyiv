#!/usr/bin/env python3
"""
cdo_entrypoint.py — Chief Design Officer: Cloud Run Entrypoint

Orchestrates the CDO audit workflow:
1. Run design compliance audit (cdo_audit.py) with Playwright
2. Save structured report to GCS cdo_audits/
3. Alert on FAIL status

Runs as a Cloud Run Job every 2 hours via Cloud Scheduler.

Usage:
  python3 scripts/cdo_entrypoint.py
"""

import os
import sys
import subprocess
import json
from datetime import datetime, timezone

try:
    from google.cloud import storage  # type: ignore
    HAS_GCP = True
except ImportError:
    HAS_GCP = False

BUCKET_NAME = os.environ.get("GCS_BUCKET", "www.lagazzettadikyiv.com")
AUDITS_PATH = "cdo_audits"
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "-1003796560949")


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def send_alert(message: str) -> bool:
    """Send critical design violation alert via Telegram."""
    if not TELEGRAM_BOT_TOKEN:
        return False

    import urllib.request
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read()).get("ok", False)
    except Exception as e:
        print(f"[{now()}] CDO alert failed: {e}")
        return False


def clean_old_reports(max_age_days: int = 7):
    """Remove audit reports older than N days from GCS."""
    if not HAS_GCP:
        return
    try:
        from datetime import timedelta
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)

        blobs = list(client.list_blobs(BUCKET_NAME, prefix=AUDITS_PATH))
        deleted = 0
        for blob in blobs:
            if blob.time_created and blob.time_created.replace(tzinfo=timezone.utc) < cutoff:
                blob.delete()
                deleted += 1
        if deleted:
            print(f"[{now()}] CDO: cleaned {deleted} old audit reports")
    except Exception as e:
        print(f"[{now()}] CDO cleanup failed: {e}")


def main():
    print(f"[{now()}] CDO Entrypoint starting")

    # Run audit
    cmd = [sys.executable, os.path.join(SCRIPTS_DIR, "cdo_audit.py")]
    print(f"[{now()}] CDO: Running audit...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    print(result.stdout)

    if result.returncode != 0:
        print(f"[{now()}] CDO: Audit returned FAIL")
        # Find the latest report to get violation details
        if HAS_GCP:
            try:
                client = storage.Client()
                bucket = client.bucket(BUCKET_NAME)
                blobs = sorted(
                    client.list_blobs(BUCKET_NAME, prefix=AUDITS_PATH),
                    key=lambda b: b.time_created or datetime.min.replace(tzinfo=timezone.utc),
                    reverse=True
                )
                if blobs:
                    report = json.loads(blobs[0].download_as_text())
                    violations = report.get("violations", [])
                    vlist = "\n".join(f"- {v}" for v in violations[:5])
                    alert_msg = (
                        f"*CDO AUDIT FAILED*\n\n"
                        f"*Time:* {report['timestamp']}\n"
                        f"*Violations ({len(violations)}):*\n{vlist}\n\n"
                        f"Report: `gs://{BUCKET_NAME}/{AUDITS_PATH}/`"
                    )
                    send_alert(alert_msg)
            except Exception as e:
                print(f"[{now()}] CDO alert generation failed: {e}")

    # Clean old reports
    clean_old_reports()

    print(f"[{now()}] CDO Entrypoint complete")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
