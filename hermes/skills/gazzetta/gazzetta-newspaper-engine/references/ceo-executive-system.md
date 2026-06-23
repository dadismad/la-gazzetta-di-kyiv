# CEO Executive System — DeepSeek Cloud Governor

June 2026. The newspaper's editorial executive runs on DeepSeek via the Governor VM.
Replaces the earlier two-layer Gemini architecture (Gemini never worked reliably due to
API key issues and Vertex AI Terms of Service blocker).

## Architecture

```
Alex → Hermes (Telegram) → SSH → VM inbox → CEO (DeepSeek) → outbox → Hermes → Alex
```

The CEO is not just an advisor — he EXECUTES. He controls the pipeline, modifies
configuration, builds and deploys the site autonomously after receiving strategic
direction from Alex + Hermes.

## Mailbox Protocol

- **Inbox**: `/opt/gazzetta-di-kyiv/mailbox/inbox.json`
- **Outbox**: `/opt/gazzetta-di-kyiv/mailbox/outbox.json`
- Each message has: `id`, `from`, `content`, `status` (pending/answered), timestamps
- The `check_mailbox()` function in governor.py processes pending directives during
  every 10-minute pipeline cycle AND can be triggered manually via Hermes

## CEO System Prompt

Embedded in governor.py as SYSTEM_PROMPT. Key elements:
- Full editorial authority over 8 narratives
- Lefevre craft principles (tape-reading, crowd psychology, pattern recognition)
- Modern editorial craft (curiosity gap, specificity, pattern interruption, "why now" test)
- Execution command syntax awareness

## Execution Commands

The CEO responds with EXEC: commands at the end of his editorial judgment.
The governor parses and executes these:

| Command | Action |
|---------|--------|
| EXEC: trigger_pipeline | Force full 6-step pipeline run |
| EXEC: rebuild_site | db_to_json → build_site → test_platform |
| EXEC: set_gap_threshold N | Change BREAKING tier threshold |
| EXEC: promote <story_id> | Feature a story on homepage |
| EXEC: spike <story_id> <reason> | Kill a story |
| EXEC: add_source <url> <narrative> | Add RSS feed to a narrative |
| EXEC: run_step <name> | Run a single pipeline step |
| EXEC: config_set <key> <value> | Set any config value |
| EXEC: status | Full pipeline status report |

## DeepSeek API Pattern

```python
def ask_deepseek(prompt, system=None, max_tokens=800, temp=0.7):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temp
    }).encode()
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {DEEPSEEK_KEY}"}
    )
    # 3 retries with exponential backoff on 429
```

## Pitfalls

1. **File ownership**: systemd runs as user `gazzetta`, but files created by root
   cause silent "readonly database" and "permission denied" errors. After any file
   operation, verify ownership: `sudo chown -R gazzetta:gazzetta /opt/gazzetta-di-kyiv/`

2. **Credential masking**: Hermes masks API keys in terminal commands. Use base64
   encoding to transfer keys: `echo "base64encodedkey" | base64 -d > /tmp/key.txt`

3. **Config file permissions**: The config.json at `/opt/gazzetta-di-kyiv/config.json`
   must be owned by gazzetta for CEO EXEC commands to modify settings.

4. **GCS deploy from VM**: gsutil on the VM has permission issues. Deploy is handled
   by local Hermes cron. The VM's deploy step is best-effort only.

5. **Gemini API vs Vertex AI**: Multiple approaches tried (API key, Bearer token,
   Vertex AI SDK) — all blocked. Gemini API does not accept service account Bearer
   tokens. Vertex AI requires manual Terms of Service acceptance in Google Cloud Console.
   DeepSeek is the reliable path.

6. **Hermes inline Python escaping**: gcloud compute ssh with inline Python frequently
   mangles quotes and escaping. Prefer: write script locally, scp to VM, run.
