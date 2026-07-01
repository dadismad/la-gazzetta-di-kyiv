# Governor v2 — Mailbox Executive Editor (June 2026)

The governor now includes a conversational editorial executive via Gemini. Alex sends directives through Hermes, which writes them to the VM's mailbox. The governor processes them each pipeline cycle and responds.

## Communication Flow

```
Alex (Telegram) → Hermes → SSH write to VM inbox.json
                              ↓
                    Governor cycle reads inbox
                              ↓
                    Gemini API with editorial context
                              ↓
                    Governor writes outbox.json
                              ↓
         Alex ← Hermes reads outbox ← SSH read from VM
```

## Mailbox Format

**Inbox** (`/opt/gazzetta-di-kyiv/mailbox/inbox.json`):
```json
{
  "messages": [
    {
      "id": "msg-001",
      "from": "Alexander (via Hermes)",
      "content": "What narratives need attention?",
      "status": "pending",
      "sent_at": "2026-06-19T15:00:00Z"
    }
  ]
}
```

**Outbox** (`/opt/gazzetta-di-kyiv/mailbox/outbox.json`):
```json
{
  "responses": [
    {
      "id": "msg-001",
      "from": "Executive Editor, La Gazzetta di Kyiv",
      "to": "Alexander (via Hermes)",
      "content": "Based on current data, dollar_decline shows...",
      "at": "2026-06-19T15:02:00Z"
    }
  ]
}
```

## Hermes Send Command (write directive)

```bash
# Write directive to VM inbox
gcloud compute ssh gazzetta-prod --zone=us-central1-a --command="
sudo -u gazzetta tee /opt/gazzetta-di-kyiv/mailbox/inbox.json << 'EOF'
{\"messages\":[{\"id\":\"$(date +%s)\",\"from\":\"Alexander (via Hermes)\",\"content\":\"YOUR MESSAGE\",\"status\":\"pending\",\"sent_at\":\"$(date -Iseconds)\"}]}
EOF"

# Trigger governor to process immediately
gcloud compute ssh gazzetta-prod --zone=us-central1-a --command="
sudo systemctl start gazzetta-governor.service"

# Read response after cycle completes (~10s)
gcloud compute ssh gazzetta-prod --zone=us-central1-a --command="
sudo -u gazzetta cat /opt/gazzetta-di-kyiv/mailbox/outbox.json"
```

## Editorial Context

The executive editor receives a full context snapshot with each directive:
- Total story count and narrative distribution
- Top 5 stories by contradiction gap (headline, gap, tier, container, capital volume)
- Market benchmarks (SPY, QQQ, TLT, DX-Y.NYB, ^VIX)
- Current timestamp

The system prompt establishes the editor as the newspaper's executive with authority to discuss strategy, plan actions, and give editorial direction.

## Gemini Model & Cost

- Model: `gemini-2.0-flash` (fast, cheap)
- Auth: API key from `.env` (`GEMINI_API_KEY`)
- Retry: 3 attempts with exponential backoff (1s/2s/4s)
- Billing: prepaid credits at https://ai.studio/projects
- Key format: `AQ.` prefix (53 chars), NOT `AIza` standard format
