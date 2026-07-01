#!/usr/bin/env python3
"""
Telegram Channel Stats Tracker — minimal, no third-party dependencies.
Polls subscriber count and saves to a CSV log. Run via cron or manually.
"""

import json
import urllib.request
import os
from datetime import datetime, timezone
from pathlib import Path

STATS_LOG = Path("/opt/gazzetta-di-kyiv/data/telegram_stats.csv")
CHAT_ID = "-1003990434181"


def get_token():
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
    path = "projects/project-e5e0244c-b94d-41a1-810/secrets/gazzetta-telegram-token/versions/latest"
    resp = client.access_secret_version(request={"name": path})
    return resp.payload.data.decode("utf-8")


def get_chat_stats(token):
    url = f"https://api.telegram.org/bot{token}/getChat?chat_id={CHAT_ID}"
    resp = json.loads(urllib.request.urlopen(url, timeout=15).read())
    if not resp.get("ok"):
        raise RuntimeError(f"Telegram API error: {resp}")
    chat = resp["result"]
    return {
        "member_count": chat.get("member_count", chat.get("active_usernames_count", 0)),
        "title": chat.get("title", ""),
    }


def get_member_count(token):
    url = f"https://api.telegram.org/bot{token}/getChatMemberCount?chat_id={CHAT_ID}"
    resp = json.loads(urllib.request.urlopen(url, timeout=15).read())
    if resp.get("ok"):
        return resp["result"]
    return 0


def main():
    token = get_token()
    now = datetime.now(timezone.utc).isoformat()
    member_count = get_member_count(token)

    # Append to CSV
    is_new = not STATS_LOG.exists()
    with open(STATS_LOG, "a") as f:
        if is_new:
            f.write("timestamp,member_count\n")
        f.write(f"{now},{member_count}\n")

    print(f"[{now}] Subscribers: {member_count}")


if __name__ == "__main__":
    main()
