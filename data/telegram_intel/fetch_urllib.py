#!/usr/bin/env python3
"""Fetch Telegram channel messages using urllib (no external deps)."""
import urllib.request
import urllib.error
import re
import json
import sys
import html as html_mod
from datetime import datetime, timezone

CHANNELS = [
    "trad_fin",
    "MonitoringSituation",
    "ASupersharij",
    "infinityhedge",
    "ethanlevins",
    "markettwits",
]

def fetch_channel(channel):
    url = f"https://t.me/s/{channel}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [ERROR] Failed to fetch {channel}: {e}", file=sys.stderr)
        return []

    messages = []
    # Find message blocks
    # Each message is in a div with class tgme_widget_message_wrap
    pattern = r'<div[^>]*class="tgme_widget_message_wrap[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>\s*</div>'
    blocks = re.findall(pattern, html, re.DOTALL)

    # If the above fails, try simpler approach
    if not blocks:
        # Try to parse individual message divs
        pattern2 = r'class="tgme_widget_message[^"]*"[^>]*data-post="([^"]*)"[^>]*>.*?<time datetime="([^"]*)"'
        times = re.findall(pattern2, html, re.DOTALL)

        # Extract full message blocks
        blocks2 = re.findall(
            r'<div[^>]*class="tgme_widget_message[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>',
            html, re.DOTALL
        )

        # Parse individual messages
        text_pattern = r'<div class="tgme_widget_message_text[^"]*"[^>]*dir="auto">(.*?)</div>'
        for i, block in enumerate(blocks2):
            text_match = re.search(text_pattern, block, re.DOTALL)
            if not text_match:
                continue
            raw_text = text_match.group(1)
            text = re.sub(r'<br\s*/?>', '\n', raw_text)
            text = re.sub(r'<[^>]+>', '', text)
            text = html_mod.unescape(text)
            text = text.strip()
            if not text:
                continue

            date_str = times[i][1] if i < len(times) else ""
            post_id = times[i][0] if i < len(times) else ""

            messages.append({
                "text": text,
                "date": date_str,
                "post_id": post_id,
            })
    else:
        for block in blocks:
            text_match = re.search(
                r'<div class="tgme_widget_message_text[^"]*"[^>]*dir="auto">(.*?)</div>',
                block, re.DOTALL
            )
            if not text_match:
                continue
            raw_text = text_match.group(1)
            text = re.sub(r'<br\s*/?>', '\n', raw_text)
            text = re.sub(r'<[^>]+>', '', text)
            text = html_mod.unescape(text)
            text = text.strip()
            if not text:
                continue

            time_match = re.search(r'time datetime="([^"]+)"', block)
            date_str = time_match.group(1) if time_match else ""

            post_match = re.search(r'data-post="([^"]+)"', block)
            post_id = post_match.group(1) if post_match else ""

            messages.append({
                "text": text,
                "date": date_str,
                "post_id": post_id,
            })

    return messages

def main():
    all_messages = {}
    now = datetime.now(timezone.utc)

    for channel in CHANNELS:
        print(f"@{channel}...", file=sys.stderr)
        all_messages[channel] = fetch_channel(channel)
        print(f"  {len(all_messages[channel])} messages", file=sys.stderr)

    print("\n=== ALL MESSAGES ===")
    for ch, msgs in all_messages.items():
        print(f"\n{'='*60}")
        print(f"@{ch} ({len(msgs)} messages):")
        print(f"{'='*60}")
        if not msgs:
            print("  [no messages]")
        for i, m in enumerate(msgs):
            date_str = m["date"][:19] if m["date"] else "NO DATE"
            text_preview = m["text"][:300].replace("\n", " | ")
            print(f"\n  [{i+1}] {date_str}")
            print(f"  {m['post_id']}")
            print(f"  {text_preview}")

    output = {
        "timestamp": now.isoformat(),
        "timezone": "UTC",
        "channels": all_messages,
    }
    with open("/Users/alexstocchi/projects/gazzetta-di-kyiv/data/telegram_intel/raw_all.json", "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nSaved raw_all.json", file=sys.stderr)

if __name__ == "__main__":
    main()
