#!/usr/bin/env python3
"""Extract all messages from downloaded Telegram HTML files."""
import re
import json
import sys
import html as html_mod
from datetime import datetime, timezone

CHANNELS = {
    "trad_fin": "/tmp/tg_trad_fin.html",
    "MonitoringSituation": "/tmp/tg_MonitoringSituation.html",
    "ASupersharij": "/tmp/tg_ASupersharij.html",
    "infinityhedge": "/tmp/tg_infinityhedge.html",
    "ethanlevins": "/tmp/tg_ethanlevins.html",
    "marketwits": "/tmp/tg_marketwits.html",
}

# First get MonitoringSituation
CHANNELS["MonitoringSituation"] = None

def extract_messages_from_html(html, channel_name):
    """Extract messages using regex from a t.me page HTML."""
    messages = []
    
    # Find all message blocks by looking for data-post attribute
    # Each message starts with a div that has data-post="channel/postid"
    pattern = r'<div class="tgme_widget_message[^"]*"[^>]*data-post="([^"]+)"[^>]*>.*?<div class="tgme_widget_message_text[^"]*"[^>]*dir="auto">(.*?)</div>.*?<time datetime="([^"]+)"'
    
    matches = re.findall(pattern, html, re.DOTALL)
    
    for post_id, raw_text, date_str in matches:
        # Clean text
        text = re.sub(r'<br\s*/?>', '\n', raw_text)
        text = re.sub(r'<[^>]+>', '', text)
        text = html_mod.unescape(text)
        text = text.replace('&amp;', '&')
        text = text.strip()
        
        if not text:
            continue
        
        messages.append({
            "text": text,
            "date": date_str,
            "post_id": post_id,
            "channel": channel_name,
        })
    
    return messages

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except:
        return None

def main():
    now = datetime.now(timezone.utc)
    print(f"Current time: {now.isoformat()}", file=sys.stderr)
    
    all_channels = {}
    
    for ch_name, filepath in CHANNELS.items():
        if filepath is None:
            # Fetch MonitoringSituation
            import requests
            url = f"https://t.me/s/{ch_name}"
            headers = {"User-Agent": "Mozilla/5.0"}
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                html = resp.text
            except Exception as e:
                print(f"  [ERROR] {ch_name}: {e}", file=sys.stderr)
                continue
        else:
            try:
                with open(filepath) as f:
                    html = f.read()
            except FileNotFoundError:
                print(f"  [ERROR] File not found: {filepath}", file=sys.stderr)
                continue
        
        msgs = extract_messages_from_html(html, ch_name)
        print(f"@{ch_name}: {len(msgs)} messages extracted", file=sys.stderr)
        
        # Print each with date
        for m in msgs:
            dt = parse_date(m["date"])
            age = (now - dt).total_seconds() / 60 if dt else -1
            age_str = f"{age:.0f}min ago" if age >= 0 else "unknown"
            text_snip = m["text"][:120].replace("\n", " | ")
            print(f"  {m['post_id']:40s} | {age_str:>12s} | {text_snip}", file=sys.stderr)
        
        all_channels[ch_name] = msgs
    
    # Save full output
    output = {
        "timestamp": now.isoformat(),
        "timezone": "UTC",
        "channels": all_channels,
    }
    
    with open("/Users/alexstocchi/projects/gazzetta-di-kyiv/data/telegram_intel/raw_all.json", "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved to raw_all.json", file=sys.stderr)
    
    # Print JSON to stdout
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
