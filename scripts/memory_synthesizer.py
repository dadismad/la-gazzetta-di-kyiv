#!/usr/bin/env python3
"""
memory_synthesizer.py — Module 6: Cross-Session Memory Synthesis

Architect V2. Daily Cloud Run Job that:
1. Downloads the pipeline run log (pipeline-run-log.jsonl) from GCS
2. Analyzes patterns: failure clusters, error frequencies, performance trends
3. Generates DRAFT_SKILL_UPDATE.md with identified structural improvements
4. Uploads the draft to GCS for C-Suite review
5. Optionally sends a Telegram summary

This creates the self-improving feedback loop:
  pipeline runs → log to GCS → daily synthesis → draft skills → C-Suite review → permanent skill

Usage (Cloud Run entrypoint):
  python3 scripts/memory_synthesizer.py

Or as a standalone for testing:
  python3 scripts/memory_synthesizer.py --days 7
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict
from pathlib import Path

try:
    from google.cloud import storage  # type: ignore
    HAS_GCP = True
except ImportError:
    HAS_GCP = False
    print("WARNING: google.cloud.storage not available — running in local/dry-run mode")

PROJECT_ID = os.environ.get("GCP_PROJECT", "project-e5e0244c-b94d-41a1-810")
BUCKET_NAME = os.environ.get("GCS_BUCKET", "www.lagazzettadikyiv.com")
LOG_BLOB = "pipeline-run-log.jsonl"
DRAFT_BLOB = "DRAFT_SKILL_UPDATE.md"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "-1003796560949")


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── GCS Operations ─────────────────────────────────────────────

def download_log() -> list[dict]:
    """Download pipeline run log from GCS, parse JSONL, return list of entries."""
    if not HAS_GCP:
        print(f"[{now()}] No GCP client — cannot download log")
        return []

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(LOG_BLOB)

    if not blob.exists():
        print(f"[{now()}] No pipeline run log found at gs://{BUCKET_NAME}/{LOG_BLOB}")
        return []

    raw = blob.download_as_text()
    entries = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    print(f"[{now()}] Downloaded {len(entries)} pipeline run entries")
    return entries


def upload_draft(content: str) -> bool:
    """Upload the draft skill update to GCS."""
    if not HAS_GCP:
        print(f"[{now()}] No GCP client — writing draft locally")
        Path("/tmp/DRAFT_SKILL_UPDATE.md").write_text(content)
        return False

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(DRAFT_BLOB)
    blob.cache_control = "no-store"
    blob.upload_from_string(content)
    print(f"[{now()}] Draft uploaded to gs://{BUCKET_NAME}/{DRAFT_BLOB}")
    return True


# ── Pattern Analysis ───────────────────────────────────────────

def analyze_entries(entries: list[dict], days: int = 7) -> dict:
    """Analyze pipeline run entries for patterns and anomalies."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    recent = [
        e for e in entries
        if datetime.fromisoformat(e.get("timestamp", "2000-01-01T00:00:00Z").replace("Z", "+00:00")) > cutoff
    ]

    if not recent:
        return {"error": "No entries in the analysis window", "count": 0}

    total = len(recent)
    failures = [e for e in recent if e.get("exit_code", 0) != 0]
    successes = total - len(failures)
    fail_rate = len(failures) / total * 100 if total > 0 else 0

    # Identify failure clusters (time-bucketed: 1-hour windows)
    fail_windows = defaultdict(int)
    for f in failures:
        try:
            ts = datetime.fromisoformat(f["timestamp"].replace("Z", "+00:00"))
            bucket = ts.replace(minute=0, second=0, microsecond=0)
            fail_windows[bucket.isoformat()] += 1
        except (KeyError, ValueError):
            continue

    # Find the worst hour
    worst_hour = max(fail_windows.items(), key=lambda x: x[1]) if fail_windows else (None, 0)

    # Extract error messages from failure log excerpts
    error_keywords = Counter()
    for f in failures:
        excerpt = f.get("log_excerpt", "")
        for keyword in ["FAILED", "ABORT", "ERROR", "timeout", "Traceback",
                        "Permission", "401", "403", "404", "500", "denied"]:
            if keyword.lower() in excerpt.lower():
                error_keywords[keyword] += 1

    # Performance trend: check if failures are increasing
    # Split window in half, compare
    mid = len(recent) // 2
    first_half_fail = sum(1 for e in recent[:mid] if e.get("exit_code", 0) != 0)
    second_half_fail = sum(1 for e in recent[mid:] if e.get("exit_code", 0) != 0)
    trend = "increasing" if second_half_fail > first_half_fail else \
            "decreasing" if second_half_fail < first_half_fail else "stable"

    # Time since last success
    last_success_ts = None
    for e in reversed(recent):
        if e.get("exit_code", 0) == 0:
            last_success_ts = e.get("timestamp", "")
            break
    hours_since_success = "N/A"
    if last_success_ts:
        try:
            lst = datetime.fromisoformat(last_success_ts.replace("Z", "+00:00"))
            delta = datetime.now(timezone.utc) - lst
            hours_since_success = f"{delta.total_seconds()/3600:.1f}h"
        except (ValueError, TypeError):
            pass

    return {
        "total_runs": total,
        "successes": successes,
        "failures": len(failures),
        "fail_rate_pct": round(fail_rate, 1),
        "failure_trend": trend,
        "worst_hour": worst_hour[0],
        "worst_hour_failures": worst_hour[1],
        "top_errors": error_keywords.most_common(5),
        "hours_since_last_success": hours_since_success,
        "analysis_window_days": days,
        "generated_at": now(),
    }


