#!/usr/bin/env python3
"""Fetch raw HTML from each channel and dump message timestamps & texts."""
import re, urllib.request, json
from datetime import datetime, timezone, timedelta

CHANNELS = [
    "trad_fin", "MonitoringSituation", "ASupersharij",
    "infinityhedge", "ethanlevins", "markettwits"
]

now = datetime.now(timezone.utc)
cutoff = now - timedelta(minutes=60)  # 60 min to see what we might be missing

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
    
    # Find ALL datetime attributes and texts
    blocks = re.findall(
        r'<div class="tgme_widget_message_wrap[^>]*>(.*?)</div>\s*</div>\s*</div>',
        html, re.DOTALL
    )
    if not blocks:
        blocks = re.findall(
            r'<div class="tgme_widget_message[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>',
            html, re.DOTALL
        )
    
    # Also try simpler: just find all time elements with datetime
    time_blocks = re.findall(
        r'<time[^>]*datetime="([^"]+)"[^>]*>(.*?)</time>.*?<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>',
        html, re.DOTALL
    )
    
    for ts, _, text_html in time_blocks[:5]:
        try:
            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            if dt >= cutoff:
                text = re.sub(r'<[^>]+>', '', text_html).strip()
                text = text.replace('<br>', '\n').replace('&amp;', '&').replace('&#39;', "'").replace('&quot;', '"')
                if len(text) > 10:
                    print(f"\n=== {channel} [{ts[:19]}] ===")
                    print(text[:300])
                    all_msgs.append({"channel": channel, "ts": ts[:19], "text": text[:300]})
        except:
            pass
    
    # Try alternative pattern
    alt_blocks = re.findall(
        r'datetime="([^"]+)"[^>]*>.*?</time>.*?class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>',
        html, re.DOTALL
    )
    for ts, text_html in alt_blocks:
        try:
            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            if dt >= cutoff:
                text = re.sub(r'<[^>]+>', '', text_html).strip()
                text = text.replace('<br>', '\n').replace('&amp;', '&').replace('&#39;', "'").replace('&quot;', '"')
                already = any(m['channel'] == channel and m['ts'] == ts[:19] for m in all_msgs)
                if not already and len(text) > 10:
                    print(f"\n=== {channel} [{ts[:19]}] (alt) ===")
                    print(text[:300])
                    all_msgs.append({"channel": channel, "ts": ts[:19], "text": text[:300]})
        except:
            pass

print(f"\n\n=== TOTAL MESSAGES IN LAST 60 MIN: {len(all_msgs)} ===")
print(json.dumps(all_msgs, indent=2, ensure_ascii=False))
