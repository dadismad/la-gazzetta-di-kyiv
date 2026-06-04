#!/usr/bin/env python3
"""Scrape recent messages from Telegram channels via t.me/s/ web frontend."""
import json
import re
import time
import urllib.request
import urllib.error
import sys
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser

CHANNELS = [
    "trad_fin",
    "MonitoringSituation",
    "ASupersharij",
    "infinityhedge",
    "ethanlevins",
    "markettwits",
]

CUTOFF_MINUTES = 30

class TelegramExtractor(HTMLParser):
    """Parse t.me/s/ HTML to extract messages."""
    def __init__(self):
        super().__init__()
        self.messages = []
        self.in_message = False
        self.in_text = False
        self.in_date = False
        self.in_forward = False
        self.current = {}
        self.current_text_parts = []
        self.current_forward_from = ""
        self.tag_stack = []
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.tag_stack.append(tag)
        
        # Message wrapper
        if tag == "div" and "class" in attrs_dict:
            classes = attrs_dict["class"].split()
            if "tgme_widget_message_wrap" in classes:
                self.in_message = True
                # Try to get message_id
                if "data-post" in attrs_dict:
                    self.current["id"] = attrs_dict["data-post"]
                self.current_text_parts = []
                self.current_forward_from = ""
                self.current = {}
            elif "tgme_widget_message" in classes:
                if "data-post" in attrs_dict:
                    self.current["id"] = attrs_dict["data-post"]
        
        # Text content
        if tag == "div" and "class" in attrs_dict:
            classes = attrs_dict["class"].split()
            if "tgme_widget_message_text" in classes and self.in_message:
                self.in_text = True
        
        # Date
        if tag == "time" and "datetime" in attrs_dict and self.in_message:
            self.current["datetime"] = attrs_dict["datetime"]
            
        # Forwarded from
        if tag == "a" and "class" in attrs_dict:
            classes = attrs_dict["class"].split()
            if "tgme_widget_message_forwarded_from_name" in classes:
                self.in_forward = True
        
    def handle_endtag(self, tag):
        if self.tag_stack:
            self.tag_stack.pop()
        if tag == "div" and self.in_text:
            self.in_text = False
            if self.current_text_parts:
                self.current["text"] = " ".join(self.current_text_parts).strip()
        if tag == "a" and self.in_forward:
            self.in_forward = False
            if self.current_forward_from:
                self.current["forwarded_from"] = self.current_forward_from.strip()
        if tag == "div":
            # Check if we're at a message boundary
            pass
        
    def handle_data(self, data):
        if self.in_text:
            self.current_text_parts.append(data)
        if self.in_forward:
            self.current_forward_from += data

    def handle_entityref(self, name):
        if self.in_text:
            if name == "amp":
                self.current_text_parts.append("&")
            elif name == "lt":
                self.current_text_parts.append("<")
            elif name == "gt":
                self.current_text_parts.append(">")
            elif name == "quot":
                self.current_text_parts.append('"')
            else:
                self.current_text_parts.append(f"&{name};")


def fetch_channel(channel, retries=3):
    """Fetch recent messages from a Telegram channel via web."""
    url = f"https://t.me/s/{channel}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="replace")
                return html
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  ERROR fetching {channel}: {e}", file=sys.stderr)
                return None


def parse_messages(html, channel):
    """Parse Telegram messages from HTML."""
    if not html:
        return []
    
    messages = []
    
    # Use regex to extract message blocks more reliably
    # Find all message divs
    pattern = r'<div class="tgme_widget_message_wrap[^"]*"[^>]*>.*?</div>\s*</div>\s*</div>'
    
    # Simpler approach: split by message wraps and parse each
    # The tgme_widget_message_wrap contains one message
    
    # Extract data-post IDs which are unique per message
    post_pattern = r'data-post="([^"]+)"'
    posts = re.findall(post_pattern, html)
    
    # Extract message text
    text_pattern = r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>\s*</div>'
    texts = re.findall(text_pattern, html, re.DOTALL)
    
    # Extract datetimes
    dt_pattern = r'<time datetime="([^"]+)"'
    datetimes = re.findall(dt_pattern, html)
    
    # Extract forwarded from
    fwd_pattern = r'<a[^>]*class="tgme_widget_message_forwarded_from_name"[^>]*>([^<]+)</a>'
    forwards = re.findall(fwd_pattern, html)
    
    # Extract views
    views_pattern = r'class="tgme_widget_message_views[^"]*"[^>]*>([^<]+)</span>'
    views = re.findall(views_pattern, html)
    
    # Clean text from HTML tags
    def clean_html(text):
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'&amp;', '&', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        text = re.sub(r'&quot;', '"', text)
        text = re.sub(r'&#39;', "'", text)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'\s*\n\s*', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
    n = max(len(posts), len(texts), len(datetimes))
    fwd_idx = 0
    
    for i in range(n):
        msg_id = posts[i] if i < len(posts) else f"{channel}_{i}"
        dt = datetimes[i] if i < len(datetimes) else ""
        text_raw = texts[i] if i < len(texts) else ""
        text = clean_html(text_raw)
        
        fwd = ""
        if fwd_idx < len(forwards):
            # Check if this forward belongs to this message by position
            fwd = forwards[fwd_idx].strip()
            fwd_idx += 1
        
        view = views[i] if i < len(views) else ""
        
        if text or dt:
            messages.append({
                "id": msg_id,
                "channel": channel,
                "datetime": dt,
                "text": text,
                "forwarded_from": fwd,
                "views": view.strip(),
            })
    
    return messages


def is_recent(dt_str, cutoff_minutes=CUTOFF_MINUTES):
    """Check if datetime is within cutoff minutes."""
    if not dt_str:
        return False
    try:
        # Handle timezone formats
        dt_str_clean = dt_str.replace("Z", "+00:00")
        # Parse ISO format
        if "+" in dt_str_clean or dt_str_clean.count("-") > 2:
            msg_dt = datetime.fromisoformat(dt_str_clean)
        else:
            msg_dt = datetime.fromisoformat(dt_str_clean).replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=cutoff_minutes)
        return msg_dt >= cutoff
    except Exception as e:
        print(f"  Date parse error '{dt_str}': {e}", file=sys.stderr)
        return False


def main():
    all_messages = []
    
    for channel in CHANNELS:
        print(f"Fetching @{channel}...", file=sys.stderr)
        html = fetch_channel(channel)
        if html:
            messages = parse_messages(html, channel)
            recent = [m for m in messages if is_recent(m.get("datetime", ""))]
            print(f"  Found {len(messages)} total, {len(recent)} recent ({CUTOFF_MINUTES}min)", file=sys.stderr)
            all_messages.extend(recent)
            # Debug: print first few messages
            for m in recent[:3]:
                preview = m.get("text", "")[:120].replace("\n", " | ")
                print(f"  [{m.get('datetime','')}] {preview}", file=sys.stderr)
        else:
            print(f"  FAILED to fetch", file=sys.stderr)
        time.sleep(1)  # Rate limiting
    
    # Sort by datetime
    all_messages.sort(key=lambda m: m.get("datetime", ""), reverse=True)
    
    output = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "cutoff_minutes": CUTOFF_MINUTES,
        "channels_checked": CHANNELS,
        "total_recent": len(all_messages),
        "messages": all_messages,
    }
    
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