# ── Draft Generation ───────────────────────────────────────────

GENERIC_FIXES = {
    "timeout": "Consider increasing Cloud Run timeout from 600s or profiling slow stages",
    "401": "Check gcloud auth and service account key rotation",
    "403": "Verify IAM permissions for the pipeline service account",
    "Permission": "Audit IAM roles: storage.objectAdmin, run.invoker, secretmanager.secretAccessor",
    "ABORT": "Review deploy_routine.sh Stage 2.5 — test_platform.py may be detecting new data issues",
    "FAILED": "Run test_platform.py locally to isolate the failing assertion",
    "denied": "Check Secret Manager access — TELEGRAM_BOT_TOKEN and DEEPSEEK_API_KEY may need rotation",
    "Traceback": "Pull the full stack trace from Cloud Logging — the excerpt may be truncated",
}


def generate_draft(analysis: dict, entries_count: int) -> str:
    """Generate DRAFT_SKILL_UPDATE.md from pattern analysis."""

    if "error" in analysis:
        return (
            f"# DRAFT SKILL UPDATE — Memory Synthesis\n\n"
            f"**Generated:** {now()}\n"
            f"**Status:** No data — {analysis['error']}\n\n"
            f"No pipeline run log entries found in the analysis window. "
            f"This could indicate the logging mechanism is not working or "
            f"the pipeline has not run recently.\n"
        )

    lines = [
        "# DRAFT SKILL UPDATE — Architect V2 Memory Synthesis",
        "",
        f"**Generated:** {analysis['generated_at']}",
        f"**Source:** {analysis['total_runs']} pipeline runs ({analysis['analysis_window_days']}-day window)",
        f"**Log entries total:** {entries_count}",
        "",
        "---",
        "",
        "## Pipeline Health Summary",
        "",
        f"- **Runs analyzed:** {analysis['total_runs']}",
        f"- **Successes:** {analysis['successes']}",
        f"- **Failures:** {analysis['failures']}",
        f"- **Failure rate:** {analysis['fail_rate_pct']}%",
        f"- **Trend:** {analysis['failure_trend']}",
        f"- **Last success:** {analysis['hours_since_last_success']} ago",
        "",
    ]

    if analysis["failures"] > 0:
        lines.extend([
            "## Identified Issues",
            "",
            f"### Top Error Signals",
            "",
        ])
        for keyword, count in analysis["top_errors"]:
            fix = GENERIC_FIXES.get(keyword, "Investigate manually in Cloud Logging")
            lines.append(f"- **{keyword}** ({count} occurrences): {fix}")

        if analysis["worst_hour_failures"] > 1:
            lines.extend([
                "",
                f"### Failure Cluster",
                f"- **Worst window:** {analysis['worst_hour']} ({analysis['worst_hour_failures']} failures)",
                f"- This suggests a transient infrastructure issue or a data spike at this time.",
            ])

    if analysis["fail_rate_pct"] > 10:
        lines.extend([
            "",
            "## Recommended Actions",
            "",
            f"1. **Investigate failure root cause** — {analysis['fail_rate_pct']}% failure rate exceeds 10% threshold",
            f"2. **Check Cloud Logging** for full stack traces from the failure cluster",
            f"3. **Run test_platform.py locally** against current data to isolate the failing assertion",
            f"4. **Review IAM permissions** if 401/403/Permission errors appear",
        ])
    elif analysis["fail_rate_pct"] > 0:
        lines.extend([
            "",
            "## Recommended Actions",
            "",
            f"1. **Monitor** — {analysis['fail_rate_pct']}% failure rate is within normal range",
            f"2. **Investigate** the specific failure(s) for root cause",
        ])
    else:
        lines.extend([
            "",
            "## Status: HEALTHY",
            "",
            "No failures in the analysis window. Pipeline is functioning correctly.",
            "",
            "No structural improvements identified. If performance is satisfactory, "
            "consider increasing the analysis window to capture longer-term patterns.",
        ])

    lines.extend([
        "",
        "---",
        "",
        f"*Auto-generated by Architect V2 Module 6 (memory_synthesizer.py)*",
        f"*Next run: {analysis['generated_at']} + 24h*",
    ])

    return "\n".join(lines)


