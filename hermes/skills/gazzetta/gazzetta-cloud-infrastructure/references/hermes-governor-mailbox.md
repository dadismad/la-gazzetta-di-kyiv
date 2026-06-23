# Hermes ↔ Governor Mailbox Protocol

## Architecture

The Cloud Governor (`governor.py`) on the VM now serves as an **editorial executive** — a conversational Gemini persona that can discuss newspaper strategy, give editorial guidance, and plan actions. Communication flows through a file-based mailbox.

```
Alex (Telegram) → Hermes → SSH → /opt/gazzetta-di-kyiv/mailbox/inbox.json
                                        │
                              governor.py (every 10 min)
                                        │
                              Gemini API + editorial context
                                        │
                            /opt/gazzetta-di-kyiv/mailbox/outbox.json
                                        │
                            Hermes reads → relays to Alex
```

## Inbox Format

```json
{
  "messages": [
    {
      "id": "msg-001",
      "from": "Alexander (via Hermes)",
      "content": "What narratives need attention right now?",
      "status": "pending",
      "sent_at": "2026-06-19T15:00:00Z"
    }
  ]
}
```

## Outbox Format

```json
{
  "responses": [
    {
      "id": "msg-001",
      "from": "Executive Editor, La Gazzetta di Kyiv",
      "to": "Alexander (via Hermes)",
      "content": "Based on current data...",
      "at": "2026-06-19T15:10:00Z"
    }
  ]
}
```

## Sending a Directive (from Hermes)

```bash
# 1. Write inbox.json
gcloud compute ssh gazzetta-prod --zone=us-central1-a --command="
sudo -u gazzetta tee /opt/gazzetta-di-kyiv/mailbox/inbox.json << 'EOF'
{...}
EOF"

# 2. Trigger governor (it auto-processes mailbox before pipeline)
sudo systemctl start gazzetta-governor.service

# 3. Read response after governor completes
gcloud compute ssh gazzetta-prod --zone=us-central1-a --command="
sudo -u gazzetta cat /opt/gazzetta-di-kyiv/mailbox/outbox.json"
```

## Editorial Context

The Gemini executive editor receives a context snapshot each cycle:
- Time of query
- Total story count
- Top 5 stories by contradiction gap
- Narrative distribution (stories per narrative)
- Market benchmarks (SPY, QQQ, TLT, DX-Y.NYB, ^VIX)

## System Prompt

The editor persona is defined as:
- Executive Editor of La Gazzetta di Kyiv
- Capital-flow newspaper tracking money vs official narrative
- Grades stories by contradiction_gap (0-100)
- 8 narratives: dollar decline, deglobalization, China's ascent, space economy, gene editing, tech convergence, energy sovereignty, wealthy sports
- Responds in plain, direct English
- When asked for opinion, gives it
- When asked to execute, confirms what it will do

## Gemini API

- Uses Gemini API key from `.env` (`GEMINI_API_KEY`)
- Model: `gemini-2.0-flash`
- Retry: 3 attempts with exponential backoff (1s/2s/4s) on 429 rate limits
- Free tier has severe rate limits — add billing at https://aistudio.google.com/apikey
- Vertex AI (enterprise platform) was attempted but blocked by unaccepted ToS
