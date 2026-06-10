#!/usr/bin/env python3
"""Telegram channel scraper - fetches latest messages from monitored channels."""

import requests
import re
import json
import html
from datetime import datetime, timezone

CHANNELS = ['trad_fin', 'MonitoringSituation', 'ASupersharij', 'infinityhedge', 'ethanlevins', 'markettwits']
OUTPUT_FILE = '/Users/alexstocchi/projects/gazzetta-di-kyiv/data/telegram_intel/latest.json'

def scrape_channel(channel):
    """Fetch latest messages from a Telegram public channel via t.me/s/"""
    url = f'https://t.me/s/{channel}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code != 200:
            return {'channel': channel, 'status': resp.status_code, 'error': 'HTTP error', 'messages': []}
        
        text = resp.text
        
        # Parse message blocks
        messages = []
        
        # Split on message wrap divs
        blocks = re.split(r'<div class="tgme_widget_message_wrap[^"]*"[^>]*>', text)[1:]
        
        for block in blocks:
            # Find the closing div (3 levels deep)
            depth = 0
            end_idx = 0
            for i, c in enumerate(block):
                if c == '<':
                    # Simple tag detection
                    pass
            # Better approach: extract each message
            msg = {}
            
            # Message id (data-post)
            id_match = re.search(r'data-post="([^"]+)"', block)
            if id_match:
                msg['id'] = id_match.group(1)
            
            # Timestamp
            time_match = re.search(r'datetime="([^"]+)"', block)
            if time_match:
                msg['timestamp'] = time_match.group(1)
            
            # Text content
            text_match = re.search(r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>', block, re.DOTALL)
            if text_match:
                raw = text_match.group(1)
                # Replace <br> with newlines
                raw = re.sub(r'<br\s*/?>', '\n', raw)
                # Remove all HTML tags
                raw = re.sub(r'<[^>]+>', '', raw)
                # Unescape HTML entities
                raw = html.unescape(raw)
                # Decode unicode escapes
                raw = raw.encode('utf-8').decode('unicode_escape') if '\\u' in raw else raw
                msg['text'] = raw.strip()
            
            # Views
            views_match = re.search(r'<span class="tgme_widget_message_views">([^<]+)</span>', block)
            if views_match:
                msg['views'] = views_match.group(1).strip()
            
            if msg.get('text') or msg.get('id'):
                messages.append(msg)
        
        # Also try to find the channel name/title
        title_match = re.search(r'<title>([^<]+)</title>', text)
        channel_title = title_match.group(1) if title_match else channel
        
        return {
            'channel': channel,
            'title': channel_title,
            'status': 200,
            'scrape_time': datetime.now(timezone.utc).isoformat(),
            'messages_count': len(messages),
            'messages': messages[:15]  # last 15 messages
        }
    except Exception as e:
        return {'channel': channel, 'status': 0, 'error': str(e), 'messages': []}


def main():
    all_data = []
    
    for ch in CHANNELS:
        print(f"Scraping {ch}...")
        data = scrape_channel(ch)
        all_data.append(data)
        print(f"  -> {data.get('messages_count', 0)} messages")
        if 'error' in data:
            print(f"  -> ERROR: {data['error']}")
    
    output = {
        'scrape_time': datetime.now(timezone.utc).isoformat(),
        'run_id': datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S'),
        'channels': all_data
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to {OUTPUT_FILE}")
    print(f"Total messages: {sum(d.get('messages_count', 0) for d in all_data)}")
    
    # Also output full data to stdout for inspection
    print("\n\n=== FULL DATA ===")
    # Print just the messages with timestamps for analysis
    for ch_data in all_data:
        print(f"\n--- {ch_data['channel']} ---")
        for msg in ch_data.get('messages', []):
            ts = msg.get('timestamp', 'N/A')
            text = msg.get('text', '')[:300]
            print(f"[{ts}] {text}")
            print()

if __name__ == '__main__':
    main()
