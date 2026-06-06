#!/usr/bin/env python3
"""Scrape recent messages from public Telegram channels via t.me/s/"""
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
    
    # Split by message wrap
    pattern = r'class="tgme_widget_message_wrap js-widget_message_wrap"(.*?)</div>\s*</div>\s*</div>\s*</div>'
    blocks = re.findall(pattern, html, re.DOTALL)
    
    print(f"  Raw blocks found: {len(blocks)}", file=sys.stderr)
    
    for block in blocks:
        # Extract text
        text_match = re.search(r'<div class="tgme_widget_message_text[^"]*"[^>]*dir="auto">(.*?)</div>', block, re.DOTALL)
        if not text_match:
            continue
        
        raw_text = text_match.group(1)
        # Convert <br/> to newlines
        text = re.sub(r'<br\s*/?>', '\n', raw_text)
        # Remove other HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Unescape HTML entities (&#036; -> $, &#39; -> ', etc.)
        text = html_mod.unescape(text)
        # Fix any remaining ampersand issues
        text = text.replace('&amp;', '&')
        text = text.strip()
        
        if not text:
            continue
        
        # Extract datetime
        time_match = re.search(r'time datetime="([^"]+)"', block)
        date_str = time_match.group(1) if time_match else ""
        
        # Extract post ID
        post_match = re.search(r'data-post="([^"]+)"', block)
        post_id = post_match.group(1) if post_match else ""
        
        messages.append({
            "text": text,
            "date": date_str,
            "post_id": post_id,
        })
    
    return messages

def parse_tg_date(date_str):
    """Parse Telegram datetime string to datetime object."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except:
        return None

def main():
    cutoff = datetime.now(timezone.utc).timestamp() - 30 * 60  # 30 min ago
    
    all_messages = {}
    
    for channel in CHANNELS:
        print(f"\nFetching @{channel}...", file=sys.stderr)
        messages = fetch_channel(channel)
        
        recent = []
        for m in messages:
            dt = parse_tg_date(m["date"])
            if dt and dt.timestamp() >= cutoff:
                recent.append(m)
            elif not dt:
                # Can't parse date, include for safety but flag it
                m["date_unknown"] = True
                recent.append(m)
        
        all_messages[channel] = {
            "total": len(messages),
            "recent_30min": recent,
        }
        print(f"  Recent (30min): {len(recent)}/{len(messages)}", file=sys.stderr)

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "channels": all_messages,
    }
    
    # Print summary
    print("\n=== RAW SUMMARY ===", file=sys.stderr)
    for ch, data in all_messages.items():
        print(f"\n@{ch} ({data['recent_30min']} recent):", file=sys.stderr)
        if not data["recent_30min"]:
            print("  [no recent messages]", file=sys.stderr)
        for i, m in enumerate(data["recent_30min"]):
            text_preview = m["text"][:200].replace("\n", " | ")
            print(f"  [{i+1}] {m['date'][:19] if m['date'] else '?'} | {text_preview}", file=sys.stderr)

    # Save raw output
    with open("/Users/alexstocchi/projects/gazzetta-di-kyiv/data/telegram_intel/raw_scrape.json", "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved raw output.", file=sys.stderr)
    
    # Print messages to stdout for pipe capture
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
