#!/usr/bin/env python3
"""Scrape public Telegram channels via t.me/s/ for actionable geopolitical/financial intel."""

import json
import re
import time
import urllib.request
import urllib.error
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

OUTPUT = "/Users/alexstocchi/projects/gazzetta-di-kyiv/data/telegram_intel/latest.json"

class TelegramHTMLParser(HTMLParser):
    """Parse t.me/s/ HTML to extract messages with timestamps."""
    def __init__(self):
        super().__init__()
        self.messages = []
        self.current = None
        self.in_msg = False
        self.in_text = False
        self.in_time = False
        self.in_link = False
        self.in_forward_bg = False
        self.text_parts = []
        self.skip_tags = 0
        self.tag_stack = []
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # Detect message wrapper
        cls = attrs_dict.get("class", "")
        
        # Detect forward banner
        if tag == "div" and "tgme_widget_message_forwarded" in cls:
            self.in_forward_bg = True
            
        if tag == "div" and "tgme_widget_message_wrap" in cls:
            if self.current and self.current.get("text"):
                self.messages.append(self.current)
            self.current = {"channel": self.channel, "text": "", "datetime": None, "links": []}
            self.in_msg = True
            self.text_parts = []
            
        if self.in_msg:
            if tag == "div" and "tgme_widget_message_bubble" in cls:
                pass
            elif tag == "time" and "time" in attrs_dict.get("class", ""):
                self.in_time = True
                self.skip_tags = 0
            elif tag == "div" and "tgme_widget_message_text" in cls:
                self.in_text = True
                self.text_parts = []
            elif tag == "a" and self.in_text:
                href = attrs_dict.get("href", "")
                if not href.startswith("tg://"):
                    self.text_parts.append(f"[LINK:{href}]")
            elif tag == "br":
                if self.in_text:
                    self.text_parts.append("\n")
            elif tag == "span" and "emoji" in cls:
                self.skip_tags = 1  # skip emoji img tags soon
        
    def handle_data(self, data):
        if self.in_time:
            self.time_data = data.strip()
        if self.in_text and not self.in_forward_bg and not self.in_link:
            data = data.strip()
            if data:
                self.text_parts.append(data)
                
    def handle_endtag(self, tag):
        if tag == "time" and self.in_time:
            self.in_time = False
            if self.current and hasattr(self, 'time_data'):
                try:
                    dt = datetime.fromtimestamp(int(self.time_data), tz=timezone.utc)
                    self.current["datetime"] = dt.isoformat()
                except:
                    pass
        if tag == "div" and self.in_text:
            pass
        # Reset forward banner detection on div close
        self.tag_stack = self.tag_stack[:-1] if self.tag_stack else []
        
    def parse(self, html, channel):
        self.channel = channel
        self.messages = []
        self.current = None
        self.in_msg = False
        self.in_text = False
        self.in_time = False
        self.in_forward_bg = False
        self.text_parts = []
        
        # Clean forwarded stuff
        # Remove forwarded banners
        html = re.sub(r'<div class="tgme_widget_message_forwarded[^>]*>.*?</div>', '', html, flags=re.DOTALL)
        
        self.feed(html)
        
        if self.current and self.current.get("text"):
            self.messages.append(self.current)
            
        # Post-process: join text
        for m in self.messages:
            text = " ".join([p for p in m["text_parts"] if p]) if "text_parts" in m else ""
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r' +\n', '\n', text)
            text = re.sub(r'\n +', '\n', text)
            m["text"] = text.strip()
            if "text_parts" in m:
                del m["text_parts"]
                
        return self.messages


def fetch_channel(channel, max_retries=3):
    """Fetch public messages from a Telegram channel via t.me/s/."""
    url = f"https://t.me/s/{channel}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as resp:
                html = resp.read().decode("utf-8", errors="replace")
            return html
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  ERROR fetching {channel}: {e}")
                return None


