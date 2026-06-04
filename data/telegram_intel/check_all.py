#!/usr/bin/env python3
"""Fetch ALL visible messages from each channel, dump with absolute timestamps."""
import re, urllib.request, json
from datetime import datetime, timezone, timedelta

CHANNELS = [
    "trad_fin", "MonitoringSituation", "ASupersharij",
    "infinityhedge", "ethanlevins", "markettwits"
]

now = datetime.now(timezone.utc)
all_msgs = []

for channel in CHANNELS:
    url = f"https://t.me/s/{channel}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"{channel}: ERROR {e}")
        continue
    
    # Find ALL messages with their timestamps
    # Pattern: <div class="tgme_widget_message_wrap...> around each message
    # Inside, find <time datetime="..."> and the text div
    
    # Split by message wrap div
    parts = re.split(r'<div class="tgme_widget_message_wrap[^>]*>', html)
    
    count = 0
    for part in parts[1:]:
        try:
            # Get datetime
            dt_match = re.search(r'datetime="([^"]+)"', part)
            if not dt_match:
                continue
            
            ts_str = dt_match.group(1)
            try:
                dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
            except:
                dt = None
            
            # Get text
            text_match = re.search(r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', part, re.DOTALL)
            if not text_match:
                continue
            
            raw = text_match.group(1)
            text = re.sub(r'<[^>]+>', '', raw)
            text = text.replace('<br>', '\n').replace('<br/>', '\n')
            text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            text = text.replace('&#39;', "'").replace('&quot;', '"')
            text = text.strip()
            
            if not text:
                continue
            
            hours_ago = (now - dt).total_seconds() / 3600 if dt else -1
            
            preview = text[:250].replace('\n', ' ')
            print(f"{channel} | {ts_str[:19]} | {hours_ago:.1f}h ago | {preview}")
            
            all_msgs.append({
                "channel": channel,
                "datetime": ts_str[:19],
                "hours_ago": round(hours_ago, 1) if dt else -1,
                "text_preview": preview
            })
            count += 1
            if count >= 10:
                break
        except Exception as e:
            pass
    
    if count == 0:
        print(f"{channel} | NO MESSAGES PARSED")
    
    print()

print(f"\n=== ALL VISIBLE MESSAGES ACROSS ALL CHANNELS ===")
print(json.dumps(all_msgs, indent=2, ensure_ascii=False))
