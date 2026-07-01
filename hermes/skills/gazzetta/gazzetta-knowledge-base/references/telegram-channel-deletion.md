# Telegram Channel Bulk Deletion

Technique for wiping all messages from a Telegram channel where the bot is admin.

## Prerequisites
- Bot must be admin of the channel with `can_delete_messages: true` and `can_post_messages: true`
- Channel ID (negative number for channels, e.g., `-1003990434181`)
- Bot token from BotFather

## Verify Permissions
```python
import urllib.request, json
r = urllib.request.urlopen(f'https://api.telegram.org/bot{token}/getChatAdministrators?chat_id={chat_id}')
data = json.loads(r.read())
for admin in data['result']:
    if admin['user']['id'] == BOT_ID:
        print(f"can_delete={admin.get('can_delete_messages')}")
```

## Deletion Algorithm

Telegram bots **cannot list channel messages** via API. The workaround:

1. **Post a probe message** to find the current message ID ceiling:
   ```python
   data = urllib.parse.urlencode({'chat_id': chat_id, 'text': 'probe'}).encode()
   req = urllib.request.Request(f'https://api.telegram.org/bot{token}/sendMessage', data=data, method='POST')
   resp = json.loads(urllib.request.urlopen(req).read())
   ceiling = resp['result']['message_id']
   # Delete the probe
   urllib.request.urlopen(f'https://api.telegram.org/bot{token}/deleteMessage?chat_id={chat_id}&message_id={ceiling}')
   ```

2. **Iterate from ID 1 to ceiling** calling `deleteMessage`:
   ```python
   for mid in range(1, ceiling):
       try:
           r = urllib.request.urlopen(f'https://api.telegram.org/bot{token}/deleteMessage?chat_id={chat_id}&message_id={mid}', timeout=5)
           if json.loads(r.read()).get('ok'):
               deleted += 1
           else:
               failed += 1
       except: failed += 1
       # Rate limit: Telegram allows ~30 msg/sec, play safe at 20/sec
       if (deleted + failed) % 20 == 0:
           print(f'{deleted} deleted, {failed} failed at ID {mid}')
       if deleted % 20 == 0 and deleted > 0:
           time.sleep(1)
   ```

3. **Result**: `deleted + failed = ceiling - 1`. Most "failures" are messages that never existed (empty IDs), which is expected.

## Pitfalls
- `getUpdates` does NOT return channel post updates for message IDs the bot didn't post itself. Don't use it.
- Message IDs are sequential but non-contiguous — expect many IDs to have no message.
- Rate limit is ~30 messages/second. Building in a 1-second sleep every 20 messages is safe.
- The probe message MUST be deleted after getting the ceiling ID, or it becomes the only remaining message.
- If channel has thousands of messages, this takes minutes. Consider running as a background process with `notify_on_complete: true`.