# ── Telegram Summary ───────────────────────────────────────────

def send_summary(analysis: dict) -> bool:
    """Send a brief summary to the C-Suite via Telegram."""
    if not TELEGRAM_BOT_TOKEN:
        return False

    if "error" in analysis:
        text = f"*Architect V2 — Daily Synthesis*\n\nNo pipeline data in window.\n\n_Generated {now()}_"
    else:
        text = (
            f"*Architect V2 — Daily Synthesis*\n\n"
            f"Runs: {analysis['total_runs']} | "
            f"Failed: {analysis['failures']} "
            f"({analysis['fail_rate_pct']}%) | "
            f"Trend: {analysis['failure_trend']}\n"
            f"Last success: {analysis['hours_since_last_success']} ago\n\n"
            f"Draft skill update at: `gs://{BUCKET_NAME}/{DRAFT_BLOB}`"
        )

    import urllib.request
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode())
            return body.get("ok", False)
    except Exception as e:
        print(f"[{now()}] Summary send failed: {e}")
        return False


# ── Main ───────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Memory Synthesizer — daily pipeline pattern analysis")
    parser.add_argument("--days", type=int, default=7, help="Analysis window in days (default: 7)")
    parser.add_argument("--no-upload", action="store_true", help="Don't upload draft to GCS")
    args = parser.parse_args()

    print(f"[{now()}] memory_synthesizer.py starting — {args.days}d window")

    entries = download_log()

    if not entries:
        print(f"[{now()}] No log entries found — generating empty draft")
        analysis = {"error": "No entries in pipeline run log", "count": 0}
    else:
        analysis = analyze_entries(entries, days=args.days)

    draft = generate_draft(analysis, len(entries))

    if not args.no_upload:
        upload_draft(draft)
    else:
        print(f"[{now()}] --no-upload: draft not uploaded")
        print(draft[:500])

    # Send Telegram summary
    if TELEGRAM_BOT_TOKEN:
        sent = send_summary(analysis)
        print(f"[{now()}] Telegram summary {'sent' if sent else 'failed'}")

    print(f"[{now()}] memory_synthesizer.py complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
