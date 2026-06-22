#!/usr/bin/env python3
"""health_check.py — Gazzetta di Kyiv site freshness watchdog.
Checks that live site data is fresh. Alerts Telegram if stale > 60 min.
Runs as systemd timer every 15 min. Script-only, no LLM dependency.
"""
import json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "") or "-1003990434181"
DATA_URL = "https://www.lagazzettadikyiv.com/data/stories-v4.json"
STALE_THRESHOLD_MINUTES = 60


def tg_send(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT:
        print("[watchdog] Telegram not configured — skipping alert")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        body = json.dumps({
            "chat_id": TELEGRAM_CHAT,
            "text": text[:4000],
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }).encode()
        req = urllib.request.Request(url, data=body,
                                     headers={"Content-Type": "application/json"})
        resp = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
        return resp.get("ok", False)
    except Exception as e:
        print(f"[watchdog] Telegram send failed: {e}")
        return False


def check():
    now = datetime.now(timezone.utc)
    print(f"[watchdog] {now.isoformat()} — checking {DATA_URL}")

    try:
        req = urllib.request.Request(DATA_URL + f"?_={int(now.timestamp())}")
        data = json.loads(urllib.request.urlopen(req, timeout=15).read().decode())
    except Exception as e:
        msg = f"*Gazzetta Watchdog ALERT*\n\nCannot fetch data: {e}"
        print(f"[watchdog] FAIL: {e}")
        tg_send(msg)
        return 1

    generated_at = data.get("generated_at", "")
    if not generated_at:
        msg = "*Gazzetta Watchdog ALERT*\n\nData has no generated_at field."
        print("[watchdog] FAIL: no generated_at")
        tg_send(msg)
        return 1

    try:
        gen_time = datetime.fromisoformat(generated_at)
    except Exception:
        msg = f"*Gazzetta Watchdog ALERT*\n\nCannot parse generated_at: {generated_at}"
        print(f"[watchdog] FAIL: bad timestamp")
        tg_send(msg)
        return 1

    age_minutes = (now - gen_time).total_seconds() / 60
    story_count = len(data.get("all_stories", []))

    if age_minutes > STALE_THRESHOLD_MINUTES:
        msg = (
            f"*Gazzetta Watchdog ALERT*\n\n"
            f"Site data is stale.\n"
            f"Last update: {generated_at}\n"
            f"Age: {age_minutes:.0f} min (threshold: {STALE_THRESHOLD_MINUTES} min)\n"
            f"Stories: {story_count}"
        )
        print(f"[watchdog] FAIL: {age_minutes:.0f} min stale")
        tg_send(msg)
        return 1

    print(f"[watchdog] PASS: {age_minutes:.0f} min old, {story_count} stories")
    return 0


if __name__ == "__main__":
    sys.exit(check())
