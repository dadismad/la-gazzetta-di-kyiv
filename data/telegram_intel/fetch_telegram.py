#!/usr/bin/env python3
"""Fetch Telegram channel messages via t.me/s/ web preview using curl subprocess."""

import re
import sys
import json
import html
import subprocess
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
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "20",
             "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
             url],
            capture_output=True, text=True, timeout=25
        )
        content = result.stdout
    except Exception as e:
        return {"channel": channel, "error": str(e), "messages": []}

    if not content or len(content) < 500:
        return {"channel": channel, "error": "empty response", "messages": []}

    messages = []
    msg_pattern = re.compile(
        r'<div class="tgme_widget_message_text js-message_text"[^>]*>(.*?)</div>',
        re.DOTALL
    )
    date_pattern = re.compile(
        r'<time[^>]*datetime="([^"]+)"[^>]*class="time"',
    )  # handles both attribute orders
    post_pattern = re.compile(r'data-post="([^"]+)"')
    
    text_matches = msg_pattern.findall(content)
    date_matches = date_pattern.findall(content)
    post_matches = post_pattern.findall(content)

    for i, msg_html in enumerate(text_matches):
        text = re.sub(r'<[^>]+>', '', msg_html)
        text = html.unescape(text).strip()
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('&#036;', '$')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
        
        if len(text) <= 5:
            continue
        
        dt_str = date_matches[i] if i < len(date_matches) else "unknown"
        post_id = post_matches[i] if i < len(post_matches) else f"{channel}/{i}"
        
        messages.append({
            "post_id": post_id,
            "datetime_raw": dt_str,
            "text": text[:4000],
        })
    
    return {"channel": channel, "error": None, "messages": messages}


def main():
    results = []
    for ch in CHANNELS:
        sys.stderr.write(f"Fetching @{ch}...\n")
        data = fetch_channel(ch)
        results.append(data)
        sys.stderr.write(f"  -> {len(data['messages'])} messages\n")
    
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
