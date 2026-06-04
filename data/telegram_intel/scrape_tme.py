#!/usr/bin/env python3
"""Scrape public Telegram channels via t.me/s/ web interface."""
import json
import os
import re
import sys
import time
import html
import urllib.request
import urllib.error

CHANNELS = [
    ("trad_fin", "@trad_fin", "trad_fin"),
    ("MonitoringSituation", "@MonitoringSituation", "MonitoringSituation"), 
    ("ASupersharij", "@ASupersharij", "ASupersharij"),
    ("infinityhedge", "@infinityhedge", "infinityhedge"),
    ("ethanlevins", "@ethanlevins", "ethanlevins"),
    ("markettwits", "@markettwits", "markettwits"),
]

NOW = int(time.time())
ONE_HOUR = 3600
CUTOFF = NOW - 1800  # Last 30 minutes

def fetch_page(url, retries=3):
    """Fetch a URL with retries and basic evasion."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=30)
            return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise

def parse_telegram_messages(html_text, channel_handle):
    """Parse Telegram Web messages from HTML."""
    messages = []
    
    # Try to find message blocks
    # Telegram web uses <div class="tgme_widget_message_wrap"> or similar patterns
    # Pattern 1: Standard message blocks
    pattern = r'<div class="tgme_widget_message_wrap[^"]*"[^>]*>.*?<div class="tgme_widget_message[^"]*"[^>]*>'
    
    # Find all message divs
    # Simpler approach: find text between message containers
    raw_msgs = re.split(r'<div class="tgme_widget_message_wrap', html_text)[1:]
    
    for raw in raw_msgs:
        msg = {}
        
        # Message ID
        mid_match = re.search(r'data-post="([^"]+)"', raw)
        if mid_match:
            msg["message_id"] = mid_match.group(1)
        
        # Timestamp
        time_match = re.search(r'datetime="([^"]+)"', raw)
        if time_match:
            dt_str = time_match.group(1)
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                msg["date"] = int(dt.timestamp())
            except:
                pass
        
        # Text content - try multiple selectors
        text = ""
        # Try the message text div
        text_match = re.search(r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>\s*</div>', raw, re.DOTALL)
        if text_match:
            text = text_match.group(1)
            # Clean HTML tags
            text = re.sub(r'<[^>]+>', ' ', text)
            text = html.unescape(text)
            text = re.sub(r'\s+', ' ', text).strip()
        
        if not text:
            # Try inside bubble
            text_match = re.search(r'class="tgme_widget_message_bubble[^"]*"[^>]*>.*?<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', raw, re.DOTALL)
            if text_match:
                text = text_match.group(1)
                text = re.sub(r'<[^>]+>', ' ', text)
                text = html.unescape(text)
                text = re.sub(r'\s+', ' ', text).strip()
        
        msg["text"] = text
        
        # Only include if we have text or essential data
        if msg.get("text") or msg.get("message_id"):
            messages.append(msg)
    
    return messages

def main():
    all_messages = []
    
    for short_name, handle, alias in CHANNELS:
        url = f"https://t.me/s/{short_name}"
        print(f"Fetching {url}...")
        
        try:
            html_text = fetch_page(url)
            msgs = parse_telegram_messages(html_text, handle)
            print(f"  Found {len(msgs)} messages")
            
            for msg in msgs:
                dt = msg.get("date", 0)
                if dt:
                    ts = time.strftime("%H:%M:%S UTC", time.gmtime(dt))
                    age = NOW - dt
                    age_str = f"{age//60}m ago" if age < 3600 else f"{age//3600}h ago"
                else:
                    ts = "?"
                    age_str = "?"
                
                text_preview = msg.get("text", "")[:200]
                print(f"  [{ts} ({age_str})] {text_preview}")
                
                all_messages.append({
                    "channel": alias,
                    "channel_handle": handle,
                    "message_id": msg.get("message_id", ""),
                    "timestamp": msg.get("date", 0),
                    "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(msg.get("date", 0))) if msg.get("date") else "",
                    "text": msg.get("text", ""),
                    "age_seconds": NOW - msg.get("date", 0) if msg.get("date") else None,
                })
                
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Filter to last 30 minutes
    recent = [m for m in all_messages if m.get("timestamp") and (NOW - m["timestamp"]) <= 1800]
    print(f"\n=== SUMMARY ===")
    print(f"Total messages found: {len(all_messages)}")
    print(f"Messages from last 30 min: {len(recent)}")
    
    # Save all
    out_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(out_dir, "latest_raw.json"), "w") as f:
        json.dump(all_messages, f, indent=2, ensure_ascii=False)
    
    with open(os.path.join(out_dir, "messages_summary.json"), "w") as f:
        json.dump(recent if recent else all_messages, f, indent=2, ensure_ascii=False)
    
    print(f"Data saved to {out_dir}/")

if __name__ == "__main__":
    main()