def extract_messages_simple(html, channel):
    """Extract messages using regex from t.me/s/ HTML."""
    messages = []
    
    # Find all message blocks
    # Pattern: tgme_widget_message_wrap blocks
    blocks = re.findall(
        r'<div class="tgme_widget_message_wrap[^"]*"[^>]*>.*?<div class="tgme_widget_message[^>]*>.*?</div>\s*</div>',
        html, re.DOTALL
    )
    
    for block in blocks:
        msg = {"channel": channel, "text": "", "datetime": None, "links": [], "has_forward": False}
        
        # Check for forwarded message
        if 'tgme_widget_message_forwarded' in block:
            msg["has_forward"] = True
            # Remove forwarded banner content
            block = re.sub(r'<div class="tgme_widget_message_forwarded[^>]*>.*?</div>', '', block, flags=re.DOTALL)
        
        # Extract datetime from time tag
        time_match = re.search(r'<time[^>]*datetime="([^"]+)"', block)
        if time_match:
            msg["datetime"] = time_match.group(1)
        else:
            # Try the old format with data-date
            time_match2 = re.search(r'<time[^>]*>(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', block)
            if time_match2:
                msg["datetime"] = time_match2.group(1)
        
        # Extract text from message text div
        text_match = re.search(r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', block, re.DOTALL)
        if text_match:
            text_html = text_match.group(1)
            # Extract links
            links = re.findall(r'href="(https?://[^"]+)"', text_html)
            msg["links"] = links
            # Strip HTML tags
            text = re.sub(r'<br\s*/?>', '\n', text_html)
            text = re.sub(r'<[^>]+>', '', text)
            # Decode HTML entities
            text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
            # Clean up whitespace
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = text.strip()
            msg["text"] = text
        
        # Also try to find the message text in <span class="tgme_widget_message_text">
        if not msg["text"]:
            span_match = re.search(r'<span class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</span>', block, re.DOTALL)
            if span_match:
                text_html = span_match.group(1)
                links = re.findall(r'href="(https?://[^"]+)"', text_html)
                msg["links"] = links
                text = re.sub(r'<br\s*/?>', '\n', text_html)
                text = re.sub(r'<[^>]+>', '', text)
                text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
                text = re.sub(r'\n{3,}', '\n\n', text)
                text = text.strip()
                msg["text"] = text
        
        if msg["text"] or msg["links"]:
            messages.append(msg)
    
    return messages


def parse_datetime(dt_str):
    """Parse various datetime formats from Telegram."""
    if not dt_str:
        return None
    try:
        # Try ISO format with timezone
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00').replace('+00:00', '+00:00'))
    except:
        pass
    try:
        # Try timestamp
        return datetime.fromtimestamp(int(dt_str), tz=timezone.utc)
    except:
        pass
    return None


def is_within_last_30min(dt):
    """Check if datetime is within the last 30 minutes."""
    if not dt:
        return False
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=30)
    return dt >= cutoff


def main():
    print(f"=== Telegram Channel Monitor ===")
    print(f"Time: {datetime.now(timezone.utc).isoformat()} UTC")
    print(f"Channels: {', '.join(CHANNELS)}")
    print()
    
    all_messages = []
    
    for channel in CHANNELS:
        print(f"Fetching @{channel}...", end=" ", flush=True)
        html = fetch_channel(channel)
        if html:
            messages = extract_messages_simple(html, channel)
            print(f"{len(messages)} messages found")
            for m in messages:
                dt = parse_datetime(m["datetime"])
                if dt:
                    age = datetime.now(timezone.utc) - dt
                    age_mins = age.total_seconds() / 60
                    m["age_minutes"] = round(age_mins, 1)
                    print(f"  [{age_mins:.0f}m ago] {m['text'][:120]}...")
                else:
                    m["age_minutes"] = None
                    print(f"  [no time] {m['text'][:120]}...")
            all_messages.extend(messages)
        else:
            print("FAILED")
    
    # Sort by datetime (most recent first)
    all_messages.sort(key=lambda m: parse_datetime(m["datetime"]) or datetime.min, reverse=True)
    
    # Save all messages
    output = {
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "total_messages": len(all_messages),
        "channels": CHANNELS,
        "messages": all_messages
    }
    
    with open(OUTPUT, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(all_messages)} messages to {OUTPUT}")
    
    # Filter to last 30 minutes
    recent = [m for m in all_messages if is_within_last_30min(parse_datetime(m["datetime"]))]
    print(f"\nMessages in last 30 min: {len(recent)}")
    
    return all_messages, recent


if __name__ == "__main__":
    all_msgs, recent = main()
