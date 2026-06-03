#!/usr/bin/env python3
"""Fetch recent Telegram messages from public channels via t.me/s/ web view."""

import json
import re
import urllib.request
import urllib.error
import sys
from datetime import datetime, timezone, timedelta

CHANNELS = [
    "trad_fin",
    "MonitoringSituation",
    "ASupersharij",
    "infinityhedge",
    "ethanlevins",
    "markettwits",
]

OUTPUT_PATH = "/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv/data/telegram_intel/latest.json"

CUTOFF_MINUTES = 30

def fetch_channel(channel):
    """Fetch the public Telegram channel web page."""
    url = f"https://t.me/s/{channel}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        return html
    except urllib.error.HTTPError as e:
        return f"HTTP_ERROR:{e.code}"
    except Exception as e:
        return f"FETCH_ERROR:{str(e)}"


def parse_messages(html, channel):
    """Parse messages from Telegram web HTML."""
    messages = []

    # Each message is typically in a div with class "tgme_widget_message_wrap js-widget_message_wrap"
    # or in the newer format with "tgme_widget_message"
    message_blocks = re.split(r'<div class="tgme_widget_message_wrap', html)

    if len(message_blocks) <= 1:
        # Try alternative parsing
        message_blocks = re.split(r'<div class="tgme_widget_message[^"]*"[^>]*>', html)
        # Filter out non-message blocks
        message_blocks = [b for b in message_blocks if 'tgme_widget_message_text' in b]

    for block in message_blocks[1:]:  # Skip the first split portion (before any message)
        try:
            # Extract message text
            text_match = re.search(
                r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>',
                block, re.DOTALL
            )
            if not text_match:
                text_match = re.search(
                    r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>',
                    block, re.DOTALL
                )

            if not text_match:
                continue

            raw_text = text_match.group(1)
            # Strip HTML tags
            text = re.sub(r'<[^>]+>', '', raw_text)
            text = text.replace('<br>', '\n').replace('<br/>', '\n')
            text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            text = text.replace('&#39;', "'").replace('&quot;', '"')
            text = text.strip()

            if not text:
                continue

            # Extract date/time
            datetime_match = re.search(
                r'datetime=["\']([^"\']+)["\']',
                block
            )
            if datetime_match:
                ts_str = datetime_match.group(1)
                try:
                    published = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                except:
                    published = None
            else:
                # Try time tag
                time_match = re.search(r'<time[^>]*datetime=["\']([^"\']+)["\']', block)
                if time_match:
                    ts_str = time_match.group(1)
                    try:
                        published = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                    except:
                        published = None
                else:
                    published = None

            # Extract message link (for permalink)
            link_match = re.search(
                r'<a class="tgme_widget_message_date"[^>]*href=["\']([^"\']+)["\']',
                block
            )
            link = link_match.group(1) if link_match else f"https://t.me/{channel}"

            messages.append({
                "channel": channel,
                "text": text,
                "published": published.isoformat() if published else None,
                "link": link,
            })
        except Exception as e:
            continue

    return messages


def is_recent(msg, cutoff_minutes=CUTOFF_MINUTES):
    """Check if message is within the cutoff window."""
    if not msg["published"]:
        return False
    try:
        published = datetime.fromisoformat(msg["published"])
        now = datetime.now(timezone.utc)
        # Check for timezone awareness
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        return (now - published) < timedelta(minutes=cutoff_minutes)
    except:
        return False


def main():
    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=CUTOFF_MINUTES)
    all_messages = []
    errors = []

    print(f"=== TELEGRAM SCRAPE: {datetime.now(timezone.utc).isoformat()} ===")
    print(f"Cutoff: {cutoff_time.isoformat()}")

    for channel in CHANNELS:
        print(f"\n--- {channel} ---")
        html = fetch_channel(channel)
        if html.startswith("HTTP_ERROR") or html.startswith("FETCH_ERROR"):
            errors.append({"channel": channel, "error": html})
            print(f"  ERROR: {html}")
            continue

        messages = parse_messages(html, channel)

        # Keep only recent messages
        recent = [m for m in messages if is_recent(m)]
        total_recent = len(recent)
        print(f"  Found {len(messages)} total, {total_recent} recent")

        # Show preview of recent messages
        for m in recent:
            preview = m["text"][:200].replace('\n', ' ')
            print(f"  [{m['published'][:19]}] {preview}...")

        all_messages.extend(recent)

    # Build output
    output = {
        "scrape_timestamp": datetime.now(timezone.utc).isoformat(),
        "cutoff_minutes": CUTOFF_MINUTES,
        "total_recent_messages": len(all_messages),
        "channels_checked": CHANNELS,
        "errors": errors,
        "messages": all_messages,
    }

    # Write output
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n=== TOTAL: {len(all_messages)} recent messages written to {OUTPUT_PATH} ===")

    # Also print structured analysis input
    print("\n=== MESSAGE DUMP FOR ANALYSIS ===")
    print(json.dumps(all_messages, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
