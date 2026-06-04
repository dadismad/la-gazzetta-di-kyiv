#!/usr/bin/env python3
"""Fetch latest messages from Telegram channels using the Bot API."""
import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse

# Read bot token from .env
env_path = os.path.expanduser("~/.hermes/.env")
token = None
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("TELEGRAM_BOT_TOKEN=") and not line.startswith("#"):
            token = line.split("=", 1)[1].strip()
            break

if not token or token.startswith("***") or len(token) < 20:
    print(f"ERROR: Invalid bot token (len={len(token) if token else 0})")
    sys.exit(1)

API = f"https://api.telegram.org/bot{token}"

# Channels to monitor
CHANNELS = [
    "@trad_fin",
    "@MonitoringSituation",
    "@ASupersharij",
    "@infinityhedge",
    "@ethanlevins",
    "@markettwits",
]

def api_call(method, params=None):
    url = f"{API}/{method}"
    data = None
    if params:
        data = urllib.parse.urlencode(params).encode()
    try:
        req = urllib.request.Request(url, data=data)
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()
            return json.loads(body)
        except:
            return {"ok": False, "error": f"HTTP {e.code}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def main():
    results = {}
    
    # First get bot info
    me = api_call("getMe")
    if not me.get("ok"):
        print(f"Bot API unreachable: {me}")
        sys.exit(1)
    bot_name = me.get("result", {}).get("username", "UNKNOWN")
    print(f"Bot: @{bot_name}")
    results["_bot"] = bot_name
    results["_fetched_at"] = int(time.time())
    
    # Try getUpdates to see what's visible
    updates = api_call("getUpdates", {
        "timeout": 3,
        "allowed_updates": json.dumps(["message", "channel_post"])
    })
    print(f"Updates available: {len(updates.get('result', []))} items")
    results["_updates_count"] = len(updates.get("result", []))
    
    # Build a map of chat_id -> messages from updates
    update_msgs = {}
    if updates.get("ok"):
        for update in updates.get("result", []):
            msg = update.get("message") or update.get("channel_post")
            if msg:
                chat = msg.get("chat", {})
                cid = str(chat.get("id"))
                if cid not in update_msgs:
                    update_msgs[cid] = []
                update_msgs[cid].append({
                    "update_id": update["update_id"],
                    "message_id": msg.get("message_id"),
                    "date": msg.get("date"),
                    "text": msg.get("text", ""),
                    "caption": msg.get("caption", ""),
                })
    
    for channel in CHANNELS:
        print(f"\n=== {channel} ===")
        
        # Get chat info
        chat_info = api_call("getChat", {"chat_id": channel})
        if not chat_info.get("ok"):
            print(f"  getChat failed: {chat_info.get('error', 'unknown')}")
            results[channel] = {"error": chat_info.get("error", "unknown")}
            continue
        
        result = chat_info["result"]
        chat_id = str(result.get("id"))
        print(f"  Chat: {result.get('title', 'N/A')} (id={chat_id})")
        
        # Check if bot is in the chat
        member_info = api_call("getChatMember", {"chat_id": channel, "user_id": me["result"]["id"]})
        print(f"  Bot membership: {'OK' if member_info.get('ok') else member_info.get('error', 'N/A')}")
        
        channel_data = {
            "chat_id": chat_id,
            "title": result.get("title", ""),
            "username": result.get("username", ""),
            "type": result.get("type", ""),
        }
        
        # Check if we have messages from this chat in updates
        if chat_id in update_msgs:
            msgs = update_msgs[chat_id]
            msgs.sort(key=lambda x: x["date"])
            channel_data["messages"] = msgs[-20:]  # last 20
            for m in msgs[-5:]:
                ts = time.strftime("%H:%M:%S UTC", time.gmtime(m["date"]))
                text = (m.get("text") or m.get("caption") or "")[:300]
                print(f"  [{ts}] #{m['message_id']}: {text}")
        else:
            channel_data["messages"] = []
            print(f"  No messages visible to bot")
        
        results[channel] = channel_data

    # Save results
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "latest_raw.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {out_path}")
    
    # Also output a summary JSON for downstream consumption
    summary = []
    ch_names = {
        "@trad_fin": "trad_fin",
        "@MonitoringSituation": "MonitoringSituation",
        "@ASupersharij": "ASupersharij",
        "@infinityhedge": "infinityhedge",
        "@ethanlevins": "ethanlevins",
        "@markettwits": "markettwits",
    }
    for ch, alias in ch_names.items():
        ch_data = results.get(ch, {})
        if "messages" in ch_data and ch_data["messages"]:
            for msg in ch_data["messages"]:
                summary.append({
                    "channel": alias,
                    "channel_handle": ch,
                    "message_id": msg.get("message_id"),
                    "timestamp": msg.get("date"),
                    "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(msg.get("date", 0))),
                    "text": msg.get("text") or msg.get("caption") or "",
                })
    summary_out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "messages_summary.json")
    with open(summary_out, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Summary saved to {summary_out}")
    print(f"Total messages collected: {len(summary)}")

if __name__ == "__main__":
    main()
