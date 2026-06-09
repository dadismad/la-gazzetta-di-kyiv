#!/usr/bin/env python3
"""Fetch ALL messages from all channels, no time filter."""
import requests
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
    """Fetch messages from a Telegram channel via t.me web."""
    url = f"https://t.me/s/{channel}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"  [ERROR] Failed to fetch {channel}: {e}", file=sys.stderr)
        return []

    messages = []
    
    # Split by message wrap - each wrap ends at the </div> of its parent bubble
    pattern = r'class="tgme_widget_message_wrap js-widget_message_wrap"(.*?)</div>\s*</div>\s*</div>\s*</div>'
    blocks = re.findall(pattern, html, re.DOTALL)
    
    for block in blocks:
        # Extract text
        text_match = re.search(r'<div class="tgme_widget_message_text[^"]*"[^>]*dir="auto">(.*?)</div>', block, re.DOTALL)
        if not text_match:
            continue
        
        raw_text = text_match.group(1)
        text = re.sub(r'<br\s*/?>', '\n', raw_text)
        text = re.sub(r'<[^>]+>', '', text)
        text = html_mod.unescape(text)
        text = text.replace('&amp;', '&')
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

    # Print out ALL messages with their dates
    print("\n=== ALL MESSAGES ===")
    for ch, msgs in all_messages.items():
        print(f"\n{'='*60}")
        print(f"@{ch} ({len(msgs)} messages):")
        print(f"{'='*60}")
        if not msgs:
            print("  [no messages]")
        for i, m in enumerate(msgs):
            date_str = m["date"][:19] if m["date"] else "NO DATE"
            text_preview = m["text"][:250].replace("\n", " | ")
            print(f"\n  [{i+1}] {date_str}")
            print(f"  {m['post_id']}")
            print(f"  {text_preview}")
    
    # Save all
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
